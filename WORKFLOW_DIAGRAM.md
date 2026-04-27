# SportAcademia - Core Workflow Diagram

## 🔄 High-Level User Journeys

### Journey 1: **New Student Signs Up Online**

```
┌─────────────────────────────────────────────────────────┐
│ LANDING PAGE (index.html)                               │
│ • See features, pricing, sports types                   │
│ • Click "Get Started" or "Pricing" section              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ REGISTER PAGE (register.html)                           │
│ • Enter: name, email, password                          │
│ • Select sport/classes of interest                      │
│ • Accept terms                                          │
│ [Create Account button]                                 │
└────────────────┬────────────────────────────────────────┘
                 │ ✅ Account created, JWT token issued
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STUDENT DASHBOARD                                       │
│ • "My Classes" (currently empty)                        │
│ • "Available Classes" section                           │
│ • "My Membership" card                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Student browses classes, clicks "Enroll" on Karate     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STRIPE CHECKOUT (Stripe-hosted)                         │
│ • Select membership plan                                │
│ • Enter card details                                    │
│ • Confirm payment                                       │
└────────────────┬────────────────────────────────────────┘
                 │ ✅ Stripe webhook → System records subscription
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STUDENT DASHBOARD (Updated)                             │
│ • "My Classes": Karate Level 1 (Mon/Wed/Fri 6pm)       │
│ • "My Membership": Active until [date]                  │
│ • Ready to attend first class!                          │
└─────────────────────────────────────────────────────────┘
```

---

### Journey 2: **Receptionist Enrolls a Walk-In Student**

```
┌─────────────────────────────────────────────────────────┐
│ RECEPTIONIST DASHBOARD                                  │
│ • Welcome [Receptionist Name]                           │
│ • [New Enrollment] button                               │
└────────────────┬────────────────────────────────────────┘
                 │ Click "New Enrollment"
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ENROLLMENT FORM                                         │
│ ✓ Student Info:                                         │
│   - Full Name: [Maria Garcia]                           │
│   - Email: [maria@email.com]                            │
│   - Phone: [555-1234]                                   │
│   - DOB: [1995-03-15]                                   │
│                                                         │
│ ✓ Classes:                                              │
│   ☑ Karate Level 1 (Mon/Wed/Fri 6pm)                   │
│   ☐ Karate Advanced                                     │
│                                                         │
│ ✓ Payment:                                              │
│   ○ Pay Now (Stripe link)                               │
│   ○ Cash (record manually)                              │
│   ○ Check (record manually)                             │
│                                                         │
│ [Create Account & Enroll] button                        │
└────────────────┬────────────────────────────────────────┘
                 │ Receptionist selects "Pay Now"
                 ▼
┌─────────────────────────────────────────────────────────┐
│ • Account created for Maria                             │
│ • Stripe payment link generated                         │
│ • SMS/Email sent to Maria: "Click to pay"              │
│ • Admin notified of pending payment                     │
└────────────────┬────────────────────────────────────────┘
                 │ Maria receives SMS, clicks link
                 ▼
┌─────────────────────────────────────────────────────────┐
│ STRIPE CHECKOUT (on Maria's phone)                      │
│ • Payment processed ✅                                  │
└────────────────┬────────────────────────────────────────┘
                 │ Stripe webhook → System updates
                 ▼
┌─────────────────────────────────────────────────────────┐
│ • Maria's account marked PAID                           │
│ • Maria enrolled in Karate Level 1                      │
│ • Confirmation email sent                               │
│ • Admin dashboard updated (payment recorded)            │
└─────────────────────────────────────────────────────────┘
```

---

### Journey 3: **Instructor Marks Attendance**

