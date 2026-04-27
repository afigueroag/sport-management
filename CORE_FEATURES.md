# SportAcademia - Core Features & Workflow Document

**Last Updated**: 2026-04-27  
**Phase**: Planning (before Phase 2)  
**Scope**: MVP features for Phase 2-6

---

## 📋 User Roles & Permissions

### 1. **Academy Owner / Admin**
**Primary Goal**: Monitor revenue, student health, and operational metrics

| Feature | Access | Priority |
|---------|--------|----------|
| View Dashboard (KPIs) | ✅ Read | P0 |
| Manage Students (CRUD) | ✅ Create, Edit, Delete | P1 |
| Manage Classes (CRUD) | ✅ Create, Edit, Delete | P1 |
| Manage Instructors | ✅ Assign to classes | P1 |
| View Attendance Reports | ✅ Read all | P1 |
| View Revenue & Payments | ✅ Read, reconcile | P0 |
| Manage Receptionist Staff | ✅ Create, Edit | P2 |
| Access Admin Panel | ✅ Full | P0 |

---

### 2. **Instructor / Teacher**
**Primary Goal**: Mark attendance, manage their classes

| Feature | Access | Priority |
|---------|--------|----------|
| View My Classes | ✅ Read | P0 |
| Mark Attendance | ✅ Create/Edit | P0 |
| View Attendance History | ✅ Read own classes | P0 |
| Add Student Notes | ✅ Create/Edit | P1 |
| Request Schedule Change | ✅ Submit request | P2 |
| View Class Roster | ✅ Read | P0 |

---

### 3. **Receptionist / Staff**
**Primary Goal**: Handle enrollments and payments

| Feature | Access | Priority |
|---------|--------|----------|
| Enroll Students | ✅ Create student + enroll class | P1 |
| Record Manual Payments | ✅ Create payment record | P1 |
| View Student List | ✅ Read | P0 |
| Send Payment Reminders | ✅ Create/Send | P2 |
| View Class Schedule | ✅ Read | P0 |

---

### 4. **Student / Member**
**Primary Goal**: View schedule, manage membership, attend classes

| Feature | Access | Priority |
|---------|--------|----------|
| View My Classes | ✅ Read | P0 |
| View Payment Status | ✅ Read | P0 |
| Self-Enroll in Classes | ✅ Join available class | P1 |
| View Attendance History | ✅ Read own | P1 |
| View Invoice History | ✅ Read own | P0 |
| Make Payment (Stripe) | ✅ Update subscription | P0 |

---

## 🎯 Core Workflows

### Workflow 1: **Admin Dashboard (Primary Use Case)**

```
Admin logs in
    ↓
[DASHBOARD LANDING]
    ├─ Baseline Metrics (top)
    │   ├─ Active Students count
    │   ├─ Accounts Receivable (overdue + current month)
    │   └─ Sales this month
    │
    ├─ Sales Chart (middle)
    │   └─ Column graph: sales by month (fiscal year)
    │
    ├─ Action Items (bottom)
    │   ├─ List of students with pending payments
    │   ├─ CTA button: "Send Payment Reminder"
    │   └─ List of instructors with invoiced hours
    │
    ├─ Navigation to sub-sections
    │   ├─ Students (manage)
    │   ├─ Classes (schedule)
    │   ├─ Payments (reconcile)
    │   └─ Reports (analyze)
```

---

### Workflow 2: **Instructor Marking Attendance**

```
Instructor logs in
    ↓
[INSTRUCTOR DASHBOARD]
    ├─ "My Classes Today" widget
    │   └─ Shows upcoming class + "Mark Attendance" button
    │
    ├─ Click "Mark Attendance"
    │   ↓
    ├─ [ATTENDANCE MARKING PAGE]
    │   ├─ Class name, time, date
    │   ├─ List of enrolled students with checkboxes
    │   ├─ Toggle: Present ☑️ / Absent ☐
    │   └─ "Save Attendance" button
    │
    ├─ Attendance saved
    │   └─ Instructor can view past attendance records
```

