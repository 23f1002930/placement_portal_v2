# API Documentation

All JSON responses use `{success, message, data}` or `{success, message, errors}`. Protected calls require the Flask session cookie. List endpoints accept `page`, `per_page`, and where relevant `search`.

| Method | URL | Role | Purpose / common errors |
|---|---|---|---|
| POST | `/api/auth/login`, `/logout` | Public / signed in | Create or clear session; 401 invalid credentials |
| GET | `/api/auth/me` | Any | Current safe user record |
| POST | `/api/auth/register/student`, `/company` | Public | Create role profile; 400 duplicate/invalid input |
| GET | `/api/admin/dashboard` | Admin | Aggregate counts |
| GET | `/api/admin/students`, `/companies`, `/drives`, `/applications` | Admin | Paginated administration lists |
| PATCH | `/api/admin/companies/{id}/{approve|reject|blacklist|activate}` | Admin | Company moderation |
| PATCH | `/api/admin/students/{id}/{blacklist|activate}` | Admin | Student moderation |
| PATCH | `/api/admin/drives/{id}/{approve|reject}` | Admin | Drive moderation |
| GET | `/api/admin/reports/summary` | Admin | Placement aggregates |
| GET, PUT | `/api/company/profile` | Company | Read/update own profile |
| GET | `/api/company/dashboard` | Company | Own counts |
| GET, POST | `/api/company/drives` | Company | List/create; 403 until approved |
| GET, PUT | `/api/company/drives/{id}` | Company owner | Read/edit pending/rejected drive |
| GET | `/api/company/drives/{id}/applications` | Company owner | Paginated applicants |
| GET | `/api/company/applications/{id}` | Company owner | Applicant detail |
| PATCH | `/api/company/applications/{id}/{shortlist|reject|interview|select}` | Company owner | Validated status change; 409 invalid transition |
| POST | `/api/company/applications/{id}/offer-letter` | Company owner | Download a real PDF for a selected student; returns 401/403/404/409 as applicable |
| GET, PUT | `/api/student/profile` | Student | Read/update own profile |
| POST | `/api/student/profile/resume` | Student | Multipart field `resume`, PDF, max 5 MB |
| GET | `/api/student/profile/resume` | Student | Download the authenticated student's resume |
| GET | `/api/student/dashboard`, `/drives`, `/drives/{id}` | Student | Counts and eligible approved drives |
| POST | `/api/student/drives/{id}/apply` | Student | Apply; 403 blacklist, 409 duplicate/deadline/ineligible |
| GET | `/api/student/applications`, `/history` | Student | Own applications / selected history |
| POST | `/api/student/export` | Student | Queue CSV batch job; local fallback if Redis is unavailable |
| GET | `/api/student/exports/{name}` | Student | Download export |
| GET | `/api/student/exports/jobs/{id}` | Student | Poll an owned asynchronous export job |

Admin mutation endpoints also include `PATCH /api/admin/companies/{id}/deactivate`, `PATCH /api/admin/students/{id}/deactivate`, and `PATCH /api/admin/drives/{id}/close`. They return `409` for invalid state transitions and `403` for role violations.
| GET | `/api/notifications` | Any | Own notifications |
| PATCH | `/api/notifications/{id}/read` | Owner | Mark read |
