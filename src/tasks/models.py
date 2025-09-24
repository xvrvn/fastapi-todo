from datetime import datetime, timezone

from sqlmodel import Boolean, Column, Field, SQLModel


class Task(SQLModel, table=True):
    __tablename__ = "tasks"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    description: str | None = Field(default=None)
    is_done: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    owner_id: int = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