---

### Workflow 3: **Student Self-Enrollment**

```
Student logs in
    ↓
[STUDENT DASHBOARD]
    ├─ "My Classes" (already enrolled)
    ├─ "Available Classes" section
    │   ├─ Browse classes by sport/time
    │   ├─ Show capacity (e.g., "8/10 spots filled")
    │   └─ "Enroll" button
    │
    ├─ Click "Enroll"
    │   ↓
    ├─ Check current membership
    │   ├─ If membership covers it → Auto-enroll ✅
    │   ├─ If need to pay → Redirect to payment
    │
    ├─ After payment
    │   └─ Student enrolled in class
    │
    ├─ View Payment Status
    │   ├─ Membership: "Active until 2026-05-31"
    │   ├─ Classes included: "Unlimited"
    │   └─ Payment history
```

---

### Workflow 4: **Receptionist Enrolling a Student**

```
Receptionist in lobby
    ↓
[RECEPTIONIST DASHBOARD]
    ├─ "New Enrollment" form
    │   ├─ Student name, email, phone, DOB
    │   ├─ Select sport/classes to enroll
    │   ├─ Select payment method
    │   │   ├─ Stripe (student pays online)
    │   │   ├─ Cash (record manually)
    │   │   └─ Check (record manually)
    │   └─ "Create Account & Enroll" button
    │
    ├─ Student account created
    │   └─ Email sent with login credentials
    │
    ├─ Payment processed
    │   ├─ If online: Stripe checkout link sent
    │   ├─ If cash/check: Amount recorded, marked pending
    │   └─ Student enrolled in selected classes
```

---

## 💾 Database Schema (High Level)

```sql
-- Users (admin, instructor, receptionist, student roles)
users
├─ id (PK)
├─ email (unique)
├─ password_hash
├─ full_name
├─ role (enum: admin, instructor, receptionist, student)
├─ created_at
└─ is_active

-- Students (extends users, student-specific data)
students
├─ id (FK → users.id)
├─ phone
├─ date_of_birth
├─ emergency_contact_name
├─ emergency_contact_phone
├─ created_at

-- Classes (course offerings)
classes
├─ id (PK)
├─ name (e.g., "Karate Level 1")
├─ sport_type (e.g., "karate", "pilates")
├─ instructor_id (FK → users.id)
├─ capacity (max students)
├─ day_of_week (Monday, Tuesday, etc.)
├─ start_time
├─ end_time
├─ recurring (boolean)
└─ is_active

-- Class Sessions (individual class occurrences)
class_sessions
├─ id (PK)
├─ class_id (FK → classes.id)
├─ session_date
├─ session_time
└─ is_canceled

-- Enrollments (student ↔ class relationship)
enrollments
├─ id (PK)
├─ student_id (FK → students.id)
├─ class_id (FK → classes.id)
├─ enrolled_at
├─ status (active, paused, canceled)
└─ canceled_at

-- Attendance (per session, per student)
attendance
├─ id (PK)
├─ student_id (FK → students.id)
├─ class_session_id (FK → class_sessions.id)
├─ marked_by (instructor_id, FK → users.id)
├─ status (present, absent, excused)
├─ notes (optional)
└─ marked_at

-- Memberships (subscription plans)
memberships
├─ id (PK)
├─ name (e.g., "Monthly Unlimited")
├─ description
├─ price_monthly
├─ class_limit (null = unlimited)
├─ duration_months
├─ stripe_price_id
└─ is_active

-- Subscriptions (student subscription to membership)
subscriptions
├─ id (PK)
├─ student_id (FK → students.id)
├─ membership_id (FK → memberships.id)
├─ stripe_subscription_id
├─ status (active, paused, canceled)
├─ started_at
├─ current_period_end
└─ canceled_at

-- Payments (invoices, transactions)
payments
├─ id (PK)
├─ student_id (FK → students.id)
├─ subscription_id (FK → subscriptions.id, nullable)
├─ amount_cents
├─ currency (USD, MXN)
├─ status (pending, paid, failed, refunded)
├─ payment_method (stripe, cash, check)
├─ stripe_payment_intent_id (nullable)
├─ invoice_number
├─ due_date
├─ paid_at
├─ created_at
└─ updated_at
```

