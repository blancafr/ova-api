from datetime import timedelta
from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.crud.user import create_user, get_user_by_email, authenticate
from app.auth.security import create_access_token
from app.auth.auth import get_current_active_superuser, CurrentUser
from app.config import settings
from app.schemas.user import Token, UserCreate, UserPublic
from app.db.user_database import get_db

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_db)]

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    user = authenticate(db=session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(access_token=create_access_token(user.id, expires_delta=access_token_expires))

@router.get("/me", response_model=UserPublic)
def read_me(current_user: CurrentUser) -> Any:
    return current_user

@router.post("/create", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
def create_user_endpoint(*, session: SessionDep, user_in: UserCreate) -> Any:
    user = get_user_by_email(db=session, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="The user with this email already exists in the system.")
    return create_user(db=session, user_create=user_in)
