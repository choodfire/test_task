from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consts import TaskStatus
from app.models.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        result = await self.session.execute(select(Task).where(Task.id == task_id))

        return result.scalar_one_or_none()

    async def list(self, status: TaskStatus | None, limit: int, offset: int) -> list[Task]:
        stmt = select(Task).order_by(Task.created_at.desc())

        if status is not None:
            stmt = stmt.where(Task.status == status)

        result = await self.session.execute(stmt.limit(limit).offset(offset))

        return result.scalars().all()

    async def update(
        self,
        task_id: UUID,
        status: TaskStatus | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        result: str | None = None,
        error_message: str | None = None,
    ) -> bool:
        values: dict = {}

        if status is not None:
            values["status"] = status

        if started_at is not None:
            values["started_at"] = started_at

        if finished_at is not None:
            values["finished_at"] = finished_at

        if result is not None:
            values["result"] = result

        if error_message is not None:
            values["error_message"] = error_message

        if values == {}:
            return False

        res = await self.session.execute(
            update(Task).where(Task.id == task_id).values(**values).execution_options(synchronize_session="fetch")
        )

        await self.session.commit()

        return res.rowcount > 0
