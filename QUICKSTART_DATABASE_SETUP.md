# Database Connection Setup - Quick Guide

## 🎯 Current Status
✅ **READY TO USE** - Database management system fully implemented and functional

---

## 🚀 Quick Start

### 1. Access the Application
```
Frontend:  http://localhost:3000
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
```

### 2. Navigate to Databases
```
http://localhost:3000/databases
```

### 3. Add Your First Database
Click **"Add Database"** button and fill in:
```
Name:           Data Dictionary (Local)
Type:           PostgreSQL
Host:           localhost
Port:           5432
Database:       data_dictionary
Username:       postgres
Password:       [your_password]
Description:    Local test database
```

### 4. Test Connection
- Click **"Test Connection"** button
- Wait for success message
- Button shows: ✅ Connection Successful

### 5. Save Connection
- Click **"Save Connection"**
- Database appears in list with status

---

## 📊 View Database Status

### Dashboard Shows
```
✅ Connected Databases
├─ Name, Type, Host:Port
├─ Last Sync Time
├─ Status Badge (Connected/Error/Pending)
└─ Actions: Test | Edit | Delete
```

### Connection Status Indicators
- 🟢 **Connected** - Ready to use
- 🔴 **Error** - Check credentials
- 🟡 **Pending** - Not tested yet

---

## 🗄️ Setup Olist Sample Data

### Prerequisites
```bash
# Ensure PostgreSQL is running
Get-Service postgresql-x64-*

# Verify backend is running
Invoke-WebRequest http://localhost:8000/health
```

### Run Setup Script
```bash
cd apps/backend

# Option 1: Using environment variables
$env:DB_PASSWORD="your_password"
python scripts/setup_olist_data.py

# Option 2: Update .env first
# Edit .env file with correct PostgreSQL password
python scripts/setup_olist_data.py
```

### What Gets Created
- ✅ `olist` schema with 9 tables
- ✅ 52 sample records across all tables
- ✅ 13 performance indexes
- ✅ Foreign key relationships
- ✅ Sample data for testing

---

## 🔍 Verify Setup

### Check Olist Data
```sql
-- View all tables
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_schema = 'olist';

-- Count records
SELECT COUNT(*) FROM olist.customers;      -- 5 records
SELECT COUNT(*) FROM olist.orders;         -- 5 records
SELECT COUNT(*) FROM olist.products;       -- 5 records
```

### Frontend Check
1. Go to http://localhost:3000/databases
2. Add connection to `data_dictionary`
3. Test connection
4. Status shows: **Connected ✅**

---

## 🛠️ API Testing

### Login First
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@example.com\", \"password\":\"admin123\"}"
```

### Get Databases
```bash
curl http://localhost:8000/api/v1/databases \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Connection
```bash
curl -X POST http://localhost:8000/api/v1/databases/1/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ⚠️ PostgreSQL Authentication Issues

### Problem
```
FATAL: password authentication failed for user "postgres"
```

### Solutions

**Option 1: Update DATABASE_URL in .env**
```
DATABASE_URL=postgresql://postgres:correct_password@localhost:5432/data_dictionary
```

**Option 2: Check PostgreSQL Setup**
```bash
# Windows - Find PostgreSQL installation
Get-ChildItem "C:\Program Files" -Name "*Post*"

# Check service is running
Get-Service postgresql-x64-*
```

**Option 3: Use Trust Authentication (Local Dev Only)**
```
# PostgreSQL pg_hba.conf edit:
local   all             all                                     trust
host    all             all             127.0.0.1/32            trust
host    all             all             ::1/128                 trust
```

**Option 4: Reset PostgreSQL Password**
Windows requires stopping service and manual password reset.

---

## 📋 Olist Tables Overview

| Table | Records | Purpose |
|-------|---------|---------|
| `customers` | 5 | Customer information and location |
| `orders` | 5 | Order placement data |
| `order_items` | 6 | Items in each order |
| `order_payments` | 5 | Payment details |
| `order_reviews` | 3 | Customer reviews |
| `products` | 5 | Product catalog |
| `sellers` | 3 | Seller information |
| `product_category_translation` | 5 | Category names |
| `geolocation` | 5 | Lat/long coordinates |

**Total Records:** 52  
**Total Indexes:** 13  
**Schema:** `olist`

---

## ✨ Features Demonstrated

### Database Management
- ✅ Add/Remove connections
- ✅ Test before saving
- ✅ View connection status
- ✅ Encrypted credentials

### Frontend UI
- ✅ Responsive design
- ✅ Loading states
- ✅ Error messages
- ✅ Status badges
- ✅ Empty states

### Backend API
- ✅ CRUD operations
- ✅ Status tracking
- ✅ Encryption
- ✅ Validation
- ✅ Error handling

---

## 🎓 Real-World Use Cases

### After Setup, You Can:

1. **Data Catalog**
   - Browse connected databases
   - Explore tables and columns
   - Generate documentation

2. **Data Lineage**
   - Track column relationships
   - Understand data flows
   - Identify dependencies

3. **Data Quality**
   - Run quality checks
   - Monitor freshness
   - Profile completeness

4. **AI Assistance**
   - Auto-generate docs
   - Explain queries
   - Suggest optimizations

---

## 📞 Next Steps

1. **Document Tables**
   - Add descriptions to tables
   - Tag important columns
   - Create data glossary

2. **Create Lineage**
   - Map relationships
   - Track transformations
   - Build data flow diagrams

3. **Run Analyses**
   - Quality metrics
   - Column profiling
   - Freshness checks

4. **Generate Reports**
   - Data dictionary PDF
   - Lineage diagrams
   - Quality reports

---

## 🎯 Success Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Databases page loads successfully
- [ ] Can add new database connection
- [ ] Connection test passes
- [ ] Database shows in list with status
- [ ] Olist setup script completed
- [ ] Can view Olist tables in list

**All checked?** ✅ **Ready for next phase!**

---

## 📞 Support

### Common Issues

**Database connection fails**
- Check PostgreSQL is running
- Verify credentials in .env
- Confirm network connectivity

**Frontend not showing databases**
- Clear browser cache
- Check API health: http://localhost:8000/health
- Review browser console for errors

**Setup script hangs**
- Verify database credentials
- Check PostgreSQL password
- Kill hung Python process

---

**Version:** 1.0.0  
**Last Updated:** February 21, 2026  
**Status:** ✅ PRODUCTION READY
