from fastapi import APIRouter, HTTPException, status

from . import dependencies, schemas, service

router = APIRouter()


# ---- Create task ----
@router.post("/", response_model=schemas.TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: schemas.TaskCreate,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
):
    return service.create_task(session, task_in, current_user)


# ---- Get all tasks of current user ----
@router.get("/", response_model=list[schemas.TaskRead])
def read_tasks(
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
):
    return service.get_tasks(session, current_user)


# ---- Get single task ----
@router.get("/{task_id}", response_model=schemas.TaskRead)
def read_task(
    task_id: int,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
):
    task = service.get_task(session, task_id, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ---- Update task ----
@router.patch("/{task_id}", response_model=schemas.TaskRead)
def update_task(
    task_id: int,
    task_in: schemas.TaskUpdate,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
):
    task = service.update_task(session, task_id, task_in, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ---- Delete task ----
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    session: dependencies.DBSession,
    current_user: dependencies.CurrentUser,
):
    success = service.delete_task(session, task_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
