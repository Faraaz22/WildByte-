"""Database routes per PROJECT_RULES: POST/GET databases, GET schemas, POST sync."""

from typing import Annotated
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import func

from src.api.dependencies import CurrentUser, get_db
from src.config.settings import get_settings
from src.models.database import Database, DatabaseType
from src.models.schema import Schema
from src.schemas.database import (
    DatabaseCreate,
    DatabaseUpdate,
    DatabaseResponse,
    DatabaseListResponse,
    TestConnectionByUriRequest,
    CreateDatabaseFromUriRequest,
)
from src.schemas.schema import SchemaResponse
from src.utils.crypto import CredentialManager, decrypt_connection_string
from src.services.schema_extraction import _to_asyncpg_uri, extract_and_sync_postgres

router = APIRouter(prefix="/databases", tags=["databases"])
settings = get_settings()


def _encrypt_connection_string(conn_str: str) -> str:
    """Encrypt connection string if key is set; otherwise placeholder for dev."""
    if not settings.encryption_key or settings.encryption_key.startswith("generate_"):
        return "placeholder_encrypted"
    try:
        return CredentialManager(settings.encryption_key).encrypt(conn_str)
    except Exception:
        return "placeholder_encrypted"


def _build_connection_string(
    db_type: str,
    host: str,
    port: int,
    database_name: str,
    username: str,
    password: str,
) -> str:
    """Build a connection string for the given type."""
    if db_type == "postgresql":
        return f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
    if db_type == "mysql":
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
    return f"{db_type}://{username}:***@{host}:{port}/{database_name}"


def _parse_pg_uri(uri: str) -> dict:
    """Parse postgresql URI into components for Database model (host, port, database_name)."""
    parsed = urlparse(uri)
    path = (parsed.path or "").lstrip("/").split("/")[0] or ""
    return {
        "host": parsed.hostname or "",
        "port": parsed.port or 5432,
        "database_name": path or "postgres",
    }


