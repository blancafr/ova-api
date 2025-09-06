
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, Field
from typing import Annotated
import uuid

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: Annotated[str, Field(min_length=8, max_length=40)]


class UserRegister(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=40)]
    full_name: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserPublic(UserBase):
    id: uuid.UUID

class TokenPayload(BaseModel):
    sub: str | None = None
