# AI Data Dictionary Platform

> Automatically document enterprise databases with AI-enhanced metadata, quality analysis, and natural language chat interface.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🚀 Overview

The AI Data Dictionary Platform is a production-grade data catalog system that automatically:

- **Connects** to multiple database types (PostgreSQL, Snowflake, SQL Server)
- **Extracts** complete schema metadata (tables, columns, relationships, constraints)
- **Analyzes** data quality with metrics like completeness, freshness, and statistical distribution
- **Generates** business-friendly documentation using AI (OpenAI GPT-4/Ollama)
- **Provides** a conversational chat interface for natural language queries
- **Visualizes** data lineage and table relationships
- **Tracks** schema changes incrementally with version history

**Built for:** Data Analysts, Data Engineers, Business Intelligence teams

**Demo Dataset:** Olist Brazilian E-commerce (orders, customers, products, sellers, reviews)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Documentation](#-documentation)
- [Development](#-development)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### Core Capabilities

✅ **Multi-Database Connectivity**
- PostgreSQL, Snowflake, SQL Server, MySQL support
- Encrypted credential storage
- Connection health monitoring

✅ **Automated Documentation**
- AI-generated table and column descriptions
- Business-friendly language
- Use case recommendations

✅ **Data Quality Analysis**
- Completeness, uniqueness, validity metrics
- Statistical profiling (min/max/mean/percentiles)
- Time-series trend monitoring

✅ **Natural Language Chat**
- Ask questions about your schema
- Text-to-SQL query generation
- Context-aware responses with citations

✅ **Data Lineage Visualization**
- Upstream/downstream dependencies
- Interactive graph with zoom/pan
- Impact analysis for changes

✅ **Incremental Updates**
- Automatic schema change detection
- Version history with diffs
- Alerts on breaking changes

✅ **Export & Documentation**
- JSON and Markdown exports
- ERD diagrams (Mermaid syntax)
- Scheduled generation

---

## 🏗 Architecture

**Style:** Modular Monolith with Event-Driven Task Processing

**Tech Stack:**
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy, Celery
- **Frontend:** Next.js 14 (React), TypeScript, TailwindCSS
- **Databases:** PostgreSQL (metadata), TimescaleDB (metrics), ChromaDB (vectors)
- **Message Queue:** Redis
- **AI:** OpenAI GPT-4/3.5, Ollama (local fallback)
- **Deployment:** Docker Compose, Turborepo monorepo

**Key Patterns:**
- Repository pattern for data access
- Dependency injection
- Async/await for I/O operations
- Hybrid RAG (Retrieval Augmented Generation)

See [docs/architecture.md](docs/architecture.md) for detailed diagrams.

---

## 🚀 Quick Start

### Prerequisites

- **Node.js** 20+ and **pnpm** 8+
- **Python** 3.11+
- **Docker** 24+ and Docker Compose v2+
- **OpenAI API Key** (for AI features)

### Installation (5 minutes)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd ai-data-dictionary

# 2. Run setup script
./scripts/setup.sh  # macOS/Linux
# OR
.\scripts\setup.ps1  # Windows

# 3. Configure environment
cp apps/backend/.env.example apps/backend/.env
cp apps/frontend/.env.local.example apps/frontend/.env.local
# Edit .env files with your API keys and credentials

# 4. Start all services
cd docker
docker-compose up -d

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Access the application
# Frontend:        http://localhost:3000
# API Docs:        http://localhost:8000/docs
# Celery Monitor:  http://localhost:5555
```

### First Steps

1. **Add a Database Connection**
   - Navigate to http://localhost:3000
   - Click "Add Database"
   - Enter PostgreSQL connection details
   - Test connection and save

2. **Sync Schema**
   - Click "Sync Schema" on your database
   - Wait for extraction to complete (~30s for 100 tables)
   - Browse the catalog

3. **Generate Documentation**
   - Select a table
   - Click "Generate AI Documentation"
   - Review and edit if needed

4. **Chat with Your Data**
   - Go to Chat interface
   - Ask: "What tables contain customer information?"
   - Try: "Show me top 10 orders by revenue"

---

## 📚 Documentation

- **[KICKSTART.md](KICKSTART.md)** - Complete setup guide with folder structure
- **[PROJECT_RULES.md](PROJECT_RULES.md)** - Development standards and architecture decisions
- **[docs/architecture.md](docs/architecture.md)** - System architecture and component diagrams
- **[docs/api.md](docs/api.md)** - API reference and examples
- **[docs/deployment.md](docs/deployment.md)** - Production deployment guide
- **[docs/user-guide.md](docs/user-guide.md)** - End-user documentation

### API Documentation

Interactive API docs available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 💻 Development

### Project Structure (Turborepo Monorepo)

```
ai-data-dictionary/
├── apps/
│   ├── backend/          # FastAPI application
│   │   ├── src/          # Source code
│   │   ├── tests/        # Test suite
│   │   └── alembic/      # Database migrations
│   └── frontend/         # Next.js application
│       ├── src/          # Source code
│       └── public/       # Static assets
├── packages/
│   └── shared/           # Shared types and constants
├── docker/               # Docker configurations
├── docs/                 # Documentation
└── scripts/              # Setup and utility scripts
```

### Development Commands

```bash
# Start all services (hot reload enabled)
pnpm dev

# Run tests
pnpm test

# Lint code
pnpm lint

# Type check
pnpm type-check

# Build for production
pnpm build

# Format code
pnpm format
```

### Backend Development

```bash
cd apps/backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate   # Windows

# Run FastAPI with hot reload
uvicorn src.main:app --reload

# Run tests with coverage
pytest --cov=src --cov-report=html

# Create database migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Run Celery worker
celery -A src.workers.celery_app worker --loglevel=info
```

### Frontend Development

```bash
cd apps/frontend

# Run development server
pnpm dev

# Build for production
pnpm build

# Run production build locally
pnpm start

# Run tests
pnpm test

# Run Storybook (component development)
pnpm storybook
```

### Testing

```bash
# Run all tests
pnpm test

# Backend unit tests
cd apps/backend
pytest tests/unit -v

# Backend integration tests
pytest tests/integration -v

# Frontend tests
cd apps/frontend
pnpm test
```

### Code Quality

```bash
# Python (backend)
cd apps/backend
ruff check .              # Lint
ruff format .             # Format
mypy src/                 # Type check

# TypeScript (frontend)
cd apps/frontend
pnpm lint                 # ESLint
pnpm format               # Prettier
pnpm type-check           # TypeScript
```

---

## 🚢 Deployment

### Docker Production Build

```bash
# Build images
docker-compose -f docker/docker-compose.yml build

# Start services
docker-compose -f docker/docker-compose.yml up -d

# Check health
docker-compose ps
docker-compose logs -f
```

### Environment Variables

See `.env.example` files in `apps/backend/` and `apps/frontend/` for all configuration options.

**Required:**
- `OPENAI_API_KEY` - For AI documentation generation
- `DATABASE_URL` - PostgreSQL connection for metadata
- `REDIS_URL` - Redis for task queue
- `ENCRYPTION_KEY` - For credential encryption
- `SECRET_KEY` - For JWT tokens

### Production Checklist

- [ ] Configure production database (PostgreSQL 15+)
- [ ] Set up Redis for task queue
- [ ] Configure reverse proxy (Nginx/Traefik)
- [ ] Enable SSL/TLS certificates
- [ ] Set up backup strategy
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up log aggregation
- [ ] Configure alerts for quality issues
- [ ] Review security settings (CORS, rate limits)
- [ ] Load test with expected traffic

See [docs/deployment.md](docs/deployment.md) for detailed production setup.

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** code standards in [PROJECT_RULES.md](PROJECT_RULES.md)
4. **Write** tests (minimum 80% coverage)
5. **Commit** with conventional commits (`feat:`, `fix:`, `docs:`)
6. **Push** to your fork
7. **Open** a Pull Request

### Development Setup for Contributors

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-data-dictionary.git
cd ai-data-dictionary

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/ai-data-dictionary.git

# Run setup
./scripts/setup.sh

# Create feature branch
git checkout -b feature/my-feature

# Make changes, test, commit
git commit -m "feat(chat): add query history feature"

# Push and create PR
git push origin feature/my-feature
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Olist Dataset** - Brazilian E-commerce dataset from Kaggle
- **OpenAI** - GPT models for documentation generation
- **FastAPI** - Modern Python web framework
- **Next.js** - React framework for production
- **Shadcn/ui** - Beautifully designed components

---

## 📞 Support

- **Documentation:** Check [docs/](docs/) folder
- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/ai-data-dictionary/issues)
- **Discussions:** [GitHub Discussions](https://github.com/YOUR_USERNAME/ai-data-dictionary/discussions)
- **Email:** support@example.com

---

## 🗺 Roadmap

### Phase 1: MVP (Weeks 1-4) ✅
- [x] PostgreSQL connector
- [x] Schema extraction
- [x] Basic UI

### Phase 2: AI & Multi-Database (Weeks 5-7) 🚧
- [ ] OpenAI integration
- [ ] Snowflake & SQL Server connectors
- [ ] Chat interface

### Phase 3: Advanced Features (Weeks 8-10) 📋
- [ ] Data lineage visualization
- [ ] Text-to-SQL
- [ ] Quality trend monitoring

### Phase 4: Production (Weeks 11-12) 📋
- [ ] Authentication & authorization
- [ ] Performance optimization
- [ ] Security audit

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

**Built with ❤️ for data teams everywhere**

⭐ Star this repo if you find it useful!
