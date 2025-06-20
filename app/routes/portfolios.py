import os
import requests
import shutil
import pandas as pd 
from pydantic import BaseModel
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse, RedirectResponse
from app.services.file_handler import save_csv, save_received_csv, get_csv_path, portfolio_to_html, load_portfolio, get_load_portfolio
from app.services.lookthrough import run_lookthrough, check_local_availability
from app.services.indexing import load_index, add_received_entry
from app.deps import templates
from app.config import DATA_DIR, SERVER_ADDRESS

router = APIRouter()

UPLOAD_DIR = os.path.join(DATA_DIR, "portfolios")
RECEIVED_DIR = os.path.join(DATA_DIR, "received_portfolios")

@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.get("/upload/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    saved_path = save_csv(file)
    #return {"status": "uploaded", "file": saved_path}
    return RedirectResponse(url="/portfolios", status_code=303)

@router.get("/portfolios/", response_class=HTMLResponse)
async def upload_form(request: Request):
    df = load_index(index='owned')
    rows = df.to_dict(orient='records')
    return templates.TemplateResponse("portfolios.html", {
        "request": request,
        "rows": rows,
    })

@router.get("/files/")
async def get_files(request: Request):
    files = 'load_owned_index()'

    return templates.TemplateResponse("files.html", {"request": request, "files": files})

@router.post("/trigger-lookthrough/{portfolio_id}/{navdate}/")
async def trigger_lookthrough(portfolio_id: str, navdate: str):
    await run_lookthrough(portfolio_id=portfolio_id, navdate=navdate)
    #return {"status": "calculated"}
    return RedirectResponse(url=f"/portfolios/{portfolio_id}/{navdate}/", status_code=303)

@router.post("/webhook/receive-file/")
async def receive_file(file: UploadFile = File(...)):
    save_received_csv(file)
    return {"status": "received", "filename": file.filename}
    
class FileRequest(BaseModel):
    portfolio_id: str
    navdate: str
    receiver_url: str

@router.post("/webhook/send-file/")
def send_file(request: FileRequest):
    file_path = os.path.join(UPLOAD_DIR, get_csv_path(portfolio_id=request.portfolio_id, navdate=request.navdate, status="owned"))

    print(file_path)
    print(request.receiver_url)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    file_name = f"{request.portfolio_id}_{request.navdate}.csv"

    with open(file_path, "rb") as f:
        files = {"file": (file_name, f)}
        try:
            response = requests.post(request.receiver_url, files=files, timeout=10)
            print(f"Status: {response.status_code}, Body: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return {"status": "sent", "to": request.receiver_url, "response": response.json()}

COLUMNS_TO_DISPLAY = [
    "14_Identification_code_of_the_instrument",
    "17_Instrument_name",
    "21_Quotation_currency_(A)",
    "24_Market_valuation_in_portfolio_currency_(B)"
]

@router.get("/portfolios/{portfolio_id}/{nav_date}/")
async def index(request: Request, portfolio_id: str, nav_date: str):
    main_df = get_load_portfolio(portfolio_id=portfolio_id, navdate=nav_date)
    
    portfolio_name = main_df['3_Portfolio_name'][0]
    
    main_df = main_df[COLUMNS_TO_DISPLAY + ["15_Type_of_identification_code_for_the_instrument"]]
    data = main_df.to_dict(orient="records")

    child_data = {}
    for row in data:
        instrument_id = row.get("14_Identification_code_of_the_instrument")
        type_code = row.get("15_Type_of_identification_code_for_the_instrument")
        if str(type_code) == "99" and instrument_id:
            instrument_id = str(instrument_id).strip()
            
            child_df = get_load_portfolio(portfolio_id=instrument_id, navdate=nav_date)
            
            if child_df is not None:
                if all(col in child_df.columns for col in COLUMNS_TO_DISPLAY):
                    child_df = child_df[COLUMNS_TO_DISPLAY]

                child_data[instrument_id] = {
                    "columns": COLUMNS_TO_DISPLAY,
                    "rows": child_df.to_dict(orient="records")
                }

    return templates.TemplateResponse("portfolio_view.html", {
        "request": request,
        "data": data,
        "child_data": child_data,
        "portfolio_id": portfolio_id,
        "navdate": nav_date,
        "portfolio_name": portfolio_name
    })