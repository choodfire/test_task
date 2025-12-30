import uuid

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base
from app.models.consts import TaskPriority, TaskStatus


class Task(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(
        Enum(TaskPriority, name="task_priority", create_type=False),
        nullable=False,
        default=TaskPriority.MEDIUM,
        index=True,
    )
    status = Column(
        Enum(TaskStatus, name="task_status", create_type=False), nullable=False, default=TaskStatus.NEW, index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"Task name={self.name} status={self.status} priority={self.priority}>"
