import asyncio
import json
import logging
from datetime import datetime
from uuid import UUID

import aio_pika
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_sessionmaker
from app.messaging.rabbitmq import get_task_producer
from app.models.consts import TaskStatus
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger()


class TaskWorker:
    def __init__(self) -> None:
        self.sessionmaker = get_sessionmaker()
        self.producer = get_task_producer()

    async def handle_message(self, message: aio_pika.IncomingMessage) -> None:
        async with message.process():
            payload = json.loads(message.body)
            task_id = UUID(payload["task_id"])

            async with self.sessionmaker() as session:
                await self.process_task(session, task_id)

    async def process_task(self, session: AsyncSession, task_id: UUID) -> None:
        logger.info(f"processing task id={task_id}")

        repository = TaskRepository(session)
        task = await repository.get_by_id(task_id)
        if not task:
            logger.warning(f"task id={task_id} not found")
            return

        if task.status == TaskStatus.CANCELLED:
            logger.warning(f"task id={task_id} was cancelled")
            return

        try:
            await repository.update(
                task_id=task.id,
                status=TaskStatus.IN_PROGRESS,
                started_at=datetime.utcnow(),
            )

            await asyncio.sleep(5)

            await repository.update(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                finished_at=datetime.utcnow(),
                result="OK",
            )

            logger.info(f"processed task id={task_id}")

        except Exception as exc:
            logger.warning(f"task id={task_id} was finished with error: {str(exc)}")
            await repository.update(
                task_id=task.id,
                status=TaskStatus.FAILED,
                finished_at=None,
                result=None,
                error_message=str(exc),
            )

    async def run(self) -> None:
        connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD,
        )

        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(
            settings.RABBITMQ_QUEUE_NAME,
            durable=True,
            arguments={"x-max-priority": 3},
        )

        logger.info("Worker started, waiting for tasks...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.handle_message(message)
