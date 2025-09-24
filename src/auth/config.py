import os
from pathlib import Path

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    SMTP_SERVER: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    FROM_EMAIL: EmailStr | None = None

    class Config:
        env_file = str(Path(__file__).parent.parent / ".env")
        extra = "forbid"


auth_settings = AuthSettings(
    SECRET_KEY=os.getenv("SECRET_KEY", "changeme"),
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=int(
        os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES", 15)
    ),
    SMTP_SERVER=os.getenv("SMTP_SERVER"),
    SMTP_PORT=int(os.getenv("SMTP_PORT", 0)) if os.getenv("SMTP_PORT") else None,
    SMTP_USER=os.getenv("SMTP_USER"),
    SMTP_PASSWORD=os.getenv("SMTP_PASSWORD"),
    FROM_EMAIL=os.getenv("FROM_EMAIL"),
)
