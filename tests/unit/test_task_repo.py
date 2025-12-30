from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.consts import TaskPriority, TaskStatus
from app.models.task import Task
from app.repositories.task_repository import TaskRepository

pytestmark = pytest.mark.asyncio


async def test_create_task(session: AsyncSession) -> None:
    repo = TaskRepository(session)

    task = Task(
        name="Repo create",
        description="Test create",
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.NEW,
    )

    created = await repo.create(task)

    assert created.id is not None
    assert created.name == "Repo create"
    assert created.status == TaskStatus.NEW


async def test_get_by_id(session: AsyncSession) -> None:
    repo = TaskRepository(session)

    task = Task(
        name="Repo get",
        description=None,
        priority=TaskPriority.MEDIUM,
        status=TaskStatus.NEW,
    )

    created = await repo.create(task)

    fetched = await repo.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Repo get"


async def test_get_by_id_not_found(session: AsyncSession) -> None:
    repo = TaskRepository(session)

    task = await repo.get_by_id(uuid4())

    assert task is None


async def test_list_tasks(session: AsyncSession) -> None:
    repo = TaskRepository(session)

    task1 = Task(name="List 1", description=None, priority=TaskPriority.LOW, status=TaskStatus.NEW)
    task2 = Task(name="List 2", description=None, priority=TaskPriority.MEDIUM, status=TaskStatus.NEW)

    await repo.create(task1)
    await repo.create(task2)

    tasks = await repo.list(status=None, limit=10, offset=0)

    assert len(tasks) >= 2
    assert all(isinstance(t, Task) for t in tasks)


async def test_list_tasks_by_status(session: AsyncSession) -> None:
    repo = TaskRepository(session)

    task = Task(name="Filtered", description=None, priority=TaskPriority.MEDIUM, status=TaskStatus.PENDING)
    await repo.create(task)

    tasks = await repo.list(status=TaskStatus.PENDING, limit=10, offset=0)

    assert any(t.id == task.id for t in tasks)


async def test_update_task(session: AsyncSession) -> None:
    repo = TaskRepository(session)

    task = Task(name="Update test", description=None, priority=TaskPriority.HIGH, status=TaskStatus.NEW)
    created = await repo.create(task)

    result = await repo.update(
        task_id=created.id,
        status=TaskStatus.PENDING,
        started_at=datetime.utcnow(),
        result="ok",
        error_message=None,
    )

    assert result is True

    updated = await repo.get_by_id(created.id)
    assert updated.status == TaskStatus.PENDING
    assert updated.result == "ok"


async def test_update_nonexistent_task(session: AsyncSession) -> None:
    repo = TaskRepository(session)

    result = await repo.update(task_id=uuid4(), status=TaskStatus.CANCELLED)

    assert result is False
