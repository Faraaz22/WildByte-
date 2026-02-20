# AI Data Dictionary Platform - Project Rules & Standards

**Version:** 1.0  
**Last Updated:** February 20, 2026  
**Status:** Active

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Principles](#architecture-principles)
3. [Code Standards](#code-standards)
4. [API Design Rules](#api-design-rules)
5. [Database Standards](#database-standards)
6. [AI/LLM Integration Guidelines](#aillm-integration-guidelines)
7. [Security Requirements](#security-requirements)
8. [Testing Standards](#testing-standards)
9. [Documentation Requirements](#documentation-requirements)
10. [Performance Benchmarks](#performance-benchmarks)
11. [Git Workflow](#git-workflow)
12. [Deployment Rules](#deployment-rules)
13. [Error Handling](#error-handling)
14. [Logging & Monitoring](#logging--monitoring)
15. [UI/UX Guidelines](#uiux-guidelines)

---

## Project Overview

### Mission Statement
Build a production-grade, AI-enhanced data dictionary platform that automatically documents enterprise databases, performs data quality analysis, and enables natural language interaction with database metadata.

### Core Objectives
1. **Automated Documentation:** Generate business-friendly documentation for database schemas using AI
2. **Data Quality Insights:** Provide completeness, freshness, and statistical analysis metrics
3. **Natural Language Interface:** Enable chat-based queries and text-to-SQL generation
4. **Lineage Visualization:** Show upstream/downstream table dependencies
5. **Incremental Updates:** Track and respond to schema changes automatically

### Target Users
- **Primary:** Data Analysts (Business Intelligence, reporting, ad-hoc analysis)
- **Secondary:** Data Engineers (schema management, quality monitoring, impact analysis)

### Demo Dataset
- **Source:** Olist Brazilian E-commerce (Kaggle)
- **Tables:** orders, customers, order_items, products, sellers, reviews, payments, geolocation
- **Use Case:** Demonstrates real-world e-commerce analytics workflows

---

## Architecture Principles

### 1. Modular Monolith Architecture

**RULE 1.1: Single Deployable Unit**
- All services run within a single application boundary
- Clear module boundaries with defined interfaces
- Modules: `auth`, `catalog`, `quality`, `lineage`, `chat`, `export`, `ingestion`, `audit`

**RULE 1.2: Module Isolation**
- Modules communicate through well-defined service interfaces
- No direct database access across module boundaries
- Each module has its own service layer (`services/`) and repository layer (`repositories/`)

**RULE 1.3: Shared Kernel**
- Common utilities in `src/utils/` (logging, crypto, validators, retry logic)
- Shared models in `src/models/` (database, schemas, tables, columns)
- Configuration in `src/config/` (settings, database connection)

### 2. Event-Driven Task Processing

**RULE 2.1: Async Task Execution**
- Long-running operations MUST be Celery tasks: schema extraction, quality analysis, AI doc generation, lineage extraction
- HTTP endpoints return task IDs immediately, clients poll for status
- Task state stored in PostgreSQL `task_results` table

**RULE 2.2: Event Topics**
- `schema.extracted` → trigger AI documentation, quality analysis, lineage extraction
- `schema.changed` → trigger incremental documentation update, notification
- `quality.violation` → trigger alerts
- `export.completed` → trigger notification

**RULE 2.3: Task Scheduling**
- Celery Beat for periodic tasks:
  - Incremental sync: Every 30 minutes
  - Full sync: Daily at 2 AM (configurable)
  - Quality monitoring: Every 6 hours
- Schedule configuration in `src/workers/schedules.py`

### 3. Hybrid RAG (Retrieval Augmented Generation)

**RULE 3.1: Dual Retrieval Strategy**
- **Structured retrieval:** Query PostgreSQL metadata for exact table/column matches
- **Vector retrieval:** Query ChromaDB for semantic similarity on descriptions/documentation
- **Hybrid scoring:** Combine exact match (weight: 0.6) + semantic match (weight: 0.4)

**RULE 3.2: Context Window Management**
- Maximum 5 tables in LLM context (token limit: ~16k for GPT-4 Turbo)
- Prioritize tables by relevance score
- Include: table description, columns with types, sample values, FK relationships, quality metrics

**RULE 3.3: Tool Calling**
- LLM can invoke tools: `get_table_schema`, `get_lineage`, `get_quality_metrics`, `execute_sql` (read-only)
- Validate tool parameters before execution
- Return tool results to LLM for final response synthesis

### 4. Tech Stack Constraints

**Backend (Python 3.11+):**
- Framework: FastAPI 0.109+
- ORM: SQLAlchemy 2.0+
- Task Queue: Celery 5.3+ with Redis 5.0+
- Database Connectors: snowflake-connector-python, psycopg2-binary, pyodbc
- AI: OpenAI 1.12+, LangChain 0.1+, ChromaDB 0.4+
- Data Quality: ydata-profiling 4.6+, pandera 0.18+
- Utilities: pydantic 2.0+, tenacity, structlog

**Frontend (React/Next.js 14):**
- Framework: Next.js 14 (App Router)
- Language: TypeScript 5.0+
- State Management: TanStack Query (server state), Zustand (UI state)
- UI Components: Shadcn/ui (built on Radix UI)
- Styling: Tailwind CSS 3.0+
- Visualizations: Recharts (charts), React Flow (lineage graphs)
- Code Editor: Monaco Editor (SQL syntax highlighting)

**Infrastructure:**
- Metadata Database: PostgreSQL 15+ with TimescaleDB extension
- Vector Database: ChromaDB (embedded mode)
- Message Broker: Redis 7.0+
- Containerization: Docker with Docker Compose
- Local LLM (optional): Ollama with Llama 3 8B

---

## Code Standards

### 1. Python Standards

**RULE 3.1: Type Hints (Mandatory)**
```python
# ✅ CORRECT
def extract_schema(
    connection: Connection,
    schema_name: str,
    include_views: bool = True
) -> SchemaMetadata:
    pass

# ❌ INCORRECT - No type hints
def extract_schema(connection, schema_name, include_views=True):
    pass
```

**RULE 3.2: Pydantic for Data Validation**
- All API request/response models MUST use Pydantic
- Use `ConfigDict(from_attributes=True)` for ORM compatibility
```python
class TableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    row_count: int | None = None
    description: str | None = None
    created_at: datetime
```

**RULE 3.3: Async/Await for I/O Operations**
- Use `async def` for database queries, HTTP requests, file I/O
- Use `asyncio.gather()` for parallel operations
```python
# ✅ CORRECT
async def get_multiple_tables(table_ids: list[int]) -> list[Table]:
    tasks = [get_table(tid) for tid in table_ids]
    return await asyncio.gather(*tasks)
```

**RULE 3.4: Naming Conventions**
- Classes: PascalCase (`DatabaseConnector`, `SchemaExtractor`)
- Functions/Methods: snake_case (`extract_schema`, `get_lineage`)
- Constants: UPPER_SNAKE_CASE (`MAX_CONTEXT_TABLES`, `DEFAULT_POOL_SIZE`)
- Private members: Leading underscore (`_validate_connection`)

**RULE 3.5: Docstrings (Google Style)**
```python
def analyze_quality(table_id: int, sample_size: int = 10000) -> QualityMetrics:
    """
    Analyze data quality metrics for a table.
    
    Args:
        table_id: Primary key of the table to analyze
        sample_size: Number of rows to sample for analysis (default: 10000)
        
    Returns:
        QualityMetrics object containing completeness, uniqueness, and distribution stats
        
    Raises:
        TableNotFoundError: If table_id does not exist
        ConnectionError: If database connection fails
        
    Example:
        >>> metrics = analyze_quality(table_id=42, sample_size=5000)
        >>> print(metrics.completeness_pct)
        97.5
    """
    pass
```

**RULE 3.6: Error Handling**
- Use custom exceptions in `src/exceptions.py`
- Catch specific exceptions, not bare `except:`
```python
# ✅ CORRECT
try:
    connection = connector.connect()
except ConnectionError as e:
    logger.error(f"Failed to connect: {e}")
    raise DatabaseConnectionError(f"Cannot connect to {db_type}") from e

# ❌ INCORRECT
try:
    connection = connector.connect()
except:
    pass
```

**RULE 3.7: Logging**
- Use structlog for structured logging
- Include context: `user_id`, `database_id`, `table_id`, `task_id`
```python
logger.info(
    "schema_extraction_started",
    database_id=database_id,
    table_count=len(tables),
    user_id=current_user.id
)
```

**RULE 3.8: Code Formatting**
- Formatter: `ruff format` (compatible with Black)
- Linter: `ruff check` (replaces Flake8, isort, pyupgrade)
- Max line length: 100 characters
- Import order: stdlib → third-party → local

### 2. TypeScript/React Standards

**RULE 3.9: TypeScript Strict Mode**
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

**RULE 3.10: Component Structure**
- Functional components with hooks (no class components)
- One component per file
- Co-locate styles, tests, and types
```tsx
// ✅ CORRECT structure
components/
  TableDetail/
    TableDetail.tsx
    TableDetail.test.tsx
    types.ts
    hooks.ts
```

**RULE 3.11: Props Interface**
```tsx
// ✅ CORRECT
interface TableDetailProps {
  tableId: number;
  onEdit?: () => void;
  className?: string;
}

export function TableDetail({ tableId, onEdit, className }: TableDetailProps) {
  // ...
}
```

**RULE 3.12: Data Fetching with TanStack Query**
```tsx
// ✅ CORRECT - Server state managed by React Query
import { useQuery } from '@tanstack/react-query';

export function useTable(tableId: number) {
  return useQuery({
    queryKey: ['table', tableId],
    queryFn: () => fetchTable(tableId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
```

**RULE 3.13: UI State with Zustand**
```tsx
// ✅ CORRECT - UI state in Zustand store
import { create } from 'zustand';

interface FilterState {
  selectedSchema: string | null;
  searchQuery: string;
  setSelectedSchema: (schema: string | null) => void;
  setSearchQuery: (query: string) => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  selectedSchema: null,
  searchQuery: '',
  setSelectedSchema: (schema) => set({ selectedSchema: schema }),
  setSearchQuery: (query) => set({ searchQuery: query }),
}));
```

**RULE 3.14: Naming Conventions**
- Components: PascalCase (`TableDetail.tsx`)
- Hooks: camelCase with `use` prefix (`useTable.ts`)
- Utils: camelCase (`formatTimestamp.ts`)
- Constants: UPPER_SNAKE_CASE (`API_BASE_URL`)

---

## API Design Rules

### 1. REST Conventions

**RULE 4.1: Resource-Based URLs**
```
✅ CORRECT:
POST   /api/databases
GET    /api/databases/{id}
GET    /api/databases/{id}/schemas
POST   /api/databases/{id}/sync
GET    /api/tables/{id}/lineage

❌ INCORRECT:
POST   /api/create-database
GET    /api/get-database?id=123
POST   /api/sync-database-schema
```

**RULE 4.2: HTTP Status Codes**
- `200 OK` - Successful GET, PUT, PATCH
- `201 Created` - Successful POST with new resource
- `202 Accepted` - Async task started (return task_id)
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Missing/invalid authentication
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource doesn't exist
- `422 Unprocessable Entity` - Semantic validation error
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - Database/external service down

**RULE 4.3: Request/Response Format**
```json
// ✅ CORRECT - Request
POST /api/databases
{
  "name": "production_db",
  "type": "postgresql",
  "connection_config": {
    "host": "db.example.com",
    "port": 5432,
    "database": "sales",
    "username": "readonly_user"
  }
}

// ✅ CORRECT - Success Response (201)
{
  "id": 42,
  "name": "production_db",
  "type": "postgresql",
  "status": "connected",
  "created_at": "2026-02-20T10:30:00Z",
  "last_sync_at": null
}

// ✅ CORRECT - Error Response (400)
{
  "error": "ValidationError",
  "message": "Invalid connection configuration",
  "details": [
    {
      "field": "connection_config.host",
      "error": "Required field missing"
    }
  ],
  "request_id": "req_abc123"
}
```

**RULE 4.4: Pagination**
```
GET /api/tables?page=2&page_size=50&sort=-created_at

Response:
{
  "data": [...],
  "pagination": {
    "page": 2,
    "page_size": 50,
    "total_count": 1247,
    "total_pages": 25,
    "has_next": true,
    "has_previous": true
  }
}
```

**RULE 4.5: Filtering and Search**
```
GET /api/tables?schema_id=5&search=customer&has_quality_issues=true

// Multiple filters combined with AND logic
// Search is case-insensitive, matches table name or description
```

**RULE 4.6: Async Task Response**
```json
// ✅ CORRECT - Return task ID immediately (202)
POST /api/databases/42/sync
{
  "task_id": "task_abc123xyz",
  "status": "pending",
  "status_url": "/api/tasks/task_abc123xyz"
}

// Poll status endpoint
GET /api/tasks/task_abc123xyz
{
  "task_id": "task_abc123xyz",
  "status": "running",
  "progress": 45,
  "progress_message": "Extracted 23 of 51 tables",
  "started_at": "2026-02-20T10:35:00Z",
  "result": null
}
```

**RULE 4.7: API Versioning**
- Version in URL: `/api/v1/databases`
- Current version: v1
- Deprecation policy: 6 months notice before removing old version

### 2. FastAPI Implementation

**RULE 4.8: Route Organization**
```python
# src/api/routes/tables.py
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.dependencies import get_current_user, get_table_service
from src.models.schemas import TableResponse, TableCreate

router = APIRouter(prefix="/tables", tags=["tables"])

@router.get("/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: int,
    service: TableService = Depends(get_table_service),
    current_user: User = Depends(get_current_user)
) -> TableResponse:
    """
    Get table details including columns and relationships.
    
    Requires authentication. Returns 404 if table not found.
    """
    table = await service.get_table(table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table {table_id} not found"
        )
    return table
```

**RULE 4.9: Dependency Injection**
```python
# src/api/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.database import get_db
from src.services.table_service import TableService

async def get_table_service(
    db: AsyncSession = Depends(get_db)
) -> TableService:
    return TableService(db)

async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    # Validate token, return user
    pass
```

**RULE 4.10: Request Validation**
```python
from pydantic import BaseModel, Field, validator

class DatabaseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: DatabaseType  # Enum
    connection_config: dict
    
    @validator('name')
    def validate_name(cls, v):
        if not v.replace('_', '').isalnum():
            raise ValueError('Name must be alphanumeric with underscores')
        return v
```

---

## Database Standards

### 1. Schema Design

**RULE 5.1: Primary Keys**
- Use integer `id` as primary key (auto-increment)
- UUID alternative for distributed systems or external APIs
```sql
CREATE TABLE tables (
    id SERIAL PRIMARY KEY,
    -- OR for UUID
    id UUID PRIMARY KEY DEFAULT gen_random_uuid()
);
```

**RULE 5.2: Timestamp Columns**
- All tables MUST have `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Mutable tables MUST have `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- Use trigger to auto-update `updated_at`

**RULE 5.3: Soft Deletes**
- Use `deleted_at TIMESTAMPTZ NULL` for soft deletes
- Filter `WHERE deleted_at IS NULL` in queries
- Physical deletion for sensitive data (GDPR compliance)

**RULE 5.4: Foreign Keys**
- Always define FK constraints with `ON DELETE` action:
  - `CASCADE` - Delete dependent records (e.g., table → columns)
  - `SET NULL` - Optional relationship
  - `RESTRICT` - Prevent deletion if dependents exist
```sql
CREATE TABLE columns (
    id SERIAL PRIMARY KEY,
    table_id INTEGER NOT NULL REFERENCES tables(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL
);
```

**RULE 5.5: Indexes**
- Index all foreign keys
- Index columns used in WHERE, JOIN, ORDER BY
- Compound indexes for common filter combinations
```sql
CREATE INDEX idx_tables_schema_id ON tables(schema_id);
CREATE INDEX idx_tables_search ON tables USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX idx_quality_metrics_composite ON quality_metrics(table_id, metric_type, measured_at DESC);
```

**RULE 5.6: JSON Columns**
- Use JSONB (not JSON) for better performance
- Index commonly queried JSON paths with GIN indexes
```sql
CREATE TABLE tables (
    id SERIAL PRIMARY KEY,
    metadata JSONB,
    CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX idx_tables_metadata_gin ON tables USING gin(metadata);
```

### 2. SQLAlchemy Models

**RULE 5.7: Model Structure**
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Table(Base):
    __tablename__ = 'tables'
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    schema_id = Column(Integer, ForeignKey('schemas.id', ondelete='CASCADE'), nullable=False)
    
    # Attributes
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    row_count = Column(Integer, nullable=True)
    metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    schema = relationship('Schema', back_populates='tables')
    columns = relationship('Column', back_populates='table', cascade='all, delete-orphan')
    
    # Indexes
    __table_args__ = (
        Index('idx_tables_schema_name', 'schema_id', 'name'),
    )
```

**RULE 5.8: Repository Pattern**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class TableRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, table_id: int) -> Table | None:
        result = await self.db.execute(
            select(Table).where(Table.id == table_id, Table.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()
    
    async def create(self, table: Table) -> Table:
        self.db.add(table)
        await self.db.commit()
        await self.db.refresh(table)
        return table
```

### 3. Alembic Migrations

**RULE 5.9: Migration Files**
- Generate migrations: `alembic revision --autogenerate -m "Add lineage_edges table"`
- Never edit generated migrations after commit
- Test migrations: upgrade → downgrade → upgrade
```python
# migrations/versions/abc123_add_lineage_edges.py
def upgrade():
    op.create_table(
        'lineage_edges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('source_table_id', sa.Integer(), nullable=False),
        sa.Column('target_table_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['source_table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_table_id'], ['tables.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('lineage_edges')
```

---

## AI/LLM Integration Guidelines

### 1. Provider Abstraction

**RULE 6.1: LLM Client Interface**
```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: dict
    ) -> dict:
        pass

class OpenAIClient(LLMClient):
    # Implementation
    pass

class OllamaClient(LLMClient):
    # Implementation
    pass
```

**RULE 6.2: Provider Selection**
- Default: OpenAI (GPT-4 Turbo for complex, GPT-3.5 for simple)
- Fallback: Ollama (Llama 3 8B) if OpenAI unavailable or privacy mode enabled
- Configuration in `settings.ai_provider` (openai|ollama|auto)

### 2. Prompt Engineering

**RULE 6.3: Prompt Templates**
```python
# src/ai/prompts.py
TABLE_DOCUMENTATION_PROMPT = """
You are a data documentation expert. Generate business-friendly documentation for a database table.

**Table Information:**
- Name: {table_name}
- Schema: {schema_name}
- Row Count: {row_count:,}
- Type: {table_type}

**Columns:**
{columns_description}

**Relationships:**
{relationships_description}

**Data Quality:**
- Completeness: {completeness_pct}%
- Freshness: Last updated {freshness_hours} hours ago

**Task:**
Generate:
1. A 2-3 sentence business-friendly description explaining what this table contains and its purpose
2. 3-5 primary use cases (bullet points)
3. Data freshness assessment (Good/Moderate/Stale)
4. Key considerations for users (missing data, update frequency, known issues)

**Format your response as JSON:**
{{
  "description": "...",
  "use_cases": ["...", "..."],
  "freshness_assessment": "Good|Moderate|Stale",
  "considerations": ["...", "..."]
}}
"""
```

**RULE 6.4: Token Management**
- Calculate tokens before sending: `tiktoken.encoding_for_model("gpt-4")`
- Max context: 16k tokens (leave 2k buffer for response)
- Truncate long column lists: "...and 47 more columns"

**RULE 6.5: Retry Logic**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
async def generate_documentation(table_id: int) -> dict:
    # Call LLM with retry on rate limit or transient errors
    pass
```

### 3. RAG Implementation

**RULE 6.6: Embedding Generation**
- Model: OpenAI `text-embedding-3-small` (1536 dimensions, $0.02/1M tokens)
- Embed: table name + description + column names + column descriptions
- Batch embeddings: 100 tables per API call
```python
async def generate_embeddings(tables: list[Table]) -> list[list[float]]:
    texts = [
        f"Table: {t.name}. {t.description or ''}. "
        f"Columns: {', '.join(c.name for c in t.columns)}"
        for t in tables
    ]
    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [e.embedding for e in response.data]
```

**RULE 6.7: Vector Search**
```python
# ChromaDB query
results = collection.query(
    query_embeddings=[question_embedding],
    n_results=5,
    where={"schema_id": schema_id},  # Optional filter
    include=["metadatas", "documents", "distances"]
)
```

**RULE 6.8: Context Assembly**
- Combine exact match (table name search) + semantic match (vector search)
- Rerank by composite score: `0.6 * exact_score + 0.4 * semantic_score`
- Include top 3-5 tables in context
- Add FK relationships between included tables

### 4. Text-to-SQL Safety

**RULE 6.9: Query Validation**
```python
import sqlparse
from sqlglot import parse_one, exp

def validate_sql(sql: str, db_type: str) -> tuple[bool, str]:
    # 1. Parse SQL
    try:
        parsed = sqlparse.parse(sql)[0]
    except Exception as e:
        return False, f"Syntax error: {e}"
    
    # 2. Check statement type
    stmt_type = parsed.get_type()
    if stmt_type not in ('SELECT', 'WITH'):
        return False, f"Only SELECT queries allowed, got {stmt_type}"
    
    # 3. Check for forbidden keywords
    forbidden = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER', 'CREATE']
    sql_upper = sql.upper()
    for keyword in forbidden:
        if keyword in sql_upper:
            return False, f"Forbidden keyword: {keyword}"
    
    # 4. Validate dialect-specific syntax
    try:
        parse_one(sql, dialect=db_type)
    except Exception as e:
        return False, f"Dialect error: {e}"
    
    return True, "Valid"
```

**RULE 6.10: Execution Constraints**
- Read-only connection (PostgreSQL: read_only=true)
- Query timeout: 30 seconds
- Result limit: LIMIT 1000 (inject if missing)
- Cost estimation: Run EXPLAIN before execution, warn if high cost

**RULE 6.11: LLM Query Refinement**
- If query validation fails, send error back to LLM for correction
- Max 3 retry attempts
- Include schema context + error message in refinement prompt

---

## Security Requirements

### 1. Authentication & Authorization

**RULE 7.1: Authentication Method**
- JWT-based authentication (implementation TBD in Phase 2)
- Tokens expire after 24 hours
- Refresh tokens for extended sessions (7 days)
- Store tokens in httpOnly cookies (not localStorage)

**RULE 7.2: Password Requirements (Future)**
- Minimum 12 characters
- Hash with bcrypt (cost factor: 12)
- Enforce password rotation every 90 days

**RULE 7.3: Role-Based Access Control (RBAC)**
```python
class Role(Enum):
    VIEWER = "viewer"       # Read-only access
    ANALYST = "analyst"     # Read + text-to-SQL execution
    ENGINEER = "engineer"   # Read + Write (manage databases, quality rules)
    ADMIN = "admin"         # Full access
```

### 2. Data Security

**RULE 7.4: Credential Encryption**
```python
from cryptography.fernet import Fernet

class CredentialManager:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```
- Encryption key stored in environment variable `ENCRYPTION_KEY`
- Rotate keys every 6 months (migration script to re-encrypt)

**RULE 7.5: Connection String Security**
- Never log connection strings or credentials
- Mask credentials in API responses: `password: "***"`
- Audit log for all credential access

**RULE 7.6: SQL Injection Prevention**
- ALWAYS use parameterized queries
```python
# ✅ CORRECT
query = "SELECT * FROM tables WHERE id = :table_id"
result = await db.execute(query, {"table_id": table_id})

# ❌ INCORRECT - SQL injection risk
query = f"SELECT * FROM tables WHERE id = {table_id}"
```

### 3. API Security

**RULE 7.7: Rate Limiting**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/chat/message")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def send_message(request: Request):
    pass
```

**RULE 7.8: CORS Configuration**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**RULE 7.9: Input Sanitization**
- Validate all user inputs with Pydantic
- Escape HTML in user-generated content (table descriptions, comments)
- Maximum request body size: 10 MB

---

## Testing Standards

### 1. Test Coverage

**RULE 8.1: Minimum Coverage**
- Overall: 80% code coverage
- Critical paths: 100% (authentication, SQL validation, credential encryption)
- Test command: `pytest --cov=src --cov-report=html --cov-report=term`

**RULE 8.2: Test Organization**
```
tests/
  unit/
    test_connectors.py
    test_extractors.py
    test_quality_analyzer.py
    test_ai_service.py
  integration/
    test_api_databases.py
    test_api_tables.py
    test_celery_tasks.py
  e2e/
    test_user_flows.py
```

### 2. Unit Tests

**RULE 8.3: Test Structure (Arrange-Act-Assert)**
```python
import pytest
from unittest.mock import Mock, patch

def test_extract_schema_success():
    # Arrange
    mock_connection = Mock()
    mock_connection.execute.return_value = [
        {'table_name': 'users', 'row_count': 1000}
    ]
    extractor = SchemaExtractor(mock_connection)
    
    # Act
    result = extractor.extract_schema('public')
    
    # Assert
    assert len(result.tables) == 1
    assert result.tables[0].name == 'users'
    assert result.tables[0].row_count == 1000
```

**RULE 8.4: Fixtures**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from src.config.database import Base

@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()

@pytest.fixture
def test_db_session(test_db_engine):
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
```

**RULE 8.5: Mocking External Services**
```python
@pytest.fixture
def mock_openai_client(mocker):
    mock = mocker.patch('openai.OpenAI')
    mock.return_value.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content='{"description": "Test table"}'))]
    )
    return mock

def test_generate_documentation(mock_openai_client):
    service = AIService()
    result = service.generate_documentation(table_id=1)
    assert result['description'] == 'Test table'
    mock_openai_client.return_value.chat.completions.create.assert_called_once()
```

### 3. Integration Tests

**RULE 8.6: API Testing**
```python
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_create_database():
    response = client.post(
        "/api/databases",
        json={
            "name": "test_db",
            "type": "postgresql",
            "connection_config": {"host": "localhost"}
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == 'test_db'
    assert 'id' in data
```

**RULE 8.7: Task Testing (Celery Eager Mode)**
```python
# tests/conftest.py
@pytest.fixture(scope="session")
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
        'task_always_eager': True,  # Execute tasks synchronously
        'task_eager_propagates': True
    }

def test_extract_schema_task(celery_app, test_db):
    result = extract_schema_task.apply(args=[1])
    assert result.successful()
    assert result.result['tables_extracted'] > 0
```

### 4. E2E Tests

**RULE 8.8: Playwright Tests**
```python
# tests/e2e/test_user_flows.py
from playwright.sync_api import Page, expect

def test_add_database_and_sync(page: Page):
    # Navigate to app
    page.goto("http://localhost:3000")
    
    # Click "Add Database" button
    page.click("text=Add Database")
    
    # Fill form
    page.fill("input[name='name']", "My Database")
    page.select_option("select[name='type']", "postgresql")
    page.fill("input[name='host']", "localhost")
    
    # Submit
    page.click("button:has-text('Connect')")
    
    # Wait for success message
    expect(page.locator("text=Database connected successfully")).to_be_visible()
    
    # Trigger sync
    page.click("button:has-text('Sync Schema')")
    expect(page.locator("text=Sync in progress")).to_be_visible()
```

---

## Documentation Requirements

### 1. Code Documentation

**RULE 9.1: Module Docstrings**
```python
"""
Schema extraction module.

This module provides connectors and extractors for retrieving schema metadata
from various database types (PostgreSQL, Snowflake, SQL Server).

Classes:
    SchemaExtractor: Main extractor class
    DatabaseConnector: Abstract connector interface
    
Functions:
    extract_schema: Extract full schema metadata
    
Example:
    >>> connector = PostgreSQLConnector(connection_string)
    >>> extractor = SchemaExtractor(connector)
    >>> schema = extractor.extract_schema('public')
"""
```

**RULE 9.2: Function/Method Docstrings**
- Required for all public functions
- Include: description, args, returns, raises, example
- See RULE 3.5 for format

**RULE 9.3: Inline Comments**
- Explain WHY, not WHAT (code should be self-explanatory)
- Use for complex algorithms, non-obvious workarounds
```python
# ✅ CORRECT
# ChromaDB doesn't support empty embeddings, so we use a zero vector
# as a placeholder for tables without descriptions
embedding = embeddings[0] if embeddings else [0.0] * 1536

# ❌ INCORRECT - Comment explains what code obviously does
# Set the name variable to the table name
name = table.name
```

### 2. API Documentation

**RULE 9.4: OpenAPI/Swagger**
- FastAPI auto-generates docs at `/docs` and `/redoc`
- Enrich with descriptions, examples, response schemas
```python
@router.post(
    "/databases",
    response_model=DatabaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new database connection",
    description="""
    Create a new database connection for schema extraction.
    
    Supports PostgreSQL, Snowflake, SQL Server, and MySQL.
    Credentials are encrypted before storage.
    
    Returns connection details with generated ID.
    """,
    responses={
        201: {"description": "Database created successfully"},
        400: {"description": "Invalid connection configuration"},
        401: {"description": "Authentication required"}
    }
)
async def create_database(database: DatabaseCreate):
    pass
```

### 3. User Documentation

**RULE 9.5: README.md Structure**
```markdown
# AI Data Dictionary Platform

## Quick Start
- Prerequisites
- Installation (Docker Compose)
- Configuration (.env setup)
- Running the app

## Features
- Schema extraction
- AI documentation
- Chat interface
- Lineage visualization

## API Reference
- Link to /docs

## Architecture
- High-level diagram
- Component overview

## Contributing
- Development setup
- Testing
- Pull request process

## License
```

**RULE 9.6: Changelog (CHANGELOG.md)**
- Format: Keep a Changelog (https://keepachangelog.com/)
- Sections: Added, Changed, Deprecated, Removed, Fixed, Security
```markdown
# Changelog

## [Unreleased]

## [1.0.0] - 2026-02-20
### Added
- Schema extraction for PostgreSQL, Snowflake, SQL Server
- AI-powered documentation generation
- Chat interface with text-to-SQL
- Data lineage visualization
```

---

## Performance Benchmarks

### 1. Target Metrics

**RULE 10.1: API Response Times**
- Simple GET (single resource): <100ms (p95)
- Complex GET (with joins): <300ms (p95)
- POST/PUT/DELETE: <200ms (p95)
- Search/Filter: <500ms (p95)

**RULE 10.2: Task Execution Times**
- Schema extraction (100 tables): <30 seconds
- AI documentation generation (single table): <5 seconds (OpenAI), <10 seconds (Ollama)
- Quality analysis (1M rows, sampled): <60 seconds
- Lineage extraction (100 tables): <15 seconds
- Incremental sync (10 changed tables): <5 seconds

**RULE 10.3: Chat Performance**
- Simple Q&A response: <3 seconds
- Text-to-SQL generation: <8 seconds
- Intent classification: <500ms
- Vector search (5 results): <200ms

**RULE 10.4: UI Performance**
- First Contentful Paint (FCP): <1.5 seconds
- Time to Interactive (TTI): <3 seconds
- Lineage graph render (100 nodes): <2 seconds
- Table list load (1000 items, paginated): <1 second

### 2. Load Testing

**RULE 10.5: Load Test Scenarios**
```python
# Locust load test
from locust import HttpUser, task, between

class DataDictUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_tables(self):
        self.client.get("/api/tables?page=1&page_size=50")
    
    @task(2)
    def view_table_detail(self):
        self.client.get(f"/api/tables/{random.randint(1, 100)}")
    
    @task(1)
    def chat_message(self):
        self.client.post("/api/chat/message", json={
            "message": "What tables contain customer data?"
        })
```

**Target Load:**
- Concurrent users: 50
- Requests per second: 200
- Error rate: <1%
- Response time p95: <500ms

### 3. Database Performance

**RULE 10.6: Query Optimization**
- All queries analyzed with EXPLAIN ANALYZE
- N+1 queries prohibited (use eager loading or batch queries)
```python
# ✅ CORRECT - Eager load relationships
tables = await db.execute(
    select(Table)
    .options(joinedload(Table.columns))
    .where(Table.schema_id == schema_id)
)

# ❌ INCORRECT - N+1 query (fetches columns for each table separately)
tables = await db.execute(select(Table).where(Table.schema_id == schema_id))
for table in tables:
    columns = table.columns  # Triggers separate query
```

**RULE 10.7: Connection Pooling**
```python
# SQLAlchemy engine configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Base pool size
    max_overflow=10,        # Additional connections under load
    pool_timeout=30,        # Wait max 30s for available connection
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Check connection health before use
)
```

---

## Git Workflow

### 1. Branch Strategy

**RULE 11.1: Branch Naming**
```
main           - Production-ready code
develop        - Integration branch for features
feature/*      - New features (feature/add-lineage-viz)
bugfix/*       - Bug fixes (bugfix/fix-null-handling)
hotfix/*       - Critical production fixes (hotfix/sql-injection)
release/*      - Release preparation (release/v1.0.0)
```

**RULE 11.2: Branch Lifecycle**
1. Create feature branch from `develop`: `git checkout -b feature/add-lineage-viz develop`
2. Develop with frequent commits
3. Push and create Pull Request to `develop`
4. Code review + CI passes
5. Merge to `develop` (squash merge)
6. Delete feature branch

### 2. Commit Messages

**RULE 11.3: Commit Format (Conventional Commits)**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Code style (formatting, no logic change)
- `refactor` - Code restructuring (no functional change)
- `perf` - Performance improvement
- `test` - Adding/updating tests
- `chore` - Build process, dependencies, tooling

**Examples:**
```
feat(chat): add text-to-SQL query generation

Implement RAG-based context retrieval and LLM-powered SQL generation
with validation and safety checks.

Closes #42

---

fix(api): handle null values in quality metrics endpoint

Previously returned 500 error when quality_metrics table had null
values. Now returns default values and logs warning.

Fixes #58
```

**RULE 11.4: Commit Frequency**
- Commit often with logical groupings
- Each commit should pass tests (atomic commits)
- Use `git commit --amend` to fix last commit before push

### 3. Pull Requests

**RULE 11.5: PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass locally

## Screenshots (if UI changes)

## Related Issues
Closes #XX
```

**RULE 11.6: Code Review Requirements**
- Minimum 1 approval required
- All CI checks must pass
- No unresolved conversations
- Reviewer checklist:
  - Code quality and style
  - Test coverage
  - Security considerations
  - Documentation completeness

---

## Deployment Rules

### 1. Docker Configuration

**RULE 12.1: Dockerfile Best Practices**
```dockerfile
# Multi-stage build for smaller image size
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/

# Set environment
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**RULE 12.2: Docker Compose Structure**
```yaml
version: '3.9'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/datadict
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend/src:/app/src  # Hot reload in dev
    networks:
      - datadict-network
  
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=datadict
      - POSTGRES_USER=datadict_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - datadict-network
  
  # ... other services

networks:
  datadict-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  chromadb_data:
```

### 2. Environment Configuration

**RULE 12.3: Environment Variables**
```bash
# .env.example (committed to repo)
# Copy to .env and fill in values

# Application
APP_NAME=AI Data Dictionary
DEBUG=false
LOG_LEVEL=INFO

# Database (Metadata Storage)
DATABASE_URL=postgresql://user:password@localhost:5432/datadict

# Redis (Task Queue)
REDIS_URL=redis://localhost:6379/0

# AI/LLM
OPENAI_API_KEY=sk-...
AI_PROVIDER=openai  # openai|ollama|auto
OLLAMA_BASE_URL=http://localhost:11434

# Security
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Features
ENABLE_AI_DOCS=true
ENABLE_LINEAGE=true
ENABLE_TEXT_TO_SQL=true

# Performance
CELERY_WORKER_CONCURRENCY=4
MAX_CONNECTIONS_POOL=20
```

**RULE 12.4: Secrets Management**
- Development: .env files (not committed)
- Production: Environment variables or secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Never commit secrets to Git
- Use `.env.example` as template

### 3. Health Checks

**RULE 12.5: Health Check Endpoints**
```python
@router.get("/health", tags=["system"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for load balancer/orchestrator.
    
    Checks:
    - API server is running
    - Database connection is alive
    - Redis connection is alive
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        await db.execute(text("SELECT 1"))
        health["checks"]["database"] = "healthy"
    except Exception as e:
        health["checks"]["database"] = f"unhealthy: {e}"
        health["status"] = "unhealthy"
    
    # Redis check
    try:
        await redis_client.ping()
        health["checks"]["redis"] = "healthy"
    except Exception as e:
        health["checks"]["redis"] = f"unhealthy: {e}"
        health["status"] = "unhealthy"
    
    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)
```

---

## Error Handling

### 1. Exception Hierarchy

**RULE 13.1: Custom Exceptions**
```python
# src/exceptions.py

class DataDictException(Exception):
    """Base exception for all application errors"""
    pass

class DatabaseConnectionError(DataDictException):
    """Failed to connect to database"""
    pass

class TableNotFoundError(DataDictException):
    """Requested table does not exist"""
    pass

class SchemaExtractionError(DataDictException):
    """Failed to extract schema metadata"""
    pass

class AIServiceError(DataDictException):
    """LLM API error or generation failure"""
    pass

class ValidationError(DataDictException):
    """Input validation failed"""
    pass

class AuthenticationError(DataDictException):
    """Authentication failed"""
    pass

class AuthorizationError(DataDictException):
    """User not authorized for this operation"""
    pass
```

**RULE 13.2: Exception Handling Pattern**
```python
from src.exceptions import TableNotFoundError, DatabaseConnectionError
from fastapi import HTTPException, status

async def get_table(table_id: int) -> Table:
    try:
        table = await table_repository.get_by_id(table_id)
        if not table:
            raise TableNotFoundError(f"Table {table_id} not found")
        return table
    except TableNotFoundError as e:
        logger.warning("table_not_found", table_id=table_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseConnectionError as e:
        logger.error("database_connection_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable"
        )
    except Exception as e:
        logger.exception("unexpected_error", table_id=table_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
```

### 2. Error Responses

**RULE 13.3: Consistent Error Format**
```json
{
  "error": "TableNotFoundError",
  "message": "Table 42 not found",
  "details": null,
  "request_id": "req_abc123",
  "timestamp": "2026-02-20T10:30:00Z"
}

// Validation error with field details
{
  "error": "ValidationError",
  "message": "Invalid request data",
  "details": [
    {
      "field": "connection_config.port",
      "error": "Value must be between 1 and 65535",
      "provided_value": 99999
    }
  ],
  "request_id": "req_def456",
  "timestamp": "2026-02-20T10:31:00Z"
}
```

---

## Logging & Monitoring

### 1. Logging Standards

**RULE 14.1: Structured Logging with Structlog**
```python
import structlog

logger = structlog.get_logger()

# ✅ CORRECT - Structured with context
logger.info(
    "schema_extraction_completed",
    database_id=42,
    schema_name="public",
    tables_extracted=23,
    duration_seconds=12.5,
    user_id=user.id
)

# ❌ INCORRECT - Unstructured string
logger.info(f"Extracted 23 tables from database 42 in 12.5 seconds")
```

**RULE 14.2: Log Levels**
- `DEBUG` - Detailed information for diagnosing problems (not in production)
- `INFO` - General informational messages (task started/completed, user actions)
- `WARNING` - Warning messages (deprecated features, recoverable errors)
- `ERROR` - Error messages (handled exceptions, failed operations)
- `CRITICAL` - Critical errors (application crash, data corruption)

**RULE 14.3: Sensitive Data**
- NEVER log passwords, API keys, tokens, credit cards
- Mask connection strings: `postgresql://user:***@host:5432/db`
- Truncate long data: `description: "Long text..."[:100]`

**RULE 14.4: Log Configuration**
```python
# src/config/logging.py
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()  # JSON for production
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
```

### 2. Monitoring

**RULE 14.5: Metrics to Track**
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
schema_extractions = Counter(
    'schema_extractions_total',
    'Total schema extractions',
    ['database_type', 'status']
)

ai_doc_generations = Counter(
    'ai_documentation_generations_total',
    'AI documentation generations',
    ['provider', 'status']
)

active_databases = Gauge(
    'active_databases',
    'Number of registered databases'
)

# Task queue metrics
celery_task_duration = Histogram(
    'celery_task_duration_seconds',
    'Task execution duration',
    ['task_name']
)
```

**RULE 14.6: Prometheus Endpoint**
```python
from prometheus_client import make_asgi_app

# Mount Prometheus metrics at /metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

---

## UI/UX Guidelines

### 1. Design System

**RULE 15.1: Color Palette**
```css
/* Primary colors */
--color-primary: #3b82f6;        /* Blue - primary actions */
--color-primary-hover: #2563eb;
--color-secondary: #8b5cf6;      /* Purple - AI features */

/* Semantic colors */
--color-success: #10b981;        /* Green - success states */
--color-warning: #f59e0b;        /* Orange - warnings */
--color-error: #ef4444;          /* Red - errors */
--color-info: #06b6d4;           /* Cyan - information */

/* Neutral colors (light mode) */
--color-bg: #ffffff;
--color-bg-secondary: #f9fafb;
--color-text: #111827;
--color-text-secondary: #6b7280;
--color-border: #e5e7eb;
```

**RULE 15.2: Typography**
```css
/* Font families */
--font-sans: 'Inter', system-ui, sans-serif;
--font-mono: 'Fira Code', 'Monaco', monospace;

/* Font sizes */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
```

**RULE 15.3: Spacing (8px grid)**
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
```

### 2. Component Guidelines

**RULE 15.4: Button Variants**
```tsx
// Primary - Main actions (Connect, Sync, Generate)
<Button variant="primary" onClick={handleSync}>
  Sync Schema
</Button>

// Secondary - Less prominent actions
<Button variant="secondary" onClick={handleCancel}>
  Cancel
</Button>

// Ghost - Tertiary actions, icon buttons
<Button variant="ghost" size="icon">
  <IconSettings />
</Button>

// Destructive - Dangerous actions (Delete, Drop)
<Button variant="destructive" onClick={handleDelete}>
  Delete Database
</Button>
```

**RULE 15.5: Loading States**
- Show skeleton loaders for initial page load
- Show spinners for button actions (disable button during loading)
- Show progress bars for long-running tasks with percentage
- Optimistic updates where possible (update UI, rollback on error)

**RULE 15.6: Empty States**
```tsx
// Informative empty states with action
<EmptyState
  icon={<IconDatabase />}
  title="No databases connected"
  description="Connect your first database to start generating documentation"
  action={
    <Button onClick={openAddDatabaseModal}>
      Add Database
    </Button>
  }
/>
```

**RULE 15.7: Error States**
```tsx
// Inline error messages
<Alert variant="error">
  <AlertTitle>Connection failed</AlertTitle>
  <AlertDescription>
    Unable to connect to database. Check credentials and try again.
  </AlertDescription>
  <Button variant="ghost" onClick={retry}>Retry</Button>
</Alert>
```

### 3. Accessibility (WCAG 2.1 AA)

**RULE 15.8: Keyboard Navigation**
- All interactive elements accessible via Tab
- Visible focus indicators (outline)
- Escape key closes modals/dropdowns
- Enter/Space activates buttons

**RULE 15.9: ARIA Labels**
```tsx
<button aria-label="Delete table" onClick={handleDelete}>
  <IconTrash />
</button>

<input
  type="search"
  aria-label="Search tables"
  placeholder="Search..."
/>
```

**RULE 15.10: Color Contrast**
- Text on background: Minimum 4.5:1 ratio
- Large text (18pt+): Minimum 3:1 ratio
- Interactive elements: Include non-color indicators (icons, underlines)

### 4. Responsive Design

**RULE 15.11: Breakpoints**
```css
/* Mobile-first approach */
@media (min-width: 640px)  { /* sm */ }
@media (min-width: 768px)  { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

**RULE 15.12: Mobile Considerations**
- Stack layouts vertically on mobile
- Increase touch target size: Minimum 44x44px
- Hide secondary information, show on expand
- Bottom sheet for modals on mobile

---

## Project Phases & Scope

### Phase 1: MVP (Weeks 1-4)
**Included:**
- PostgreSQL connector only
- Basic schema extraction (tables, columns, relationships)
- Manual documentation editing
- Simple table browsing UI
- Docker Compose setup

**Excluded:**
- AI documentation (manual only)
- Multiple database types
- Chat interface
- Lineage visualization
- Data quality analysis

### Phase 2: AI & Multi-Database (Weeks 5-7)
**Included:**
- OpenAI integration for documentation
- Snowflake, SQL Server connectors
- Basic chat Q&A (no text-to-SQL)
- Incremental schema updates
- Quality analysis (basic metrics)

### Phase 3: Advanced Features (Weeks 8-10)
**Included:**
- Text-to-SQL generation
- Data lineage visualization
- Quality trend monitoring
- Markdown/JSON exports
- Ollama local LLM support

### Phase 4: Production Hardening (Weeks 11-12)
**Included:**
- Authentication & authorization
- Comprehensive testing (80% coverage)
- Performance optimization
- Security audit
- Production deployment guide

---

## Acceptance Criteria

### Success Criteria (End of Phase 3)
1. **Functionality:**
   - ✅ Connect to PostgreSQL, Snowflake, SQL Server
   - ✅ Extract schema metadata (100+ tables in <30s)
   - ✅ Generate AI documentation for all tables
   - ✅ Chat interface answers 90% of test questions correctly
   - ✅ Text-to-SQL generates valid queries for 80% of test cases
   - ✅ Lineage visualization for FK relationships
   - ✅ Quality metrics for key columns
   - ✅ Incremental updates detect schema changes within 30 minutes

2. **Performance:**
   - ✅ API response time p95 <500ms
   - ✅ Chat response time <8 seconds
   - ✅ UI loads in <3 seconds (TTI)

3. **Quality:**
   - ✅ Test coverage >80%
   - ✅ Zero critical security vulnerabilities
   - ✅ All documentation complete

4. **Usability:**
   - ✅ Analyst can onboard and answer first question in <15 minutes
   - ✅ Engineer can add database and trigger sync in <5 minutes
   - ✅ No prior data catalog tool knowledge required

---

## Constraints & Assumptions

### Constraints
1. **Technology:** Python 3.11+, React/Next.js 14, PostgreSQL 15+
2. **Deployment:** Docker Compose (cloud deployment out of scope for MVP)
3. **AI Provider:** OpenAI API key required (cost: ~$50/month for demo)
4. **Database Access:** Read-only access sufficient; no write operations to source databases
5. **Timeline:** 12 weeks to production-ready Phase 4

### Assumptions
1. **Data Volume:** <10,000 tables per database (scalability testing deferred)
2. **Concurrency:** <50 concurrent users (load testing in Phase 4)
3. **Network:** Source databases accessible via network from app server
4. **Credentials:** Manual credential entry (SSO integration out of scope)
5. **Languages:** English only for AI-generated content

---

## Definition of Done

A feature is "done" when:
1. ✅ Code implemented and peer-reviewed
2. ✅ Unit tests written with >80% coverage
3. ✅ Integration tests pass
4. ✅ API documentation updated (/docs)
5. ✅ User documentation updated (README, guides)
6. ✅ Code formatted and linted (ruff)
7. ✅ Type checking passes (mypy for Python, tsc for TypeScript)
8. ✅ Manual testing completed by developer
9. ✅ No new high/critical security vulnerabilities
10. ✅ Deployed to staging environment
11. ✅ Product owner approval

---

## Glossary

- **Schema Metadata:** Information about database structure (tables, columns, types, constraints)
- **Data Dictionary:** Comprehensive documentation of database entities with business context
- **RAG (Retrieval Augmented Generation):** AI technique combining database search with LLM generation
- **Text-to-SQL:** Converting natural language questions into SQL queries
- **Data Lineage:** Tracking data flow and dependencies between tables
- **Quality Metrics:** Measurements of data completeness, accuracy, freshness, consistency
- **Incremental Sync:** Detecting and processing only changed schema elements
- **Modular Monolith:** Single deployable application with well-defined internal module boundaries
- **Event-Driven Tasks:** Asynchronous background jobs triggered by events

---

## Change Log

| Date       | Version | Changes                                      | Author |
|------------|---------|----------------------------------------------|--------|
| 2026-02-20 | 1.0     | Initial rules document                       | Team   |

---

**Document Status:** Active  
**Next Review Date:** 2026-03-20  
**Maintainer:** Engineering Team

---

*This document serves as the single source of truth for development standards, architecture decisions, and project guidelines. All team members must read and follow these rules. Updates require team consensus and version increment.*
