from pydantic import BaseModel

class PacienteCreate(BaseModel):
    sexo: str
    edad: str
    enfermedad: str
    comentario: str
    fecha: str
