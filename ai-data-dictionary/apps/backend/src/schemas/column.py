"""Pydantic schemas for Column API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ColumnResponse(BaseModel):
    """Schema for column response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    table_id: int
    name: str
    data_type: str
    ordinal_position: int
    description: Optional[str] = None
    ai_generated_description: Optional[str] = None
    is_nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    is_unique: bool
    default_value: Optional[str] = None
    max_length: Optional[int] = None
    numeric_precision: Optional[int] = None
    numeric_scale: Optional[int] = None
    null_count: Optional[int] = None
    null_percentage: Optional[float] = None
    distinct_count: Optional[int] = None
    sample_values: Optional[list] = None
    foreign_key_table: Optional[str] = None
    foreign_key_column: Optional[str] = None
    created_at: datetime
    updated_at: datetime
