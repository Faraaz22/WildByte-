"""Stats endpoint for overview metrics."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser, get_db
from src.models.database import Database
from src.models.schema import Schema
from src.models.table import Table

router = APIRouter(tags=["stats"])


@router.get("/stats")
async def get_stats(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Return overview metrics: total databases, schemas, tables, and tables per database for charts."""
    db_count = await db.execute(
        select(func.count()).select_from(Database).where(Database.deleted_at.is_(None))
    )
    schema_count = await db.execute(
        select(func.count())
        .select_from(Schema)
        .join(Database, Schema.database_id == Database.id)
        .where(Schema.deleted_at.is_(None), Database.deleted_at.is_(None))
    )
    table_count = await db.execute(
        select(func.count())
        .select_from(Table)
        .join(Schema, Table.schema_id == Schema.id)
        .join(Database, Schema.database_id == Database.id)
        .where(Table.deleted_at.is_(None), Schema.deleted_at.is_(None), Database.deleted_at.is_(None))
    )
    # Tables per database for bar chart
    tables_per_db_q = (
        select(Database.id, Database.name, func.count(Table.id).label("table_count"))
        .join(Schema, Schema.database_id == Database.id)
        .join(Table, Table.schema_id == Schema.id)
        .where(
            Database.deleted_at.is_(None),
            Schema.deleted_at.is_(None),
            Table.deleted_at.is_(None),
        )
        .group_by(Database.id, Database.name)
    )
    per_db_result = await db.execute(tables_per_db_q)
    tables_per_database = [
        {"database_id": r[0], "database_name": r[1], "table_count": r[2]}
        for r in per_db_result.all()
    ]
    return {
        "total_databases": db_count.scalar() or 0,
        "total_schemas": schema_count.scalar() or 0,
        "total_tables": table_count.scalar() or 0,
        "tables_per_database": tables_per_database,
    }
