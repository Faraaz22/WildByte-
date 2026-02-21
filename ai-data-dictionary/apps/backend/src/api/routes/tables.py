"""Table routes per PROJECT_RULES: GET list (paginated/filtered), GET by id."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser, get_db
from src.models.table import Table
from src.models.column import Column
from src.schemas.table import (
    TableResponse,
    TableDetailResponse,
    TableListResponse,
    TableUpdate,
)
from src.schemas.column import ColumnResponse

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get("", response_model=TableListResponse)
async def list_tables(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    schema_id: int | None = Query(None),
    search: str | None = Query(None),
    has_quality_issues: bool | None = Query(None),
    sort: str = Query("-created_at", description="Sort: created_at, -created_at, name, -name"),
) -> TableListResponse:
    """List tables with pagination and filters."""
    q = select(Table).where(Table.deleted_at.is_(None))
    if schema_id is not None:
        q = q.where(Table.schema_id == schema_id)
    if search:
        q = q.where(
            Table.name.ilike(f"%{search}%")
            | (Table.description.isnot(None) & Table.description.ilike(f"%{search}%"))
        )
    if has_quality_issues is not None:
        q = q.where(Table.has_quality_issues == has_quality_issues)
    if sort.lstrip("-") == "created_at":
        q = q.order_by(Table.created_at.desc() if sort.startswith("-") else Table.created_at.asc())
    elif sort.lstrip("-") == "name":
        q = q.order_by(Table.name.desc() if sort.startswith("-") else Table.name.asc())
    else:
        q = q.order_by(Table.created_at.desc())

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    items = list(result.scalars().all())
    total_pages = (total + page_size - 1) // page_size if total else 0
    return TableListResponse(
        data=[TableResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{table_id}", response_model=TableDetailResponse)
async def get_table(
    table_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TableDetailResponse:
    """Get table by ID with columns."""
    result = await db.execute(
        select(Table).where(
            Table.id == table_id,
            Table.deleted_at.is_(None),
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    cols_result = await db.execute(select(Column).where(Column.table_id == table_id, Column.deleted_at.is_(None)).order_by(Column.ordinal_position))
    columns = [ColumnResponse.model_validate(c) for c in cols_result.scalars().all()]
    return TableDetailResponse(
        id=row.id,
        schema_id=row.schema_id,
        name=row.name,
        table_type=row.table_type,
        description=row.description,
        ai_generated_description=row.ai_generated_description,
        use_cases=row.use_cases,
        freshness_assessment=row.freshness_assessment,
        considerations=row.considerations,
        row_count=row.row_count,
        size_bytes=row.size_bytes,
        has_quality_issues=row.has_quality_issues,
        completeness_pct=row.completeness_pct,
        freshness_hours=row.freshness_hours,
        metadata_json=row.metadata_json,
        columns=columns,
        created_at=row.created_at,
        updated_at=row.updated_at,
        last_analyzed_at=row.last_analyzed_at,
    )


@router.patch("/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: int,
    body: TableUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TableResponse:
    """Update table metadata (description, etc.)."""
    result = await db.execute(
        select(Table).where(
            Table.id == table_id,
            Table.deleted_at.is_(None),
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return TableResponse.model_validate(row)
