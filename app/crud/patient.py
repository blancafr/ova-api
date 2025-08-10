from app.models.patient import Patient
from app.schemas.patient import PatientCreate
from sqlalchemy.orm import Session

def create_patient(db: Session, patient: PatientCreate) :
    db_patient = Patient(
        gender=patient.gender,
        age=patient.age,
        comment=patient.comment,
        disease=patient.disease,
        date_registered=patient.date
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient
