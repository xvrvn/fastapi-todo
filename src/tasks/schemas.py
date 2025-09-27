# src/tasks/schemas.py
from datetime import datetime

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None
    priority: int | None = None


class TaskRead(TaskBase):
    id: int
    is_done: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskFilter(BaseModel):
    is_done: bool | None = None
    priority: int | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    q: str | None = None  # search query (title/description)


class PaginationParams(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)


class PaginatedTasks(BaseModel):
    total: int
    items: list[TaskRead]
