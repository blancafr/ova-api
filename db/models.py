from sqlalchemy import Column, Integer, String
from .config import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    sexo = Column(String, index=True)
    edad = Column(String)
    enfermedad = Column(String)
    comentario = Column(String)
    fecha_registro = Column(String)