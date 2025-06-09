import os
import shutil
from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from app.services.file_handler import save_csv, get_csv_path
from app.services.transfer import send_file_ws, fetch_file_ws
from app.services.calculator import run_lookthrough
from app.deps import templates

router = APIRouter()

UPLOAD_DIR = "app/data/portfolios"

@router.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    saved_path = save_csv(file)
    return {"status": "uploaded", "file": saved_path}

@router.post("/trigger-lookthrough/{filename}")
async def trigger_lookthrough(filename: str):
    path = get_csv_path(filename)
    results = run_lookthrough(path)
    return {"status": "calculated", "results": results}

@router.websocket("/ws/fetch/{filename}")
async def websocket_fetch(websocket: WebSocket, filename: str):
    await websocket.accept()
    try:
        file_path = get_csv_path(filename)
        with open(file_path, "rb") as f:
            await websocket.send_bytes(f.read())
    except FileNotFoundError:
        await websocket.send_text("error: file not found")
    finally:
        await websocket.close()

@router.websocket("/ws/send/{filename}")
async def websocket_send(websocket: WebSocket, filename: str):
    await websocket.accept()
    save_path = get_csv_path(f"received_{filename}")
    with open(save_path, "wb") as f:
        try:
            data = await websocket.receive_bytes()
            f.write(data)
        except WebSocketDisconnect:
            pass
    await websocket.close()
