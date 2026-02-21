"""Chat service using Gemini (free tier: gemini-1.5-flash)."""

import json
import time
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.config.settings import get_settings

settings = get_settings()


def _format_schema_for_prompt(context: dict) -> str:
    """Turn schema context dict into a string for the LLM."""
    parts = [
        f"Database: {context.get('database_name', 'Unknown')} (id={context.get('database_id')})",
        "",
        "Schemas and tables:",
    ]
    for schema in context.get("schemas", []):
        parts.append(f"  Schema: {schema['name']}")
        for table in schema.get("tables", []):
            cols = table.get("columns", [])
            col_strs = [
                f"{c['name']} ({c['data_type']})"
                + (" PK" if c.get("is_primary_key") else "")
                + (" FK→" + (c.get("foreign_key_ref") or "?") if c.get("is_foreign_key") else "")
                for c in cols
            ]
            parts.append(f"    Table: {table['name']} ({table.get('table_type', 'table')})")
            if table.get("description"):
                parts.append(f"      Description: {table['description']}")
            parts.append("      Columns: " + ", ".join(col_strs))
        parts.append("")
    parts.append("Lineage (upstream → downstream):")
    for edge in context.get("lineage", []):
        parts.append(f"  {edge.get('upstream')} → {edge.get('downstream')} ({edge.get('type', '')})")
    return "\n".join(parts)


async def chat_with_schema(
    message: str,
    schema_context: dict,
    conversation_id: str | None = None,
) -> dict[str, Any]:
    """
    Send user message to Gemini with schema context. Uses gemini-1.5-flash (free tier).
    Returns dict with response, conversation_id, message_id, processing_time_ms, etc.
    """
    if not settings.gemini_api_key:
        return {
            "response": "Gemini is not configured. Set GEMINI_API_KEY in .env to use chat.",
            "conversation_id": conversation_id or str(uuid4()),
            "message_id": str(uuid4()),
            "intent": "clarification",
            "processing_time_ms": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "error": "missing_gemini_api_key",
        }

    try:
        try:
            import google.generativeai as genai
        except ImportError as ie:
            return {
                "response": "Chat requires the google-generativeai package. From the backend folder run: pip install google-generativeai (or install from requirements.txt). Then restart the backend.",
                "conversation_id": conversation_id or str(uuid4()),
                "message_id": str(uuid4()),
                "intent": "clarification",
                "processing_time_ms": 0,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "error": str(ie),
            }

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(settings.gemini_model)

        schema_text = _format_schema_for_prompt(schema_context)
        system_instruction = """You are a helpful data dictionary assistant. You have access to the database schema (tables, columns, types, primary/foreign keys) and lineage (table dependencies). Answer questions about tables, columns, relationships, and suggest SQL when appropriate. Be concise and accurate. If the user asks for SQL, return only safe SELECT queries."""

        prompt = f"""Schema context:
{schema_text}

User question: {message}

Answer based on the schema and lineage above. Use markdown for lists and code (e.g. SQL) when relevant."""

        start = time.perf_counter()
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=8192,
            ),
        )
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        text = ""
        if response and response.candidates:
            for part in response.candidates[0].content.parts:
                if hasattr(part, "text") and part.text:
                    text += part.text

        if not text and response.prompt_feedback:
            text = "I couldn't generate a reply. Please try rephrasing or check that your database has been synced."

        conv_id = conversation_id or str(uuid4())
        return {
            "response": text.strip() or "No response generated.",
            "conversation_id": conv_id,
            "message_id": str(uuid4()),
            "intent": "question_answer",
            "processing_time_ms": elapsed_ms,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "response": f"Sorry, an error occurred: {str(e)}",
            "conversation_id": conversation_id or str(uuid4()),
            "message_id": str(uuid4()),
            "intent": "clarification",
            "processing_time_ms": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
        }
