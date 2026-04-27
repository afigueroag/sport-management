# Backend Setup - Phase 4

## 📋 Overview

Phase 4 sets up the FastAPI backend with PostgreSQL database and complete project structure.

### Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL (async with asyncpg)
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)

## 🗂️ Project Structure

```
backend/
├── __init__.py
├── main.py                 ← FastAPI app entry point
├── config.py               ← Settings (env vars, secrets)
├── database.py             ← SQLAlchemy setup
├── models/                 ← ORM models (SQLAlchemy)
│   ├── __init__.py
│   ├── user.py            ← User model + roles
│   ├── student.py         ← Student model
│   ├── class_model.py     ← Class & ClassSession models
│   ├── enrollment.py      ← Student-Class relationship
│   ├── attendance.py      ← Attendance tracking
│   ├── membership.py      ← Membership plans
│   ├── subscription.py    ← Student subscriptions
│   └── payment.py         ← Payments & invoices
├── schemas/               ← Pydantic models (request/response)
│   ├── __init__.py
│   ├── user.py            ← User schemas
│   ├── student.py         ← Student schemas
│   └── auth.py            ← Auth token schemas
├── routers/               ← API endpoints (coming Phase 4+)
│   └── __init__.py
├── services/              ← Business logic (coming Phase 5)
│   └── __init__.py
└── utils/                 ← Helper functions
    ├── __init__.py
    └── security.py        ← Password hashing & JWT
```

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings
nano .env
```

Key variables:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/sport_management_db
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
```

### 3. Setup PostgreSQL

#### Option A: Local PostgreSQL
```bash
# Install PostgreSQL (if not installed)
# macOS:
brew install postgresql

# Ubuntu/Debian:
sudo apt-get install postgresql

# Start PostgreSQL
# macOS:
brew services start postgresql

# Ubuntu:
sudo systemctl start postgresql

# Create database
psql -U postgres -c "CREATE DATABASE sport_management_db;"

# Create user (optional, for security)
psql -U postgres -c "CREATE USER sport_admin WITH PASSWORD 'secure_password';"
psql -U postgres -c "ALTER ROLE sport_admin WITH CREATEDB;"
```

#### Option B: Azure SQL Database
```
# Get connection string from Azure Portal
# Update DATABASE_URL in .env with Azure connection string:
DATABASE_URL=postgresql+asyncpg://user:password@server.database.windows.net:5432/database_name?sslmode=require
```

#### Option C: Docker PostgreSQL
```bash
docker run --name postgres-sportacademia \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=sport_management_db \
  -p 5432:5432 \
  -d postgres:16
```

### 4. Initialize Database

```bash
# Using Alembic (when migrations are created)
alembic upgrade head

# Or manually create tables from models
# (SQLAlchemy will create tables on first run with our setup)
```

## 🚀 Running the Server

### Development Mode
```bash
cd backend
python main.py
```

Server runs at: `http://localhost:8000`

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Access API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📊 Database Models (11 Tables)

### Core Models

1. **User** (`users` table)
   - id (PK)
   - email (unique)
   - full_name
   - password_hash
   - role (admin, instructor, student, receptionist)
   - is_active, is_verified
   - created_at, updated_at

2. **Student** (`students` table)
   - id (FK → users.id)
   - phone
   - date_of_birth
   - emergency_contact_name, emergency_contact_phone
   - created_at, updated_at

3. **Class** (`classes` table)
   - id (PK)
   - name
   - sport_type
   - instructor_id (FK → users.id)
   - capacity
   - day_of_week (M-Su)
   - start_time, end_time
   - is_active
   - created_at, updated_at

4. **ClassSession** (`class_sessions` table)
   - id (PK)
   - class_id (FK → classes.id)
   - session_date
   - is_canceled

5. **Enrollment** (`enrollments` table)
   - id (PK)
   - student_id (FK → students.id)
   - class_id (FK → classes.id)
   - status (active, paused, canceled)
   - enrolled_at, canceled_at

6. **Attendance** (`attendance` table)
   - id (PK)
   - student_id (FK → students.id)
   - class_session_id (FK → class_sessions.id)
   - marked_by (FK → users.id)
   - status (present, absent, excused)
   - notes
   - marked_at, created_at

7. **Membership** (`memberships` table)
   - id (PK)
   - name (e.g., "Monthly Unlimited")
   - description
   - price_cents
   - currency
   - class_limit (null = unlimited)
   - duration_months
   - stripe_price_id
   - is_active
   - created_at, updated_at

8. **Subscription** (`subscriptions` table)
   - id (PK)
   - student_id (FK → students.id)
   - membership_id (FK → memberships.id)
   - status (active, paused, canceled, pending)
   - stripe_subscription_id
   - started_at, current_period_end, canceled_at
   - created_at, updated_at

9. **Payment** (`payments` table)
   - id (PK)
   - student_id (FK → students.id)
   - subscription_id (FK → subscriptions.id, nullable)
   - amount_cents
   - currency
   - status (pending, paid, failed, refunded)
   - payment_method (stripe, cash, check)
   - invoice_number (unique)
   - stripe_payment_intent_id
   - due_date, paid_at
   - created_at, updated_at

## 🔐 Security Features

### Password Hashing
- Using bcrypt via passlib
- Passwords never stored in plain text
- Always validate with `verify_password()`

### JWT Authentication
- Access tokens: 15 minutes expiry
- Refresh tokens: 7 days expiry
- Tokens signed with SECRET_KEY (change in production!)
- Uses HS256 algorithm

### CORS
- Configured for frontend origins
- Prevents cross-origin attacks
- Customizable in config.py

## 🧪 Testing the Backend

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "app": "SportAcademia",
  "version": "0.1.0"
}
```

### API Documentation
- Open `http://localhost:8000/docs` in browser
- Swagger UI auto-generated from FastAPI
- Test endpoints interactively

## 📝 Upcoming in Phase 5

- Auth routers (login, register, refresh token)
- Student CRUD routers
- Class management routers
- Attendance marking routers
- Payment/subscription routers
- Report/dashboard data endpoints

## 🔄 Database Migrations (Alembic)

### Create a Migration
```bash
alembic revision --autogenerate -m "Create users table"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

## 🐛 Troubleshooting

### Connection Error: "Cannot connect to database"
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Check database name and credentials

### Port 8000 Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Import Errors
- Ensure you're in backend directory
- Check PYTHONPATH includes backend
- Verify all dependencies installed: `pip install -r requirements.txt`

## 📚 Key Dependencies

| Package | Purpose |
|---------|---------|
| fastapi | Web framework |
| uvicorn | ASGI server |
| sqlalchemy | ORM |
| psycopg2 | PostgreSQL driver |
| asyncpg | Async PostgreSQL driver |
| python-jose | JWT handling |
| passlib | Password hashing |
| pydantic | Data validation |
| alembic | Database migrations |
| stripe | Payment processing |

## 🚀 Next Steps

1. **Phase 5**: Build API routers (auth, students, classes, payments)
2. **Phase 6**: Wire frontend to API endpoints
3. **Phase 7**: Stripe integration & webhooks
4. **Phase 8**: Production hardening (Docker, security, monitoring)

---

For more information, see the main README.md
