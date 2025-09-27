from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from . import dependencies, schemas, service
from .utils import task_cache_key_builder

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: schemas.TaskCreate,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
    background_tasks: BackgroundTasks,
):
    task = await service.create_task(session, task_in, current_user)
    if FastAPICache.get_backend():
        background_tasks.add_task(FastAPICache.clear, namespace="tasks")
    return task


@router.get("/", response_model=schemas.PaginatedTasks)
@cache(expire=60, namespace="tasks", key_builder=task_cache_key_builder)  # type: ignore
async def read_tasks(
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
    is_done: bool | None = Query(None),
    priority: int | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    filters = schemas.TaskFilter(
        is_done=is_done, priority=priority, start_date=start_date, end_date=end_date
    )
    pagination = schemas.PaginationParams(limit=limit, offset=offset)
    return await service.get_tasks(session, current_user, filters, pagination)


@router.get("/stats")
async def stats(
    session: dependencies.DBSession, current_user: dependencies.CurrentUser
):
    return await service.task_stats(session, current_user)


@router.get("/{task_id}", response_model=schemas.TaskRead)
async def read_task(
    task_id: int,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
):
    task = await service.get_task(session, task_id, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=schemas.TaskRead)
async def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
    background_tasks: BackgroundTasks,
):
    task = await service.update_task(session, task_id, task_in, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if FastAPICache.get_backend():
        background_tasks.add_task(FastAPICache.clear, namespace="tasks")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
    background_tasks: BackgroundTasks,
):
    success = await service.delete_task(session, task_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    if FastAPICache.get_backend():
        background_tasks.add_task(FastAPICache.clear, namespace="tasks")
    return None
