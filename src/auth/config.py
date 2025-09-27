# src/auth/config.py
from pathlib import Path

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    SECRET_KEY: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    SMTP_SERVER: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    FROM_EMAIL: EmailStr | None = None

    model_config = {
        "env_file": str(Path(__file__).parent.parent / ".env"),
        "extra": "forbid",
    }


auth_settings = AuthSettings()
