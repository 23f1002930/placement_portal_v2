# Placement Portal Application V2 — Project Report

> Replace bracketed placeholders before submission. Keep the final rendered report within five pages and add the presentation video link.

## 1. Student Details

- Name: `[Student name]`
- Roll/Register number: `[Register number]`
- Programme and department: `[Programme / Department]`
- Email: `[Institution email]`

## 2. Project and Problem Approach

The Placement Portal coordinates institute recruitment among an administrator, companies, and students. I approached the problem with a role-based Flask REST API, a responsive Vue/Bootstrap interface, and a relational SQLite schema. The workflow starts with company approval, continues through drive approval and eligibility-controlled student applications, and finishes with interview and selection tracking.

Important integrity rules are enforced on the server. A database unique constraint prevents duplicate student-drive applications. Company queries include ownership checks, student queries expose only the signed-in student's records, and admin routes require the ADMIN role. Background tasks use Celery and Redis for daily deadline reminders, monthly reports, and CSV exports.

## 3. Frameworks and Libraries

- Python, Flask and Flask-SQLAlchemy
- SQLite and SQLAlchemy
- Vue 3, Bootstrap 5 and browser `fetch`
- Redis and Celery/Celery Beat
- Werkzeug password hashing and secure filenames
- Python SMTP/email, CSV, and Google Chat webhook support

## 4. Database and API

The database contains User, Student, Company, PlacementDrive, Application, Notification, ExportJob, and ActivityLog tables. The complete ER diagram is in `docs/ER_DIAGRAM.md`. API endpoints, roles, requests, and common errors are documented in `docs/API_DOCUMENTATION.md`.

## 5. AI/LLM Declaration

AI/LLM assistance was used for architecture suggestions, implementation support, debugging, automated tests, UI refinement, and documentation drafting. I reviewed the implementation and am responsible for understanding and explaining the submitted code. Further details are recorded in `docs/AI_USAGE.md`.

Presentation video: `[Paste Google Drive presentation video link here]`
