# Placement Portal Application V2

A local, role-based campus recruitment system for one administrator, companies, and students. Flask exposes a session-authenticated REST API; Vue 3 and Bootstrap provide the browser UI; SQLAlchemy stores data in SQLite; Celery and Redis support scheduled work.

## Features

- Student/company registration and one programmatically-created admin
- Company and drive approval, rejection and blacklist controls
- Server-side eligibility, deadlines, ownership checks and application status transitions
- Unique database constraint preventing duplicate applications
- Resume upload, notifications, CSV export and HTML monthly reports
- Professional PDF offer-letter generation for selected students
- Pagination and search on major listings; activity audit log
- Optional Celery/Redis operation: the main application remains usable without either service

## Quick start (Windows PowerShell)

```powershell
cd submission\placement_portal
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\init_db.py
python run.py
```

Open `http://127.0.0.1:5000`. Development admin: `admin` / `Admin@123`. Change these using `ADMIN_USERNAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` before initialization.

For background jobs, start Redis locally, then run:

```powershell
celery -A celery_worker.celery_app worker --pool=solo --loglevel=info
celery -A celery_worker.celery_app beat --loglevel=info
```

Celery Beat runs deadline reminders every day at 9:00 AM and the admin activity report on the first day of each month at 8:00 AM. Keep both the worker and Beat terminals open.

## Email and Google Chat setup

Copy `.env.example` to `.env`. For Gmail SMTP, enable two-factor authentication and create an App Password, then configure:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-account@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_FROM=your-account@gmail.com
```

For Google Chat, create a webhook in the target Space under **Apps & integrations → Webhooks** and set:

```env
GOOGLE_CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/...
```

Restart Flask, the Celery worker, and Celery Beat after changing `.env`. When SMTP or Chat is unavailable, messages are retained in `reports/notification-fallback.log`; the application does not crash.

Redis must be listening on `localhost:6379`. On Windows, use WSL Redis or a Redis-compatible Windows service. Confirm it with `redis-cli ping` (expected response: `PONG`). CSV export is queued through Celery when Redis is available and safely runs locally otherwise.

Run tests with `pytest -q`. Redis connectivity can be checked with `redis-cli ping`. The frontend uses Vue/Bootstrap CDNs, so first page load needs internet; downloaded local copies can replace those script/style URLs for a fully offline demo.

## Environment and folders

Copy `.env.example` to `.env` and set a strong `SECRET_KEY`. Runtime data goes to `instance/`, `uploads/`, `exports/`, and `reports/`, all ignored by Git. SQLite tables are created only by `scripts/init_db.py`; no manual SQL is needed.

## Demo sequence

Register a company → admin approves it → company creates a drive → admin approves it → register/login as student → apply → company shortlists, schedules, and selects → student checks history and exports CSV.

See [API documentation](docs/API_DOCUMENTATION.md), [architecture](docs/ARCHITECTURE.md), [viva guide](docs/VIVA_GUIDE.md), and the editable [project report](docs/PROJECT_REPORT.md).
