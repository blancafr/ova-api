
import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

from pydantic import (
    EmailStr,
)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file (one level above ./backend/)
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    SECRET_KEY: str = secrets.token_urlsafe(32)
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

settings = Settings()  # type: ignore
