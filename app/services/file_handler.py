import os
import shutil
from fastapi import UploadFile
from app.config import UPLOAD_DIR

portfolios_dir = os.path.join(UPLOAD_DIR, "portfolios")

def save_csv(file: UploadFile) -> str:
    os.makedirs(portfolios_dir, exist_ok=True)
    path = os.path.join(portfolios_dir, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file.filename

def get_csv_path(filename: str) -> str:
    return os.path.join(portfolios_dir, filename)
