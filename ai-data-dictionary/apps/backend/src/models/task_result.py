"""TaskResult model for async task tracking."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


class TaskResult(Base):
    """
    Async task execution result.
    
    Stores status and results of Celery tasks for polling by clients.
    """

    __tablename__ = "task_results"

    # Primary key
    task_id: Mapped[str] = mapped_column(String(255), primary_key=True)

    # Required fields
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
    )  # pending, running, success, failed, cancelled

    # Optional fields
    progress: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
        server_default="0",
    )  # 0-100
    result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_traceback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata
    args: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    kwargs: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<TaskResult(task_id='{self.task_id}', name='{self.task_name}', status='{self.status}', progress={self.progress}%)>"
