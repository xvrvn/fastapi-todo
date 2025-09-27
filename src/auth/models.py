# src/auth/models.py
from datetime import datetime, timezone

from sqlmodel import TIMESTAMP, Boolean, Column, Field, SQLModel, String, func


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(
        sa_column=Column("email", String, unique=True, index=True, nullable=False)
    )
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(
        default=True,
        sa_column=Column(
            Boolean,
            default=True,
            nullable=False,
        ),
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
