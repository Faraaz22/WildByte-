"""Pydantic schemas for Table API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from .column import ColumnResponse


class TableResponse(BaseModel):
    """Schema for table list response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    schema_id: int
    name: str
    table_type: str
    description: Optional[str] = None
    ai_generated_description: Optional[str] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    has_quality_issues: bool
    completeness_pct: Optional[float] = None
    freshness_hours: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    last_analyzed_at: Optional[datetime] = None


class TableDetailResponse(BaseModel):
    """Schema for detailed table response with columns."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    schema_id: int
    name: str
    table_type: str
    description: Optional[str] = None
    ai_generated_description: Optional[str] = None
    use_cases: Optional[list[str]] = None
    freshness_assessment: Optional[str] = None
    considerations: Optional[list[str]] = None
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    has_quality_issues: bool
    completeness_pct: Optional[float] = None
    freshness_hours: Optional[int] = None
    metadata_json: Optional[dict] = None
    columns: list[ColumnResponse] = []
    created_at: datetime
    updated_at: datetime
    last_analyzed_at: Optional[datetime] = None


class TableUpdate(BaseModel):
    """Schema for updating table metadata."""

    description: Optional[str] = Field(None, description="User-provided description")
    metadata_json: Optional[dict] = Field(None, description="Additional metadata")


class TableListResponse(BaseModel):
    """Schema for paginated list of tables."""

    data: list[TableResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
