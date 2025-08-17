from typing import List
from sqlalchemy.orm import Session
from app.models.registry import Registry
from app.schemas.registry import RegistryCreate, RegistryInDB
from datetime import date
from sqlalchemy import func

def create_registry_record(db: Session, record: RegistryCreate):
    db_record = Registry(
        id=record.id,
        row_num=record.row_num,
        date=record.date,
        sex=record.sex,
        age=record.age,
        diseases=",".join(record.diseases)
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_latest_date_records(db: Session):
    latest_date = db.query(func.max(Registry.id)).scalar()
    if not latest_date:
        return []
    
    records = db.query(Registry).filter(Registry.id == latest_date).all()
    registries = [RegistryInDB.from_orm(r) for r in records]
    return registries

