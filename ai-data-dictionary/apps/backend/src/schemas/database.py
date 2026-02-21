"""Pydantic schemas for Database API."""

from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


class DatabaseType(str, Enum):
    """Supported database types."""

    POSTGRESQL = "postgresql"
    SNOWFLAKE = "snowflake"
    SQLSERVER = "sqlserver"
    MYSQL = "mysql"


class TestConnectionByUriRequest(BaseModel):
    """Schema for testing a database connection by URI."""

    connection_uri: str = Field(..., min_length=1, description="PostgreSQL URI, e.g. postgresql://user:pass@host:5432/dbname")


class CreateDatabaseFromUriRequest(BaseModel):
    """Schema for creating a database connection from a URI."""

    name: str = Field(..., min_length=1, max_length=100, description="Display name for the connection")
    connection_uri: str = Field(..., min_length=1, description="PostgreSQL URI")
    description: Optional[str] = Field(None, description="Optional description")


class DatabaseCreate(BaseModel):
    """Schema for creating a new database connection."""

    name: str = Field(..., min_length=1, max_length=100, description="Database name")
    db_type: DatabaseType = Field(..., description="Database type")
    host: str = Field(..., description="Database host")
    port: int = Field(..., ge=1, le=65535, description="Database port")
    database_name: str = Field(..., description="Database/catalog name")
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    description: Optional[str] = Field(None, description="Optional description")

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "production_db",
            "db_type": "postgresql",
            "host": "db.example.com",
            "port": 5432,
            "database_name": "analytics",
            "username": "readonly_user",
            "password": "secure_password",
            "description": "Production analytics database"
        }
    })


class DatabaseUpdate(BaseModel):
    """Schema for updating a database connection."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None)
    host: Optional[str] = Field(None)
    port: Optional[int] = Field(None, ge=1, le=65535)
    database_name: Optional[str] = Field(None)
    username: Optional[str] = Field(None)
    password: Optional[str] = Field(None)


class DatabaseResponse(BaseModel):
    """Schema for database response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    db_type: str
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database_name: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    sync_status: str
    sync_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DatabaseListResponse(BaseModel):
    """Schema for paginated list of databases."""

    data: list[DatabaseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