```
┌─────────────────────────────────────────────────────────┐
│ INSTRUCTOR LOGS IN                                      │
│ • Email: maria.teacher@academy.com                      │
│ • Password: [••••••••]                                  │
│ [Login button]                                          │
└────────────────┬────────────────────────────────────────┘
                 │ ✅ JWT token issued
                 ▼
┌─────────────────────────────────────────────────────────┐
│ INSTRUCTOR DASHBOARD                                    │
│ ┌────────────────────────────────────────────────────┐  │
│ │ TODAY'S CLASSES                                    │  │
│ │                                                    │  │
│ │ Karate Level 1 @ 6:00 PM                          │  │
│ │ [Mark Attendance] [View Details]                  │  │
│ │                                                    │  │
│ │ Karate Advanced @ 7:30 PM                         │  │
│ │ [Mark Attendance] [View Details]                  │  │
│ └────────────────────────────────────────────────────┘  │
│                                                         │
│ [View All Classes] [View Attendance History]           │
└────────────────┬────────────────────────────────────────┘
                 │ 5:55 PM: Class is about to start
                 │ Instructor clicks "Mark Attendance"
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ATTENDANCE MARKING SHEET                                │
│ ┌────────────────────────────────────────────────────┐  │
│ │ Karate Level 1 - Monday, April 27, 6:00 PM        │  │
│ │ Capacity: 12 students                              │  │
│ │                                                    │  │
│ │ ☑ John Smith          [Present]                   │  │
│ │ ☑ Maria Garcia        [Present]                   │  │
│ │ ☐ Ahmed Hassan        [Absent]                    │  │
│ │ ☑ Sarah Chen          [Present]                   │  │
│ │ ☑ Luis Rodriguez      [Present]                   │  │
│ │ ☑ (empty slot)                                    │  │
│ │                                                    │  │
│ │ Attendance: 4/5 present (80%)                      │  │
│ │                                                    │  │
│ │ [Save Attendance]  [Cancel]                       │  │
│ └────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────┘
                 │ Instructor clicks "Save"
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ✅ Attendance recorded!                                 │
│                                                         │
│ • Database updated                                      │
│ • Admin can see this in reports                         │
│ • Student can see in their history                      │
│                                                         │
│ [View More Classes] [Back to Dashboard]                │
└─────────────────────────────────────────────────────────┘
```

---

### Journey 4: **Admin Reviews Dashboard & Sends Reminder**

```
┌─────────────────────────────────────────────────────────┐
│ ADMIN LOGS IN                                           │
│ • Email: admin@academy.com                              │
│ • Password: [••••••••]                                  │
│ [Login button]                                          │
└────────────────┬────────────────────────────────────────┘
                 │ ✅ JWT token issued, Admin permissions loaded
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ADMIN DASHBOARD (Landing)                               │
│                                                         │
│ ╔═══════════════╦═══════════════╦════════════════╗     │
│ ║ ACTIVE        ║ ACCOUNTS      ║ SALES THIS     ║     │
│ ║ STUDENTS: 42  ║ RECEIVABLE:   ║ MONTH: $1,200  ║     │
│ ║               ║ $2,340        ║                ║     │
│ ╚═══════════════╩═══════════════╩════════════════╝     │
│                                                         │
│ ┌────────────────────────────────────────────────────┐  │
│ │ SALES BY MONTH (Fiscal Year)                       │  │
│ │                                                    │  │
│ │ 2000 ┤     ┌─┐                                      │  │
│ │ 1500 ┤     │ │                                      │  │
│ │ 1000 ┤ ┌─┐ │ │ ┌─┐                                 │  │
│ │  500 ┤ │ │ │ │ │ │ ┌─┐ ┌─┐                        │  │
│ │    0 ┼─┴─┴─┴─┴─┴─┴─┴─┴─┴─ Jan Feb Mar Apr May    │  │
│ └────────────────────────────────────────────────────┘  │
│                                                         │
│ ┌────────────────────────────────────────────────────┐  │
│ │ STUDENTS WITH PENDING PAYMENTS (Action Needed)    │  │
│ │                                                    │  │
│ │ ☐ John Doe       $50.00    30 days overdue       │  │
│ │   [Send Reminder]  [Mark Paid]  [Email]          │  │
│ │                                                    │  │
│ │ ☐ Jane Smith     $100.00   7 days overdue        │  │
│ │   [Send Reminder]  [Mark Paid]  [Email]          │  │
│ │                                                    │  │
│ │ ☐ Ahmed Hassan   $75.00    Today due             │  │
│ │   [Send Reminder]  [Mark Paid]  [Email]          │  │
│ └────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────┘
                 │ Admin clicks [Send Reminder] for John
                 ▼
┌─────────────────────────────────────────────────────────┐
│ ✅ REMINDER SENT!                                       │
│                                                         │
│ John Doe:                                               │
│ • Email sent: "Your payment is 30 days overdue..."     │
│ • SMS sent: "Pay now: [link]"                          │
│                                                         │
│ [View All Reminders] [Back to Dashboard]               │
└─────────────────────────────────────────────────────────┘
```

