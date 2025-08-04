from sqlalchemy import Column, Integer, String
from app.db.patient_database import Base

class Patient(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    gender = Column("sexo", String, index=True)
    age = Column("edad", String)
    disease = Column("enfermedad", String)
    comment = Column("comentario", String)
    date_registered = Column("fecha_registro", String)