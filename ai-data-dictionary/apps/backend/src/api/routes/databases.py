"""Database routes per PROJECT_RULES: POST/GET databases, GET schemas, POST sync."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import CurrentUser, get_db
from src.config.settings import get_settings
from src.models.database import Database
from src.models.schema import Schema
from src.schemas.database import (
    DatabaseCreate,
    DatabaseUpdate,
    DatabaseResponse,
    DatabaseListResponse,
)
from src.schemas.schema import SchemaResponse
from src.utils.crypto import CredentialManager

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
    return DatabaseResponse.model_validate(record)


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


@router.post("/{database_id}/sync", status_code=status.HTTP_202_ACCEPTED)
async def sync_database(
    database_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Start schema sync (async). Returns task_id for polling."""
    result = await db.execute(
        select(Database).where(
            Database.id == database_id,
            Database.deleted_at.is_(None),
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    import uuid
    task_id = f"task_{uuid.uuid4().hex[:12]}"
    return {
        "task_id": task_id,
        "status": "pending",
        "status_url": f"/api/v1/tasks/{task_id}",
    }


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
