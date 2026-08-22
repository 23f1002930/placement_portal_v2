# Architecture

```text
Browser (Vue 3 + Bootstrap + fetch)
                 |
             Flask API
        /           |          \
SQLAlchemy/SQLite  Redis     Celery worker/beat
                              |       |
                         reminders  CSV/HTML
```

`create_app()` constructs Flask and registers the `/api` blueprint. `models.py` owns persistence, `api.py` owns request validation and authorization, and `tasks.py` contains reusable task bodies. Sessions store only user ID and role; every protected endpoint rechecks the account and role. SQLite foreign keys and the `(student_id, drive_id)` unique constraint preserve core integrity.

