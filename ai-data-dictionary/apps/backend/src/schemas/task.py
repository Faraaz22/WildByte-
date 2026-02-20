"""Pydantic schemas for Task API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatusResponse(BaseModel):
    """Schema for async task status response."""

    task_id: str
    task_name: str
    status: str = Field(
        ...,
        description="Task status: pending, running, success, failed, cancelled"
    )
    progress: int = Field(..., ge=0, le=100, description="Progress percentage")
    result: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status_url: str = Field(..., description="URL to poll for status updates")

    model_config = {"json_schema_extra": {
        "example": {
            "task_id": "task_abc123xyz",
            "task_name": "extract_schema",
            "status": "running",
            "progress": 45,
            "result": None,
            "error_message": None,
            "created_at": "2026-02-20T10:30:00Z",
            "started_at": "2026-02-20T10:30:05Z",
            "completed_at": None,
            "status_url": "/api/v1/tasks/task_abc123xyz"
        }
    }}
