from fastapi import UploadFile, File, APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import shutil
import os
from datetime import datetime

from app.db.registry_database import get_db
from app.crud.registry import get_latest_date_records, create_registry_record
from app.processing.pipeline import process_image_file

UPLOAD_DIR = "uploads"

def save_upload_file(file):
    file_location = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    print(f"{datetime.now().isoformat()}: Imagen recibida: {file.filename}")
    return

def process_upload_file(file, db: Session = Depends(get_db)):
    file_location = f"{UPLOAD_DIR}/{file.filename}"

    latest_records = get_latest_date_records(db)

    new_records = process_image_file(file_location, latest_records)

    if new_records:
        for record in new_records:
            create_registry_record(db, record)
    return new_records

def list_uploaded_images():
    files = os.listdir(UPLOAD_DIR)
    images = [file for file in files if file.lower().endswith((".jpg", ".jpeg", ".png"))]
    html_content = "<html><body><h2>Imágenes subidas:</h2>"
    for image in images:
        html_content += f'<img src="/images/{image}" alt="{image}" width="300" /><br>'
    html_content += "</body></html>"
    return HTMLResponse(content=html_content)