import json
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from urllib.request import Request, urlopen
from flask import current_app

def _local_log(subject, body, recipient):
    os.makedirs(current_app.config["REPORT_FOLDER"], exist_ok=True)
    path=os.path.join(current_app.config["REPORT_FOLDER"], "notification-fallback.log")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"[{datetime.now().isoformat()}] TO={recipient} SUBJECT={subject}\n{body}\n\n")
    return "LOCAL_LOG"

def send_email(subject, body, recipient, html=False):
    """Send SMTP mail when configured; otherwise preserve it in a local audit log."""
    if not current_app.config.get("SMTP_HOST") or not recipient:
        return _local_log(subject, body, recipient or "not-configured")
    message=EmailMessage(); message["Subject"]=subject; message["From"]=current_app.config.get("SMTP_FROM","placement@localhost"); message["To"]=recipient
    if html: message.set_content("Open this report in an HTML-capable mail client."); message.add_alternative(body, subtype="html")
    else: message.set_content(body)
    try:
        with smtplib.SMTP(current_app.config["SMTP_HOST"], current_app.config.get("SMTP_PORT",587), timeout=10) as smtp:
            smtp.starttls()
            if current_app.config.get("SMTP_USERNAME"): smtp.login(current_app.config["SMTP_USERNAME"], current_app.config.get("SMTP_PASSWORD",""))
            smtp.send_message(message)
        return "EMAIL"
    except Exception:
        return _local_log(subject, body, recipient)

def send_chat(message):
    url=current_app.config.get("GOOGLE_CHAT_WEBHOOK_URL","")
    if not url: return "SKIPPED"
    try:
        request=Request(url,data=json.dumps({"text":message}).encode(),headers={"Content-Type":"application/json"},method="POST")
        with urlopen(request,timeout=10): pass
        return "GOOGLE_CHAT"
    except Exception:
        _local_log("Google Chat fallback",message,"webhook")
        return "LOCAL_LOG"
