"""Pydantic schemas for Chat API."""

from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """Schema for chat message request."""

    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    database_id: Optional[int] = Field(None, description="Scope search to specific database")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")

    model_config = {"json_schema_extra": {
        "example": {
            "message": "Show me all customer tables",
            "database_id": 1,
            "conversation_id": "conv_xyz789"
        }
    }}


class ChatToolCall(BaseModel):
    """Schema for LLM tool call."""

    tool_name: str
    parameters: dict
    result: Optional[dict] = None


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""

    conversation_id: str
    message_id: str
    response: str = Field(..., description="AI assistant response")
    intent: Literal["search", "text_to_sql", "question_answer", "clarification"] = Field(
        ...,
        description="Detected intent of user message"
    )
    
    # For search intent
    relevant_tables: Optional[list[int]] = Field(None, description="List of relevant table IDs")
    
    # For text-to-sql intent
    sql_query: Optional[str] = Field(None, description="Generated SQL query")
    sql_explanation: Optional[str] = Field(None, description="Explanation of SQL query")
    query_results: Optional[list[dict]] = Field(None, description="Query execution results")
    
    # Tool calls
    tool_calls: Optional[list[ChatToolCall]] = Field(None, description="Tools invoked by LLM")
    
    # Metadata
    processing_time_ms: int = Field(..., description="Response generation time in milliseconds")
    tokens_used: Optional[int] = Field(None, description="LLM tokens consumed")
    created_at: datetime

    model_config = {"json_schema_extra": {
        "example": {
            "conversation_id": "conv_xyz789",
            "message_id": "msg_abc123",
            "response": "I found 3 customer-related tables: customers, customer_orders, and customer_addresses.",
            "intent": "search",
            "relevant_tables": [1, 5, 8],
            "sql_query": None,
            "sql_explanation": None,
            "query_results": None,
            "tool_calls": [],
            "processing_time_ms": 1250,
            "tokens_used": 450,
            "created_at": "2026-02-20T10:35:00Z"
        }
    }}
