# PostgreSQL Authentication & Olist Setup Troubleshooting Guide

## 🔍 Problem Analysis

Your project has successfully completed:
- ✅ Backend database API with 7 endpoints
- ✅ Frontend database management UI with status indicators
- ✅ Connection testing and encryption
- ✅ Olist schema design (9 tables, 52 records, 13 indexes)

**Current Issue**: PostgreSQL password authentication failure when running setup scripts

---

## 🚨 Common PostgreSQL Authentication Issues

### Issue 1: Password Mismatch
**Symptom**: `FATAL: password authentication failed for user postgres`

**Causes**:
- `.env` contains wrong password
- PostgreSQL password differs from configured credentials
- Password contains special characters that need escaping

**Solutions**:

#### Solution 1A: Reset PostgreSQL Password
```powershell
# On Windows - Open Command Prompt as Administrator
cd "C:\Program Files\PostgreSQL\<version>\bin"

# Stop PostgreSQL service
Stop-Service -Name "postgresql-x64-<version>" -Force

# Reset password using pg_ctl
pg_ctl -D "C:\Program Files\PostgreSQL\<version>\data" start

# Then connect with trust auth and update password
psql -U postgres

# In psql:
ALTER USER postgres WITH PASSWORD 'your_new_password';
\q
```

#### Solution 1B: Update .env Configuration
```env
# apps/backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:your_actual_password@localhost:5432/data_dictionary
```

#### Solution 1C: Use Environment Variable
```powershell
# PowerShell - Run before setup
$env:PGPASSWORD = 'your_actual_password'

# Then run setup
python scripts/setup_olist_data.py
```

---

### Issue 2: PostgreSQL Not Running
**Symptom**: Connection refused / Cannot connect

**Solution**:
```powershell
# Check if service is running
Get-Service -Name "postgresql-x64-*"

# If not running, start it
Start-Service -Name "postgresql-x64-18"

# Verify it's listening
netstat -ano | findstr :5432
```

---

### Issue 3: Trust Authentication Not Configured
**Symptom**: Still auth failure after resetting password

**Solution**: Edit PostgreSQL configuration

```powershell
# On Windows, find pg_hba.conf
# Typically at: C:\Program Files\PostgreSQL\<version>\data\pg_hba.conf

# Open in notepad
notepad "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"

# Look for localhost entries, change to:
# Local connections use trust for now
local   all             postgres                                trust
host    all             postgres        127.0.0.1/32            trust
host    all             postgres        ::1/128                 trust

# Save file and restart PostgreSQL service
Restart-Service -Name "postgresql-x64-18"
```

---

## 🚀 Setup Options

### Option 1: Using PowerShell Script (RECOMMENDED - Windows)

```powershell
cd "d:\AI data dictionary Agent\ai-data-dictionary\apps\backend"

# Option A: With password parameter
powershell -ExecutionPolicy Bypass -File scripts/setup_olist_with_psql.ps1 -PostgresPassword "your_password"

# Option B: With environment variable
$env:PGPASSWORD = "your_password"
powershell -ExecutionPolicy Bypass -File scripts/setup_olist_with_psql.ps1

# Option C: Accept default localhost:postgres
powershell -ExecutionPolicy Bypass -File scripts/setup_olist_with_psql.ps1
```

### Option 2: Using Bash Script (Linux/Mac)

```bash
cd "d:\AI data dictionary Agent\ai-data-dictionary\apps\backend"

# With password
bash scripts/setup_olist_with_psql.sh -u postgres -p your_password

# Default parameters
bash scripts/setup_olist_with_psql.sh
```

### Option 3: Using Python (Original - requires auth fix)

```powershell
cd "d:\AI data dictionary Agent\ai-data-dictionary\apps\backend"

# Set all connection details
$env:DB_PASSWORD = "your_actual_password"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_USER = "postgres"
$env:DB_NAME = "data_dictionary"

# Run synchronous setup (recommended)
python scripts/setup_olist_data.py
```

### Option 4: Manual SQL Execution

```powershell
# Using psql CLI directly
psql -h localhost -p 5432 -U postgres -d data_dictionary -f scripts/setup_olist_manual.sql

# Or paste the SQL content directly in pgAdmin UI
# - Open pgAdmin
# - Connect to data_dictionary
# - Open Query Tool
# - Copy-paste SQL from setup_olist_with_psql.ps1
# - Execute
```

---

## 📋 Step-by-Step Diagnosis

### Step 1: Verify PostgreSQL is Running
```powershell
# Check service status
Get-Service postgresql-x64-* | Select-Object Status, Name

# Check if port is listening
Test-NetConnection -ComputerName localhost -Port 5432
```

**Expected Output**:
```
Status Name
------ ----
Running postgresql-x64-18

ComputerName     : localhost
RemotePort       : 5432
TcpTestSucceeded : True
```

### Step 2: Test Connection with psql
```powershell
# Try to connect
psql -h localhost -U postgres -d postgres -c "SELECT version();"

# If prompts for password, enter it
# Expected: PostgreSQL version info
```

### Step 3: Verify data_dictionary Database Exists
```powershell
# List all databases
psql -h localhost -U postgres -d postgres -c "\l"

# Expected output should include: data_dictionary
```

### Step 4: Check Backend Health (Proves Backend Can Connect)
```powershell
# Terminal 1: Start backend (if not running)
cd "d:\AI data dictionary Agent\ai-data-dictionary\apps\backend"
python -m uvicorn src.main:app --reload

# Terminal 2: Test health endpoint
curl -s http://localhost:8000/health | ConvertFrom-Json
```

