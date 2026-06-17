from fastapi import APIRouter, HTTPException

from app.models.schemas import Task, TaskCreate, TaskUpdate
from app.services import tasks as tasks_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=list[Task])
def list_tasks():
    return tasks_service.list_tasks()


@router.post("", response_model=Task)
def create_task(data: TaskCreate):
    return tasks_service.create_task(data)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: str):
    task = tasks_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: str, data: TaskUpdate):
    task = tasks_service.update_task(task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}")
def delete_task(task_id: str):
    if not tasks_service.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}
