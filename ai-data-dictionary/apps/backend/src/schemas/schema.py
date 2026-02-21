"""Pydantic schemas for Schema API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SchemaResponse(BaseModel):
    """Schema for database schema response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    database_id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    table_count: Optional[int] = None  # Computed field
