from pydantic import BaseModel

class PatientCreate(BaseModel):
    gender: str
    age: str
    disease: str
    comment: str
    date: str
