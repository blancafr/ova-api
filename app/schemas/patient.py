from pydantic import BaseModel, Field

class PatientCreate(BaseModel):
    gender: str = Field(..., alias="sexo")
    age: str = Field(..., alias="edad")
    disease: str = Field(..., alias="enfermedad")
    comment: str = Field(..., alias="comentario")
    date: str = Field(..., alias="fecha")