from fastapi import APIRouter, Depends, HTTPException
from app.schemas.patient import PatientCreate
from app.db.patient_database import get_db
from app.crud import patient as patient_crud
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/paciente/")
async def create_patient(p: PatientCreate, db: Session = Depends(get_db)):
    try:
        return patient_crud.create_patient(db, p)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating patient: {e}")