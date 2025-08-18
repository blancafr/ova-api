from pydantic import BaseModel, Field

class PatientCreate(BaseModel):
    gender: str = Field(..., alias="sexo")
    age: str = Field(..., alias="edad")
    disease: str = Field(..., alias="enfermedad")
    comment: str = Field(..., alias="comentario")
    date: str = Field(..., alias="fecha")

class Patient(BaseModel):
    pass

class PatientInDB(Patient):
    class Config:
        from_attributes = True