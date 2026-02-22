# AI Data Dictionary

An intelligent data dictionary application that automatically extracts, documents, and visualizes database schemas with AI-powered insights.

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.11, 3.12, or 3.13 (Python 3.14 has some dependency compatibility issues)
- **Node.js**: >= 20.0.0
- **pnpm**: >= 8.0.0 (or npm/yarn)
- **PostgreSQL**: 12+ (for the application database)
- **Redis**: 5.0+ (optional, for Celery task queue)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-data-dictionary
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd apps/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Backend Configuration

```bash
# Copy environment template
cp .env.example .env

# Generate secure keys
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"
# On Linux/Mac, you can also use:
# openssl rand -hex 32  # For JWT_SECRET_KEY

# Edit .env file and update:
# - ENCRYPTION_KEY (from above command)
# - JWT_SECRET_KEY (generate a random secret)
# - DATABASE_URL (PostgreSQL connection string)
# - OPENAI_API_KEY (optional, for LLM features)
# - GEMINI_API_KEY (optional, for chat features)
```

**Example `.env` file:**

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/data_dictionary
ENCRYPTION_KEY=your-generated-fernet-key-here
JWT_SECRET_KEY=your-random-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

#### 4. Initialize Database

```bash
# Run database migrations (if using Alembic)
alembic upgrade head

# Or initialize database manually
python scripts/init_db.py
```

This creates:
- All required database tables
- Default admin user:
  - **Email**: `admin@example.com`
  - **Password**: `admin123`
  - ⚠️ **Change this password after first login!**

#### 5. Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
pnpm install
# or
npm install
```

#### 6. Frontend Configuration

```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local and set:
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏃 Running the Application

### Start Backend

```bash
cd apps/backend

# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate     # Linux/Mac

# Run with uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the start script
# Windows:
powershell -ExecutionPolicy Bypass -File start.ps1
# Linux/Mac:
bash start.sh
```

Backend will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Start Frontend

```bash
cd apps/frontend

# Development mode
pnpm dev
# or
npm run dev
```

Frontend will be available at:
- **Application**: http://localhost:3000

### Start Both (Monorepo)

From the root directory:

```bash
# Install dependencies for all workspaces
pnpm install

# Start both backend and frontend
pnpm dev

# Or start individually
pnpm dev:frontend  # Frontend only
```

## 📦 Project Structure

```
ai-data-dictionary/
├── apps/
│   ├── backend/          # FastAPI backend
│   │   ├── src/
│   │   │   ├── api/      # API routes
│   │   │   ├── config/   # Configuration
│   │   │   ├── models/   # SQLAlchemy models
│   │   │   ├── schemas/  # Pydantic schemas
│   │   │   ├── services/ # Business logic
│   │   │   └── utils/    # Utilities
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/         # Next.js frontend
│       ├── src/
│       │   ├── app/      # Next.js app router pages
│       │   └── components/
│       ├── package.json
│       └── .env.example
├── package.json          # Root monorepo config
└── README.md
```

## 🔑 Key Features

- **Database Connection Management**: Connect to multiple PostgreSQL databases
- **Schema Extraction**: Automatically extract schemas, tables, columns, and relationships
- **Data Lineage**: Visualize table dependencies and relationships
- **AI-Powered Chat**: Ask questions about your database schema using AI
- **SQL Validation**: Validate and improve SQL queries with LLM assistance
- **Documentation**: Auto-generate documentation for tables and columns

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user info

### Databases
- `GET /api/v1/databases` - List all databases
- `POST /api/v1/databases` - Create new database connection
- `GET /api/v1/databases/{id}` - Get database details
- `POST /api/v1/databases/{id}/sync` - Sync database schema

### Schemas & Tables
- `GET /api/v1/schemas` - List schemas
- `GET /api/v1/tables` - List tables
- `GET /api/v1/tables/{id}` - Get table details

### Lineage
- `GET /api/v1/lineage` - Get full lineage graph
- `GET /api/v1/tables/{id}/lineage` - Get table lineage

### AI & Chat
- `POST /api/v1/ai/chat` - Chat with AI about schema
- `GET /api/v1/ai/schema-context` - Get schema context for agents

## 🛠️ Development

### Backend Development

```bash
cd apps/backend

# Run tests
pytest

# Run with coverage
pytest --cov=src

# Lint code
ruff check src/

# Format code
ruff format src/
```

### Frontend Development

```bash
cd apps/frontend

# Type check
pnpm type-check

# Lint
pnpm lint

# Build for production
pnpm build

# Start production server
pnpm start
```

## 🐛 Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError` for a package
**Solution**: Ensure virtual environment is activated and run `pip install -r requirements.txt`

**Problem**: Database connection errors
**Solution**: 
- Verify PostgreSQL is running
- Check `DATABASE_URL` in `.env` file
- Ensure database exists: `createdb data_dictionary`

**Problem**: `ImportError: cannot import name 'X'`
**Solution**: Check Python version (use 3.11-3.13), some packages don't support Python 3.14 yet

### Frontend Issues

**Problem**: `Connection refused` to backend
**Solution**: 
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS settings in backend

**Problem**: `Module not found` errors
**Solution**: Run `pnpm install` in the frontend directory

### Common Issues

**Port already in use**:
```bash
# Windows: Find process using port
netstat -ano | findstr :8000
# Kill process (replace PID)
taskkill /PID <PID> /F

# Linux/Mac: Find and kill process
lsof -ti:8000 | xargs kill -9
```

## 📚 Additional Documentation

- [Backend Quick Start](apps/backend/QUICKSTART.md)
- [Backend README](apps/backend/README.md)
- [Project Documentation Index](DOCUMENTATION_INDEX.md)
- [Complete Project Summary](COMPLETE_PROJECT_SUMMARY.md)

## 🔒 Security Notes

- **Never commit `.env` files** - They contain sensitive credentials
- **Change default admin password** after first login
- **Use strong encryption keys** in production
- **Rotate JWT secrets** regularly in production
- **Use HTTPS** in production environments

## 📝 License

MIT License

Copyright (c) 2026 WildeByte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

## 📞 Support

For issues and questions:
1. Check the [Documentation Index](DOCUMENTATION_INDEX.md)
2. Review [Troubleshooting](#-troubleshooting) section
3. Check existing issues in the repository

---

**Happy coding! 🎉**
