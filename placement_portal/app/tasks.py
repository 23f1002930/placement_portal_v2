import csv
import os
from datetime import datetime, timedelta, timezone
from flask import current_app
from .extensions import db
from .models import Application, ExportJob, Notification, PlacementDrive, Student, User
from .notifications import send_chat, send_email

def utc(value): return value.replace(tzinfo=timezone.utc) if value and value.tzinfo is None else value

def eligible(student, drive):
    return drive.eligible_department in ("ALL",student.department) and student.cgpa>=drive.minimum_cgpa and student.year==drive.eligible_year

def daily_deadline_reminder():
    """Notify eligible students about approved drives whose deadline is within 24 hours."""
    start=datetime.now(timezone.utc); end=start+timedelta(days=1); count=0
    drives=PlacementDrive.query.filter_by(status="APPROVED").all()
    for drive in drives:
        deadline=utc(drive.application_deadline)
        if not deadline or not start <= deadline <= end: continue
        applied={application.student_id for application in drive.applications}; drive_count=0
        for student in Student.query.join(User).filter(User.is_active.is_(True),User.is_blacklisted.is_(False)).all():
            if student.id in applied or not eligible(student,drive): continue
            message=f"Application deadline for {drive.job_title} at {drive.company.company_name} is {deadline.isoformat()}."
            db.session.add(Notification(user_id=student.user_id,title="Application deadline reminder",message=message,type="REMINDER"))
            send_email("Placement application deadline",message,student.user.email); count+=1; drive_count+=1
        if drive_count: send_chat(f"Placement reminder: {drive.job_title} application deadline is {deadline.isoformat()}.")
    db.session.commit(); return count

daily_reminders = daily_deadline_reminder

def monthly_report():
    now=datetime.now(timezone.utc); current_start=datetime(now.year,now.month,1,tzinfo=timezone.utc)
    previous_end=current_start; previous_start=datetime(previous_end.year-1,12,1,tzinfo=timezone.utc) if previous_end.month==1 else datetime(previous_end.year,previous_end.month-1,1,tzinfo=timezone.utc)
    drives=[d for d in PlacementDrive.query.all() if utc(d.drive_date) and previous_start <= utc(d.drive_date) < previous_end]
    applications=[a for a in Application.query.all() if previous_start <= utc(a.application_date) < previous_end]
    applied_students=len({a.student_id for a in applications}); selected=sum(a.status=="SELECTED" for a in applications)
    companies=len({d.company_id for d in drives}); label=previous_start.strftime("%B %Y")
    html=f"<!doctype html><html><body><h1>Placement Monthly Activity Report - {label}</h1><table><tr><th>Metric</th><th>Value</th></tr><tr><td>Drives conducted</td><td>{len(drives)}</td></tr><tr><td>Participating companies</td><td>{companies}</td></tr><tr><td>Students applied</td><td>{applied_students}</td></tr><tr><td>Students selected</td><td>{selected}</td></tr><tr><td>Total applications</td><td>{len(applications)}</td></tr></table></body></html>"
    os.makedirs(current_app.config["REPORT_FOLDER"],exist_ok=True); path=os.path.join(current_app.config["REPORT_FOLDER"],f"monthly-{previous_start:%Y-%m}.html")
    with open(path,"w",encoding="utf-8") as handle: handle.write(html)
    admin=User.query.filter_by(role="ADMIN").first(); channel=send_email(f"Monthly placement report - {label}",html,admin.email if admin else "",html=True)
    return {"path":path,"drives":len(drives),"students_applied":applied_students,"selected":selected,"delivery":channel}

def generate_export(job_id):
    job=db.session.get(ExportJob,job_id)
    if not job: return None
    job.status="PROCESSING"; db.session.commit()
    try:
        student=job.student_id
        rows=Application.query.filter_by(student_id=student).all(); os.makedirs(current_app.config["EXPORT_FOLDER"],exist_ok=True)
        name=f"applications_student_{student}_job_{job.id}.csv"; path=os.path.join(current_app.config["EXPORT_FOLDER"],name)
        with open(path,"w",newline="",encoding="utf-8") as handle:
            writer=csv.writer(handle); writer.writerow(["Student ID","Company Name","Drive Title","Application Status","Application Date","Interview Date"])
            for application in rows: writer.writerow([student,application.drive.company.company_name,application.drive.job_title,application.status,application.application_date.isoformat(),application.interview_date.isoformat() if application.interview_date else ""])
        job.status="COMPLETED"; job.file_path=path; job.completed_at=datetime.now(timezone.utc)
        db.session.add(Notification(user_id=job.student.user_id,title="Export ready",message=name,type="EXPORT")); db.session.commit(); return path
    except Exception as exc:
        job.status="FAILED"; job.error_message=str(exc); db.session.commit(); raise
