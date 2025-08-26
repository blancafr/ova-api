from sqlalchemy.orm import Session
from app.auth.security import get_password_hash, verify_password
from app.schemas.user import UserCreate
from app.models.user import User


def create_user(*, db: Session, user_create: UserCreate) -> User:
    db_user = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        full_name=user_create.full_name,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(*, db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate(*, db: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(db=db, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
