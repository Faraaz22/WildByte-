"""Validation utilities."""

import re
from typing import Tuple

import sqlparse
from sqlglot import parse_one, exp

from src.exceptions import ValidationError, SQLValidationError


def validate_connection_string(connection_string: str, db_type: str) -> Tuple[bool, str]:
    """
    Validate database connection string format.
    
    Args:
        connection_string: Database connection string
        db_type: Database type (postgresql, snowflake, sqlserver, mysql)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not connection_string:
        return False, "Connection string cannot be empty"

    patterns = {
        "postgresql": r"postgresql(\+asyncpg)?://[\w.-]+:[\w.-]+@[\w.-]+:\d+/[\w.-]+",
        "snowflake": r"snowflake://[\w.-]+:[\w.-]+@[\w.-]+/[\w.-]+",
        "sqlserver": r"mssql\+pyodbc://[\w.-]+:[\w.-]+@[\w.-]+/[\w.-]+",
        "mysql": r"mysql(\+pymysql)?://[\w.-]+:[\w.-]+@[\w.-]+:\d+/[\w.-]+",
    }

    pattern = patterns.get(db_type.lower())
    if not pattern:
        return False, f"Unsupported database type: {db_type}"

    if not re.match(pattern, connection_string):
        return False, f"Invalid {db_type} connection string format"

    return True, "Valid"


def validate_sql_query(sql: str, db_type: str) -> Tuple[bool, str]:
    """
    Validate SQL query for safety and correctness.
    
    Checks for:
    - Valid SQL syntax
    - Read-only operations (no INSERT, UPDATE, DELETE, DROP, CREATE, ALTER)
    - No multiple statements
    - No suspicious keywords (EXEC, EXECUTE, xp_cmdshell, etc.)
    
    Args:
        sql: SQL query string
        db_type: Database type for dialect-specific parsing
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Raises:
        SQLValidationError: If query is invalid or unsafe
    """
    if not sql or not sql.strip():
        return False, "SQL query cannot be empty"

    # Parse SQL
    try:
        parsed = sqlparse.parse(sql)
    except Exception as e:
        return False, f"SQL parsing error: {str(e)}"

    if len(parsed) == 0:
        return False, "No SQL statements found"

    if len(parsed) > 1:
        return False, "Multiple SQL statements not allowed"

    statement = parsed[0]

    # Check statement type (must be SELECT)
    statement_type = statement.get_type()
    if statement_type != "SELECT":
        return False, f"Only SELECT queries allowed, found: {statement_type}"

    # Check for dangerous keywords
    dangerous_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "TRUNCATE",
        "EXEC", "EXECUTE", "xp_cmdshell", "sp_executesql", "GRANT", "REVOKE",
    ]

    sql_upper = sql.upper()
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return False, f"Dangerous keyword not allowed: {keyword}"

    # Additional validation with sqlglot
    try:
        tree = parse_one(sql, dialect=db_type if db_type in ["postgres", "snowflake", "mysql"] else "postgres")
        
        # Ensure it's a SELECT expression
        if not isinstance(tree, exp.Select):
            return False, "Only SELECT queries are allowed"

    except Exception as e:
        return False, f"SQL validation error: {str(e)}"

    return True, "Valid"
