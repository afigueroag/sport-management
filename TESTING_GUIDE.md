# SportAcademia Testing Guide

Complete manual for testing all features of the SportAcademia application.

---

## Part 1: Setup & Prerequisites

### 1.1 Verify PostgreSQL is Running

```cmd
psql -U postgres -h localhost -d sport_academy
```

Enter password: `Laredo35`

You should see the PostgreSQL prompt `sport_academy=#`. Type `\q` to exit.

### 1.2 Start the Backend Server

Open Command Prompt in the project directory:

```cmd
cd C:\Users\afigu\repos\sport-management
venv\Scripts\activate
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 1.3 Create Test Users (All Roles)

Open a new Command Prompt window and run:

```cmd
cd C:\Users\afigu\repos\sport-management
venv\Scripts\activate
python << EOF
import asyncio
from backend.config import settings
from backend.database import async_session
from backend.models.user import User, UserRole
from backend.utils.security import hash_password
from sqlalchemy import select

async def create_test_users():
    async with async_session() as session:
        users_data = [
            ("admin@test.com", "Admin User", UserRole.ADMIN),
            ("instructor@test.com", "Instructor User", UserRole.INSTRUCTOR),
            ("student@test.com", "Student User", UserRole.STUDENT),
            ("receptionist@test.com", "Receptionist User", UserRole.RECEPTIONIST),
        ]
        
        for email, name, role in users_data:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            if not result.scalar():
                user = User(
                    email=email,
                    full_name=name,
                    password_hash=hash_password("password123"),
                    role=role,
                    is_active=True,
                )
                session.add(user)
                print(f"Created {role.value}: {email}")
        
        await session.commit()
        print("All test users created!")

asyncio.run(create_test_users())
EOF
```

---

## Part 2: Testing the Frontend

### 2.1 Access the Application

Open your browser and go to:
```
http://127.0.0.1:8000/index.html
```

You should see the SportAcademia landing page with:
- Header with logo and navigation
- Hero section with "Gestiona tu Academia"
- Features section
- Pricing plans
- Footer

### 2.2 Test Landing Page

- [ ] Scroll through all sections
- [ ] Verify responsive layout (resize browser window)
- [ ] Click buttons and links (should work or show appropriate state)
- [ ] Check that styling matches the design system (blue primary, orange accent)

### 2.3 Test Authentication Flow

#### Register New User

1. Click **"Registrarse"** button on landing page
2. Fill in the form:
   - Email: `newuser@test.com`
   - Password: `TestPass123`
   - Confirm Password: `TestPass123`
   - Full Name: `Test User`
3. Click **"Crear Cuenta"**

**Expected Results:**
- [ ] Form validates (no empty fields)
- [ ] Success message appears
- [ ] Redirected to dashboard automatically
- [ ] User data displayed in navbar

#### Login

1. From landing page, click **"Iniciar Sesión"**
2. Enter credentials:
   - Email: `admin@test.com`
   - Password: `password123`
3. Click **"Iniciar Sesión"**

**Expected Results:**
- [ ] Login succeeds
- [ ] Redirected to admin dashboard
- [ ] User name "Admin User" shown in navbar
- [ ] Role badge shows "Administrador"

#### Logout

1. Click **"Cerrar Sesión"** button in navbar
2. Should return to landing page

**Expected Results:**
- [ ] Session cleared
- [ ] Redirected to login
- [ ] Cannot access dashboard without login (try refreshing)

### 2.4 Test Admin Dashboard

Login as: `admin@test.com` / `password123`

**Check displayed metrics:**
- [ ] "Estudiantes Activos" - shows count
- [ ] "Ventas Este Mes" - shows currency amount
- [ ] "Cuentas por Cobrar" - shows subscription count
- [ ] Change indicators (↑/↓) visible

**Expected Behavior:**
- [ ] Metrics load from API
- [ ] Numbers are realistic
- [ ] Page layout is clean and organized
- [ ] No console errors in Developer Tools (F12)

### 2.5 Test Instructor Dashboard

Login as: `instructor@test.com` / `password123`

**Check displayed sections:**
- [ ] "Mis Clases" section visible
- [ ] "Acciones Rápidas" with links
- [ ] Quick links functional

**Expected Behavior:**
- [ ] Dashboard is role-specific
- [ ] Shows instructor-relevant information
- [ ] Navigation to other features available

### 2.6 Test Student Dashboard

Login as: `student@test.com` / `password123`

**Check displayed sections:**
- [ ] "Mi Membresía" card with status
- [ ] "Mis Clases" section with enrolled classes
- [ ] "Clases Disponibles" section
- [ ] "Mi Historial de Pagos" table

**Expected Behavior:**
- [ ] Different layout from admin/instructor
- [ ] Shows student-specific data
- [ ] Can view class details and payment history

### 2.7 Test Receptionist Dashboard

Login as: `receptionist@test.com` / `password123`

**Check:**
- [ ] Dashboard loads (or shows coming soon message)
- [ ] Appropriate access level applied

---

## Part 3: Testing the API

### 3.1 Access Swagger Documentation

Open browser:
```
http://127.0.0.1:8000/docs
```

You should see interactive API documentation with all endpoints.

### 3.2 Test Authentication Endpoints

#### Register Endpoint
1. Click **POST /api/auth/register**
2. Click **"Try it out"**
3. Enter JSON:
```json
{
  "email": "apitest@test.com",
  "password": "TestPassword123",
  "full_name": "API Test User"
}
```
4. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns: `access_token`, `refresh_token`, `user` object
- [ ] Token is JWT format (header.payload.signature)

#### Login Endpoint
1. Click **POST /api/auth/login**
2. Click **"Try it out"**
3. Enter JSON:
```json
{
  "email": "admin@test.com",
  "password": "password123"
}
```
4. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns tokens and user information
- [ ] Token has correct expiration time

#### Get Current User (Protected)
1. Click **GET /api/auth/me**
2. Click **"Try it out"**
3. In "Authorization" field, paste the token from login:
   ```
   Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
4. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns current user information
- [ ] Without token: 401 Unauthorized error

### 3.3 Test Student Endpoints

#### Get Students (Admin Only)
1. Click **GET /api/students**
2. Authorize with admin token
3. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns list of students
- [ ] As student role: 403 Forbidden error

#### Create Student (Admin/Receptionist)
1. Click **POST /api/students**
2. Authorize with admin token
3. Enter JSON:
```json
{
  "email": "newstudent@test.com",
  "full_name": "New Student",
  "phone": "+34 123 456 789",
  "date_of_birth": "2000-01-15"
}
```
4. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200 or 201
- [ ] Returns created student with ID
- [ ] Student appears in student list

#### Get Student by ID
1. Click **GET /api/students/{student_id}**
2. Enter a student ID from the list
3. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns specific student details

### 3.4 Test Class Endpoints

#### List Classes
1. Click **GET /api/classes**
2. Click **"Execute"** (no auth required for listing)

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns empty list or existing classes

#### Create Class (Instructor/Admin)
1. Click **POST /api/classes**
2. Authorize with admin token
3. Enter JSON:
```json
{
  "name": "Karate Nivel 1",
  "sport_type": "Karate",
  "description": "Beginner karate class",
  "instructor_id": "instructor-uuid-here",
  "capacity": 20,
  "location": "Sala 1",
  "day_of_week": "MONDAY",
  "start_time": "18:00",
  "end_time": "19:00"
}
```
4. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 201
- [ ] Returns created class with ID
- [ ] Class appears in classes list

### 3.5 Test Dashboard Endpoints

#### Get Admin Summary (Protected)
1. Click **GET /api/dashboard/admin/summary**
2. Authorize with admin token
3. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns metrics:
  - `total_active_students`
  - `total_classes`
  - `total_enrollments`
  - `total_subscriptions`
  - `monthly_revenue`
  - `last_30_days_attendance`

#### Get Instructor Summary
1. Click **GET /api/dashboard/instructor/summary**
2. Authorize with instructor token
3. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns instructor-specific metrics

#### Get Student Summary
1. Click **GET /api/dashboard/student/summary**
2. Authorize with student token
3. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns student-specific metrics

### 3.6 Test Enrollment Endpoints

#### Create Enrollment
1. Click **POST /api/enrollments**
2. Authorize with student token
3. Enter JSON:
```json
{
  "student_id": "student-uuid",
  "class_id": "class-uuid"
}
```
4. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 201
- [ ] Returns enrollment with status "ACTIVE"
- [ ] Duplicate enrollment fails with 409 Conflict

#### Get Enrollments
1. Click **GET /api/enrollments**
2. Authorize with admin token
3. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns list of all enrollments
- [ ] Can filter by student_id, class_id, status

### 3.7 Test Attendance Endpoints

#### Mark Attendance (Instructor)
1. Click **POST /api/attendance**
2. Authorize with instructor token
3. Enter JSON:
```json
{
  "student_id": "student-uuid",
  "class_session_id": "session-uuid",
  "status": "PRESENT",
  "notes": "Attended and participated well"
}
```
4. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 201
- [ ] Returns attendance record
- [ ] Duplicate marking fails with 409 Conflict

#### Get Attendance
1. Click **GET /api/attendance**
2. Authorize with admin token
3. Click **"Execute"**

**Expected Results:**
- [ ] Response code: 200
- [ ] Returns attendance records
- [ ] Can filter by student, status, date

---

## Part 4: Testing Data Persistence

### 4.1 Verify Database Updates

