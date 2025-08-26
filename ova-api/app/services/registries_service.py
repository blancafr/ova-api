from fastapi import Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import shutil
import os

from collections import Counter, defaultdict
from typing import Optional, Dict
from datetime import date, datetime

from app.db.registry_database import get_db
from app.crud.registry import get_latest_date_records, create_registry_record, get_registries
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

def get_disease_counts(db: Session, start_date: Optional[date], end_date: Optional[date], sex: Optional[str], age: Optional[str]) -> Dict[str, int]:
    registries = get_registries(db, start_date, end_date, sex, age)
    counter = Counter()
    for rec in registries:
        for d in rec.diseases.split(","):
            counter[d.strip().lower()] += 1
    return dict(counter)

def get_total_patients(db: Session, start_date: Optional[date], end_date: Optional[date], sex: Optional[str], age: Optional[str]) -> int:
    registries = get_registries(db, start_date, end_date, sex, age)
    return len(registries)

def get_avg_diseases_per_patient(db: Session, start_date: Optional[date], end_date: Optional[date], sex: Optional[str], age: Optional[str]) -> float:
    registries = get_registries(db, start_date, end_date, sex, age)
    if not registries:
        return 0
    total_diseases = sum(len(r.diseases.split(",")) for r in registries)
    return total_diseases / len(registries)

def get_patients_per_day(db: Session, start_date: Optional[date], end_date: Optional[date], sex: Optional[str], age: Optional[str]) -> Dict[date, int]:
    registries = get_registries(db, start_date, end_date, sex, age)
    daily_counts = defaultdict(int)
    for r in registries:
        daily_counts[r.date] += 1
    return dict(sorted(daily_counts.items()))
