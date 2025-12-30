from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.consts import TaskPriority, TaskStatus


class TaskCreateRequest(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    result: str | None
    error_message: str | None
