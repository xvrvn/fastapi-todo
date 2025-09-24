from datetime import datetime, timezone

from sqlmodel import Session, select

from src.auth.models import User

from .models import Task
from .schemas import TaskCreate, TaskUpdate


# ---- CRUD ----
def create_task(session: Session, task_in: TaskCreate, user: User) -> Task:
    task = Task(**task_in.model_dump(), owner_id=user.id)  # type: ignore
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_tasks(session: Session, user: User) -> list[Task]:
    statement = select(Task).where(Task.owner_id == user.id)
    return session.exec(statement).all()  # type: ignore


def get_task(session: Session, task_id: int, user: User) -> Task | None:
    statement = select(Task).where(Task.id == task_id, Task.owner_id == user.id)
    return session.exec(statement).first()


def update_task(
    session: Session, task_id: int, task_in: TaskUpdate, user: User
) -> Task | None:
    task = get_task(session, task_id, user)
    if not task:
        return None
    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    task.updated_at = datetime.now(tz=timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int, user: User) -> bool:
    task = get_task(session, task_id, user)
    if not task:
        return False
    session.delete(task)
    session.commit()
    return True
