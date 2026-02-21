"""QualityMetric model for data quality measurements."""

from __future__ import annotations

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey, Float, Integer, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.config.database import Base

if TYPE_CHECKING:
    from src.models.table import Table


class QualityMetric(Base):
    """
    Data quality metric measurement.
    
    Stores time-series quality metrics for tables including completeness,
    freshness, statistical analysis, and anomalies.
    """

    __tablename__ = "quality_metrics"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign keys
    table_id: Mapped[int] = mapped_column(
        ForeignKey("tables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Required fields
    metric_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # completeness, freshness, uniqueness, validity, statistical
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Optional fields
    column_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    threshold_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    threshold_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_violation: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        server_default="false",
    )
    violation_severity: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )  # low, medium, high, critical

    # Statistical details
    sample_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default={},
        server_default="{}",
    )  # Additional metric-specific data

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    table: Mapped["Table"] = relationship("Table", back_populates="quality_metrics")

    # Indexes
    __table_args__ = (
        Index(
            "idx_quality_metrics_composite",
            "table_id",
            "metric_type",
            "measured_at",
            postgresql_ops={"measured_at": "DESC"},
        ),
        Index("idx_quality_metrics_violations", "is_violation", "violation_severity"),
    )

    def __repr__(self) -> str:
        return f"<QualityMetric(id={self.id}, table_id={self.table_id}, type='{self.metric_type}', name='{self.metric_name}', value={self.metric_value})>"
