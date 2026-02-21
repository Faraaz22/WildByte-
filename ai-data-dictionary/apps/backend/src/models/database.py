"""Database model for storing database connection metadata."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.config.database import Base

if TYPE_CHECKING:
    from src.models.schema import Schema


class DatabaseType(str, enum.Enum):
    """Supported database types."""

    POSTGRESQL = "postgresql"
    SNOWFLAKE = "snowflake"
    SQLSERVER = "sqlserver"
    MYSQL = "mysql"


class Database(Base):
    """
    Database connection metadata.
    
    Stores configuration for connected databases including connection details
    and synchronization status.
    """

    __tablename__ = "databases"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Required fields
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    db_type: Mapped[DatabaseType] = mapped_column(
        SQLEnum(
            DatabaseType,
            name="database_type",
            create_constraint=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        nullable=False,
    )
    connection_string_encrypted: Mapped[str] = mapped_column(Text, nullable=False)

    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    host: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    port: Mapped[Optional[int]] = mapped_column(nullable=True)
    database_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Sync status
    last_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="pending",
        server_default="pending"
    )
    sync_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # Relationships
    schemas: Mapped[list["Schema"]] = relationship(
        "Schema",
        back_populates="database",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Database(id={self.id}, name='{self.name}', type='{self.db_type}')>"
