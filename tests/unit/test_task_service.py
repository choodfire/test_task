import uuid
from unittest.mock import Mock, patch

import pytest

from app.messaging.producer import TaskProducer
from app.models.consts import TaskPriority, TaskStatus
from app.schemas.task import TaskCreateRequest
from app.services.task_service import TaskService

pytestmark = pytest.mark.asyncio


@patch.object(TaskProducer, "publish")
async def test_create_task(rmq_mock: Mock, task_service: TaskService) -> None:
    payload = TaskCreateRequest(
        name="Test task",
        description="Test description",
        priority=TaskPriority.MEDIUM,
    )

    task = await task_service.create_task(payload)

    assert task.id is not None

    assert isinstance(task.id, uuid.UUID)
    assert task.name == payload.name
    assert task.description == payload.description
    assert task.priority == payload.priority
    assert task.status == TaskStatus.PENDING
    assert rmq_mock.called


@patch.object(TaskProducer, "publish")
async def test_get_task(rmq_mock: Mock, task_service: TaskService) -> None:
    payload = TaskCreateRequest(
        name="Get task",
        description=None,
        priority=TaskPriority.MEDIUM,
    )

    created = await task_service.create_task(payload)

    task = await task_service.get_task(created.id)

    assert task is not None
    assert task.id == created.id
    assert rmq_mock.called


async def test_get_task_not_found(task_service: TaskService) -> None:
    task = await task_service.get_task(uuid.uuid4())

    assert task is None


@patch.object(TaskProducer, "publish")
async def test_list_tasks(rmq_mock: Mock, task_service: TaskService) -> None:
    payload1 = TaskCreateRequest(
        name="Task 1",
        description=None,
        priority=TaskPriority.MEDIUM,
    )

    payload2 = TaskCreateRequest(
        name="Task 2",
        description=None,
        priority=TaskPriority.MEDIUM,
    )

    await task_service.create_task(payload1)
    await task_service.create_task(payload2)

    tasks = await task_service.list_tasks(
        status=None,
        limit=10,
        offset=0,
    )

    assert len(tasks) >= 2
    assert all(t.id is not None for t in tasks)
    assert rmq_mock.called


@patch.object(TaskProducer, "publish")
async def test_cancel_task_success(rmq_mock: Mock, task_service: TaskService) -> None:
    payload = TaskCreateRequest(
        name="Cancelable",
        description=None,
        priority=TaskPriority.LOW,
    )

    task = await task_service.create_task(payload)

    result = await task_service.cancel_task(task.id)

    assert result is True

    cancelled = await task_service.get_task(task.id)
    assert cancelled.status == TaskStatus.CANCELLED
    assert rmq_mock.called


async def test_cancel_task_not_found(task_service: TaskService) -> None:
    result = await task_service.cancel_task(uuid.uuid4())

    assert result is False
