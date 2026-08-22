# Viva Guide

The objective is to replace manual placement spreadsheets with one controlled workflow. Vue renders views and calls Flask using native `fetch`. Flask validates requests, sessions and roles. SQLAlchemy maps Python classes to SQLite tables. Relationships express ownership; the application unique constraint prevents a duplicate even under concurrent requests.

Authentication proves identity with Werkzeug password hashes and a server-signed session cookie. Authorization checks ADMIN, COMPANY or STUDENT on every protected route. Companies can query only drives tied to their profile; students can query only their own records.

Eligibility compares department (`ALL` or exact), minimum CGPA, and academic year on the server. Only approved drives before their deadline accept applications. The lifecycle is APPLIED → SHORTLISTED → SELECTED/REJECTED, with APPLIED also allowed to become REJECTED.

Redis is Celery's broker/result backend. Celery Beat runs deadline reminders daily at 9:00 AM and the monthly report on day one at 8:00 AM. Reminder delivery supports SMTP and Google Chat, with a local log fallback. CSV export writes student ID, company, drive, status, application date, and interview date in a user-triggered Celery job. Monthly reporting aggregates drives, applicants, and selections into HTML and emails the admin. If Redis, SMTP or a webhook is absent, interactive placement work still runs and delivery is preserved locally.

Security controls include hashed passwords, safe filenames, PDF-only 5 MB uploads, HttpOnly/SameSite cookies, ownership checks, parameterized ORM queries, environment-based secrets, and generic error responses. API failures use meaningful 400/401/403/404/409 codes. The cache TTL is configured with `CACHE_TTL`; a production extension can cache read-only dashboard results and invalidate them after mutations.

Files to explain: `app/models.py`, `app/api.py`, `app/tasks.py`, `app/__init__.py`, and `frontend/app.js`.