---

## 🔌 API Endpoints (Required for MVP)

### Authentication
```
POST   /api/auth/register       (student self-register)
POST   /api/auth/login          (all roles)
POST   /api/auth/logout         (all roles)
POST   /api/auth/refresh-token  (all roles)
GET    /api/auth/me             (current user)
```

### Students (Admin + Receptionist)
```
GET    /api/students            (list all)
GET    /api/students/:id        (detail)
POST   /api/students            (create new student)
PUT    /api/students/:id        (update student)
DELETE /api/students/:id        (soft delete)
GET    /api/students/:id/payments (payment history)
```

### Classes (Admin + Instructor)
```
GET    /api/classes             (list all)
GET    /api/classes/:id         (detail)
POST   /api/classes             (create)
PUT    /api/classes/:id         (update)
DELETE /api/classes/:id         (delete)
GET    /api/classes/:id/sessions (upcoming/past sessions)
```

### Enrollments (Admin + Receptionist + Student)
```
GET    /api/enrollments         (list my enrollments)
POST   /api/enrollments         (student self-enroll)
DELETE /api/enrollments/:id     (unenroll)
```

### Attendance (Instructor)
```
GET    /api/attendance/class-session/:id (get attendance for class)
POST   /api/attendance          (mark attendance)
PUT    /api/attendance/:id      (update attendance)
GET    /api/attendance/student/:id (student's attendance history)
```

### Payments (Admin + Receptionist + Student)
```
GET    /api/payments            (admin: all payments, student: own)
GET    /api/payments/:id        (detail)
POST   /api/payments            (receptionist: manual payment record)
GET    /api/memberships         (list all plans)
POST   /api/payments/checkout   (create Stripe checkout session)
POST   /api/payments/webhook    (Stripe webhook handler)
```

### Dashboard / Reports (Admin)
```
GET    /api/dashboard/summary   (KPIs: active students, revenue, etc.)
GET    /api/reports/sales       (monthly sales chart data)
GET    /api/reports/pending-payments (students with overdue invoices)
GET    /api/reports/attendance  (attendance metrics)
```

---

## 📊 Dashboard Layouts

### Admin Dashboard
```
┌─────────────────────────────────────────┐
│ TOP METRICS ROW                         │
├──────────────┬──────────────┬───────────┤
│ Active       │ Accounts     │ Sales     │
│ Students: 42 │ Receivable:  │ This Mon: │
│              │ $2,340       │ $1,200    │
└──────────────┴──────────────┴───────────┘

┌─────────────────────────────────────────┐
│ SALES CHART (by month, fiscal year)     │
│                                         │
│ [Bar Chart: Sales Trend]                │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PENDING PAYMENTS (Action Items)         │
├─────────────────────────────────────────┤
│ ☐ John Doe - $50.00 (30 days overdue)  │
│   [Send Reminder] [Mark Paid]           │
│                                         │
│ ☐ Jane Smith - $100.00 (7 days)        │
│   [Send Reminder] [Mark Paid]           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ STAFF HOURS (Invoiced)                  │
├─────────────────────────────────────────┤
│ Maria (Instructor) - 20 hours this month│
│ Luis (Instructor) - 18 hours            │
│ Ana (Receptionist) - 40 hours           │
└─────────────────────────────────────────┘
```

