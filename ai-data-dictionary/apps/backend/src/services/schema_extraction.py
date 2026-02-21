"""
Extract schema metadata from a PostgreSQL database and persist to our catalog.

Used by sync_database to populate Schema, Table, Column, and LineageEdge from
information_schema and referential_constraints.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.models.column import Column
from src.models.database import Database
from src.models.lineage_edge import LineageEdge
from src.models.schema import Schema
from src.models.table import Table


def _to_asyncpg_uri(uri: str) -> str:
    """Convert postgresql:// to postgresql+asyncpg:// for async engine."""
    if uri.startswith("postgresql+asyncpg://"):
        return uri
    if uri.startswith("postgresql://"):
        return uri.replace("postgresql://", "postgresql+asyncpg://", 1)
    return uri


async def extract_and_sync_postgres(
    db_session: AsyncSession,
    database_id: int,
    connection_string: str,
) -> dict[str, Any]:
    """
    Connect to the target PostgreSQL, extract schemas/tables/columns/FKs,
    and persist to our catalog. Replaces existing data for this database.

    Returns:
        Summary with counts: schemas, tables, columns, lineage_edges.
    """
    # Resolve placeholder (dev without encryption)
    if connection_string == "placeholder_encrypted":
        raise ValueError(
            "Cannot sync: connection string not available. Set ENCRYPTION_KEY to store credentials."
        )

    async_uri = _to_asyncpg_uri(connection_string)
    engine = create_async_engine(async_uri, pool_pre_ping=True)

    try:
        async with engine.connect() as conn:
            # 1) Schemas (exclude system)
            schema_rows = await conn.execute(
                text("""
                    SELECT schema_name
                    FROM information_schema.schemata
                    WHERE catalog_name = current_database()
                      AND schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                    ORDER BY schema_name
                """)
            )
            schema_names = [row[0] for row in schema_rows.fetchall()]

            # 2) Tables per schema: (schema_name, table_name, table_type)
            tables_by_schema: dict[str, list[tuple[str, str]]] = {}
            for sn in schema_names:
                tbl_rows = await conn.execute(
                    text("""
                        SELECT table_name, table_type
                        FROM information_schema.tables
                        WHERE table_schema = :schema
                        ORDER BY table_name
                    """),
                    {"schema": sn},
                )
                tables_by_schema[sn] = [(r[0], r[1]) for r in tbl_rows.fetchall()]

            # 3) All columns for our schemas
            placeholders = ", ".join(f":s{i}" for i in range(len(schema_names)))
            params = {f"s{i}": sn for i, sn in enumerate(schema_names)}
            col_rows = await conn.execute(
                text(f"""
                    SELECT table_schema, table_name, column_name, data_type, ordinal_position, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema IN ({placeholders})
                    ORDER BY table_schema, table_name, ordinal_position
                """),
                params,
            )
            all_columns = col_rows.fetchall()

            # 4) Foreign keys
            fk_rows = await conn.execute(
                text("""
                    SELECT
                        kcu.table_schema,
                        kcu.table_name,
                        ccu.table_schema AS ref_schema,
                        ccu.table_name AS ref_table
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage ccu
                      ON tc.constraint_name = ccu.constraint_name AND tc.table_schema = ccu.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    ORDER BY kcu.table_schema, kcu.table_name
                """)
            )
            fk_tuples = [(r[0], r[1], r[2], r[3]) for r in fk_rows.fetchall()]

        await engine.dispose()
    except Exception as e:
        await engine.dispose()
        raise RuntimeError(f"Failed to extract from target database: {e}") from e

    # Load our database row and decrypt is already done by caller
    db_result = await db_session.execute(
        select(Database).where(Database.id == database_id, Database.deleted_at.is_(None))
    )
    db_row = db_result.scalar_one_or_none()
    if not db_row:
        raise ValueError("Database not found")

    # Delete existing schemas for this database (cascade deletes tables, columns, lineage edges)
    existing = await db_session.execute(
        select(Schema).where(Schema.database_id == database_id, Schema.deleted_at.is_(None))
    )
    for schema in existing.scalars().all():
        await db_session.delete(schema)
    await db_session.flush()

    schema_id_by_name: dict[str, int] = {}
    table_id_by_key: dict[tuple[str, str], int] = {}  # (schema_name, table_name) -> table_id

    # Create Schema records
    for sn in schema_names:
        s = Schema(database_id=database_id, name=sn)
        db_session.add(s)
        await db_session.flush()
        schema_id_by_name[sn] = s.id

    # Create Table and Column records
    for sn in schema_names:
        schema_id = schema_id_by_name[sn]
        for table_name, table_type in tables_by_schema.get(sn, []):
            tbl = Table(
                schema_id=schema_id,
                name=table_name,
                table_type=table_type if table_type in ("table", "view", "materialized view") else "table",
            )
            db_session.add(tbl)
            await db_session.flush()
            table_id_by_key[(sn, table_name)] = tbl.id
        await db_session.flush()

    # Add columns (grouped by table)
    cols_by_table: dict[tuple[str, str], list[tuple[str, str, int, str]]] = {}
    for row in all_columns:
        ts, tn, col_name, data_type, ord_pos, is_nullable = row
        key = (ts, tn)
        if key not in cols_by_table:
            cols_by_table[key] = []
        cols_by_table[key].append((col_name, data_type or "unknown", ord_pos or 0, is_nullable or "YES"))

    for (sn, table_name), cols in cols_by_table.items():
        tbl_id = table_id_by_key.get((sn, table_name))
        if not tbl_id:
            continue
        for pos, (col_name, data_type, ord_pos, is_nullable) in enumerate(cols, start=1):
            col = Column(
                table_id=tbl_id,
                name=col_name,
                data_type=data_type,
                ordinal_position=ord_pos or pos,
                is_nullable=(is_nullable == "YES"),
            )
            db_session.add(col)
    await db_session.flush()

    # Create lineage edges from FK (deduplicate by upstream_id, downstream_id)
    seen_edges: set[tuple[int, int]] = set()
    edges_created = 0
    for kcu_schema, kcu_table, ccu_schema, ccu_table in fk_tuples:
        downstream_id = table_id_by_key.get((kcu_schema, kcu_table))
        upstream_id = table_id_by_key.get((ccu_schema, ccu_table))
        if downstream_id and upstream_id and upstream_id != downstream_id:
            key = (upstream_id, downstream_id)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edge = LineageEdge(
                upstream_table_id=upstream_id,
                downstream_table_id=downstream_id,
                relationship_type="foreign_key",
                description=f"{ccu_schema}.{ccu_table} -> {kcu_schema}.{kcu_table}",
            )
            db_session.add(edge)
            edges_created += 1

    await db_session.flush()

    # Update database sync status
    db_row.sync_status = "connected"
    db_row.sync_error = None
    db_row.last_sync_at = datetime.now(timezone.utc)
    await db_session.flush()

    total_columns = sum(len(c) for c in cols_by_table.values())
    return {
        "schemas": len(schema_names),
        "tables": sum(len(tables_by_schema.get(sn, [])) for sn in schema_names),
        "columns": total_columns,
        "lineage_edges": edges_created,
    }
