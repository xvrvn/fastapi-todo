import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {
        "extra": "forbid",
    }


settings = Settings(
    DATABASE_URL=os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://nolos:123456@localhost:5432/tododb"
    ),
    SECRET_KEY=os.getenv("SECRET_KEY", "your_super_secret_key"),
    ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)),
    SMTP_SERVER=os.getenv("SMTP_SERVER", "smtp.example.com"),
    SMTP_PORT=int(os.getenv("SMTP_PORT", 587)),
    SMTP_USER=os.getenv("SMTP_USER", "user@example.com"),
    SMTP_PASSWORD=os.getenv("SMTP_PASSWORD", "password"),
    FROM_EMAIL=os.getenv("FROM_EMAIL", "noreply@example.com"),
    REDIS_URL=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
)
