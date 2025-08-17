from typing import List
from pydantic import BaseModel, validator
from datetime import date

class RegistryBase(BaseModel):
    row_num: int
    date: date
    id: str
    sex: str
    age: str
    diseases: List[str]

class RegistryCreate(RegistryBase):
    pass

class RegistryInDB(RegistryBase):
    @validator("diseases", pre=True)
    def parse_diseases(cls, v):
        if isinstance(v, str):
            return [d.strip() for d in v.split(",")]
        return v
    class Config:
        from_attributes=True
