import os
import requests
import shutil
import pandas as pd 
from pydantic import BaseModel
from pathlib import Path
from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from app.services.file_handler import save_csv, get_csv_path, portfolio_to_html
from app.services.transfer import send_file_ws, fetch_file_ws
from app.services.lookthrough import run_lookthrough
from app.services.indexing import load_owned_index
from app.deps import templates
from app.config import DATA_DIR

router = APIRouter()

UPLOAD_DIR = os.path.join(DATA_DIR, "portfolios")
RECEIVED_DIR = os.path.join(DATA_DIR, "received_portfolios")

@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    saved_path = save_csv(file)
    return {"status": "uploaded", "file": saved_path}

@router.get("/files/")
async def get_files(request: Request):
    files = load_owned_index()

    return templates.TemplateResponse("my_portfolios.html", {"request": request, "files": files})

@router.get("/files/{filename}", response_class=HTMLResponse)
async def portfolio_view(request: Request, filename: str):
    table = portfolio_to_html(filename)
    return templates.TemplateResponse("portfolio_view.html", {"request": request, "file": table})

@router.post("/trigger-lookthrough/{filename}")
async def trigger_lookthrough(filename: str):
    path = get_csv_path(filename)
    results = run_lookthrough(path)
    return {"status": "calculated", "results": results}

@router.post("/webhook/receive-file")
async def receive_file(file: UploadFile = File(...)):
    path = os.path.join(RECEIVED_DIR, file.filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"status": "received", "filename": file.filename}

@router.get("/request-file", response_class=HTMLResponse)
async def get_request_form():
    return """
    <html>
        <head><title>Request File</title></head>
        <body>
            <h2>Request File from Sender</h2>
            <form action="/request-file" method="post">
                Sender URL: <input type="text" name="sender_url" value="http://localhost:8000"><br>
                File Name: <input type="text" name="file_name"><br>
                <input type="submit" value="Request File">
            </form>
        </body>
    </html>
    """

@router.post("/request-file")
async def request_file_form(
    sender_url: str = Form(...),
    file_name: str = Form(...)
):
    receiver_webhook = "http://localhost:8001/webhook/receive-file"

    response = requests.post(
        f"{sender_url}/webhook/send-file",
        json={"file_name": file_name, "receiver_url": receiver_webhook}
    )

    result = response.json()
    return HTMLResponse(f"""
        <html>
            <body>
                <h3>Request Sent</h3>
                <p>Status: {response.status_code}</p>
                <p>Response: {result}</p>
                <a href="/request-file">Back</a>
            </body>
        </html>
    """)
    
class FileRequest(BaseModel):
    file_name: str
    receiver_url: str

@router.post("/webhook/send-file")
def send_file(request: FileRequest):
    file_path = os.path.join(UPLOAD_DIR, request.file_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, "rb") as f:
        files = {"file": (request.file_name, f)}
        response = requests.post(request.receiver_url, files=files)

    return {"status": "sent", "to": request.receiver_url, "response": response.json()}

COLUMNS_TO_DISPLAY = [
    "14_Identification_code_of_the_instrument",
    "17_Instrument_name",
    "21_Quotation_currency_(A)",
    "24_Market_valuation_in_portfolio_currency_(B)"
]

@router.get("/portfolio/{portfolio_id}/{nav_date}")
async def index(request: Request, portfolio_id: str, nav_date: str):
    main_df = pd.read_csv(os.path.join(UPLOAD_DIR, f"{portfolio_id}_{nav_date}.csv"))
    main_df = main_df[COLUMNS_TO_DISPLAY + ["15_Type_of_identification_code_for_the_instrument"]]  # needed for logic
    data = main_df.to_dict(orient="records")

    # Child portfolios
    child_data = {}
    for row in data:
        instrument_id = row.get("14_Identification_code_of_the_instrument")
        type_code = row.get("15_Type_of_identification_code_for_the_instrument")
        if str(type_code) == "99" and instrument_id:
            file_path = os.path.join(UPLOAD_DIR, f"{str(instrument_id).strip()}_20250531.csv")
            if os.path.exists(file_path):
                child_df = pd.read_csv(file_path)
                # Use same subset of columns
                if all(col in child_df.columns for col in COLUMNS_TO_DISPLAY):
                    child_df = child_df[COLUMNS_TO_DISPLAY]
                child_data[instrument_id] = {
                    "columns": COLUMNS_TO_DISPLAY,
                    "rows": child_df.to_dict(orient="records")
                }

    return templates.TemplateResponse("table.html", {
        "request": request,
        "data": data,
        "child_data": child_data
    })