After creating records via API, verify they're in the database:

```cmd
psql -U postgres -h localhost -d sport_academy
```

```sql
-- Check users
SELECT email, role, is_active FROM users;

-- Check students
SELECT id, email, full_name FROM students;

-- Check classes
SELECT id, name, sport_type, instructor_id FROM classes;

-- Check enrollments
SELECT id, student_id, class_id, status FROM enrollments;

-- Check attendance
SELECT id, student_id, class_session_id, status FROM attendance;

\q
```

### 4.2 Verify Frontend Reflects Changes

1. Create a new student via API
2. Refresh the student list in frontend
3. Verify new student appears

---

## Part 5: Testing Error Handling

### 5.1 Authentication Errors

**Test cases:**
- [ ] Login with wrong password → 401 Unauthorized
- [ ] Login with non-existent email → 401 Unauthorized
- [ ] Access protected endpoint without token → 401 Unauthorized
- [ ] Access protected endpoint with expired token → 401 Unauthorized
- [ ] Register with existing email → 409 Conflict

### 5.2 Authorization Errors

**Test cases:**
- [ ] Student tries to create class → 403 Forbidden
- [ ] Instructor tries to access admin dashboard → 403 Forbidden
- [ ] Receptionist tries to mark attendance → 403 Forbidden

### 5.3 Validation Errors

**Test cases:**
- [ ] Create student without email → 422 Unprocessable Entity
- [ ] Create class with invalid time → 422 error
- [ ] Register with password < 8 chars → 422 error

---

## Part 6: Testing Complete User Workflows

### Workflow 1: Student Enrollment Journey

1. **Register as new student**
   - [ ] Go to landing page
   - [ ] Click "Registrarse"
   - [ ] Fill and submit registration form

2. **Login**
   - [ ] Use new credentials to login
   - [ ] Verify dashboard shows "Sin clases inscritas"

3. **View available classes**
   - [ ] Navigate to "Clases Disponibles"
   - [ ] See list of available classes

4. **Enroll in a class**
   - [ ] Click "Inscribirme" on a class
   - [ ] Verify enrollment confirmation

5. **Check updated dashboard**
   - [ ] Refresh dashboard
   - [ ] Verify enrolled class appears

6. **Check attendance (after class)**
   - [ ] Login as instructor
   - [ ] Mark attendance for the class
   - [ ] Login as student, verify attendance recorded

### Workflow 2: Instructor Class Management

1. **Login as instructor**
   - [ ] `instructor@test.com` / `password123`
   - [ ] Verify instructor dashboard loads

2. **View assigned classes**
   - [ ] Check "Mis Clases" section
   - [ ] Verify instructor's classes displayed

3. **Mark attendance**
   - [ ] Click "Marcar Asistencia"
   - [ ] Select students and mark present/absent
   - [ ] Submit attendance

4. **View student details**
   - [ ] Click on a student name
   - [ ] Verify student info loads
   - [ ] Check attendance history

### Workflow 3: Admin Dashboard & Reports

1. **Login as admin**
   - [ ] `admin@test.com` / `password123`

2. **View metrics**
   - [ ] Check active students count
   - [ ] Verify revenue calculation
   - [ ] Check accounts receivable

3. **View pending payments**
   - [ ] Scroll to "Estudiantes con Pagos Pendientes"
   - [ ] Verify student list with amounts

4. **View staff hours**
   - [ ] Check "Horas Facturables del Personal"
   - [ ] Verify instructor hours displayed

---

## Part 7: Testing Responsiveness

### Mobile View (375px width)

1. Open browser Developer Tools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select "iPhone 12" or similar

**Test:**
- [ ] Navigation menu collapses to hamburger
- [ ] Content stacks vertically
- [ ] Buttons are still clickable
- [ ] Forms are readable
- [ ] No horizontal scrolling needed

### Tablet View (768px width)

1. Select "iPad" in device toolbar

**Test:**
- [ ] Layout adjusts appropriately
- [ ] Navigation visible (not collapsed)
- [ ] Content arranged in 2 columns where needed
- [ ] All elements accessible

### Desktop View (1280px+)

**Test:**
- [ ] Full layout with sidebars visible
- [ ] Multi-column layouts working
- [ ] Spacing appropriate

---

## Part 8: Console & Performance Checks

### Open Developer Tools (F12)

#### Console Tab
- [ ] No red error messages
- [ ] No unhandled promise rejections
- [ ] Only informational logs (✓ User data loaded, etc.)

#### Network Tab
1. Refresh page (Ctrl+R)
2. Check all requests

**Verify:**
- [ ] All API requests return 200-201 status
- [ ] No 404 or 500 errors
- [ ] Load times reasonable (< 200ms per request)
- [ ] No duplicate requests

