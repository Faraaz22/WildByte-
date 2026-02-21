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

            # 4) Foreign keys (with column names for precise lineage)
            fk_rows = await conn.execute(
                text("""
                    SELECT
                        kcu.table_schema,
                        kcu.table_name,
                        kcu.column_name,
                        ccu.table_schema AS ref_schema,
                        ccu.table_name AS ref_table,
                        ccu.column_name AS ref_column
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                      AND tc.constraint_catalog = kcu.constraint_catalog
                    JOIN information_schema.constraint_column_usage ccu
                      ON tc.constraint_name = ccu.constraint_name
                      AND tc.table_schema = ccu.table_schema
                      AND tc.constraint_catalog = ccu.constraint_catalog
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    ORDER BY kcu.table_schema, kcu.table_name, kcu.ordinal_position
                """)
            )
            # (kcu_schema, kcu_table, kcu_column, ref_schema, ref_table, ref_column)
            fk_tuples = [tuple(r) for r in fk_rows.fetchall()]

            # 5) Columns that are part of a UNIQUE constraint (for one-to-one detection)
            unique_rows = await conn.execute(
                text("""
                    SELECT kcu.table_schema, kcu.table_name, kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                      AND tc.constraint_catalog = kcu.constraint_catalog
                    WHERE tc.constraint_type = 'UNIQUE'
                      AND tc.table_schema IN (SELECT schema_name FROM information_schema.schemata
                        WHERE catalog_name = current_database()
                        AND schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast'))
                """)
            )
            unique_columns: set[tuple[str, str, str]] = {
                (r[0], r[1], r[2]) for r in unique_rows.fetchall()
            }

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

    # Build (table_schema, table_name, column_name) -> (ref_schema, ref_table, ref_column)
    fk_by_column: dict[tuple[str, str, str], tuple[str, str, str]] = {}
    for row in fk_tuples:
        kcu_schema, kcu_table, kcu_col, ref_schema, ref_table, ref_col = (
            row[0], row[1], row[2], row[3], row[4], row[5]
        )
        fk_by_column[(kcu_schema, kcu_table, kcu_col)] = (ref_schema, ref_table, ref_col or "")

    for (sn, table_name), cols in cols_by_table.items():
        tbl_id = table_id_by_key.get((sn, table_name))
        if not tbl_id:
            continue
        for pos, (col_name, data_type, ord_pos, is_nullable) in enumerate(cols, start=1):
            fk_ref = fk_by_column.get((sn, table_name, col_name))
            col = Column(
                table_id=tbl_id,
                name=col_name,
                data_type=data_type,
                ordinal_position=ord_pos or pos,
                is_nullable=(is_nullable == "YES"),
                is_foreign_key=bool(fk_ref),
                foreign_key_table=f"{fk_ref[0]}.{fk_ref[1]}" if fk_ref else None,
                foreign_key_column=(fk_ref[2] if (fk_ref and len(fk_ref) > 2 and fk_ref[2]) else None),
            )
            db_session.add(col)
    await db_session.flush()

    # Create lineage edges from FK (deduplicate by upstream_id, downstream_id; collect column pairs)
    # key (upstream_id, downstream_id) -> list of (ref_col, kcu_col) for column_mapping
    edge_column_pairs: dict[tuple[int, int], list[tuple[str, str]]] = {}
    # downstream (schema, table) -> set of column names that are FK (for unique check)
    downstream_fk_cols: dict[tuple[str, str], set[str]] = {}
    for row in fk_tuples:
        kcu_schema, kcu_table, kcu_col, ccu_schema, ccu_table, ccu_col = (
            row[0], row[1], row[2], row[3], row[4], row[5]
        )
        downstream_id = table_id_by_key.get((kcu_schema, kcu_table))
        upstream_id = table_id_by_key.get((ccu_schema, ccu_table))
        if not downstream_id or not upstream_id or upstream_id == downstream_id:
            continue
        key = (upstream_id, downstream_id)
        ref_col = ccu_col or ""
        if key not in edge_column_pairs:
            edge_column_pairs[key] = []
        edge_column_pairs[key].append((ref_col, kcu_col))
        dt_key = (kcu_schema, kcu_table)
        if dt_key not in downstream_fk_cols:
            downstream_fk_cols[dt_key] = set()
        downstream_fk_cols[dt_key].add(kcu_col)

    # Tables that are likely join tables: exactly 2 FK columns and few total columns
    fk_count_per_table: dict[tuple[str, str], int] = {}
    for (sch, tbl), cols in downstream_fk_cols.items():
        fk_count_per_table[(sch, tbl)] = len(cols)
    join_table_keys: set[tuple[str, str]] = set()
    for (sch, tbl), fk_count in fk_count_per_table.items():
        if fk_count != 2:
            continue
        col_count = len(cols_by_table.get((sch, tbl), []))
        if col_count <= 6:
            join_table_keys.add((sch, tbl))
    join_table_ids = {table_id_by_key[k] for k in join_table_keys if k in table_id_by_key}

    seen_edges: set[tuple[int, int]] = set()
    edges_created = 0
    key_to_downstream_key: dict[tuple[int, int], tuple[str, str]] = {}
    for row in fk_tuples:
        kcu_schema, kcu_table, kcu_col, ccu_schema, ccu_table, ccu_col = (
            row[0], row[1], row[2], row[3], row[4], row[5]
        )
        downstream_id = table_id_by_key.get((kcu_schema, kcu_table))
        upstream_id = table_id_by_key.get((ccu_schema, ccu_table))
        if downstream_id and upstream_id and upstream_id != downstream_id:
            key = (upstream_id, downstream_id)
            key_to_downstream_key[key] = (kcu_schema, kcu_table)
    for row in fk_tuples:
        kcu_schema, kcu_table, kcu_col, ccu_schema, ccu_table, ccu_col = (
            row[0], row[1], row[2], row[3], row[4], row[5]
        )
        downstream_id = table_id_by_key.get((kcu_schema, kcu_table))
        upstream_id = table_id_by_key.get((ccu_schema, ccu_table))
        if downstream_id and upstream_id and upstream_id != downstream_id:
            key = (upstream_id, downstream_id)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            pairs = edge_column_pairs.get(key, [])
            column_mapping_list = [
                {"referenced_column": p[0], "referencing_column": p[1]} for p in pairs
            ]
            # Cardinality: if all FK columns in downstream are UNIQUE -> one_to_one, else one_to_many
            dt_key = key_to_downstream_key.get(key, (kcu_schema, kcu_table))
            fk_cols = downstream_fk_cols.get(dt_key, set())
            all_unique = (
                all((dt_key[0], dt_key[1], c) in unique_columns for c in fk_cols)
                if fk_cols else False
            )
            cardinality = "one_to_one" if all_unique else "one_to_many"
            is_join = downstream_id in join_table_ids
            if is_join:
                cardinality = "many_to_many"
            metadata_json = {
                "cardinality": cardinality,
                "is_join_table": is_join,
            }
            edge = LineageEdge(
                upstream_table_id=upstream_id,
                downstream_table_id=downstream_id,
                relationship_type="foreign_key",
                description=f"{ccu_schema}.{ccu_table} → {kcu_schema}.{kcu_table}",
                column_mapping={"pairs": column_mapping_list} if column_mapping_list else None,
                metadata_json=metadata_json,
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
