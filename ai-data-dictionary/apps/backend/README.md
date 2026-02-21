# AI Data Dictionary - Backend

Backend service for the AI Data Dictionary platform, built with FastAPI, PostgreSQL, and LangChain.

## Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration scripts
│   │   └── 001_initial_schema.py
│   └── env.py                  # Alembic environment
├── src/
│   ├── api/                    # FastAPI routes (to be implemented)
│   ├── config/                 # Configuration and settings
│   │   ├── database.py         # Database connection
│   │   └── settings.py         # Application settings
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── database.py         # Database connection metadata
│   │   ├── schema.py           # Database schema metadata
│   │   ├── table.py            # Table metadata
│   │   ├── column.py           # Column metadata
│   │   ├── lineage_edge.py     # Table lineage relationships
│   │   ├── quality_metric.py   # Data quality metrics
│   │   ├── task_result.py      # Async task results
│   │   └── user.py             # User accounts (Phase 2)
│   ├── schemas/                # Pydantic schemas for API
│   │   ├── database.py         # Database API schemas
│   │   ├── schema.py           # Schema API schemas
│   │   ├── table.py            # Table API schemas
│   │   ├── column.py           # Column API schemas
│   │   ├── lineage.py          # Lineage API schemas
│   │   ├── quality.py          # Quality metrics API schemas
│   │   ├── task.py             # Task status API schemas
│   │   └── chat.py             # Chat API schemas
│   ├── services/               # Business logic (to be implemented)
│   ├── repositories/           # Data access layer (to be implemented)
│   ├── workers/                # Celery tasks (to be implemented)
│   ├── utils/                  # Utilities
│   │   ├── crypto.py           # Credential encryption
│   │   ├── logger.py           # Structured logging
│   │   └── validators.py       # Validation utilities
│   └── exceptions.py           # Custom exceptions
├── tests/                      # Test suite (to be implemented)
├── alembic.ini                 # Alembic configuration
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variables template
```

## Database Schema

### Core Tables

1. **databases** - Database connection metadata
   - Stores connection details, sync status, and credentials (encrypted)

2. **schemas** - Database schemas/namespaces
   - Organizes tables within databases

3. **tables** - Table metadata
   - Includes AI-generated descriptions, quality metrics, row counts

4. **columns** - Column metadata
   - Data types, constraints, sample values, quality stats

5. **lineage_edges** - Table dependencies
   - Foreign keys, view dependencies, ETL transformations

6. **quality_metrics** - Data quality measurements
   - Time-series metrics: completeness, freshness, statistical analysis

7. **task_results** - Async task tracking
   - Status and results of Celery background tasks

8. **users** - User accounts (Phase 2)
   - Authentication and RBAC

## Setup Instructions

### 1. Install Dependencies

```bash
cd ai-data-dictionary/apps/backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Update the following critical values:
- `DATABASE_URL` - PostgreSQL connection string
- `OPENAI_API_KEY` - Your OpenAI API key
- `ENCRYPTION_KEY` - Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `JWT_SECRET_KEY` - Generate random secret key

### 3. Setup Database

Create PostgreSQL database:

```bash
createdb data_dictionary
```

Run migrations:

```bash
alembic upgrade head
```

### 4. Run Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Database Migrations

### Create New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

## Testing

Run tests with coverage:

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

## Code Quality

Format code with Ruff:

```bash
ruff format .
```

Lint code:

```bash
ruff check .
```

## Architecture Principles

### Modular Monolith
- Clear module boundaries with defined interfaces
- Modules: auth, catalog, quality, lineage, chat, export, ingestion, audit

### Event-Driven Tasks
- Long-running operations as Celery tasks
- HTTP endpoints return task IDs for polling

### Hybrid RAG
- Structured retrieval from PostgreSQL
- Vector search with ChromaDB
- Combined scoring for optimal results

## Technology Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 15+ with TimescaleDB
- **ORM**: SQLAlchemy 2.0+
- **Task Queue**: Celery 5.3+ with Redis
- **AI**: OpenAI 1.12+, LangChain 0.1+, ChromaDB 0.4+
- **Data Quality**: ydata-profiling, pandera
- **Validation**: Pydantic 2.0+

## Next Steps

1. Implement API routes in `src/api/`
2. Implement services in `src/services/`
3. Implement Celery tasks in `src/workers/`
4. Add comprehensive tests in `tests/`
5. Setup Docker Compose for local development

## License

See main project README for license information.
