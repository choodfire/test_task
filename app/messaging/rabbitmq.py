import aio_pika
from aio_pika import RobustChannel, RobustConnection

from app.core.config import settings
from app.messaging.producer import TaskProducer

_connection: RobustConnection | None = None
_channel: RobustChannel | None = None
_producer: TaskProducer | None = None


def get_task_producer() -> TaskProducer:
    global _producer

    if _producer is None:
        _producer = TaskProducer()

    return _producer


async def get_connection() -> RobustConnection:
    global _connection

    if _connection is None:
        _connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASSWORD,
        )

    return _connection


async def get_channel() -> RobustChannel:
    global _channel

    if _channel is None:
        connection = await get_connection()
        _channel = await connection.channel()
        await _channel.set_qos(prefetch_count=1)

    return _channel
