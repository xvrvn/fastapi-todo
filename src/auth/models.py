from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Boolean, Column, Field, SQLModel, String


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(
        sa_column=Column("email", String, unique=True, index=True, nullable=False)
    )
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(
        default=True, sa_column=Column("is_active", Boolean, default=True)
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=ZoneInfo("Asia/Shanghai"))
    )
