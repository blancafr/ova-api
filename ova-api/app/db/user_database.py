from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.schemas.user import UserCreate
from app.config import settings
from app.crud import user as user_crud

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from app.models import user  # importa modelos

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """Initialize the database with a superuser if it doesn't exist."""
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        u = user_crud.get_user_by_email(db=db, email=settings.FIRST_SUPERUSER)
        if not u:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user_crud.create_user(session=db, user_create=user_in)
    finally:
        db.close()
