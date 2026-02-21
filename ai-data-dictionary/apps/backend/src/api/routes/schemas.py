"""Schema routes: list schemas (optionally by database_id)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser, get_db
from src.models.schema import Schema
from src.schemas.schema import SchemaResponse

router = APIRouter(prefix="/schemas", tags=["schemas"])


@router.get("", response_model=list[SchemaResponse])
async def list_schemas(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    database_id: int | None = Query(None, description="Filter by database ID"),
) -> list[SchemaResponse]:
    """List schemas, optionally filtered by database_id."""
    q = select(Schema).where(Schema.deleted_at.is_(None))
    if database_id is not None:
        q = q.where(Schema.database_id == database_id)
    result = await db.execute(q)
    return [SchemaResponse.model_validate(s) for s in result.scalars().all()]
