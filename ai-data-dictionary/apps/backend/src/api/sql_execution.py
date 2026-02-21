"""SQL execution and editing API endpoints."""

from typing import Annotated, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import get_current_user
from src.config.database import get_db
from src.config.settings import get_settings
from src.models.user import User
from src.services.llm_service import LLMService, SQLValidator

router = APIRouter()
settings = get_settings()


# Pydantic schemas
class SQLValidationRequest(BaseModel):
    """SQL validation request."""

    sql: str = Field(..., description="SQL query to validate")
    context: Optional[str] = Field(None, description="Optional database schema context")


class SQLValidationResponse(BaseModel):
    """SQL validation response."""

    valid: bool
    is_read_only: bool
    error: Optional[str] = None
    formatted_sql: Optional[str] = None
    tables: Optional[list[str]] = None
    llm_analysis: Optional[dict] = None


class SQLExecutionRequest(BaseModel):
    """SQL execution request."""

    sql: str = Field(..., description="SQL query to execute")
    validate_with_llm: bool = Field(
        True, description="Whether to validate with LLM before execution"
    )
    allow_write: bool = Field(
        False, description="Allow write operations (INSERT, UPDATE, DELETE)"
    )


class SQLExecutionResponse(BaseModel):
    """SQL execution response."""

    success: bool
    rows_affected: Optional[int] = None
    data: Optional[list[dict]] = None
    columns: Optional[list[str]] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None
    validation: Optional[dict] = None


class NaturalLanguageToSQLRequest(BaseModel):
    """Natural language to SQL request."""

    question: str = Field(..., description="Natural language question")
    schema_context: str = Field(..., description="Database schema information")


class NaturalLanguageToSQLResponse(BaseModel):
    """Natural language to SQL response."""

    sql: Optional[str] = None
    explanation: Optional[str] = None
    confidence: Optional[float] = None
    validation: Optional[dict] = None
    error: Optional[str] = None


class SQLExplanationRequest(BaseModel):
    """SQL explanation request."""

    sql: str = Field(..., description="SQL query to explain")


class SQLExplanationResponse(BaseModel):
    """SQL explanation response."""

    summary: Optional[str] = None
    detailed_steps: Optional[list[str]] = None
    error: Optional[str] = None


@router.post("/validate", response_model=SQLValidationResponse)
async def validate_sql(
    request: SQLValidationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Validate SQL query with LLM assistance.
    
    Args:
        request: SQL validation request
        current_user: Current authenticated user
        
    Returns:
        Validation results with LLM suggestions
    """
    llm_service = LLMService()
    result = await llm_service.validate_and_improve_sql(request.sql, request.context)

    return SQLValidationResponse(
        valid=result["valid"],
        is_read_only=result.get("is_read_only", False),
        error=result.get("error"),
        formatted_sql=result.get("formatted_sql"),
        tables=result.get("tables"),
        llm_analysis=result.get("llm_analysis"),
    )


@router.post("/execute", response_model=SQLExecutionResponse)
async def execute_sql(
    request: SQLExecutionRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Execute SQL query with safety checks.
    
    Args:
        request: SQL execution request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Execution results
        
    Raises:
        HTTPException: If query is unsafe or execution fails
    """
    import time

    # Basic validation
    is_valid, error = SQLValidator.validate_sql_syntax(request.sql)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid SQL syntax: {error}",
        )

    # Check if read-only
    is_read_only = SQLValidator.is_read_only(request.sql)
    if not is_read_only and not request.allow_write:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Write operations are not allowed. Set allow_write=true if you want to execute write operations.",
        )

    # Optional LLM validation
    validation_result = None
    if request.validate_with_llm:
        llm_service = LLMService()
        validation_result = await llm_service.validate_and_improve_sql(request.sql)

        if not validation_result["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SQL validation failed: {validation_result.get('error')}",
            )

    # Execute query
    try:
        start_time = time.time()

        result = await db.execute(text(request.sql))

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        # Handle SELECT queries
        if is_read_only:
            # Fetch results
            rows = result.fetchall()

            # Convert to list of dictionaries
            data = []
            columns = list(result.keys()) if rows else []

            for row in rows:
                data.append(dict(row._mapping))

            return SQLExecutionResponse(
                success=True,
                data=data[:settings.max_query_result_rows],  # Limit rows
                columns=columns,
                execution_time_ms=round(execution_time, 2),
                validation=validation_result,
            )
        else:
            # Handle write operations
            await db.commit()
            rows_affected = getattr(result, 'rowcount', None)
            return SQLExecutionResponse(
                success=True,
                rows_affected=rows_affected,
                execution_time_ms=round(execution_time, 2),
                validation=validation_result,
            )

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(e)}",
        )


@router.post("/generate", response_model=NaturalLanguageToSQLResponse)
async def generate_sql_from_natural_language(
    request: NaturalLanguageToSQLRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Generate SQL from natural language question.
    
    Args:
        request: Natural language question and schema context
        current_user: Current authenticated user
        
    Returns:
        Generated SQL query with explanation
    """
    llm_service = LLMService()
    result = await llm_service.generate_sql_from_natural_language(
        request.question, request.schema_context
    )

    return NaturalLanguageToSQLResponse(
        sql=result.get("sql"),
        explanation=result.get("explanation"),
        confidence=result.get("confidence"),
        validation=result.get("validation"),
        error=result.get("error"),
    )


@router.post("/explain", response_model=SQLExplanationResponse)
async def explain_sql(
    request: SQLExplanationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Explain SQL query in plain English.
    
    Args:
        request: SQL query to explain
        current_user: Current authenticated user
        
    Returns:
        Plain English explanation of the query
    """
    llm_service = LLMService()
    result = await llm_service.explain_sql_query(request.sql)

    return SQLExplanationResponse(
        summary=result.get("summary"),
        detailed_steps=result.get("detailed_steps"),
        error=result.get("error"),
    )


@router.post("/format")
async def format_sql(
    sql: str,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Format SQL query for better readability.
    
    Args:
        sql: SQL query to format
        current_user: Current authenticated user
        
    Returns:
        Formatted SQL
    """
    import sqlparse

    try:
        formatted = sqlparse.format(
            sql,
            reindent=True,
            keyword_case="upper",
            identifier_case="lower",
            strip_comments=False,
            use_space_around_operators=True,
        )
        return {"formatted_sql": formatted}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to format SQL: {str(e)}",
        )
