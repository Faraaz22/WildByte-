"""Database management API endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.database import get_db
from src.models.database import Database
from src.models.user import User
from src.schemas.database import (
    DatabaseCreate,
    DatabaseUpdate,
    DatabaseResponse,
    DatabaseListResponse,
)
from src.api.auth import get_current_user
from src.utils.crypto import encrypt_connection_string, decrypt_connection_string

router = APIRouter()


@router.get("/", response_model=DatabaseListResponse)
async def list_databases(
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all database connections with pagination.
    
    Returns paginated list of databases with sync status.
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get total count
    count_query = select(func.count(Database.id)).where(Database.deleted_at.is_(None))
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    
    # Get paginated data
    query = (
        select(Database)
        .where(Database.deleted_at.is_(None))
        .order_by(Database.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(query)
    databases = result.scalars().all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return DatabaseListResponse(
        data=[DatabaseResponse.model_validate(db) for db in databases],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{database_id}", response_model=DatabaseResponse)
async def get_database(
    database_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific database by ID.
    
    Returns database details including sync status.
    """
    query = select(Database).where(
        Database.id == database_id,
        Database.deleted_at.is_(None)
    )
    result = await db.execute(query)
    database = result.scalar_one_or_none()
    
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database with ID {database_id} not found"
        )
    
    return DatabaseResponse.model_validate(database)


@router.post("/", response_model=DatabaseResponse, status_code=status.HTTP_201_CREATED)
async def create_database(
    database_data: DatabaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new database connection.
    
    Encrypts credentials before storing. Does not automatically sync schemas.
    """
    # Check if database name already exists
    existing_query = select(Database).where(
        Database.name == database_data.name,
        Database.deleted_at.is_(None)
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database with name '{database_data.name}' already exists"
        )
    
    # Build connection string
    connection_string = (
        f"{database_data.db_type}://{database_data.username}:{database_data.password}"
        f"@{database_data.host}:{database_data.port}/{database_data.database_name}"
    )
    
    # Encrypt connection string
    encrypted_conn_string = encrypt_connection_string(connection_string)
    
    # Create database record
    new_database = Database(
        name=database_data.name,
        db_type=database_data.db_type,
        connection_string_encrypted=encrypted_conn_string,
        description=database_data.description,
        host=database_data.host,
        port=database_data.port,
        database_name=database_data.database_name,
        sync_status="pending",
    )
    
    db.add(new_database)
    await db.commit()
    await db.refresh(new_database)
    
    return DatabaseResponse.model_validate(new_database)


@router.put("/{database_id}", response_model=DatabaseResponse)
async def update_database(
    database_id: int,
    database_data: DatabaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing database connection.
    
    Re-encrypts credentials if password is changed.
    """
    # Get existing database
    query = select(Database).where(
        Database.id == database_id,
        Database.deleted_at.is_(None)
    )
    result = await db.execute(query)
    database = result.scalar_one_or_none()
    
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database with ID {database_id} not found"
        )
    
    # Update fields
    update_data = database_data.model_dump(exclude_unset=True)
    
    # If credentials changed, rebuild and re-encrypt connection string
    if any(key in update_data for key in ['host', 'port', 'database_name', 'username', 'password']):
        # Get current decrypted connection string
        current_conn = decrypt_connection_string(database.connection_string_encrypted)
        
        # Parse current connection string
        # Format: postgresql://user:pass@host:port/dbname
        protocol = current_conn.split('://')[0]
        rest = current_conn.split('://')[1]
        auth, location = rest.split('@')
        username, password = auth.split(':')
        host_port, db_name = location.split('/')
        host, port = host_port.split(':')
        
        # Update with new values
        new_username = update_data.get('username', username)
        new_password = update_data.get('password', password)
        new_host = update_data.get('host', host)
        new_port = update_data.get('port', port)
        new_db_name = update_data.get('database_name', db_name)
        
        # Build new connection string
        new_conn_string = f"{protocol}://{new_username}:{new_password}@{new_host}:{new_port}/{new_db_name}"
        database.connection_string_encrypted = encrypt_connection_string(new_conn_string)
        
        # Update metadata fields
        if 'host' in update_data:
            database.host = update_data['host']
        if 'port' in update_data:
            database.port = update_data['port']
        if 'database_name' in update_data:
            database.database_name = update_data['database_name']
    
    # Update other fields
    if 'name' in update_data:
        database.name = update_data['name']
    if 'description' in update_data:
        database.description = update_data['description']
    
    await db.commit()
    await db.refresh(database)
    
    return DatabaseResponse.model_validate(database)


@router.delete("/{database_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(
    database_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Soft delete a database connection.
    
    Sets deleted_at timestamp. Actual deletion happens later via cleanup job.
    """
    query = select(Database).where(
        Database.id == database_id,
        Database.deleted_at.is_(None)
    )
    result = await db.execute(query)
    database = result.scalar_one_or_none()
    
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database with ID {database_id} not found"
        )
    
    # Soft delete
    database.deleted_at = func.now()
    await db.commit()
    
    return None


@router.post("/{database_id}/test", response_model=dict)
async def test_database_connection(
    database_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Test database connection without saving.
    
    Returns connection status and error details if connection fails.
    """
    query = select(Database).where(
        Database.id == database_id,
        Database.deleted_at.is_(None)
    )
    result = await db.execute(query)
    database = result.scalar_one_or_none()
    
    if not database:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Database with ID {database_id} not found"
        )
    
    # Decrypt connection string
    connection_string = decrypt_connection_string(database.connection_string_encrypted)
    
    try:
        # Test connection based on database type
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        # Create test engine
        test_engine = create_async_engine(connection_string, pool_pre_ping=True)
        
        # Try to connect and run a simple query
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        await test_engine.dispose()
        
        # Update sync status
        database.sync_status = "connected"
        database.sync_error = None
        await db.commit()
        
        return {
            "status": "success",
            "message": "Connection successful",
            "connected": True
        }
        
    except Exception as e:
        # Update sync status with error
        database.sync_status = "error"
        database.sync_error = str(e)
        await db.commit()
        
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)}",
            "connected": False,
            "error": str(e)
        }


@router.post("/test-new", response_model=dict)
async def test_new_database_connection(
    database_data: DatabaseCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Test a new database connection before saving.
    
    Does not persist the connection. Useful for validation during creation.
    """
    # Build connection string
    connection_string = (
        f"{database_data.db_type}://{database_data.username}:{database_data.password}"
        f"@{database_data.host}:{database_data.port}/{database_data.database_name}"
    )
    
    try:
        # Test connection
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        test_engine = create_async_engine(connection_string, pool_pre_ping=True)
        
        async with test_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        
        await test_engine.dispose()
        
        return {
            "status": "success",
            "message": "Connection successful",
            "connected": True
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Connection failed: {str(e)}",
            "connected": False,
            "error": str(e)
        }
