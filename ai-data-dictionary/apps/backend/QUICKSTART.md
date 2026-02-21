# Backend Quick Start Guide

## Prerequisites

- Python 3.11 or 3.12 (3.13+ has some dependency issues)
- PostgreSQL 15+ running locally or accessible
- OpenAI API key (for LLM features)

## Setup Steps

### 1. Create Virtual Environment

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Generate secure keys
python scripts/generate_keys.py

# Edit .env file and update:
# - ENCRYPTION_KEY (from generate_keys.py output)
# - JWT_SECRET_KEY (from generate_keys.py output)
# - OPENAI_API_KEY (your OpenAI API key)
# - DATABASE_URL (if different from default)
```

### 4. Initialize Database

```bash
# Create database tables and default admin user
python scripts/init_db.py
```

This will create:
- All required database tables
- Default admin user:
  - **Email:** admin@example.com
  - **Password:** admin123
  - ⚠️ **Change this password after first login!**

### 5. Run the Application

```bash
# Development mode with auto-reload
python src/main.py

# Or using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/logout` - Logout (client-side token deletion)
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user info

### SQL Execution

- `POST /api/v1/sql/validate` - Validate SQL with LLM
- `POST /api/v1/sql/execute` - Execute SQL query
- `POST /api/v1/sql/generate` - Generate SQL from natural language
- `POST /api/v1/sql/explain` - Explain SQL query
- `POST /api/v1/sql/format` - Format SQL query

## Testing the API

### 1. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "username": "admin",
    "role": "admin"
  }
}
```

### 2. Use the Token

```bash
# Get current user info
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Execute SQL query
curl -X POST http://localhost:8000/api/v1/sql/execute \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT 1 as test", "validate_with_llm": false, "allow_write": false}'
```

## Development

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
ruff check .
ruff format .
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Database Connection Error

```
ENCRYPTION_KEY=generate_with_fernet_key_generate
```

Problem: Invalid Fernet key in .env

Solution: Run `python scripts/generate_keys.py` and update .env

### OpenAI API Error

```
openai.error.AuthenticationError: Invalid API key
```

Problem: Missing or invalid OpenAI API key

Solution: Update `OPENAI_API_KEY` in .env with a valid key from https://platform.openai.com

### Import Errors

```
ModuleNotFoundError: No module named 'src'
```

Problem: Running from wrong directory

Solution: Always run commands from the `apps/backend` directory

## Security Notes

1. **Change default password** after first login
2. **Never commit .env** file to version control
3. **Use strong JWT_SECRET_KEY** in production
4. **Enable HTTPS** in production
5. **Set DEBUG=false** in production
6. **Restrict CORS origins** to your frontend domain
