"""LLM service for SQL validation, improvement, and execution assistance."""

import re
from typing import Optional, Literal
import sqlparse
from sqlparse.sql import Token, TokenList
from sqlparse.tokens import Keyword, DML, DDL

from openai import AsyncOpenAI

from src.config.settings import get_settings

settings = get_settings()


class SQLValidator:
    """SQL validation and safety checks."""

    # Dangerous SQL keywords that could modify data or schema
    DANGEROUS_KEYWORDS = {
        "DROP",
        "DELETE",
        "TRUNCATE",
        "INSERT",
        "UPDATE",
        "ALTER",
        "CREATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
    }

    @classmethod
    def is_read_only(cls, sql: str) -> bool:
        """
        Check if SQL is read-only (SELECT queries only).
        
        Args:
            sql: SQL query to check
            
        Returns:
            True if read-only, False if potentially dangerous
        """
        # Parse SQL
        parsed = sqlparse.parse(sql)
        if not parsed:
            return False

        # Check each statement
        for statement in parsed:
            # Get the first significant token (the statement type)
            first_token = None
            for token in statement.tokens:
                if not token.is_whitespace:
                    first_token = token
                    break

            if first_token is None:
                continue

            # Check if it's a DML/DDL keyword
            if first_token.ttype in (Keyword.DML, Keyword.DDL):
                keyword = first_token.value.upper()
                if keyword in cls.DANGEROUS_KEYWORDS:
                    return False

            # Also check for dangerous keywords anywhere in the statement
            sql_upper = statement.value.upper()
            for dangerous in cls.DANGEROUS_KEYWORDS:
                # Use word boundaries to avoid false positives
                if re.search(rf"\b{dangerous}\b", sql_upper):
                    return False

        return True

    @classmethod
    def validate_sql_syntax(cls, sql: str) -> tuple[bool, Optional[str]]:
        """
        Validate SQL syntax.
        
        Args:
            sql: SQL query to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False, "Empty or invalid SQL"

            # Check for basic syntax issues
            for statement in parsed:
                if not statement.tokens:
                    return False, "Invalid SQL statement"

            return True, None
        except Exception as e:
            return False, f"SQL parsing error: {str(e)}"

    @classmethod
    def extract_tables(cls, sql: str) -> list[str]:
        """
        Extract table names from SQL query.
        
        Args:
            sql: SQL query
            
        Returns:
            List of table names
        """
        tables = []
        parsed = sqlparse.parse(sql)

        for statement in parsed:
            # Look for FROM and JOIN clauses
            from_seen = False
            for token in statement.tokens:
                if token.ttype is Keyword and token.value.upper() in ("FROM", "JOIN"):
                    from_seen = True
                elif from_seen and not token.is_whitespace:
                    if isinstance(token, sqlparse.sql.Identifier):
                        tables.append(token.get_real_name())
                    elif token.ttype is None and not token.value.upper() in ("WHERE", "GROUP", "ORDER", "LIMIT"):
                        # Plain table name
                        tables.append(token.value.strip())
                    from_seen = False

        return tables


class LLMService:
    """Service for LLM-powered SQL assistance."""

    def __init__(self):
        """Initialize LLM service."""
        if settings.ai_provider == "openai" or settings.ai_provider == "auto":
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = settings.openai_model_simple  # Use faster model for SQL tasks
        else:
            # For ollama or other providers, this would be extended
            raise NotImplementedError(f"Provider {settings.ai_provider} not yet implemented")

    async def validate_and_improve_sql(
        self, sql: str, context: Optional[str] = None
    ) -> dict:
        """
        Use LLM to validate and suggest improvements for SQL.
        
        Args:
            sql: SQL query to validate
            context: Optional context about the database schema
            
        Returns:
            Dictionary with validation results and suggestions
        """
        # First do basic validation
        is_valid, error = SQLValidator.validate_sql_syntax(sql)
        if not is_valid:
            return {
                "valid": False,
                "error": error,
                "is_read_only": False,
                "suggestions": [],
            }

        is_read_only = SQLValidator.is_read_only(sql)

        # Get LLM suggestions
        prompt = f"""Analyze this SQL query and provide:
1. Whether it's syntactically correct
2. Potential issues or risks
3. Suggestions for improvement (performance, readability)
4. Any security concerns

SQL Query:
```sql
{sql}
```

{f"Database Context: {context}" if context else ""}

Respond in JSON format with keys: issues (list), suggestions (list), security_concerns (list)"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Analyze queries and provide concise, actionable feedback.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            import json

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from LLM")
            llm_response = json.loads(content)

            return {
                "valid": True,
                "is_read_only": is_read_only,
                "formatted_sql": sqlparse.format(
                    sql, reindent=True, keyword_case="upper"
                ),
                "tables": SQLValidator.extract_tables(sql),
                "llm_analysis": llm_response,
            }

        except Exception as e:
            # If LLM fails, still return basic validation
            return {
                "valid": True,
                "is_read_only": is_read_only,
                "formatted_sql": sqlparse.format(
                    sql, reindent=True, keyword_case="upper"
                ),
                "tables": SQLValidator.extract_tables(sql),
                "llm_analysis": None,
                "llm_error": str(e),
            }

    async def generate_sql_from_natural_language(
        self, question: str, schema_context: str
    ) -> dict:
        """
        Generate SQL query from natural language question.
        
        Args:
            question: Natural language question
            schema_context: Database schema information
            
        Returns:
            Dictionary with generated SQL and explanation
        """
        prompt = f"""Convert this natural language question into a SQL query.

Question: {question}

Database Schema:
{schema_context}

Requirements:
1. Generate a valid, safe SQL query (SELECT only)
2. Use proper table and column names from the schema
3. Add appropriate WHERE clauses, JOINs if needed
4. Explain your query logic

Respond in JSON format with keys: sql (string), explanation (string), confidence (float 0-1)"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Generate safe, efficient SQL queries from natural language.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            import json

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from LLM")
            llm_response = json.loads(content)

            # Validate the generated SQL
            generated_sql = llm_response.get("sql", "")
            validation = await self.validate_and_improve_sql(generated_sql, schema_context)

            return {
                "sql": generated_sql,
                "explanation": llm_response.get("explanation", ""),
                "confidence": llm_response.get("confidence", 0.7),
                "validation": validation,
            }

        except Exception as e:
            return {
                "sql": None,
                "explanation": None,
                "error": f"Failed to generate SQL: {str(e)}",
            }

    async def explain_sql_query(self, sql: str) -> dict:
        """
        Explain what a SQL query does in plain English.
        
        Args:
            sql: SQL query to explain
            
        Returns:
            Dictionary with explanation
        """
        prompt = f"""Explain this SQL query in plain English. Be clear and concise.

SQL Query:
```sql
{sql}
```

Explain:
1. What data it retrieves
2. Which tables it uses
3. Any filtering or joining logic
4. Expected output format

Respond in JSON format with keys: summary (string), detailed_steps (list of strings)"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SQL expert. Explain queries clearly to non-technical users.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            import json

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("Empty response from LLM")
            return json.loads(content)

        except Exception as e:
            return {"error": f"Failed to explain SQL: {str(e)}"}