@router.get("", response_model=DatabaseListResponse)
async def list_databases(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
) -> DatabaseListResponse:
    """List databases with pagination."""
    q = select(Database).where(Database.deleted_at.is_(None))
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    items = list(result.scalars().all())
    total_pages = (total + page_size - 1) // page_size if total else 0
    return DatabaseListResponse(
        data=[DatabaseResponse.model_validate(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/test-connection")
async def test_connection_by_uri(
    body: TestConnectionByUriRequest,
    current_user: CurrentUser,
) -> dict:
    """Test a PostgreSQL connection by URI. Returns { connected: true/false, message?: string }."""
    uri = body.connection_uri.strip()
    if not uri.startswith("postgresql"):
        return {"connected": False, "message": "Only PostgreSQL URIs are supported (postgresql://...)"}
    async_uri = _to_asyncpg_uri(uri)
    engine = create_async_engine(async_uri, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return {"connected": True, "message": "Connected"}
    except Exception as e:
        try:
            await engine.dispose()
        except Exception:
            pass
        return {"connected": False, "message": str(e)}


@router.post("/from-uri", response_model=DatabaseResponse, status_code=status.HTTP_201_CREATED)
async def create_database_from_uri(
    body: CreateDatabaseFromUriRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DatabaseResponse:
    """Create a database connection from a PostgreSQL URI, then run initial schema sync."""
    uri = body.connection_uri.strip()
    if not uri.startswith("postgresql"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PostgreSQL URIs are supported (postgresql://...)",
        )
    parsed = _parse_pg_uri(uri)
    encrypted = _encrypt_connection_string(uri)
    record = Database(
        name=body.name,
        db_type=DatabaseType.POSTGRESQL,
        connection_string_encrypted=encrypted,
        description=body.description,
        host=parsed.get("host"),
        port=parsed.get("port"),
        database_name=parsed.get("database_name"),
        sync_status="pending",
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    # Run sync immediately so schemas/tables appear
    try:
        try:
            conn_str = decrypt_connection_string(record.connection_string_encrypted)
        except Exception:
            conn_str = uri if encrypted == "placeholder_encrypted" else ""
        if not conn_str or conn_str == "placeholder_encrypted":
            conn_str = uri
        await extract_and_sync_postgres(db, record.id, conn_str)
        await db.refresh(record)
    except Exception as e:
        record.sync_status = "error"
        record.sync_error = str(e)
        await db.flush()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return DatabaseResponse.model_validate(record)


@router.post("", response_model=DatabaseResponse, status_code=status.HTTP_201_CREATED)
async def create_database(
    body: DatabaseCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DatabaseResponse:
    """Create a new database connection (credentials stored encrypted)."""
    conn_str = _build_connection_string(
        body.db_type.value,
        body.host,
        body.port,
        body.database_name,
        body.username,
        body.password,
    )
    encrypted = _encrypt_connection_string(conn_str)
    record = Database(
        name=body.name,
        db_type=body.db_type,
        connection_string_encrypted=encrypted,
        description=body.description,
        host=body.host,
        port=body.port,
        database_name=body.database_name,
        sync_status="pending",
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    # Run initial schema sync for PostgreSQL so Tables/Lineage pages have data
    if body.db_type.value == "postgresql":
        try:
            await extract_and_sync_postgres(db, record.id, conn_str)
            await db.refresh(record)
        except Exception as e:
            record.sync_status = "error"
            record.sync_error = str(e)
            await db.flush()
    return DatabaseResponse.model_validate(record)


@router.post("/test-new")
async def test_new_database_connection(
    body: DatabaseCreate,
    current_user: CurrentUser,
) -> dict:
    """Test a new database connection before saving (alias: same as test-connection with built URI)."""
    uri = _build_connection_string(
        body.db_type.value,
        body.host,
        body.port,
        body.database_name,
        body.username,
        body.password,
    )
    if not uri.startswith("postgresql"):
        return {"connected": False, "message": "Only PostgreSQL is supported for test-new. Use test-connection with a URI for others."}
    async_uri = _to_asyncpg_uri(uri)
    engine = create_async_engine(async_uri, pool_pre_ping=True)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        await engine.dispose()
        return {"connected": True, "message": "Connected"}
    except Exception as e:
        try:
            await engine.dispose()
        except Exception:
            pass
        return {"connected": False, "message": str(e)}


@router.get("/{database_id}", response_model=DatabaseResponse)
async def get_database(
    database_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DatabaseResponse:
    """Get a database by ID."""
    result = await db.execute(
        select(Database).where(
            Database.id == database_id,
            Database.deleted_at.is_(None),
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    return DatabaseResponse.model_validate(row)


@router.patch("/{database_id}", response_model=DatabaseResponse)
async def update_database(
  database_id: int,
  body: DatabaseUpdate,
  current_user: CurrentUser,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> DatabaseResponse:
    """Update a database (partial)."""
    result = await db.execute(
        select(Database).where(
            Database.id == database_id,
            Database.deleted_at.is_(None),
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        if k not in ("password", "username"):
            setattr(row, k, v)
    await db.flush()
    await db.refresh(row)
    return DatabaseResponse.model_validate(row)


@router.get("/{database_id}/schemas", response_model=list[SchemaResponse])
async def list_database_schemas(
    database_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[SchemaResponse]:
    """Get schemas for a database."""
    result = await db.execute(
        select(Schema).where(
            Schema.database_id == database_id,
            Schema.deleted_at.is_(None),
        )
    )
    schemas = list(result.scalars().all())
    return [SchemaResponse.model_validate(s) for s in schemas]


@router.post("/{database_id}/sync")
async def sync_database(
    database_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Run schema extraction from the target database and persist schemas/tables/columns/lineage."""
    result = await db.execute(
        select(Database).where(
            Database.id == database_id,
            Database.deleted_at.is_(None),
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    try:
        conn_str = decrypt_connection_string(row.connection_string_encrypted)
    except Exception:
        conn_str = "placeholder_encrypted"
    try:
        summary = await extract_and_sync_postgres(db, database_id, conn_str)
        await db.refresh(row)
        return {
            "status": "completed",
            "message": "Schema sync completed",
            "database_id": database_id,
            **summary,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.delete("/{database_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(
    database_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """Soft-delete a database."""
    result = await db.execute(
        select(Database).where(
            Database.id == database_id,
            Database.deleted_at.is_(None),
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    from datetime import datetime, timezone
    row.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    return None
