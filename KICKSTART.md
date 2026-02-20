# AI Data Dictionary Platform - Kickstart Guide

**Version:** 1.0  
**Last Updated:** February 20, 2026  
**Purpose:** Complete step-by-step guide to initialize and build the project from scratch

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Initial Setup](#initial-setup)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Database Schema](#database-schema)
7. [Configuration Files](#configuration-files)
8. [Development Workflow](#development-workflow)
9. [Testing Setup](#testing-setup)
10. [Deployment Setup](#deployment-setup)

---

## Prerequisites

### Required Software
- **Node.js:** 20.x LTS or higher
- **Python:** 3.11 or higher
- **Docker:** 24.0+ and Docker Compose v2.0+
- **Git:** Latest version
- **PostgreSQL Client:** For local database management
- **VS Code:** Recommended IDE with extensions:
  - Python
  - Pylance
  - ESLint
  - Prettier
  - Docker
  - GitLens

### Required Accounts
- **OpenAI API Key:** For AI documentation generation (https://platform.openai.com/)
- **GitHub Account:** For version control and CI/CD

### System Requirements
- **OS:** Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+)
- **RAM:** Minimum 8GB (16GB recommended)
- **Disk Space:** 10GB free space
- **CPU:** 4 cores recommended for Docker

---

## Project Structure

### Complete Folder Structure (Turborepo Monorepo)

```
ai-data-dictionary/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── backend-tests.yml
│       └── frontend-tests.yml
├── apps/
│   ├── backend/
│   │   ├── alembic/
│   │   │   ├── versions/
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── README
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── dependencies.py
│   │   │   │   ├── main.py
│   │   │   │   ├── middleware/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── cors.py
│   │   │   │   │   ├── error_handler.py
│   │   │   │   │   └── logging.py
│   │   │   │   └── routes/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── databases.py
│   │   │   │       ├── schemas.py
│   │   │   │       ├── tables.py
│   │   │   │       ├── columns.py
│   │   │   │       ├── chat.py
│   │   │   │       ├── lineage.py
│   │   │   │       ├── quality.py
│   │   │   │       ├── export.py
│   │   │   │       ├── tasks.py
│   │   │   │       └── health.py
│   │   │   ├── config/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── settings.py
│   │   │   │   ├── database.py
│   │   │   │   └── logging.py
│   │   │   ├── connectors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── factory.py
│   │   │   │   ├── postgresql.py
│   │   │   │   ├── snowflake.py
│   │   │   │   └── sqlserver.py
│   │   │   ├── extractors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schema_extractor.py
│   │   │   │   ├── lineage_extractor.py
│   │   │   │   └── quality_analyzer.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py
│   │   │   │   ├── schema.py
│   │   │   │   ├── table.py
│   │   │   │   ├── column.py
│   │   │   │   ├── relationship.py
│   │   │   │   ├── quality_metric.py
│   │   │   │   ├── lineage_edge.py
│   │   │   │   ├── documentation.py
│   │   │   │   ├── task_result.py
│   │   │   │   ├── schema_version.py
│   │   │   │   └── enums.py
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py
│   │   │   │   ├── table.py
│   │   │   │   ├── column.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── quality.py
│   │   │   │   ├── lineage.py
│   │   │   │   ├── export.py
│   │   │   │   └── common.py
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── database_repository.py
│   │   │   │   ├── table_repository.py
│   │   │   │   ├── column_repository.py
│   │   │   │   ├── documentation_repository.py
│   │   │   │   ├── quality_repository.py
│   │   │   │   └── lineage_repository.py
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database_service.py
│   │   │   │   ├── metadata_service.py
│   │   │   │   ├── ai_service.py
│   │   │   │   ├── quality_service.py
│   │   │   │   ├── lineage_service.py
│   │   │   │   ├── export_service.py
│   │   │   │   ├── versioning_service.py
│   │   │   │   └── chat_service.py
│   │   │   ├── ai/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── llm_client.py
│   │   │   │   ├── openai_client.py
│   │   │   │   ├── ollama_client.py
│   │   │   │   ├── prompts.py
│   │   │   │   ├── embeddings.py
│   │   │   │   ├── rag.py
│   │   │   │   └── text_to_sql.py
│   │   │   ├── workers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── celery_app.py
│   │   │   │   ├── tasks.py
│   │   │   │   └── schedules.py
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── crypto.py
│   │   │   │   ├── retry.py
│   │   │   │   ├── validators.py
│   │   │   │   ├── parsers.py
│   │   │   │   └── hash.py
│   │   │   └── exceptions.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── unit/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_connectors.py
│   │   │   │   ├── test_extractors.py
│   │   │   │   ├── test_quality_analyzer.py
│   │   │   │   ├── test_ai_service.py
│   │   │   │   └── test_text_to_sql.py
│   │   │   ├── integration/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_api_databases.py
│   │   │   │   ├── test_api_tables.py
│   │   │   │   ├── test_api_chat.py
│   │   │   │   └── test_celery_tasks.py
│   │   │   └── e2e/
│   │   │       ├── __init__.py
│   │   │       └── test_user_flows.py
│   │   ├── scripts/
│   │   │   ├── setup_db.py
│   │   │   ├── seed_olist_data.py
│   │   │   ├── generate_encryption_key.py
│   │   │   └── run_migrations.py
│   │   ├── .env.example
│   │   ├── .gitignore
│   │   ├── alembic.ini
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── requirements.txt
│   │   └── README.md
│   └── frontend/
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx
│       │   │   ├── page.tsx
│       │   │   ├── globals.css
│       │   │   ├── databases/
│       │   │   │   ├── page.tsx
│       │   │   │   └── [id]/
│       │   │   │       └── page.tsx
│       │   │   ├── tables/
│       │   │   │   └── [id]/
│       │   │   │       └── page.tsx
│       │   │   ├── chat/
│       │   │   │   └── page.tsx
│       │   │   ├── lineage/
│       │   │   │   └── page.tsx
│       │   │   └── settings/
│       │   │       └── page.tsx
│       │   ├── components/
│       │   │   ├── ui/
│       │   │   │   ├── button.tsx
│       │   │   │   ├── card.tsx
│       │   │   │   ├── input.tsx
│       │   │   │   ├── alert.tsx
│       │   │   │   ├── dialog.tsx
│       │   │   │   ├── dropdown.tsx
│       │   │   │   ├── tabs.tsx
│       │   │   │   └── badge.tsx
│       │   │   ├── layout/
│       │   │   │   ├── header.tsx
│       │   │   │   ├── sidebar.tsx
│       │   │   │   └── footer.tsx
│       │   │   ├── database/
│       │   │   │   ├── database-card.tsx
│       │   │   │   ├── database-form.tsx
│       │   │   │   └── connection-test.tsx
│       │   │   ├── schema/
│       │   │   │   ├── schema-tree.tsx
│       │   │   │   └── schema-selector.tsx
│       │   │   ├── table/
│       │   │   │   ├── table-detail.tsx
│       │   │   │   ├── table-list.tsx
│       │   │   │   ├── column-list.tsx
│       │   │   │   └── table-stats.tsx
│       │   │   ├── chat/
│       │   │   │   ├── chat-interface.tsx
│       │   │   │   ├── message-list.tsx
│       │   │   │   ├── message-input.tsx
│       │   │   │   └── sql-display.tsx
│       │   │   ├── lineage/
│       │   │   │   ├── lineage-graph.tsx
│       │   │   │   ├── lineage-controls.tsx
│       │   │   │   └── lineage-legend.tsx
│       │   │   ├── quality/
│       │   │   │   ├── quality-dashboard.tsx
│       │   │   │   ├── quality-metrics.tsx
│       │   │   │   └── quality-trends.tsx
│       │   │   └── common/
│       │   │       ├── loading.tsx
│       │   │       ├── error-boundary.tsx
│       │   │       ├── empty-state.tsx
│       │   │       └── search-bar.tsx
│       │   ├── hooks/
│       │   │   ├── use-database.ts
│       │   │   ├── use-table.ts
│       │   │   ├── use-chat.ts
│       │   │   ├── use-lineage.ts
│       │   │   ├── use-quality.ts
│       │   │   └── use-debounce.ts
│       │   ├── lib/
│       │   │   ├── api-client.ts
│       │   │   ├── query-client.ts
│       │   │   └── utils.ts
│       │   ├── stores/
│       │   │   ├── filter-store.ts
│       │   │   ├── ui-store.ts
│       │   │   └── chat-store.ts
│       │   ├── types/
│       │   │   ├── database.ts
│       │   │   ├── table.ts
│       │   │   ├── chat.ts
│       │   │   ├── lineage.ts
│       │   │   └── api.ts
│       │   └── styles/
│       │       └── themes.css
│       ├── public/
│       │   ├── favicon.ico
│       │   └── logo.svg
│       ├── .env.local.example
│       ├── .eslintrc.json
│       ├── .gitignore
│       ├── Dockerfile
│       ├── next.config.js
│       ├── package.json
│       ├── postcss.config.js
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       └── README.md
├── packages/
│   └── shared/
│       ├── src/
│       │   ├── types/
│       │   │   └── common.ts
│       │   └── constants/
│       │       └── index.ts
│       ├── package.json
│       └── tsconfig.json
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.dev.yml
│   ├── docker-compose.test.yml
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── .dockerignore
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── deployment.md
│   └── user-guide.md
├── scripts/
│   ├── setup.sh
│   ├── setup.ps1
│   └── download-olist-data.py
├── .gitignore
├── .editorconfig
├── .prettierrc
├── turbo.json
├── package.json
├── pnpm-workspace.yaml
├── README.md
├── PROJECT_RULES.md
├── KICKSTART.md
└── CHANGELOG.md
```

---

## Initial Setup

### Step 1: Clone and Initialize Repository

```bash
# Create project directory
mkdir ai-data-dictionary
cd ai-data-dictionary

# Initialize git
git init
git branch -M main

# Create all directories at once
mkdir -p apps/backend/src/{api/{routes,middleware},config,connectors,extractors,models,schemas,repositories,services,ai,workers,utils}
mkdir -p apps/backend/tests/{unit,integration,e2e}
mkdir -p apps/backend/alembic/versions
mkdir -p apps/backend/scripts
mkdir -p apps/frontend/src/{app/{databases,tables,chat,lineage,settings},components/{ui,layout,database,schema,table,chat,lineage,quality,common},hooks,lib,stores,types,styles}
mkdir -p apps/frontend/public
mkdir -p packages/shared/src/{types,constants}
mkdir -p docker
mkdir -p docs
mkdir -p scripts
mkdir -p .github/workflows
```

### Step 2: Install Turborepo

```bash
# Initialize Node.js project
npm init -y

# Install Turborepo globally (optional)
npm install -g turbo

# Install pnpm (recommended for monorepo)
npm install -g pnpm
```

### Step 3: Create Turborepo Configuration

Create `turbo.json`:
```json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^lint"]
    },
    "test": {
      "dependsOn": ["^build"],
      "outputs": ["coverage/**"]
    },
    "type-check": {
      "dependsOn": ["^type-check"]
    }
  }
}
```

Create `package.json` (root):
```json
{
  "name": "ai-data-dictionary",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^1.13.0",
    "prettier": "^3.2.5"
  },
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=8.0.0"
  },
  "packageManager": "pnpm@8.15.0"
}
```

Create `pnpm-workspace.yaml`:
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

---

## Backend Setup

### Step 1: Python Environment

```bash
cd apps/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### Step 2: Create `requirements.txt`

```txt
# Core Framework
fastapi==0.109.2
uvicorn[standard]==0.27.1
python-multipart==0.0.9

# Database
sqlalchemy==2.0.27
alembic==1.13.1
asyncpg==0.29.0
psycopg2-binary==2.9.9

# Database Connectors
snowflake-connector-python==3.7.0
snowflake-sqlalchemy==1.5.1
pyodbc==5.1.0
pymysql==1.1.0

# Task Queue
celery==5.3.6
redis==5.0.1
flower==2.0.1

# AI/ML
openai==1.12.0
tiktoken==0.6.0
langchain==0.1.7
chromadb==0.4.22

# Data Quality
ydata-profiling==4.6.4
pandera==0.18.0
sqlparse==0.4.4
sqlglot==20.11.0

# Data Validation
pydantic==2.6.1
pydantic-settings==2.1.0
email-validator==2.1.0

# Security
cryptography==42.0.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
slowapi==0.1.9

# Utilities
python-dotenv==1.0.1
structlog==24.1.0
tenacity==8.2.3
httpx==0.26.0

# Monitoring
prometheus-client==0.19.0

# Development
pytest==8.0.0
pytest-asyncio==0.23.5
pytest-cov==4.1.0
pytest-mock==3.12.0
black==24.1.1
ruff==0.2.1
mypy==1.8.0
pre-commit==3.6.0
```

### Step 3: Create `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ai-data-dictionary"
version = "1.0.0"
description = "AI-enhanced data dictionary platform"
readme = "README.md"
requires-python = ">=3.11"
license = {file = "LICENSE"}
authors = [
    {name = "Your Team", email = "team@example.com"}
]

[tool.ruff]
line-length = 100
target-version = "py311"
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "**/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### Step 5: Create Environment Configuration

Create `.env.example`:
```bash
# Application
APP_NAME=AI Data Dictionary
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=generate-with-openssl-rand-hex-32
ENCRYPTION_KEY=generate-with-python-script

# Database (Metadata Storage)
DATABASE_URL=postgresql+asyncpg://datadict_user:securepassword@localhost:5432/datadict_db

# Redis (Task Queue & Cache)
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CELERY_WORKER_CONCURRENCY=4

# AI/LLM
OPENAI_API_KEY=sk-your-openai-key-here
AI_PROVIDER=openai
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=text-embedding-3-small

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8000
CHROMADB_PERSIST_DIRECTORY=./data/chromadb

# Features
ENABLE_AI_DOCS=true
ENABLE_LINEAGE=true
ENABLE_TEXT_TO_SQL=true
ENABLE_QUALITY_CHECKS=true

# Performance
MAX_CONNECTIONS_POOL=20
MAX_OVERFLOW_POOL=10
POOL_TIMEOUT=30
POOL_RECYCLE=3600

# Security
CORS_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
MAX_REQUEST_SIZE=10485760

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
CHAT_RATE_LIMIT_PER_MINUTE=10
```

### Step 6: Generate Encryption Key

Create `scripts/generate_encryption_key.py`:
```python
from cryptography.fernet import Fernet
import secrets

def generate_keys():
    # Generate encryption key for Fernet
    encryption_key = Fernet.generate_key().decode()
    print(f"ENCRYPTION_KEY={encryption_key}")
    
    # Generate secret key for JWT
    secret_key = secrets.token_hex(32)
    print(f"SECRET_KEY={secret_key}")

if __name__ == "__main__":
    generate_keys()
```

Run it:
```bash
python scripts/generate_encryption_key.py
# Copy the output to your .env file
```

---

## Frontend Setup

### Step 1: Initialize Next.js App

```bash
cd apps/frontend

# Create package.json
```

Create `package.json`:
```json
{
  "name": "@ai-datadict/frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "@tanstack/react-query": "^5.20.0",
    "@tanstack/react-query-devtools": "^5.20.0",
    "zustand": "^4.5.0",
    "reactflow": "^11.10.4",
    "recharts": "^2.12.0",
    "@monaco-editor/react": "^4.6.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.1",
    "lucide-react": "^0.323.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "date-fns": "^3.3.1",
    "axios": "^1.6.7"
  },
  "devDependencies": {
    "@types/node": "^20.11.16",
    "@types/react": "^18.2.52",
    "@types/react-dom": "^18.2.18",
    "typescript": "^5.3.3",
    "eslint": "^8.56.0",
    "eslint-config-next": "14.1.0",
    "@typescript-eslint/parser": "^6.20.0",
    "@typescript-eslint/eslint-plugin": "^6.20.0",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.17",
    "prettier": "^3.2.5",
    "prettier-plugin-tailwindcss": "^0.5.11"
  }
}
```

### Step 2: Install Frontend Dependencies

```bash
pnpm install
```

### Step 3: Create Configuration Files

Create `next.config.js`:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

Create `tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

Create `tailwind.config.ts`:
```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          hover: '#2563eb',
        },
        secondary: '#8b5cf6',
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#06b6d4',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'Monaco', 'monospace'],
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
```

Create `.env.local.example`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## Database Schema

### Step 1: Database Models (SQLAlchemy)

Create `apps/backend/src/models/database.py`:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Database(Base):
    __tablename__ = 'databases'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(String(50), nullable=False)  # postgresql, snowflake, sqlserver
    connection_config = Column(JSON, nullable=False)  # Encrypted
    status = Column(String(50), default='pending')  # pending, connected, error
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    schemas = relationship('Schema', back_populates='database', cascade='all, delete-orphan')
    schema_versions = relationship('SchemaVersion', back_populates='database')
```

Create `apps/backend/src/models/schema.py`:
```python
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Schema(Base):
    __tablename__ = 'schemas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    database_id = Column(Integer, ForeignKey('databases.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    table_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    database = relationship('Database', back_populates='schemas')
    tables = relationship('Table', back_populates='schema', cascade='all, delete-orphan')
    
    __table_args__ = (
        Index('idx_schemas_database_name', 'database_id', 'name', unique=True),
    )
```

Create `apps/backend/src/models/table.py`:
```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, BigInteger, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Table(Base):
    __tablename__ = 'tables'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_id = Column(Integer, ForeignKey('schemas.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    type = Column(String(50), default='table')  # table, view, materialized_view
    row_count = Column(BigInteger, nullable=True)
    size_mb = Column(Float, nullable=True)
    description = Column(Text, nullable=True)  # AI-generated
    last_analyzed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    schema = relationship('Schema', back_populates='tables')
    columns = relationship('Column', back_populates='table', cascade='all, delete-orphan')
    quality_metrics = relationship('QualityMetric', back_populates='table')
    documentation = relationship('Documentation', back_populates='table', uselist=False)
    
    __table_args__ = (
        Index('idx_tables_schema_name', 'schema_id', 'name'),
    )
```

Create `apps/backend/src/models/column.py`:
```python
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.config.database import Base

class Column(Base):
    __tablename__ = 'columns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey('tables.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    data_type = Column(String(100), nullable=False)
    is_nullable = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    is_foreign_key = Column(Boolean, default=False)
    default_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)  # AI-generated
    sample_values = Column(JSON, nullable=True)
    ordinal_position = Column(Integer, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    table = relationship('Table', back_populates='columns')
```

Create `apps/backend/src/models/enums.py`:
```python
from enum import Enum

class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    SNOWFLAKE = "snowflake"
    SQLSERVER = "sqlserver"
    MYSQL = "mysql"

class DatabaseStatus(str, Enum):
    PENDING = "pending"
    CONNECTED = "connected"
    ERROR = "error"
    SYNCING = "syncing"

class TableType(str, Enum):
    TABLE = "table"
    VIEW = "view"
    MATERIALIZED_VIEW = "materialized_view"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"

class ChangeType(str, Enum):
    ADD_TABLE = "add_table"
    DROP_TABLE = "drop_table"
    ADD_COLUMN = "add_column"
    DROP_COLUMN = "drop_column"
    MODIFY_COLUMN = "modify_column"
    ADD_CONSTRAINT = "add_constraint"
    DROP_CONSTRAINT = "drop_constraint"

class QualityMetricType(str, Enum):
    COMPLETENESS = "completeness"
    UNIQUENESS = "uniqueness"
    FRESHNESS = "freshness"
    VALIDITY = "validity"
    CONSISTENCY = "consistency"
```

### Step 2: Alembic Configuration

Create `apps/backend/alembic.ini`:
```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = postgresql://datadict_user:securepassword@localhost:5432/datadict_db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers = console
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers = console
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
```

Create `apps/backend/alembic/env.py`:
```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config.database import Base
from src.models import *  # Import all models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Step 3: Initial Migration

```bash
cd apps/backend

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

## Configuration Files

### Backend Configuration

Create `apps/backend/src/config/settings.py`:
```python
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    # Application
    app_name: str = "AI Data Dictionary"
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str
    encryption_key: str
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Celery
    celery_broker_url: str
    celery_result_backend: str
    celery_worker_concurrency: int = 4
    
    # AI/LLM
    openai_api_key: str
    ai_provider: str = "openai"
    ollama_base_url: str = "http://localhost:11434"
    embedding_model: str = "text-embedding-3-small"
    
    # ChromaDB
    chromadb_host: str = "localhost"
    chromadb_port: int = 8000
    chromadb_persist_directory: str = "./data/chromadb"
    
    # Features
    enable_ai_docs: bool = True
    enable_lineage: bool = True
    enable_text_to_sql: bool = True
    enable_quality_checks: bool = True
    
    # Performance
    max_connections_pool: int = 20
    max_overflow_pool: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Security
    cors_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    max_request_size: int = 10485760
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    chat_rate_limit_per_minute: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

Create `apps/backend/src/config/database.py`:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config.settings import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=settings.max_connections_pool,
    max_overflow=settings.max_overflow_pool,
    pool_timeout=settings.pool_timeout,
    pool_recycle=settings.pool_recycle,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Docker Configuration

Create `docker/docker-compose.yml`:
```yaml
version: '3.9'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    container_name: datadict-postgres
    environment:
      POSTGRES_DB: datadict_db
      POSTGRES_USER: datadict_user
      POSTGRES_PASSWORD: securepassword
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - datadict-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U datadict_user -d datadict_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: datadict-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - datadict-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  chromadb:
    image: chromadb/chroma:latest
    container_name: datadict-chromadb
    volumes:
      - chromadb_data:/chroma/chroma
    ports:
      - "8000:8000"
    networks:
      - datadict-network
    environment:
      - IS_PERSISTENT=TRUE

  backend:
    build:
      context: ../apps/backend
      dockerfile: ../../docker/backend.Dockerfile
    container_name: datadict-backend
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ../apps/backend/src:/app/src
    ports:
      - "8000:8000"
    env_file:
      - ../apps/backend/.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - datadict-network

  celery-worker:
    build:
      context: ../apps/backend
      dockerfile: ../../docker/backend.Dockerfile
    container_name: datadict-celery-worker
    command: celery -A src.workers.celery_app worker --loglevel=info
    volumes:
      - ../apps/backend/src:/app/src
    env_file:
      - ../apps/backend/.env
    depends_on:
      - redis
      - postgres
    networks:
      - datadict-network

  celery-beat:
    build:
      context: ../apps/backend
      dockerfile: ../../docker/backend.Dockerfile
    container_name: datadict-celery-beat
    command: celery -A src.workers.celery_app beat --loglevel=info
    volumes:
      - ../apps/backend/src:/app/src
    env_file:
      - ../apps/backend/.env
    depends_on:
      - redis
    networks:
      - datadict-network

  flower:
    build:
      context: ../apps/backend
      dockerfile: ../../docker/backend.Dockerfile
    container_name: datadict-flower
    command: celery -A src.workers.celery_app flower --port=5555
    ports:
      - "5555:5555"
    env_file:
      - ../apps/backend/.env
    depends_on:
      - redis
    networks:
      - datadict-network

  frontend:
    build:
      context: ../apps/frontend
      dockerfile: ../../docker/frontend.Dockerfile
    container_name: datadict-frontend
    volumes:
      - ../apps/frontend/src:/app/src
      - ../apps/frontend/public:/app/public
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    networks:
      - datadict-network

networks:
  datadict-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  chromadb_data:
```

Create `docker/backend.Dockerfile`:
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq5 \
    unixodbc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker/frontend.Dockerfile`:
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

---

## Development Workflow

### Step 1: Start Services

```bash
# From project root
cd docker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### Step 2: Run Migrations

```bash
# From apps/backend
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"
```

### Step 3: Development Commands

```bash
# Backend development (with hot reload)
cd apps/backend
source venv/bin/activate
uvicorn src.main:app --reload

# Frontend development
cd apps/frontend
pnpm dev

# Run tests
pnpm test

# Lint and format
pnpm lint
pnpm format
```

---

## Testing Setup

Create `apps/backend/tests/conftest.py`:
```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from src.config.database import Base
from src.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def test_session(test_engine):
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

---

## Deployment Setup

### Step 1: Environment Setup Script

Create `scripts/setup.sh` (Linux/macOS):
```bash
#!/bin/bash

echo "Setting up AI Data Dictionary Platform..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting." >&2; exit 1; }

# Install pnpm
npm install -g pnpm

# Install Turborepo
pnpm install turbo --global

# Backend setup
cd apps/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Generate encryption keys
python scripts/generate_encryption_key.py > .env.keys
echo "Encryption keys generated. Please add them to your .env file."

# Frontend setup
cd ../frontend
pnpm install

# Return to root
cd ../..

echo "Setup complete! Please:"
echo "1. Copy apps/backend/.env.example to apps/backend/.env and fill in values"
echo "2. Copy apps/frontend/.env.local.example to apps/frontend/.env.local and fill in values"
echo "3. Add encryption keys from apps/backend/.env.keys to apps/backend/.env"
echo "4. Run 'docker-compose up' from the docker/ directory"
```

Create `scripts/setup.ps1` (Windows):
```powershell
Write-Host "Setting up AI Data Dictionary Platform..."

# Check prerequisites
$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($null -eq $docker) {
    Write-Error "Docker is required but not installed. Aborting."
    exit 1
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) {
    Write-Error "Python 3 is required but not installed. Aborting."
    exit 1
}

$node = Get-Command node -ErrorAction SilentlyContinue
if ($null -eq $node) {
    Write-Error "Node.js is required but not installed. Aborting."
    exit 1
}

# Install pnpm
npm install -g pnpm

# Install Turborepo
pnpm install turbo --global

# Backend setup
Set-Location apps\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Generate encryption keys
python scripts\generate_encryption_key.py > .env.keys
Write-Host "Encryption keys generated. Please add them to your .env file."

# Frontend setup
Set-Location ..\frontend
pnpm install

# Return to root
Set-Location ..\..

Write-Host "Setup complete! Please:"
Write-Host "1. Copy apps\backend\.env.example to apps\backend\.env and fill in values"
Write-Host "2. Copy apps\frontend\.env.local.example to apps\frontend\.env.local and fill in values"
Write-Host "3. Add encryption keys from apps\backend\.env.keys to apps\backend\.env"
Write-Host "4. Run 'docker-compose up' from the docker\ directory"
```

Make scripts executable:
```bash
chmod +x scripts/setup.sh
```

---

## Quick Start Commands

### Full Stack Development

```bash
# From project root

# 1. Initial setup (first time only)
./scripts/setup.sh  # or setup.ps1 on Windows

# 2. Configure environment
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.local.example apps/frontend/.env.local
# Edit .env files with your values

# 3. Start all services
cd docker
docker-compose up -d

# 4. Run migrations
docker-compose exec backend alembic upgrade head

# 5. Access applications
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Flower (Celery): http://localhost:5555

# 6. View logs
docker-compose logs -f

# 7. Stop services
docker-compose down
```

### Development (Hot Reload)

```bash
# Terminal 1: Backend
cd apps/backend
source venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd apps/frontend
pnpm dev

# Terminal 3: Celery Worker
cd apps/backend
celery -A src.workers.celery_app worker --loglevel=info

# Terminal 4: Celery Beat
cd apps/backend
celery -A src.workers.celery_app beat --loglevel=info
```

---

## Next Steps

### Immediate Actions
1. ✅ Run setup script
2. ✅ Configure environment variables
3. ✅ Start Docker services
4. ✅ Apply database migrations
5. ✅ Verify all services are running

### Phase 1 MVP (Weeks 1-4)
1. **Week 1:** Implement database connectors (PostgreSQL first)
2. **Week 2:** Build schema extraction and API endpoints
3. **Week 3:** Create frontend catalog browser
4. **Week 4:** Add manual documentation UI

### Phase 2 AI Integration (Weeks 5-7)
1. **Week 5:** OpenAI integration and documentation generation
2. **Week 6:** Basic chat interface
3. **Week 7:** Multi-database support (Snowflake, SQL Server)

### Phase 3 Advanced Features (Weeks 8-10)
1. **Week 8:** Data lineage extraction and visualization
2. **Week 9:** Text-to-SQL implementation
3. **Week 10:** Quality analysis and exports

---

## Helpful Resources

### Documentation
- **FastAPI:** https://fastapi.tiangolo.com/
- **Next.js:** https://nextjs.org/docs
- **SQLAlchemy:** https://docs.sqlalchemy.org/
- **TanStack Query:** https://tanstack.com/query/latest
- **Turborepo:** https://turbo.build/repo/docs

### Community
- **GitHub Issues:** Report bugs and request features
- **Discord/Slack:** (Setup team channel)
- **Documentation:** Read `docs/` folder for detailed guides

---

## Troubleshooting

### Common Issues

**1. Port conflicts:**
```bash
# Check what's using ports
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # macOS/Linux

# Kill process or change port in docker-compose.yml
```

**2. Database connection errors:**
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**3. Python import errors:**
```bash
# Reinstall dependencies
cd apps/backend
pip install -r requirements.txt --force-reinstall
```

**4. Frontend build errors:**
```bash
# Clear cache and reinstall
cd apps/frontend
rm -rf .next node_modules
pnpm install
pnpm build
```

---

## Support

For questions or issues:
1. Check `PROJECT_RULES.md` for standards
2. Review `docs/` folder for detailed documentation
3. Search GitHub issues
4. Create new issue with full error details

---

**Happy Building! 🚀**

*This kickstart guide is a living document. Update it as the project evolves.*
