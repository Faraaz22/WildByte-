"""Pydantic schemas for Lineage API."""

from typing import Optional

from pydantic import BaseModel, ConfigDict


class LineageResponse(BaseModel):
    """Schema for lineage edge response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    upstream_table_id: int
    downstream_table_id: int
    relationship_type: str
    description: Optional[str] = None
    column_mapping: Optional[dict] = None
    confidence_score: Optional[float] = None


class LineageNodeResponse(BaseModel):
    """Schema for lineage graph node."""

    id: int
    name: str
    schema_name: str
    table_type: str
    level: int  # Depth in lineage graph


class LineageEdgeResponse(BaseModel):
    """Schema for lineage graph edge."""

    source: int  # upstream_table_id
    target: int  # downstream_table_id
    relationship_type: str
    label: Optional[str] = None
    column_mapping: Optional[list[dict]] = None  # e.g. [{"referenced_column": "id", "referencing_column": "customer_id"}]
    cardinality: Optional[str] = None  # one_to_one, one_to_many, many_to_many (via join table)
    is_join_table: Optional[bool] = None


class LineageGraphResponse(BaseModel):
    """Schema for complete lineage graph."""

    nodes: list[LineageNodeResponse]
    edges: list[LineageEdgeResponse]
    root_table_id: int


class LineageFullGraphResponse(BaseModel):
    """Full lineage graph (all tables, optional database filter)."""

    nodes: list[LineageNodeResponse]
    edges: list[LineageEdgeResponse]