### Instructor Dashboard
```
┌──────────────────────────────┐
│ MY CLASSES TODAY             │
├──────────────────────────────┤
│ Karate Level 1 - 6:00 PM    │
│ [Mark Attendance] [Details]  │
│                              │
│ Karate Advanced - 7:30 PM   │
│ [Mark Attendance] [Details]  │
└──────────────────────────────┘

[Quick Links]
├─ View Attendance History
├─ View Student Roster
└─ Request Schedule Change
```

### Student Dashboard
```
┌──────────────────────────────┐
│ MY CLASSES                   │
├──────────────────────────────┤
│ Karate Level 1               │
│ Mon/Wed/Fri @ 6:00 PM       │
│ [View Details]               │
└──────────────────────────────┘

┌──────────────────────────────┐
│ AVAILABLE CLASSES            │
├──────────────────────────────┤
│ Pilates - 8:00 AM           │
│ 7/10 spots filled            │
│ [Enroll Now]                 │
└──────────────────────────────┘

┌──────────────────────────────┐
│ MY MEMBERSHIP                │
├──────────────────────────────┤
│ Plan: Monthly Unlimited      │
│ Active until: 2026-05-31     │
│ Classes: Unlimited           │
│ [Manage Subscription]        │
└──────────────────────────────┘
```

---

## 🎬 MVP Scope (Phase 2-6)

### ✅ Included in MVP

- **Phase 2**: Login/Register + Auth pages
- **Phase 3**: All three dashboards (Admin, Instructor, Student)
- **Phase 4**: Backend API + Database
  - Students CRUD
  - Classes CRUD
  - Enrollments (students can enroll/unenroll)
  - Attendance marking (instructor-only)
  - Basic user roles/permissions
- **Phase 5**: Feature pages wired to backend
  - Students management page
  - Classes/schedule page
  - Attendance marking interface
- **Phase 6**: Stripe integration
  - Membership plans
  - Stripe checkout
  - Payment recording
  - Webhook handling

### ⏱️ Phase 2+ (Not in Initial MVP)

- Receptionist payment recording (manual cash/check)
- Student notes by instructor
- Schedule change requests
- Email notifications / reminders
- Multi-location support
- Wait-lists
- Membership pause feature
- Advanced reporting / analytics
- Mobile app

---

## 🔑 Key Implementation Details

### Authentication Flow
1. User registers with email + password
2. JWT token issued (access + refresh)
3. Refresh token stored in httpOnly cookie (secure)
4. Access token valid for 15 minutes
5. Auto-refresh on page load if near expiry

### Payment Flow (Stripe)
1. Admin creates membership plans in Stripe (price, interval)
2. Student subscribes to plan → Stripe checkout session
3. Stripe confirms payment → sends webhook
4. System updates subscription status
5. Student can manage via Stripe Customer Portal

### Attendance Flow
1. Class session occurs (scheduled in advance)
2. Before/after class: Instructor opens attendance marking
3. Instructor checks off present students
4. System records attendance record
5. Attendance counts toward membership/class limits

---

## 📈 Data Requirements

### Admin needs to know:
- Total active students (count)
- Revenue this month (sum of payments)
- Accounts receivable - overdue (unpaid invoices > 30 days)
- Accounts receivable - current (unpaid invoices < 30 days)
- Sales by month (for fiscal year chart)
- List of pending payment students (with amounts, days overdue)
- Instructor hours (for payroll/invoicing)

### Instructor needs to know:
- Their assigned classes (all upcoming)
- Student roster per class
- Attendance they've marked (historical)

### Student needs to know:
- Classes they're enrolled in
- When each class meets
- Current payment status
- Invoices (due date, amount)

---

## 🚀 Next Steps

1. **Phase 2**: Build auth pages (login, register) using this core spec
2. **Phase 3**: Build dashboard shells matching these layouts
3. **Phase 4**: Build FastAPI backend with database schema above
4. **Phase 5**: Wire dashboards to real API
5. **Phase 6**: Stripe integration

This document is our single source of truth for what we're building.
