from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: str | None
    is_done: bool

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_done: bool | None = None
