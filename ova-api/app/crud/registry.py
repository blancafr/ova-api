from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.registry import Registry
from app.schemas.registry import RegistryCreate, RegistryInDB
from datetime import date
from sqlalchemy import func, and_

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

def get_registries(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    sex: Optional[str] = None,
    age: Optional[str] = None,
) -> List[Registry]:
    query = db.query(Registry)
    
    filters = []
    if start_date:
        filters.append(Registry.date >= start_date)
    if end_date:
        filters.append(Registry.date <= end_date)
    if sex:
        filters.append(Registry.sex == sex)
    if age:
        filters.append(Registry.age == age)
    
    if filters:
        query = query.filter(and_(*filters))
    
    return query.all()

