from io import BytesIO
from datetime import datetime, timedelta, timezone

from conftest import company, login, student
from test_workflows import setup_drive


def test_blacklisted_session_is_rejected(client):
    student(client)
    login(client, "stu", "secret1")
    client.post("/api/auth/logout")
    login(client, "admin", "Admin123")
    sid = client.get("/api/admin/students").get_json()["data"]["items"][0]["student_id"]
    client.patch(f"/api/admin/students/{sid}/blacklist")
    client.post("/api/auth/logout")
    assert login(client, "stu", "secret1").status_code == 403


def test_drive_close_transition(client):
    did = setup_drive(client)
    assert client.patch(f"/api/admin/drives/{did}/close").status_code == 200
    assert client.patch(f"/api/admin/drives/{did}/approve").status_code == 409


def test_fake_pdf_resume_rejected(client):
    student(client)
    login(client, "stu", "secret1")
    response = client.post("/api/student/profile/resume", data={
        "resume": (BytesIO(b"not a pdf"), "resume.pdf")
    }, content_type="multipart/form-data")
    assert response.status_code == 422


def test_company_registration_password_policy(client):
    response = client.post("/api/auth/register/company", json={
        "username": "shortco", "email": "short@example.com", "password": "123",
        "company_name": "Short Co", "hr_name": "HR", "hr_email": "hr@example.com"
    })
    assert response.status_code == 400
