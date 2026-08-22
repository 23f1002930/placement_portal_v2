# Final Requirements Audit

This matrix records the verified implementation after the V2 compliance pass. `PASS` means implemented and covered by automated or direct inspection; `ENV` means the integration is complete but requires the named external service at runtime.

| Requirement | Implementation | File | Status | Test | Notes |
|---|---|---|---|---|---|
| SQLite and programmatic initialization | SQLAlchemy SQLite schema and idempotent initializer | `config.py`, `scripts/init_db.py` | PASS | clean DB/startup | No manual DB steps |
| Role authentication and no admin registration | Hashed passwords, session RBAC, programmatic admin | `app/api.py` | PASS | `test_auth.py` | Admin registration endpoint does not exist |
| Inactive/blacklisted enforcement | Checked on every protected request and login | `app/api.py` | PASS | `test_compliance.py` | Backend enforcement |
| Admin management | Search/page, approve/reject, blacklist, deactivate/reactivate, close | `app/api.py` | PASS | `test_admin.py`, `test_compliance.py` | Valid state transitions |
| Company approval gate and ownership | Approval required for drive creation; queries derive company from session | `app/api.py` | PASS | `test_company.py` | IDOR protected |
| Drive workflow and eligibility | Pending/approved/rejected/closed and server-side eligibility/deadline rules | `app/api.py` | PASS | `test_drives.py`, `test_workflows.py` | 409/422 business errors |
| Duplicate applications | Validation plus unique `(student_id, drive_id)` constraint | `app/models.py`, `app/api.py` | PASS | `test_applications.py` | Database-enforced |
| Application transitions | Applied to shortlisted/rejected/selected with ownership checks | `app/api.py` | PASS | `test_applications.py` | Invalid transitions rejected |
| Interview scheduling | Date, mode, location/link, notes, status and result | `app/models.py`, `app/api.py` | PASS | `test_workflows.py` | Visible in application JSON |
| Placement history | All historical database applications and interview data | `app/api.py` | PASS | `test_workflows.py` | Paginated |
| Secure resumes | PDF extension/signature/size, secure name, replacement and owner download | `app/api.py`, `config.py` | PASS | `test_student.py`, `test_compliance.py` | 5 MB request limit |
| Search and pagination | Major role lists use server-side search and capped pagination | `app/api.py` | PASS | endpoint tests | Metadata includes page, per-page, total and pages |
| Redis caching | TTL cache, graceful fallback and mutation invalidation | `app/cache.py`, `app/api.py` | PASS | inspection | Login and DB workflows do not depend on Redis |
| Celery worker and Beat | Redis broker/backend and registered periodic/export tasks | `celery_worker.py` | PASS/ENV | `test_tasks.py` | Live execution requires Redis |
| Daily deadline reminder | Eligible, active, non-applicant selection; notification/email/chat fallback | `app/tasks.py` | PASS/ENV | task inspection | Scheduled daily, default 09:00 |
| Monthly HTML report | Previous month metrics, HTML file, SMTP/local fallback | `app/tasks.py` | PASS/ENV | `test_tasks.py` | Scheduled first day, default 08:00 |
| Google Chat and SMTP | Environment-only secrets with safe local logging | `app/notifications.py` | PASS/ENV | task tests | External delivery needs configuration |
| Asynchronous CSV | Celery job, persisted status, notification and owner-bound download | `app/api.py`, `app/tasks.py` | PASS/ENV | `test_workflows.py` | Safe local fallback when Redis is down |
| Offer-letter PDF | Genuine PDF, selected-only, company ownership | `app/pdf_service.py`, `app/api.py` | PASS | `test_offer_letter.py` | Correct response headers |
| Audit logging | Actor, role, action, entity, time and details fields | `app/models.py`, `app/api.py` | PASS | inspection | Major mutations logged |
| Vue 3 and Bootstrap UI | Responsive role views, validation, alerts, empty/loading states | `frontend/` | PASS | browser inspection | CDN-based Vue/Bootstrap |
| Documentation | Setup, API, architecture, viva, report and ER diagram | `README.md`, `docs/` | PASS | inspection | Matches implemented endpoints |
| Automated verification | Auth/admin/company/student/security/task/PDF workflows | `tests/` | PASS | `pytest -q` | See final run in handoff |

External Redis, SMTP and Google Chat connectivity cannot be asserted without evaluator-owned services and credentials. Their integrations fail safely and never expose secrets.
