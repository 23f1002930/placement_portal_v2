import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

def env_path(name, default):
    """Treat an unset or blank optional path as its project-local default."""
    return os.getenv(name, "").strip() or str(default)

def database_url():
    value=os.getenv("DATABASE_URL", "").strip()
    if not value:
        return f"sqlite:///{(BASE_DIR / 'instance' / 'placement_portal.db').as_posix()}"
    prefix="sqlite:///"
    if value.startswith(prefix):
        location=value[len(prefix):]
        if location and not Path(location).is_absolute():
            return prefix+(BASE_DIR / location).resolve().as_posix()
    if not value.startswith("sqlite:///"):
        raise RuntimeError("Placement Portal V2 supports SQLite only")
    return value

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = env_path("UPLOAD_FOLDER", BASE_DIR / "uploads")
    EXPORT_FOLDER = env_path("EXPORT_FOLDER", BASE_DIR / "exports")
    REPORT_FOLDER = env_path("REPORT_FOLDER", BASE_DIR / "reports")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "60"))
    DAILY_REMINDER_HOUR = int(os.getenv("DAILY_REMINDER_HOUR", "9"))
    MONTHLY_REPORT_HOUR = int(os.getenv("MONTHLY_REPORT_HOUR", "8"))
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM = os.getenv("SMTP_FROM", "placement@localhost")
    GOOGLE_CHAT_WEBHOOK_URL = os.getenv("GOOGLE_CHAT_WEBHOOK_URL", "")
    CELERY = {"broker_url": REDIS_URL, "result_backend": REDIS_URL}
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
