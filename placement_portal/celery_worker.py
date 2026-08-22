from celery import Celery
from celery.schedules import crontab
from app import create_app
from app.tasks import daily_deadline_reminder, generate_export, monthly_report

flask_app=create_app()
celery_app=Celery(flask_app.import_name)
celery_app.conf.update(flask_app.config["CELERY"])
celery_app.conf.beat_schedule={
    "daily-reminders":{"task":"tasks.daily_deadline_reminder","schedule":crontab(hour=flask_app.config["DAILY_REMINDER_HOUR"],minute=0)},
    "monthly-report":{"task":"tasks.monthly_report","schedule":crontab(day_of_month=1,hour=flask_app.config["MONTHLY_REPORT_HOUR"],minute=0)},
}
@celery_app.task(name="tasks.daily_deadline_reminder")
def reminders_task():
    with flask_app.app_context(): return daily_deadline_reminder()
@celery_app.task(name="tasks.monthly_report")
def report_task():
    with flask_app.app_context(): return monthly_report()
@celery_app.task(name="tasks.export_applications")
def export_task(job_id):
    with flask_app.app_context(): return generate_export(job_id)
