from datetime import datetime, timezone
from .extensions import db

def now(): return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)
    student = db.relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    company = db.relationship("Company", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    register_number = db.Column(db.String(40), unique=True, nullable=False)
    department = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    phone = db.Column(db.String(30), default="")
    skills = db.Column(db.Text, default="")
    resume_filename = db.Column(db.String(255))
    resume_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)
    user = db.relationship("User", back_populates="student")
    applications = db.relationship("Application", back_populates="student", cascade="all, delete-orphan")

class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    hr_name = db.Column(db.String(120), nullable=False)
    hr_email = db.Column(db.String(120), nullable=False)
    hr_phone = db.Column(db.String(30), default="")
    website = db.Column(db.String(255), default="")
    description = db.Column(db.Text, default="")
    approval_status = db.Column(db.String(15), default="PENDING", nullable=False, index=True)
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)
    user = db.relationship("User", back_populates="company")
    drives = db.relationship("PlacementDrive", back_populates="company", cascade="all, delete-orphan")

class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    job_title = db.Column(db.String(150), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_criteria = db.Column(db.Text, default="")
    eligible_department = db.Column(db.String(80), default="ALL")
    minimum_cgpa = db.Column(db.Float, default=0)
    eligible_year = db.Column(db.Integer, nullable=False)
    application_deadline = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    drive_date = db.Column(db.DateTime(timezone=True), nullable=False)
    location = db.Column(db.String(180), default="")
    salary = db.Column(db.String(80), default="")
    status = db.Column(db.String(15), default="PENDING", nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)
    company = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive", cascade="all, delete-orphan")

class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),)
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False, index=True)
    application_date = db.Column(db.DateTime(timezone=True), default=now)
    status = db.Column(db.String(15), default="APPLIED", nullable=False, index=True)
    interview_date = db.Column(db.DateTime(timezone=True))
    interview_mode = db.Column(db.String(30))
    interview_location = db.Column(db.String(500))
    interview_notes = db.Column(db.Text, default="")
    interview_status = db.Column(db.String(30))
    interview_result = db.Column(db.String(80))
    remarks = db.Column(db.Text, default="")
    updated_at = db.Column(db.DateTime(timezone=True), default=now, onupdate=now)
    student = db.relationship("Student", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")

class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), default="INFO")
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now)

class ExportJob(db.Model):
    __tablename__ = "export_jobs"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    status = db.Column(db.String(15), default="QUEUED")
    file_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime(timezone=True), default=now)
    completed_at = db.Column(db.DateTime(timezone=True))
    error_message = db.Column(db.Text)
    student = db.relationship("Student")

class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    role = db.Column(db.String(10))
    details = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime(timezone=True), default=now)
