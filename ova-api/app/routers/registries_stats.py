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
    get_disease_age_distribution,
    get_disease_related,
    get_disease_gender_distribution,
    get_disease_total_patients,
    get_disease_patients_per_day,
    get_disease_proportion_overall
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

@router.get("/disease/total")
def disease_total(
    disease: str = Query(..., description="Nombre exacto de la enfermedad"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    total = get_disease_total_patients(db, disease, start_date, end_date, sex, age)
    return {"total": total}

@router.get("/disease/gender")
def disease_gender(
    disease: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    dist = get_disease_gender_distribution(db, disease, start_date, end_date, sex, age)
    return {"gender_distribution": dist}

@router.get("/disease/age")
def disease_age(
    disease: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    dist = get_disease_age_distribution(db, disease, start_date, end_date, sex, age)
    return {"age_distribution": dist}

@router.get("/disease/related")
def disease_related(
    disease: str = Query(...),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = get_disease_related(db, disease, start_date, end_date, sex, age)
    return {"related_diseases": data}

@router.get("/disease/per-day")
def disease_per_day(
    disease: str = Query(..., description="Nombre exacto de la enfermedad"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    data = get_disease_patients_per_day(db, disease, start_date, end_date, sex, age)
    return {"patients_per_day": data}

@router.get("/disease/proportion")
def disease_proportion(
    disease: str = Query(..., description="Nombre exacto de la enfermedad"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    sex: Optional[str] = Query(None),
    age: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    p = get_disease_proportion_overall(db, disease, start_date, end_date, sex, age)
    return {"proportion": p}