# src/tasks/models.py
from datetime import datetime, timezone

from sqlmodel import TIMESTAMP, Boolean, Column, Field, SQLModel, func


class Task(SQLModel, table=True):
    __tablename__ = "tasks"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: str | None = Field(default=None)
    priority: int | None = Field(default=None)
    is_done: bool = Field(
        default=False,
        sa_column=Column(
            Boolean,
            default=False,
            nullable=False,
        ),
    )
    owner_id: int = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