**Expected Output**:
```json
{
  "status": "healthy",
  "environment": "development"
}
```

**Key Insight**: If backend health is OK but setup scripts fail with auth error, the password in `.env` differs from what backend is using.

### Step 5: Run Setup Script with Verbose Output
```powershell
# Use this to see actual SQL being executed
$env:PGPASSWORD = "your_password"

psql -h localhost -p 5432 -U postgres -d data_dictionary -f /path/to/setup_file.sql
```

---

## 🔧 Configuration Files Created

### 1. PowerShell Setup Script
**File**: `apps/backend/scripts/setup_olist_with_psql.ps1`
- Accepts parameters for all connection details
- Uses psql CLI (no Python dependency)
- Supports password prompting
- Shows execution progress
- Validates success

### 2. Bash Setup Script
**File**: `apps/backend/scripts/setup_olist_with_psql.sh`
- Same functionality as PowerShell version
- For Linux/Mac environments
- Source-compatible SQL

### 3. Python Setup Scripts (Original)
**Files**:
- `scripts/setup_olist_data.py` - Synchronous (RECOMMENDED)
- `scripts/setup_olist_database.py` - Async, separate DB
- `scripts/setup_olist_in_existing_db.py` - Async, in-schema

**Use Case**: When Python is preferred and auth is resolved

---

## 📊 Expected Results After Setup

### Database Structure
```
data_dictionary
└── olist (schema)
    ├── customers (5 rows)
    ├── orders (5 rows)
    ├── order_items (6 rows)
    ├── order_payments (5 rows)
    ├── order_reviews (3 rows)
    ├── products (5 rows)
    ├── sellers (3 rows)
    ├── product_category_name_translation (5 rows)
    └── geolocation (5 rows)
    
Total: 52 sample records
Total: 13 performance indexes
```

### Verification SQL
```sql
-- Run this to verify setup
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT tablename) as table_count
FROM (
    SELECT tablename FROM information_schema.tables WHERE table_schema = 'olist'
) AS tables;

-- Expected: 9 tables, 52+ total records
```

---

## 🎯 Quick Start Commands

### For Windows Users (PowerShell)

```powershell
# Step 1: Verify PostgreSQL
Get-Service postgresql-x64-* | Select-Object Status

# Step 2: Run Setup (no password needed if trust auth)
cd "d:\AI data dictionary Agent\ai-data-dictionary\apps\backend"
powershell -ExecutionPolicy Bypass -File scripts/setup_olist_with_psql.ps1

# Step 3: Verify Results
psql -h localhost -U postgres -d data_dictionary -c "SELECT COUNT(*) FROM olist.orders;"
```

### For Linux/Mac Users

```bash
# Step 1: Verify PostgreSQL
systemctl status postgresql

# Step 2: Run Setup
cd ~/workspace/ai-data-dictionary/apps/backend
bash scripts/setup_olist_with_psql.sh

# Step 3: Verify Results
psql -h localhost -U postgres -d data_dictionary -c "SELECT COUNT(*) FROM olist.orders;"
```

---

## 🆘 If Setup Still Fails

### Fallback Option 1: Use pgAdmin UI
1. Open pgAdmin (web interface at http://localhost:5050)
2. Connect to data_dictionary
3. Right-click → Query Tool
4. Copy SQL from `setup_olist_with_psql.ps1` (starting at line 8 after `$sqlScript = @"`)
5. Paste into Query Tool
6. Execute

### Fallback Option 2: Factory Reset PostgreSQL
```powershell
# WARNING: This will delete all data!

# Stop service
Stop-Service -Name "postgresql-x64-18"

# Remove data directory
Remove-Item "C:\Program Files\PostgreSQL\18\data" -Recurse -Force

# Reinitialize
pg_ctl.exe init -D "C:\Program Files\PostgreSQL\18\data"

# Start service
Start-Service -Name "postgresql-x64-18"

# Then run setup
```

### Fallback Option 3: Docker Alternative
If local PostgreSQL is misconfigured, use Docker:

```powershell
# Start PostgreSQL in Docker
docker run --name postgres-data-dict -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=data_dictionary -p 5432:5432 -d postgres:latest

# Then run setup
$env:PGPASSWORD = "postgres"
psql -h localhost -U postgres -d data_dictionary -f scripts/setup_olist_with_psql.sql
```

---

## 📞 Support Checklist

Before running setup, verify:
- [ ] PostgreSQL service is running (`Get-Service`)
- [ ] Port 5432 is available (`Test-NetConnection`)
- [ ] Can connect with `psql -h localhost -U postgres`
- [ ] data_dictionary database exists
- [ ] Backend health check passes (`curl http://localhost:8000/health`)
- [ ] PostgreSQL version is 12+ (`SELECT version()`)
- [ ] psql CLI is in PATH or scripts directory

---

## 🔗 Related Files

- [ARCHITECTURE_DATABASE_SYSTEM.md](ARCHITECTURE_DATABASE_SYSTEM.md) - System design
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Current status
- [QUICKSTART_DATABASE_SETUP.md](QUICKSTART_DATABASE_SETUP.md) - Quick start guide
- `apps/backend/.env` - Database connection configuration

---

**Last Updated**: February 21, 2024  
**Status**: Ready to Deploy  
**Next Step**: Run one of the setup scripts above
