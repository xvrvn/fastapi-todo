from datetime import datetime, timezone

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models import User

from .models import Task
from .schemas import (
    PaginatedTasks,
    PaginationParams,
    TaskCreate,
    TaskFilter,
    TaskUpdate,
)


async def create_task(session: AsyncSession, task_in: TaskCreate, user: User) -> Task:
    task = Task(**task_in.model_dump(), owner_id=user.id)  # type: ignore
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_tasks(
    session: AsyncSession, user: User, filters: TaskFilter, pagination: PaginationParams
) -> PaginatedTasks:
    stmt = select(Task).where(Task.owner_id == user.id)

    if filters.is_done is not None:
        stmt = stmt.where(Task.is_done == filters.is_done)
    if filters.priority is not None:
        stmt = stmt.where(Task.priority == filters.priority)
    if filters.start_date:
        stmt = stmt.where(Task.created_at >= filters.start_date)
    if filters.end_date:
        stmt = stmt.where(Task.created_at <= filters.end_date)

    total_result = await session.exec(select(func.count()).select_from(stmt.subquery()))
    total = total_result.one()

    stmt = (
        stmt.order_by(Task.created_at.desc())  # type: ignore
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
    result = await session.exec(stmt)
    items = result.all()

    return PaginatedTasks(total=total, items=items)  # type: ignore


async def get_task(session: AsyncSession, task_id: int, user: User) -> Task | None:
    stmt = select(Task).where(Task.id == task_id, Task.owner_id == user.id)
    res = await session.exec(stmt)
    return res.first()


async def update_task(
    session: AsyncSession, task_id: int, task_in: TaskUpdate, user: User
) -> Task | None:
    task = await get_task(session, task_id, user)
    if not task:
        return None
    update_data = task_in.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(task, k, v)
    task.updated_at = datetime.now(tz=timezone.utc)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def delete_task(session: AsyncSession, task_id: int, user: User) -> bool:
    task = await get_task(session, task_id, user)
    if not task:
        return False
    await session.delete(task)
    await session.commit()
    return True


async def task_stats(session: AsyncSession, user: User) -> dict:
    total_q = select(func.count()).where(Task.owner_id == user.id)
    done_q = select(func.count()).where(Task.owner_id == user.id, Task.is_done)
    total = (await session.exec(total_q)).one()
    done = (await session.exec(done_q)).one()
    return {"total": total, "done": done, "pending": total - done}
