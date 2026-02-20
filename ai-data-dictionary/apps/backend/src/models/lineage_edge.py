"""LineageEdge model for table dependencies."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

if TYPE_CHECKING:
    from src.models.table import Table


class LineageEdge(Base):
    """
    Table lineage relationship.
    
    Represents dependencies between tables (e.g., foreign keys, view dependencies,
    ETL transformations).
    """

    __tablename__ = "lineage_edges"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    upstream_table_id: Mapped[int] = mapped_column(
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    downstream_table_id: Mapped[int] = mapped_column(
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Required fields
    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # foreign_key, view_dependency, etl_transform

    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    column_mapping: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )  # {"upstream_col": "downstream_col"}
    confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)  # 0.0 to 1.0
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
    upstream_table: Mapped["Table"] = relationship(
        "Table",
        foreign_keys=[upstream_table_id],
        back_populates="downstream_edges",
    )
    downstream_table: Mapped["Table"] = relationship(
        "Table",
        foreign_keys=[downstream_table_id],
        back_populates="upstream_edges",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "upstream_table_id",
            "downstream_table_id",
            "relationship_type",
            name="uq_lineage_edge",
        ),
    )

    def __repr__(self) -> str:
        return f"<LineageEdge(id={self.id}, upstream={self.upstream_table_id}, downstream={self.downstream_table_id}, type='{self.relationship_type}')>"