---

## 📱 Page Structure

### Frontend Pages (to be built)

```
/
├── index.html                 ← Landing page (marketing)
├── register.html              ← Sign up
├── login.html                 ← Log in
├── dashboard.html             ← Role-specific dashboard
│                              (admin, instructor, student)
├── students/
│   ├── index.html             ← Student list (admin only)
│   └── [id].html              ← Student detail/edit
├── classes/
│   ├── index.html             ← Class list & schedule
│   └── [id].html              ← Class details
├── attendance/
│   └── [class-id].html        ← Mark attendance (instructor)
├── payments/
│   ├── index.html             ← Payment history (admin)
│   └── checkout.html          ← Stripe checkout redirect
└── 404.html                   ← Page not found
```

---

## 🔐 Authentication & Authorization Flow

```
User visits /login.html
    ↓
Enters email + password
    ↓
POST /api/auth/login
    ↓
Backend validates credentials
    ↓
    ├─ Valid: Issue JWT tokens (access + refresh)
    │          Return user role (admin/instructor/student)
    │
    └─ Invalid: Return error 401
                 Show error message
    ↓
Frontend stores tokens:
├─ Access token → localStorage
├─ Refresh token → httpOnly cookie (secure)
├─ User role → localStorage
    ↓
On page load:
├─ Check if token exists
├─ If yes: Redirect to role-specific dashboard
├─ If no: Redirect to login
├─ If expired: Auto-refresh using refresh token
    ↓
API requests:
├─ Include Access token in header
├─ If 401 response: Refresh token automatically
├─ If still invalid: Redirect to login
```

---

## 💾 Data Flow: New Enrollment → Payment → Confirmation

```
┌─────────────────┐
│ RECEPTIONIST    │
│ Creates Student │
└────────┬────────┘
         │ POST /api/students
         ├─ name, email, phone, dob
         ├─ class_id (to enroll)
         │ 
         ▼
┌─────────────────────────────┐
│ BACKEND                     │
│ 1. Create user account      │
│ 2. Create student record    │
│ 3. Create enrollment record │
│ 4. Return with payment link │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Receptionist views          │
│ "Payment link sent to       │
│ john@email.com"             │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ CUSTOMER (Email/SMS)        │
│ "Complete your enrollment:  │
│ [stripe-checkout-link]"     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ STRIPE CHECKOUT             │
│ (Customer fills card info)  │
└────────┬────────────────────┘
         │ Payment processed
         │
         ▼
┌─────────────────────────────┐
│ STRIPE WEBHOOK              │
│ POST /api/payments/webhook  │
│ event: invoice.paid         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ BACKEND                     │
│ 1. Record subscription      │
│ 2. Update student status    │
│ 3. Mark enrollment: active  │
│ 4. Send confirmation email  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ ADMIN DASHBOARD             │
│ • Payment appears in list   │
│ • Revenue updated           │
│ • Student marked PAID       │
└─────────────────────────────┘
```

---

## 🎯 Key Decision Points

### For Admin
- Q: "How many students owe money?"
- A: Dashboard shows "Pending Payments" list

### For Instructor  
- Q: "Did everyone show up to class?"
- A: Attendance marking page shows presence/absence

### For Student
- Q: "Can I afford another class?"
- A: Student dashboard shows "Classes Available" + membership status

### For Receptionist
- Q: "Is this student paid up?"
- A: Enrollment form shows payment status when creating account

---

This diagram is your **visual roadmap** for Phase 2-6 development.
