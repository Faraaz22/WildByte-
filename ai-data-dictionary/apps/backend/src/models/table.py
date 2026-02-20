"""Table model for database tables."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, BigInteger, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

if TYPE_CHECKING:
    from src.models.schema import Schema
    from src.models.column import Column
    from src.models.quality_metric import QualityMetric
    from src.models.lineage_edge import LineageEdge


class Table(Base):
    """
    Database table metadata.
    
    Stores information about tables including AI-generated documentation,
    row counts, and quality metrics.
    """

    __tablename__ = "tables"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    schema_id: Mapped[int] = mapped_column(
        ForeignKey("schemas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Required fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    table_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="table",
        server_default="table",
    )  # table, view, materialized_view

    # Optional fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_generated_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    row_count: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
    )

    # AI Documentation fields
    use_cases: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    freshness_assessment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    considerations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Quality flags
    has_quality_issues: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default="false",
    )
    completeness_pct: Mapped[Optional[float]] = mapped_column(nullable=True)
    freshness_hours: Mapped[Optional[int]] = mapped_column(nullable=True)

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
    last_analyzed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    schema: Mapped["Schema"] = relationship("Schema", back_populates="tables")
    columns: Mapped[list["Column"]] = relationship(
        "Column",
        back_populates="table",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    quality_metrics: Mapped[list["QualityMetric"]] = relationship(
        "QualityMetric",
        back_populates="table",
        cascade="all, delete-orphan",
    )
    upstream_edges: Mapped[list["LineageEdge"]] = relationship(
        "LineageEdge",
        foreign_keys="LineageEdge.downstream_table_id",
        back_populates="downstream_table",
        cascade="all, delete-orphan",
    )
    downstream_edges: Mapped[list["LineageEdge"]] = relationship(
        "LineageEdge",
        foreign_keys="LineageEdge.upstream_table_id",
        back_populates="upstream_table",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_tables_schema_id", "schema_id"),
        Index(
            "idx_tables_search",
            func.to_tsvector("english", name + " " + func.coalesce(description, "")),
            postgresql_using="gin",
        ),
    )

    def __repr__(self) -> str:
        return f"<Table(id={self.id}, name='{self.name}', schema_id={self.schema_id})>"
