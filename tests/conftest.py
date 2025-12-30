from typing import AsyncGenerator, Generator

import pytest
from alembic.config import Config
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from app.core.config import settings
from app.main import app
from app.messaging.producer import TaskProducer
from app.messaging.rabbitmq import get_task_producer
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService

fake = Faker()


@pytest.fixture(scope="session")
def engine() -> AsyncEngine:
    return create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=False)


@pytest.fixture(scope="session")
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncSession:
    async with session_factory() as session:
        yield session


@pytest.fixture
def task_repository(session: AsyncSession) -> TaskRepository:
    return TaskRepository(session)


@pytest.fixture
def task_producer() -> TaskProducer:
    return get_task_producer()


@pytest.fixture
def task_service(session: AsyncSession, task_repository: TaskRepository, task_producer: TaskProducer) -> TaskService:
    return TaskService(
        session=session,
        repository=task_repository,
        producer=task_producer,
    )


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> AsyncGenerator:
    assert settings.DEBUG

    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    yield


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
