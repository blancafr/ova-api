from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session
from app.auth.auth import get_current_active_superuser

from app.db.registry_database import get_db
from app.services.registries_service import (
    get_disease_counts,
    get_total_patients,
    get_avg_diseases_per_patient,
    get_patients_per_day,
)

router = APIRouter(dependencies=[Depends(get_current_active_superuser)])

@router.get("/total-patients")
def total_patients(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return {"total_patients": get_total_patients(db, start_date, end_date, sex, age)}

@router.get("/disease-counts")
def disease_counts(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return {"disease_counts": get_disease_counts(db, start_date, end_date, sex, age)}

@router.get("/avg-diseases-per-patient")
def avg_diseases_per_patient(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return {"avg_diseases_per_patient": get_avg_diseases_per_patient(db, start_date, end_date, sex, age)}

@router.get("/patients-per-day")
def patients_per_day(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return {"patients_per_day": get_patients_per_day(db, start_date, end_date, sex, age)}
