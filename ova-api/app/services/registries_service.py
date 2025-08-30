from fastapi import Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import shutil
import os

from collections import Counter, defaultdict
from typing import Optional, Dict, List, Tuple
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

def _normalize_disease_name(name: str) -> str:
    return (name or "").strip().lower()

def _split_diseases(raw: str) -> List[str]:
    if not raw:
        return []
    return [d.strip().lower() for d in raw.split(",") if d.strip()]

def _registries_for_disease(
    db: Session,
    disease: str,
    start_date: Optional[date],
    end_date: Optional[date],
    sex: Optional[str],
    age: Optional[str],
):
    target = _normalize_disease_name(disease)
    base = get_registries(db, start_date, end_date, sex, age)
    return [r for r in base if target in _split_diseases(r.diseases)]

def get_disease_total_patients(
    db: Session, disease: str, start_date: Optional[date], end_date: Optional[date],
    sex: Optional[str], age: Optional[str]
) -> int:
    regs = _registries_for_disease(db, disease, start_date, end_date, sex, age)
    return len(regs)

def get_disease_gender_distribution(
    db: Session, disease: str, start_date: Optional[date], end_date: Optional[date],
    sex: Optional[str], age: Optional[str]
) -> Dict[str, int]:
    regs = _registries_for_disease(db, disease, start_date, end_date, sex, age)
    c = Counter()
    for r in regs:
        if r.sex:
            c[r.sex] += 1
    return dict(c)

def get_disease_age_distribution(
    db: Session, disease: str, start_date: Optional[date], end_date: Optional[date],
    sex: Optional[str], age: Optional[str]
) -> Dict[str, int]:
    regs = _registries_for_disease(db, disease, start_date, end_date, sex, age)
    c = Counter()
    for r in regs:
        if r.age:
            c[r.age] += 1
    return dict(c)

def get_disease_related(
    db: Session, disease: str, start_date: Optional[date], end_date: Optional[date],
    sex: Optional[str], age: Optional[str]
) -> List[Tuple[str, int]]:
    regs = _registries_for_disease(db, disease, start_date, end_date, sex, age)
    target = _normalize_disease_name(disease)
    c = Counter()
    for r in regs:
        for d in _split_diseases(r.diseases):
            if d and d != target:
                c[d] += 1
    return sorted(c.items(), key=lambda x: x[1], reverse=True)

def get_disease_patients_per_day(
    db: Session,
    disease: str,
    start_date: Optional[date],
    end_date: Optional[date],
    sex: Optional[str],
    age: Optional[str],
):
    regs_disease = _registries_for_disease(db, disease, start_date, end_date, sex, age)
    daily_counts = defaultdict(int)
    for r in regs_disease:
        daily_counts[r.date] += 1
    # ordenado por fecha asc
    return dict(sorted(daily_counts.items()))

def get_disease_proportion_overall(
    db: Session,
    disease: str,
    start_date: Optional[date],
    end_date: Optional[date],
    sex: Optional[str],
    age: Optional[str],
) -> float:
    regs_disease = _registries_for_disease(db, disease, start_date, end_date, sex, age)
    regs_all = get_registries(db, start_date, end_date, sex, age)
    total = len(regs_disease)
    total_global = len(regs_all) if regs_all is not None else 0
    return (total / total_global) if total_global else 0.0