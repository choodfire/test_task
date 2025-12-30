import json
from uuid import UUID

import aio_pika

from app.core.config import settings


class TaskProducer:
    async def publish(self, task_id: UUID, priority: str) -> None:
        from app.messaging.rabbitmq import get_channel

        channel = await get_channel()

        message = aio_pika.Message(
            body=json.dumps({"task_id": str(task_id)}).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            priority=self._map_priority(priority),
        )

        await channel.default_exchange.publish(
            message,
            routing_key=settings.RABBITMQ_QUEUE_NAME,
        )

    @staticmethod
    def _map_priority(priority: str) -> int:
        priorities = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
        }

        return priorities.get(priority, 2)
