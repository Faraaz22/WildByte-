# Database Connection System - Architecture & Implementation

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  /databases              Route                         │ │
│  │  ├─ Databases page       List all connections         │ │
│  │  └─ /databases/new       Add new connection           │ │
│  │                                                        │ │
│  │  Features:                                             │ │
│  │  • Connection list with pagination                     │ │
│  │  • Real-time status indicators                         │ │
│  │  • Test connection before save                         │ │
│  │  • Edit/Delete management                              │ │
│  │  • Error handling & validation                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↕️ HTTP                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ /api/v1/databases/*
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  API Router: src/api/databases.py                      │ │
│  │  ├─ GET  /         List databases (paginated)          │ │
│  │  ├─ GET  /{id}     Get database details               │ │
│  │  ├─ POST /         Create database (secure)            │ │
│  │  ├─ PUT  /{id}     Update database                     │ │
│  │  ├─ DELETE /{id}   Soft delete database               │ │
│  │  ├─ POST /{id}/test Test connection                   │ │
│  │  └─ POST /test-new Test new connection                │ │
│  │                                                        │ │
│  │  Features:                                             │ │
│  │  • Fernet encryption for credentials                   │ │
│  │  • Connection status tracking                          │ │
│  │  • Detailed error logging                              │ │
│  │  • Soft deletes for audit                              │ │
│  │  • Support for multiple DB types                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↕️ SQL                               │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│             PostgreSQL (data_dictionary)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Table: databases                                      │ │
│  │  ├─ id                    (PK)                         │ │
│  │  ├─ name                  (unique)                     │ │
│  │  ├─ db_type               (enum)                       │ │
│  │  ├─ connection_string_encrypted  (Fernet)             │ │
│  │  ├─ description                                        │ │
│  │  ├─ host, port, database_name                          │ │
│  │  ├─ sync_status           (pending/connected/error)    │ │
│  │  ├─ sync_error            (error details)              │ │
│  │  ├─ last_sync_at          (timestamp)                  │ │
│  │  └─ created_at, updated_at, deleted_at                │ │
│  │                                                        │ │
│  │  Relationships:                                        │ │
│  │  └─ schemas (1:N)         Connected database schemas   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
          ┌──────────────────────────────────┐
          │  Target Databases (User's DBs)   │
          │  • PostgreSQL                    │
          │  • MySQL                         │
          │  • SQL Server                    │
          │  • Snowflake                     │
          └──────────────────────────────────┘
```

---

## 📦 Component Breakdown

### Frontend Components

#### 1. Databases List Page
**File:** `apps/frontend/src/app/databases/page.tsx`

```tsx
Features:
├─ List all database connections
├─ Display connection status
│  ├─ Connected (Green) ✅
│  ├─ Error (Red) ❌
│  └─ Pending (Yellow) ⏳
├─ Test connection button
├─ Edit database link
├─ Delete button (with confirmation)
├─ Loading states
├─ Empty state UI
└─ Add database button
```

#### 2. Add Database Form
**File:** `apps/frontend/src/app/databases/new/page.tsx`

```tsx
Form Fields:
├─ Connection Name (required)
├─ Database Type (dropdown)
│  ├─ PostgreSQL (default)
│  ├─ MySQL
│  ├─ SQL Server
│  └─ Snowflake
├─ Host (required)
├─ Port (required)
├─ Database Name (required)
├─ Username (required)
├─ Password (required, masked)
├─ Description (optional)
└─ Test/Save buttons

Validation:
├─ Field-level validation
├─ Connection test (required)
├─ Error display
├─ Success feedback
└─ Loading states
```

#### 3. Navigation Update
**File:** `apps/frontend/src/components/common/Sidebar.tsx`

```tsx
Added Navigation Item:
├─ Icon: Database (lucide-react)
├─ Label: "Databases"
├─ Route: /databases
├─ Active state highlighting
└─ Integration with routing
```

### Backend Components

#### 1. Database API Router
**File:** `apps/backend/src/api/databases.py`

```python
Endpoints Implemented:

GET /databases
├─ Pagination support (page, page_size)
├─ List all non-deleted databases
├─ Return: DatabaseListResponse
└─ Status: 200 OK

GET /databases/{id}
├─ Fetch specific database
├─ Authorization check
├─ Return: DatabaseResponse
└─ Status: 200 OK or 404

POST /databases
├─ Create new database connection
├─ Encrypt connection string
├─ Validate inputs
├─ Check for duplicates
└─ Status: 201 Created

PUT /databases/{id}
├─ Update database connection
├─ Re-encrypt if credentials changed
├─ Soft delete tracking
└─ Status: 200 OK

DELETE /databases/{id}
├─ Soft delete (sets deleted_at)
├─ Audit trail maintained
└─ Status: 204 No Content

POST /databases/{id}/test
├─ Test existing connection
├─ Update sync_status
├─ Return ConnectionStatus
└─ Status: 200 OK

POST /databases/test-new
├─ Test connection before saving
├─ No database storage
├─ Return ConnectionStatus
└─ Status: 200 OK
```

#### 2. Database Models
**File:** `apps/backend/src/models/database.py`

```python
Database (SQLAlchemy ORM)
├─ id: int (PK)
├─ name: str (unique)
├─ db_type: DatabaseType (enum)
├─ connection_string_encrypted: str
├─ description: Optional[str]
├─ host: Optional[str]
├─ port: Optional[int]
├─ database_name: Optional[str]
├─ sync_status: str (default: "pending")
├─ sync_error: Optional[str]
├─ last_sync_at: Optional[datetime]
├─ created_at: datetime
├─ updated_at: datetime
├─ deleted_at: Optional[datetime]
└─ Relationship: schemas (1:N)
```

#### 3. Database Schemas
**File:** `apps/backend/src/schemas/database.py`

```python
DatabaseCreate (Input validation)
├─ name: str (1-100 chars)
├─ db_type: DatabaseType
├─ host: str
├─ port: int (1-65535)
├─ database_name: str
├─ username: str
├─ password: str
└─ description: Optional[str]

DatabaseResponse (Output serialization)
├─ id: int
├─ name: str
├─ db_type: str
├─ description: Optional[str]
├─ host: Optional[str]
├─ port: Optional[int]
├─ database_name: Optional[str]
├─ sync_status: str
├─ sync_error: Optional[str]
├─ last_sync_at: Optional[datetime]
├─ created_at: datetime
├─ updated_at: datetime
└─ Metadata config: from_attributes=True

DatabaseListResponse
├─ data: List[DatabaseResponse]
├─ total: int
├─ page: int
├─ page_size: int
└─ total_pages: int
```

### Security Components

#### Encryption Module
**Location:** `apps/backend/src/utils/crypto.py`

```python
Functions:
├─ encrypt_connection_string(conn_str)
│  └─ Uses Fernet symmetric encryption
├─ decrypt_connection_string(encrypted)
│  └─ Decrypts for connection testing
└─ Encryption key: ENCRYPTION_KEY from .env
```

#### Authentication
**Location:** `apps/backend/src/utils/auth.py`

```python
Current Protection:
├─ JWT token validation
├─ get_current_user dependency
├─ Applied to all database endpoints
└─ Admin-level access controls
```

---

## 🔄 Data Flow

### Creating a Database Connection

```
1. User fills form
   ↓
2. Frontend validates inputs
   ↓
3. User clicks "Test Connection"
   ↓
4. POST /databases/test-new
   ├─ Backend builds connection string
   ├─ Attempts to connect
   ├─ Returns success/error status
   └─ No credentials stored
   ↓
5. User clicks "Save Connection"
   ↓
6. POST /databases
   ├─ Backend validates input
   ├─ Encrypts connection string
   ├─ Stores in database
   ├─ Returns DatabaseResponse
   └─ Frontend redirects to list
   ↓
7. User sees new connection in list
```

### Testing Connection Status

```
GET/POST /databases/{id}/test
   ↓
1. Retrieve database record
   ↓
2. Decrypt connection string
   ↓
3. Create test engine
   ↓
4. Execute test query (SELECT 1)
   ↓
5. Update sync_status:
   ├─ Success → "connected"
   ├─ Failure → "error"
   └─ Store error message
   ↓
6. Return status to frontend
   ↓
7. Frontend updates visual indicator
```

---

## 📊 Database Schema

### Databases Table

```sql
CREATE TABLE databases (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  db_type VARCHAR(50) NOT NULL,
  connection_string_encrypted TEXT NOT NULL,
  description TEXT,
  host VARCHAR(255),
  port INTEGER,
  database_name VARCHAR(255),
  sync_status VARCHAR(50) DEFAULT 'pending',
  sync_error TEXT,
  last_sync_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  deleted_at TIMESTAMP WITH TIME ZONE
);

INSERT INTO databases VALUES (
  DEFAULT,
  'My PostgreSQL DB',
  'postgresql',
  'gAAAAABl...[encrypted]',
  'Production database',
  'db.example.com',
  5432,
  'mydb',
  'connected',
  NULL,
  '2024-02-21 10:30:00+00',
  '2024-02-21 10:00:00+00',
  '2024-02-21 10:30:00+00',
  NULL
);
```

---

## 🔐 Security Implementation

### Encryption Strategy

```
Plaintext Connection String:
  postgresql://user:pass@host:5432/dbname
          ↓
  Encrypt with Fernet (symmetric key)
          ↓
Ciphertext Stored in DB:
  gAAAAABl3Z0q2...base64_encoded_cipher...KJ4=
          ↓
  Only decrypted when testing connection
          ↓
  Never shown in APIs, logs, or frontend
```

### Access Control

```
Authentication Flow:
├─ User logs in
├─ JWT token created
├─ Token sent in Authorization header
├─ Middleware validates token
├─ Route handler processes request
└─ Admin permissions checked
```

---

## 🧪 Testing Scenarios

### Scenario 1: Add PostgreSQL Connection
```
1. Navigate to /databases
2. Click "Add Database"
3. Fill form:
   - Name: "Analytics DB"
   - Type: PostgreSQL
   - Host: analytics.internal
   - Port: 5432
   - Database: analytics_prod
   - User: app_user
   - Password: ••••••••
4. Click "Test Connection"
   → Shows: ✅ Connection Successful
5. Click "Save Connection"
   → Database added to list
   → Shows status: Connected ✅
```

### Scenario 2: Connection Error
```
1. Try to add with wrong password
2. Click "Test Connection"
   → Shows: ❌ Connection failed
   → Error: "Authentication failed"
3. "Save Connection" button disabled
4. User must test connection again
```

### Scenario 3: Edit Connection
```
1. Click "Edit" on existing database
2. Modify connection details
3. Click "Test Connection"
4. Click "Save Connection"
5. Status updates in list
```

---

## 📈 Performance Considerations

### Pagination
```
GET /databases?page=1&page_size=20
├─ Default: 20 items per page
├─ Offset calculated: (page-1) × page_size
├─ Total count queried separately
─── Response includes: total_pages
└─ Frontend handles pagination controls
```

### Indexes
```sql
CREATE INDEX idx_databases_name 
  ON databases(name);  -- For unique check

CREATE INDEX idx_databases_deleted_at 
  ON databases(deleted_at);  -- For soft deletes

CREATE INDEX idx_databases_sync_status 
  ON databases(sync_status);  -- For filtering
```

### Connection Pooling
```
Backend Configuration:
├─ Pool size: 20
├─ Max overflow: 10
├─ Pool timeout: 30s
├─ Pool pre-ping: enabled
└─ Pool recycle: 3600s
```

---

## 🚀 Deployment Checklist

- [ ] Ensure PostgreSQL is running
- [ ] Database tables created (via alembic)
- [ ] .env configured with DATABASE_URL
- [ ] ENCRYPTION_KEY set in .env
- [ ] Backend started on port 8000
- [ ] Frontend started on port 3000
- [ ] CORS configured correctly
- [ ] SSL certificates (if production)
- [ ] Database backups configured
- [ ] Monitoring/logging enabled

---

## 🔮 Future Enhancements

### Phase 2: Schema Extraction
```
├─ Detect tables from connected DB
├─ Extract column metadata
├─ Establish relationships
├─ Capture constraints
└─ Update schema model
```

### Phase 3: Data Lineage
```
├─ Track column transformations
├─ Build dependency graphs
├─ Visualize data flows
└─ Generate lineage reports
```

### Phase 4: AI Documentation
```
├─ Auto-generate table descriptions
├─ Classify sensitive columns
├─ Suggest documentation
└─ Create data glossary
```

---

## 📞 Architecture Review

### Strengths
✅ Modular design with clear separation
✅ Security-first approach with encryption
✅ Comprehensive error handling
✅ Scalable pagination support
✅ Soft deletes for audit trail
✅ Type-safe with Pydantic

### Considerations
⚠️ Single encryption key (requires rotation strategy)
⚠️ Synchronous connection testing (could add async)
⚠️ No connection pooling at API level
⚠️ Error messages could be more specific

---

**Version:** 1.0.0  
**Last Updated:** February 21, 2026  
**Status:** ✅ PRODUCTION READY
