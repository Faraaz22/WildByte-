"""Lineage routes: GET /tables/{id}/lineage per PROJECT_RULES."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser, get_db
from src.models.lineage_edge import LineageEdge
from src.models.schema import Schema
from src.models.table import Table
from src.schemas.lineage import LineageGraphResponse, LineageNodeResponse, LineageEdgeResponse

router = APIRouter(tags=["lineage"])


@router.get("/tables/{table_id}/lineage", response_model=LineageGraphResponse)
async def get_table_lineage(
    table_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LineageGraphResponse:
    """Get lineage graph for a table (upstream and downstream)."""
    result = await db.execute(
        select(Table).where(Table.id == table_id, Table.deleted_at.is_(None))
    )
    root = result.scalar_one_or_none()
    if not root:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Table not found")

    # Edges where this table is upstream or downstream
    edges_q = select(LineageEdge).where(
        (LineageEdge.upstream_table_id == table_id) | (LineageEdge.downstream_table_id == table_id),
        LineageEdge.deleted_at.is_(None),
    )
    edges_result = await db.execute(edges_q)
    edges = list(edges_result.scalars().all())
    table_ids = {table_id}
    for e in edges:
        table_ids.add(e.upstream_table_id)
        table_ids.add(e.downstream_table_id)

    if not table_ids:
        return LineageGraphResponse(nodes=[], edges=[], root_table_id=table_id)

    tables_q = select(Table, Schema.name).join(
        Schema, Table.schema_id == Schema.id
    ).where(Table.id.in_(table_ids), Table.deleted_at.is_(None), Schema.deleted_at.is_(None))
    tables_result = await db.execute(tables_q)
    table_schema_map = {row[0].id: (row[0], row[1]) for row in tables_result.all()}

    nodes = []
    for tid in table_ids:
        pair = table_schema_map.get(tid)
        if pair:
            t, schema_name = pair
            nodes.append(
                LineageNodeResponse(
                    id=t.id,
                    name=t.name,
                    schema_name=schema_name or "",
                    table_type=t.table_type,
                    level=0,
                )
            )
    graph_edges = [
        LineageEdgeResponse(
            source=e.upstream_table_id,
            target=e.downstream_table_id,
            relationship_type=e.relationship_type,
            label=e.description,
        )
        for e in edges
    ]
    return LineageGraphResponse(
        nodes=nodes,
        edges=graph_edges,
        root_table_id=table_id,
    )