#### Performance Tab
1. Click "Record" (circle button)
2. Interact with app (navigate, click buttons)
3. Click "Stop" and analyze

**Verify:**
- [ ] No long tasks blocking UI (> 50ms)
- [ ] Dashboard renders in < 1 second
- [ ] API calls complete in < 500ms

---

## Part 9: Testing Edge Cases

### Test Inactive Users

```cmd
psql -U postgres -h localhost -d sport_academy
```

```sql
UPDATE users SET is_active = false WHERE email = 'student@test.com';
```

Then try to login as that user:
- [ ] Login fails with "Esta cuenta ha sido desactivada"

### Test Duplicate Enrollments

1. Enroll a student in a class via API
2. Try to enroll the same student in the same class again
3. Should fail with 409 Conflict error

### Test Class at Capacity

1. Create class with capacity = 1
2. Enroll one student
3. Try to enroll a second student
4. Should fail or warn about capacity

### Test Expired Tokens

1. Login and get token
2. Wait 15+ minutes (access token expiration)
3. Try API request with old token
4. Should fail with 401 Unauthorized
5. Use refresh token to get new access token
6. Should succeed

---

## Part 10: Troubleshooting Issues

### Issue: "Cannot GET /index.html"

**Solution:**
- [ ] Backend server running?
- [ ] Check `http://127.0.0.1:8000/health` returns JSON
- [ ] Check frontend folder exists: `frontend/index.html`

### Issue: 401 Unauthorized on Dashboard

**Solution:**
- [ ] Token stored in localStorage? (F12 → Application → Local Storage)
- [ ] Token sent in Authorization header? (F12 → Network → Request headers)
- [ ] Token format correct? Should be "Bearer eyJ..."

### Issue: Database Connection Error

**Solution:**
- [ ] PostgreSQL service running? (`net start postgresql-x64-16`)
- [ ] Database exists? (`psql -l` shows sport_academy)
- [ ] Credentials correct? (`psql -U postgres -h localhost -d sport_academy`)

### Issue: CORS Error in Console

**Solution:**
- [ ] Check backend main.py has CORS middleware
- [ ] Verify `allow_origins=["*"]`
- [ ] Restart backend server

### Issue: API Endpoints Return 404

**Solution:**
- [ ] Check router is registered in `backend/main.py`
- [ ] Verify endpoint path matches
- [ ] Check prefix (e.g., `/api/students` not `/api/student`)

---

## Part 11: Test Checklist

Print and check off as you complete:

### Authentication
- [ ] Register new user
- [ ] Login with email/password
- [ ] Logout clears session
- [ ] Protected routes block unauth access
- [ ] Token refresh works

### Dashboard
- [ ] Admin dashboard shows correct metrics
- [ ] Instructor dashboard shows their classes
- [ ] Student dashboard shows enrollments
- [ ] Receptionist can access basic functions

### Students
- [ ] Create student (admin only)
- [ ] View student list
- [ ] View individual student
- [ ] Update student info
- [ ] Cannot delete (soft delete works)

### Classes
- [ ] Create class (instructor/admin)
- [ ] View class list
- [ ] View class details
- [ ] Update class
- [ ] Instructor can only edit own classes

### Enrollments
- [ ] Enroll in class
- [ ] View enrollments
- [ ] Cannot enroll twice
- [ ] Change enrollment status

### Attendance
- [ ] Mark attendance (instructor only)
- [ ] View attendance records
- [ ] Cannot mark duplicate
- [ ] Update attendance notes

### Responsiveness
- [ ] Mobile layout correct
- [ ] Tablet layout correct
- [ ] Desktop layout correct

### Performance
- [ ] No console errors
- [ ] API responses < 500ms
- [ ] Page loads < 1s
- [ ] No 404/500 errors

### Error Handling
- [ ] Wrong password fails
- [ ] Non-existent user fails
- [ ] Permission errors (403)
- [ ] Validation errors (422)

---

## Part 12: Reporting Issues

When you find a bug, include:

1. **Steps to reproduce**
   - What did you do?
   - What user role?
   - What endpoint/page?

2. **Expected behavior**
   - What should happen?

3. **Actual behavior**
   - What actually happened?

4. **Error details**
   - Console errors (F12)?
   - API response?
   - Database state?

**Example bug report:**
```
Title: Admin cannot create student

Steps:
1. Login as admin@test.com
2. Navigate to Students page
3. Click "Add Student"
4. Enter email: newstudent@test.com
5. Click Create

Expected: Student created, appears in list
Actual: Page shows error "500 Internal Server Error"

Console error: "TypeError: Cannot read property 'id' of undefined"
```

---

## Done! 🎉

You've tested SportAcademia comprehensively. Ready to:
- [ ] Deploy to production with Docker
- [ ] Integrate real Stripe keys
- [ ] Setup email notifications
- [ ] Add more features
