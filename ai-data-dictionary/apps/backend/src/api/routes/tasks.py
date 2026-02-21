"""Task routes: GET /tasks/{task_id} for async task status (PROJECT_RULES 4.6)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser, get_db
from src.config.settings import get_settings
from src.models.task_result import TaskResult
from src.schemas.task import TaskStatusResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])
settings = get_settings()


@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskStatusResponse:
    """Get status of an async task (e.g. schema sync)."""
    result = await db.execute(select(TaskResult).where(TaskResult.task_id == task_id))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    base = f"{settings.api_v1_prefix}/tasks"
    return TaskStatusResponse(
        task_id=row.task_id,
        task_name=row.task_name,
        status=row.status,
        progress=row.progress,
        result=row.result,
        error_message=row.error_message,
        created_at=row.created_at,
        started_at=row.started_at,
        completed_at=row.completed_at,
        status_url=f"{base}/{row.task_id}",
    )
