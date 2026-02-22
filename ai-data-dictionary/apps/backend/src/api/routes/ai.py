"""AI/agent endpoints: schema context for LLM or external agents, and chat."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser, get_db
from src.models.column import Column
from src.models.database import Database
from src.models.lineage_edge import LineageEdge
from src.models.schema import Schema
from src.models.table import Table
from src.schemas.chat import ChatMessageRequest, ChatMessageResponse
from src.services.chat_service import chat_with_schema

router = APIRouter(prefix="/ai", tags=["ai"])

DEFAULT_LIMIT_TABLES = 50


def _table_to_context_row(table: Table, columns: list) -> dict:
    """Serialize a table and its columns for schema context."""
    return {
        "name": table.name,
        "table_type": table.table_type,
        "description": table.description or (getattr(table, "ai_generated_description", None) or ""),
        "columns": [
            {
                "name": c.name,
                "data_type": c.data_type,
                "is_nullable": c.is_nullable,
                "is_primary_key": getattr(c, "is_primary_key", False),
                "is_foreign_key": getattr(c, "is_foreign_key", False),
                "foreign_key_ref": (
                    f"{c.foreign_key_table}.{c.foreign_key_column}"
                    if (
                        getattr(c, "is_foreign_key", False)
                        and getattr(c, "foreign_key_table", None)
                        and getattr(c, "foreign_key_column", None)
                    )
                    else None
                ),
            }
            for c in columns
        ],
    }


def _lineage_edges_to_context(edges: list, table_id_to_key: dict[int, str]) -> list[dict]:
    """Build lineage list for context from LineageEdge rows and table id -> key map."""
    return [
        {
            "upstream": table_id_to_key.get(e.upstream_table_id, str(e.upstream_table_id)),
            "downstream": table_id_to_key.get(e.downstream_table_id, str(e.downstream_table_id)),
            "type": e.relationship_type,
        }
        for e in edges
    ]


def _empty_schema_context(database_id: int, database_name: str, schemas: list | None = None) -> dict:
    """Minimal context when no tables exist."""
    return {
        "database_id": database_id,
        "database_name": database_name,
        "schemas": [{"name": s.name, "tables": []} for s in schemas] if schemas else [],
        "lineage": [],
    }


async def _build_schema_context(
    db: AsyncSession,
    database_id: int,
    limit_tables: int = DEFAULT_LIMIT_TABLES,
) -> dict | None:
    """Build schema context dict for chat. Returns None if database not found."""
    db_result = await db.execute(
        select(Database).where(
            Database.id == database_id,
            Database.deleted_at.is_(None),
        )
    )
    database = db_result.scalar_one_or_none()
    if not database:
        return None

    schemas_q = (
        select(Schema)
        .where(Schema.database_id == database_id, Schema.deleted_at.is_(None))
        .order_by(Schema.name)
    )
    schemas_result = await db.execute(schemas_q)
    schemas = list(schemas_result.scalars().all())
    schema_ids = [s.id for s in schemas]
    if not schema_ids:
        return _empty_schema_context(database_id, database.name)

    tables_q = (
        select(Table)
        .where(Table.schema_id.in_(schema_ids), Table.deleted_at.is_(None))
        .order_by(Table.schema_id, Table.name)
        .limit(limit_tables)
    )
    tables_result = await db.execute(tables_q)
    tables = list(tables_result.scalars().all())
    table_ids = [t.id for t in tables]
    if not table_ids:
        return _empty_schema_context(database_id, database.name, schemas)

    columns_q = (
        select(Column)
        .where(Column.table_id.in_(table_ids), Column.deleted_at.is_(None))
        .order_by(Column.table_id, Column.ordinal_position)
    )
    columns_result = await db.execute(columns_q)
    columns = list(columns_result.scalars().all())
    columns_by_table: dict[int, list] = {}
    for c in columns:
        columns_by_table.setdefault(c.table_id, []).append(c)

    schema_by_id = {s.id: s.name for s in schemas}
    tables_by_schema: dict[str, list] = {}
    for t in tables:
        sname = schema_by_id.get(t.schema_id, "")
        tables_by_schema.setdefault(sname, [])
        cols = columns_by_table.get(t.id, [])
        tables_by_schema[sname].append(_table_to_context_row(t, cols))

    edges_q = select(LineageEdge).where(
        LineageEdge.deleted_at.is_(None),
        LineageEdge.upstream_table_id.in_(table_ids),
        LineageEdge.downstream_table_id.in_(table_ids),
    )
    edges_result = await db.execute(edges_q)
    edges = list(edges_result.scalars().all())
    table_id_to_key = {t.id: f"{schema_by_id.get(t.schema_id, '')}.{t.name}" for t in tables}
    lineage = _lineage_edges_to_context(edges, table_id_to_key)

    schema_list = [
        {"name": name, "tables": tbl_list}
        for name, tbl_list in sorted(tables_by_schema.items())
    ]
    return {
        "database_id": database_id,
        "database_name": database.name,
        "schemas": schema_list,
        "lineage": lineage,
        "meta": {"tables_included": len(tables), "limit_tables": limit_tables},
    }


@router.post("/chat", response_model=ChatMessageResponse)
async def post_chat_message(
    body: ChatMessageRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatMessageResponse:
    """Send a message and get an AI reply using schema context (Gemini free tier)."""
    database_id = body.database_id
    if database_id is None:
        # Use first database
        first_result = await db.execute(
            select(Database).where(Database.deleted_at.is_(None)).limit(1)
        )
        first_row = first_result.scalars().first()
        database_id = first_row.id if first_row else None

    if database_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No database connected. Add and sync a database first.",
        )

    context = await _build_schema_context(db, database_id)
    if not context:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

    result = await chat_with_schema(
        message=body.message,
        schema_context=context,
        conversation_id=body.conversation_id,
    )

    return ChatMessageResponse(
        conversation_id=result["conversation_id"],
        message_id=result["message_id"],
        response=result["response"],
        intent=result.get("intent", "question_answer"),
        processing_time_ms=result.get("processing_time_ms", 0),
        created_at=result["created_at"],
    )


@router.get("/schema-context")
async def get_schema_context_for_agent(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    database_id: int = Query(..., description="Database ID to export"),
    limit_tables: int = Query(DEFAULT_LIMIT_TABLES, ge=1, le=500, description="Max tables to include (for large DBs)"),
    search: str | None = Query(None, description="Filter tables by name/description"),
) -> dict:
    """
    Return a compact schema summary for an AI agent or SDK.
    Use limit_tables and search when you have lots of data; the agent should
    request only what it needs per question.
    """
    db_result = await db.execute(
        select(Database).where(
            Database.id == database_id,
            Database.deleted_at.is_(None),
        )
    )
    database = db_result.scalar_one_or_none()
    if not database:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

    schemas_q = (
        select(Schema)
        .where(Schema.database_id == database_id, Schema.deleted_at.is_(None))
        .order_by(Schema.name)
    )
    schemas_result = await db.execute(schemas_q)
    schemas = list(schemas_result.scalars().all())
    schema_ids = [s.id for s in schemas]
    if not schema_ids:
        return _empty_schema_context(database_id, database.name)

    tables_q = (
        select(Table)
        .where(Table.schema_id.in_(schema_ids), Table.deleted_at.is_(None))
        .order_by(Table.schema_id, Table.name)
    )
    if search and search.strip():
        search_like = f"%{search.strip()}%"
        tables_q = tables_q.where(
            Table.name.ilike(search_like)
            | (Table.description.isnot(None) & Table.description.ilike(search_like))
        )
    tables_q = tables_q.limit(limit_tables)
    tables_result = await db.execute(tables_q)
    tables = list(tables_result.scalars().all())
    table_ids = [t.id for t in tables]
    if not table_ids:
        return _empty_schema_context(database_id, database.name, schemas)

    columns_q = (
        select(Column)
        .where(Column.table_id.in_(table_ids), Column.deleted_at.is_(None))
        .order_by(Column.table_id, Column.ordinal_position)
    )
    columns_result = await db.execute(columns_q)
    columns = list(columns_result.scalars().all())
    columns_by_table: dict[int, list] = {}
    for c in columns:
        columns_by_table.setdefault(c.table_id, []).append(c)

    schema_by_id = {s.id: s.name for s in schemas}
    tables_by_schema = {}
    for t in tables:
        sname = schema_by_id.get(t.schema_id, "")
        tables_by_schema.setdefault(sname, []).append(_table_to_context_row(t, columns_by_table.get(t.id, [])))

    edges_q = select(LineageEdge).where(
        LineageEdge.deleted_at.is_(None),
        LineageEdge.upstream_table_id.in_(table_ids),
        LineageEdge.downstream_table_id.in_(table_ids),
    )
    edges_result = await db.execute(edges_q)
    edges = list(edges_result.scalars().all())
    table_id_to_key = {t.id: f"{schema_by_id.get(t.schema_id, '')}.{t.name}" for t in tables}
    lineage = _lineage_edges_to_context(edges, table_id_to_key)

    schema_list = [
        {"name": name, "tables": tbl_list}
        for name, tbl_list in sorted(tables_by_schema.items())
    ]
    return {
        "database_id": database_id,
        "database_name": database.name,
        "schemas": schema_list,
        "lineage": lineage,
        "meta": {"tables_included": len(tables), "limit_tables": limit_tables},
    }
