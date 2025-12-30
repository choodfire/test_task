from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.models.consts import TaskStatus
from app.models.task import Task
from app.schemas.task import TaskCreateRequest, TaskResponse
from app.services.task_service import TaskService, get_task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreateRequest, service: TaskService = Depends(get_task_service)) -> Task:
    task = await service.create_task(payload)

    return task


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: TaskStatus | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: TaskService = Depends(get_task_service),
) -> list[Task]:
    tasks = await service.list_tasks(status=status, limit=limit, offset=offset)

    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, service: TaskService = Depends(get_task_service)) -> Task:
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_task(task_id: UUID, service: TaskService = Depends(get_task_service)) -> None:
    success = await service.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or cannot be cancelled")


@router.get("/{task_id}/status")
async def get_task_status(task_id: UUID, service: TaskService = Depends(get_task_service)) -> dict:
    task = await service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return {"status": task.status}
