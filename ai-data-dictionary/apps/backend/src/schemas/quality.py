"""Pydantic schemas for Quality Metrics API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class QualityMetricResponse(BaseModel):
    """Schema for quality metric response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    table_id: int
    metric_type: str
    metric_name: str
    metric_value: float
    measured_at: datetime
    column_name: Optional[str] = None
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    is_violation: bool
    violation_severity: Optional[str] = None
    sample_size: Optional[int] = None
    details: Optional[dict] = None


class QualityReportResponse(BaseModel):
    """Schema for comprehensive quality report."""

    table_id: int
    table_name: str
    overall_score: float  # 0-100
    completeness_metrics: list[QualityMetricResponse]
    freshness_metrics: list[QualityMetricResponse]
    statistical_metrics: list[QualityMetricResponse]
    violations: list[QualityMetricResponse]
    generated_at: datetime
