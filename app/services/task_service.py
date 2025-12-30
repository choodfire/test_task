from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.messaging.producer import TaskProducer
from app.messaging.rabbitmq import get_task_producer
from app.models.consts import TaskStatus
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreateRequest


def get_task_service(session: AsyncSession = Depends(get_db_session)) -> "TaskService":
    repository = TaskRepository(session)
    producer = get_task_producer()

    return TaskService(
        session=session,
        repository=repository,
        producer=producer,
    )


class TaskService:
    def __init__(self, session: AsyncSession, repository: TaskRepository, producer: TaskProducer) -> None:
        self.session = session
        self.repository = repository
        self.producer = producer

    async def create_task(self, payload: TaskCreateRequest) -> Task:
        task = Task(
            name=payload.name, description=payload.description, priority=payload.priority, status=TaskStatus.NEW
        )

        task = await self.repository.create(task)

        await self.producer.publish(task_id=task.id, priority=task.priority.value)

        await self.repository.update(task_id=task.id, status=TaskStatus.PENDING)

        return task

    async def get_task(self, task_id: UUID) -> Task | None:
        return await self.repository.get_by_id(task_id)

    async def list_tasks(self, status: TaskStatus | None, limit: int, offset: int) -> list[Task]:
        return await self.repository.list(status=status, limit=limit, offset=offset)

    async def cancel_task(self, task_id: UUID) -> bool:
        task = await self.repository.get_by_id(task_id)

        if not task:
            return False

        if task.status not in [TaskStatus.NEW, TaskStatus.PENDING]:
            return False

        await self.repository.update(task_id=task_id, status=TaskStatus.CANCELLED)

        return True
