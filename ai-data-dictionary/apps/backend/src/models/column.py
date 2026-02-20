"""Column model for table columns."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Integer, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

if TYPE_CHECKING:
    from src.models.table import Table


class Column(Base):
    """
    Database column metadata.
    
    Stores detailed information about table columns including data types,
    constraints, and sample values.
    """

    __tablename__ = "columns"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    table_id: Mapped[int] = mapped_column(
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Required fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(100), nullable=False)
    ordinal_position: Mapped[int] = mapped_column(Integer, nullable=False)

    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_generated_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_nullable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    is_primary_key: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    is_foreign_key: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    is_unique: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Data characteristics
    default_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    numeric_precision: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    numeric_scale: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Quality metrics
    null_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    null_percentage: Mapped[Optional[float]] = mapped_column(nullable=True)
    distinct_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sample_values: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Foreign key reference
    foreign_key_table: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    foreign_key_column: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Metadata
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    table: Mapped["Table"] = relationship("Table", back_populates="columns")

    def __repr__(self) -> str:
        return f"<Column(id={self.id}, name='{self.name}', table_id={self.table_id}, type='{self.data_type}')>"
