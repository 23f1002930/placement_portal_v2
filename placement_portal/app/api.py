import os
from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, current_app, jsonify, request, session, send_file, send_from_directory
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from .extensions import db
from .models import User, Student, Company, PlacementDrive, Application, Notification, ExportJob, ActivityLog
from .cache import get_json, set_json, invalidate
from .tasks import generate_export
from .pdf_service import generate_offer_letter_pdf

api = Blueprint("api", __name__, url_prefix="/api")
ok = lambda message="OK", data=None, code=200: (jsonify(success=True, message=message, data=data or {}), code)
fail = lambda message, code=400, errors=None: (jsonify(success=False, message=message, errors=errors or {}), code)
def iso(value): return value.isoformat() if value else None
def log(action, entity=None, entity_id=None, details=""):
    db.session.add(ActivityLog(user_id=session.get("user_id"), role=session.get("role"), action=action, entity_type=entity, entity_id=entity_id, details=details))

def require_role(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapped(*a, **kw):
            if not session.get("user_id"): return fail("Authentication required", 401)
            if session.get("role") not in roles: return fail("Forbidden", 403)
            user = db.session.get(User, session["user_id"])
            if not user or not user.is_active: return fail("Account inactive", 403)
            if user.is_blacklisted: return fail("Account blacklisted", 403)
            return fn(*a, **kw)
        return wrapped
    return deco

def user_json(u): return {"id":u.id,"username":u.username,"email":u.email,"role":u.role,"is_active":u.is_active,"is_blacklisted":u.is_blacklisted}
def drive_json(d, student=None):
    reasons=[]
    if student:
        if d.eligible_department not in ("ALL", student.department): reasons.append("Department not eligible")
        if student.cgpa < d.minimum_cgpa: reasons.append("CGPA below minimum")
        if student.year != d.eligible_year: reasons.append("Year not eligible")
    return {"id":d.id,"company_id":d.company_id,"company":d.company.company_name,"job_title":d.job_title,"job_description":d.job_description,"eligibility_criteria":d.eligibility_criteria,"eligible_department":d.eligible_department,"minimum_cgpa":d.minimum_cgpa,"eligible_year":d.eligible_year,"application_deadline":iso(d.application_deadline),"drive_date":iso(d.drive_date),"location":d.location,"salary":d.salary,"status":d.status,"applicant_count":len(d.applications),"eligible":not reasons,"eligibility_reasons":reasons}
def app_json(a): return {"id":a.id,"student_id":a.student_id,"student":a.student.full_name,"register_number":a.student.register_number,"drive_id":a.drive_id,"job_title":a.drive.job_title,"company":a.drive.company.company_name,"status":a.status,"application_date":iso(a.application_date),"interview_date":iso(a.interview_date),"interview_mode":a.interview_mode,"interview_location":a.interview_location,"interview_notes":a.interview_notes,"interview_status":a.interview_status,"interview_result":a.interview_result,"remarks":a.remarks,"resume_filename":a.student.resume_filename}
def page(query, mapper):
    p=max(request.args.get("page",1,type=int),1); pp=min(max(request.args.get("per_page",10,type=int),1),100)
    result=query.paginate(page=p,per_page=pp,error_out=False)
    return {"items":[mapper(x) for x in result.items],"page":p,"per_page":pp,"total":result.total,"pages":result.pages}
def parse_dt(value):
    try: return datetime.fromisoformat(value.replace("Z","+00:00"))
    except Exception: return None

@api.post("/auth/register/student")
def register_student():
    d=request.get_json(silent=True) or {}; required=("username","email","password","full_name","register_number","department","year","cgpa")
    if any(d.get(k) in (None,"") for k in required): return fail("Required fields are missing")
    if len(d["password"])<6: return fail("Password must contain at least 6 characters")
    try:
        u=User(username=d["username"].strip(),email=d["email"].lower().strip(),password_hash=generate_password_hash(d["password"]),role="STUDENT")
        u.student=Student(full_name=d["full_name"],register_number=d["register_number"],department=d["department"],year=int(d["year"]),cgpa=float(d["cgpa"]),phone=d.get("phone",""),skills=d.get("skills","")); db.session.add(u); db.session.flush(); log("student registration","student",u.student.id); db.session.commit()
        return ok("Student registered",{"user":user_json(u)},201)
    except (IntegrityError,ValueError): db.session.rollback(); return fail("Username, email, or register number already exists")

@api.post("/auth/register/company")
def register_company():
    d=request.get_json(silent=True) or {}; required=("username","email","password","company_name","hr_name","hr_email")
    if any(not d.get(k) for k in required): return fail("Required fields are missing")
    if len(d.get("password",""))<6: return fail("Password must contain at least 6 characters")
    try:
        u=User(username=d["username"],email=d["email"].lower(),password_hash=generate_password_hash(d["password"]),role="COMPANY")
        u.company=Company(company_name=d["company_name"],hr_name=d["hr_name"],hr_email=d["hr_email"],hr_phone=d.get("hr_phone",""),website=d.get("website",""),description=d.get("description","")); db.session.add(u); db.session.flush(); log("company registration","company",u.company.id); db.session.commit(); return ok("Company registered; awaiting approval",{"user":user_json(u)},201)
    except IntegrityError: db.session.rollback(); return fail("Username or email already exists")

@api.post("/auth/login")
def login():
    d=request.get_json(silent=True) or {}; u=User.query.filter(or_(User.username==d.get("username",""),User.email==d.get("username",""))).first()
    if not u or not check_password_hash(u.password_hash,d.get("password","")): return fail("Invalid credentials",401)
    if not u.is_active: return fail("Account inactive",403)
    if u.is_blacklisted: return fail("Account blacklisted",403)
    session.clear(); session.update(user_id=u.id,role=u.role); log("login"); db.session.commit(); return ok("Login successful",{"user":user_json(u)})
@api.post("/auth/logout")
@require_role("ADMIN","COMPANY","STUDENT")
def logout(): log("logout"); db.session.commit(); session.clear(); return ok("Logged out")
@api.get("/auth/me")
@require_role("ADMIN","COMPANY","STUDENT")
def me(): return ok(data={"user":user_json(db.session.get(User,session["user_id"]))})

@api.get("/admin/dashboard")
@require_role("ADMIN")
def admin_dashboard():
    data=get_json("dashboard:admin")
    if data is None:
        data={"students":Student.query.count(),"companies":Company.query.count(),"drives":PlacementDrive.query.count(),"applications":Application.query.count(),"selected":Application.query.filter_by(status="SELECTED").count()}; set_json("dashboard:admin",data)
    return ok(data=data)
@api.get("/admin/students")
@require_role("ADMIN")
def admin_students():
    q=Student.query.join(User); s=request.args.get("search","");
    if s: q=q.filter(or_(Student.full_name.ilike(f"%{s}%"),Student.register_number.ilike(f"%{s}%"),User.email.ilike(f"%{s}%")))
    return ok(data=page(q,lambda x:{**user_json(x.user),"student_id":x.id,"full_name":x.full_name,"register_number":x.register_number,"department":x.department,"year":x.year,"cgpa":x.cgpa}))
@api.get("/admin/companies")
@require_role("ADMIN")
def admin_companies():
    q=Company.query.join(User); s=request.args.get("search","");
    if s: q=q.filter(or_(Company.company_name.ilike(f"%{s}%"),Company.hr_name.ilike(f"%{s}%")))
    return ok(data=page(q,lambda x:{**user_json(x.user),"company_id":x.id,"company_name":x.company_name,"hr_name":x.hr_name,"approval_status":x.approval_status,"is_blacklisted":x.is_blacklisted}))
@api.get("/admin/drives")
@require_role("ADMIN")
def admin_drives():
    q=PlacementDrive.query; s=request.args.get("search","");
    if s: q=q.filter(PlacementDrive.job_title.ilike(f"%{s}%"))
    return ok(data=page(q,drive_json))
@api.get("/admin/applications")
@require_role("ADMIN")
def admin_apps(): return ok(data=page(Application.query,app_json))
@api.get("/admin/reports/summary")
@require_role("ADMIN")
def reports():
    by_status={s:Application.query.filter_by(status=s).count() for s in ("APPLIED","SHORTLISTED","SELECTED","REJECTED")}; return ok(data={"applications_by_status":by_status,"placement_rate":round(100*by_status["SELECTED"]/max(Application.query.count(),1),2)})

def admin_company_action(cid, action):
    c=db.get_or_404(Company,cid)
    if action in ("approve","reject"): c.approval_status={"approve":"APPROVED","reject":"REJECTED"}[action]
    elif action=="blacklist": c.is_blacklisted=True; c.user.is_blacklisted=True
    elif action=="deactivate": c.user.is_active=False
    elif action=="activate": c.is_blacklisted=False; c.user.is_blacklisted=False; c.user.is_active=True
    log(f"company {action}","company",cid); db.session.commit(); invalidate(); return ok(f"Company {action}d")
for action in ("approve","reject","blacklist","deactivate","activate"):
    api.add_url_rule(f"/admin/companies/<int:cid>/{action}",f"company_{action}",require_role("ADMIN")(lambda cid,a=action:admin_company_action(cid,a)),methods=["PATCH"])
def admin_student_action(sid, action):
    s=db.get_or_404(Student,sid)
    if action=="blacklist": s.user.is_blacklisted=True
    elif action=="deactivate": s.user.is_active=False
    else: s.user.is_blacklisted=False; s.user.is_active=True
    log(f"student {action}","student",sid); db.session.commit(); return ok(f"Student {action}d")
for action in ("blacklist","deactivate","activate"):
    api.add_url_rule(f"/admin/students/<int:sid>/{action}",f"student_{action}",require_role("ADMIN")(lambda sid,a=action:admin_student_action(sid,a)),methods=["PATCH"])
def drive_action(did, action):
    d=db.get_or_404(PlacementDrive,did); target={"approve":"APPROVED","reject":"REJECTED","close":"CLOSED"}[action]
    allowed={"approve":("PENDING",),"reject":("PENDING",),"close":("APPROVED",)}
    if d.status not in allowed[action]: return fail("Invalid drive status transition",409)
    d.status=target; log(f"drive {action}","drive",did); db.session.commit(); invalidate(); return ok(f"Drive {action}d")
for action in ("approve","reject","close"):
    api.add_url_rule(f"/admin/drives/<int:did>/{action}",f"drive_{action}",require_role("ADMIN")(lambda did,a=action:drive_action(did,a)),methods=["PATCH"])

def own_company(): return Company.query.filter_by(user_id=session["user_id"]).first_or_404()
@api.route("/company/profile",methods=["GET","PUT"])
@require_role("COMPANY")
def company_profile():
    c=own_company()
    if request.method=="PUT":
        d=request.get_json() or {}
        for k in ("company_name","hr_name","hr_email","hr_phone","website","description"):
            if k in d: setattr(c,k,d[k])
        db.session.commit()
    return ok(data={"id":c.id,"company_name":c.company_name,"hr_name":c.hr_name,"hr_email":c.hr_email,"hr_phone":c.hr_phone,"website":c.website,"description":c.description,"approval_status":c.approval_status,"is_blacklisted":c.is_blacklisted})
@api.get("/company/dashboard")
@require_role("COMPANY")
def company_dashboard():
    c=own_company(); apps=Application.query.join(PlacementDrive).filter(PlacementDrive.company_id==c.id)
    return ok(data={"company_name":c.company_name,"approval_status":c.approval_status,"total_drives":len(c.drives),"active_drives":sum(d.status=="APPROVED" for d in c.drives),"total_applicants":apps.count(),"selected":apps.filter(Application.status=="SELECTED").count()})
@api.route("/company/drives",methods=["GET","POST"])
@require_role("COMPANY")
def company_drives():
    c=own_company()
    if request.method=="GET": return ok(data=page(PlacementDrive.query.filter_by(company_id=c.id),drive_json))
    if c.approval_status!="APPROVED" or c.is_blacklisted: return fail("Only approved, active companies can create drives",403)
    d=request.get_json() or {}; deadline=parse_dt(d.get("application_deadline","")); drive_date=parse_dt(d.get("drive_date",""))
    if not deadline or not drive_date or not d.get("job_title") or not d.get("job_description"): return fail("Invalid or missing drive fields")
    if deadline <= datetime.now(deadline.tzinfo or timezone.utc) or drive_date < deadline: return fail("Deadline must be in the future and before the drive date",422)
    row=PlacementDrive(company_id=c.id,job_title=d["job_title"],job_description=d["job_description"],eligibility_criteria=d.get("eligibility_criteria",""),eligible_department=d.get("eligible_department","ALL"),minimum_cgpa=float(d.get("minimum_cgpa",0)),eligible_year=int(d.get("eligible_year",1)),application_deadline=deadline,drive_date=drive_date,location=d.get("location",""),salary=d.get("salary",""))
    db.session.add(row); db.session.flush(); log("drive creation","drive",row.id); db.session.commit(); invalidate(); return ok("Drive created for approval",{"drive":drive_json(row)},201)
@api.route("/company/drives/<int:did>",methods=["GET","PUT"])
@require_role("COMPANY")
def company_drive(did):
    c=own_company(); d=PlacementDrive.query.filter_by(id=did,company_id=c.id).first_or_404()
    if request.method=="PUT":
        if d.status not in ("PENDING","REJECTED"): return fail("Approved drives cannot be edited",409)
        body=request.get_json() or {}
        for k in ("job_title","job_description","eligibility_criteria","eligible_department","minimum_cgpa","eligible_year"):
            if k in body: setattr(d,k,body[k])
        d.status="PENDING"; db.session.commit()
    return ok(data={"drive":drive_json(d)})
@api.get("/company/drives/<int:did>/applications")
@require_role("COMPANY")
def drive_apps(did):
    c=own_company(); PlacementDrive.query.filter_by(id=did,company_id=c.id).first_or_404(); return ok(data=page(Application.query.filter_by(drive_id=did),app_json))
@api.get("/company/applications/<int:aid>")
@require_role("COMPANY")
def company_app(aid):
    c=own_company(); a=Application.query.join(PlacementDrive).filter(Application.id==aid,PlacementDrive.company_id==c.id).first_or_404(); return ok(data={"application":app_json(a)})
@api.post("/company/applications/<int:aid>/offer-letter")
@require_role("COMPANY")
def offer_letter(aid):
    c=own_company(); a=db.session.get(Application,aid)
    if not a: return fail("Application not found",404)
    if a.drive.company_id!=c.id: return fail("Not authorized to access this application",403)
    if a.status!="SELECTED": return fail("Offer letters are available only for selected students",409)
    try:
        pdf=generate_offer_letter_pdf(a); filename=secure_filename(f"offer_letter_{a.student.full_name}_{c.company_name}.pdf")
        return send_file(pdf,mimetype="application/pdf",as_attachment=True,download_name=filename)
    except Exception:
        current_app.logger.exception("Offer-letter PDF generation failed")
        return fail("Unable to generate offer letter",500)
def app_action(aid, action):
    c=own_company(); a=Application.query.join(PlacementDrive).filter(Application.id==aid,PlacementDrive.company_id==c.id).first_or_404(); allowed={"shortlist":("APPLIED","SHORTLISTED"),"reject":(("APPLIED","SHORTLISTED"),"REJECTED"),"select":(("SHORTLISTED",),"SELECTED")}
    if action=="interview":
        if a.status!="SHORTLISTED": return fail("Only shortlisted applications can receive interviews",409)
        d=request.get_json() or {}; a.interview_date=parse_dt(d.get("interview_date",""))
        if not a.interview_date or not d.get("interview_mode"): return fail("Interview date and mode are required",422)
        a.interview_mode=d.get("interview_mode"); a.interview_location=d.get("interview_location",""); a.interview_notes=d.get("interview_notes",""); a.interview_status=d.get("interview_status","SCHEDULED"); a.interview_result=d.get("interview_result"); a.remarks=d.get("remarks",a.remarks)
    else:
        valid,target = (("APPLIED",),"SHORTLISTED") if action=="shortlist" else allowed[action]
        if a.status not in valid: return fail("Invalid application status transition",409)
        a.status=target
    db.session.add(Notification(user_id=a.student.user_id,title="Application updated",message=f"{a.drive.job_title}: {a.status}",type="APPLICATION")); log("application status change","application",aid); db.session.commit(); return ok("Application updated",{"application":app_json(a)})
for action in ("shortlist","reject","interview","select"):
    api.add_url_rule(f"/company/applications/<int:aid>/{action}",f"app_{action}",require_role("COMPANY")(lambda aid,a=action:app_action(aid,a)),methods=["PATCH"])

def own_student(): return Student.query.filter_by(user_id=session["user_id"]).first_or_404()
@api.route("/student/profile",methods=["GET","PUT"])
@require_role("STUDENT")
def student_profile():
    s=own_student()
    if request.method=="PUT":
        d=request.get_json() or {}
        for k in ("full_name","department","year","cgpa","phone","skills"):
            if k in d: setattr(s,k,d[k])
        db.session.commit()
    return ok(data={"id":s.id,"full_name":s.full_name,"register_number":s.register_number,"department":s.department,"year":s.year,"cgpa":s.cgpa,"phone":s.phone,"skills":s.skills,"resume_filename":s.resume_filename})
@api.post("/student/profile/resume")
@require_role("STUDENT")
def resume():
    s=own_student(); f=request.files.get("resume")
    if not f or not f.filename.lower().endswith(".pdf"): return fail("A PDF resume is required")
    header=f.stream.read(5); f.stream.seek(0)
    if header!=b"%PDF-": return fail("The uploaded file is not a valid PDF",422)
    name=f"student_{s.id}_{secure_filename(f.filename)}"; os.makedirs(current_app.config["UPLOAD_FOLDER"],exist_ok=True); path=os.path.join(current_app.config["UPLOAD_FOLDER"],name)
    old=s.resume_path; f.save(path); s.resume_filename=secure_filename(f.filename); s.resume_path=path; db.session.commit()
    if old and old!=path and os.path.isfile(old): os.remove(old)
    log("resume upload","student",s.id); db.session.commit(); return ok("Resume uploaded")
@api.get("/student/profile/resume")
@require_role("STUDENT")
def resume_download():
    s=own_student()
    if not s.resume_path or not os.path.isfile(s.resume_path): return fail("Resume not found",404)
    return send_file(s.resume_path,mimetype="application/pdf",as_attachment=True,download_name=s.resume_filename)
@api.get("/student/dashboard")
@require_role("STUDENT")
def student_dashboard():
    s=own_student(); return ok(data={"name":s.full_name,"department":s.department,"year":s.year,"cgpa":s.cgpa,"applications":len(s.applications),"shortlisted":sum(a.status=="SHORTLISTED" for a in s.applications),"selected":sum(a.status=="SELECTED" for a in s.applications)})
@api.get("/student/drives")
@require_role("STUDENT")
def student_drives():
    s=own_student(); q=PlacementDrive.query.filter_by(status="APPROVED"); term=request.args.get("search","")
    if term: q=q.join(Company).filter(or_(PlacementDrive.job_title.ilike(f"%{term}%"),Company.company_name.ilike(f"%{term}%")))
    if request.args.get("department"): q=q.filter(PlacementDrive.eligible_department.in_(["ALL",request.args["department"]]))
    return ok(data=page(q,lambda d:drive_json(d,s)))
@api.get("/student/drives/<int:did>")
@require_role("STUDENT")
def student_drive(did): return ok(data={"drive":drive_json(PlacementDrive.query.filter_by(id=did,status="APPROVED").first_or_404(),own_student())})
@api.post("/student/drives/<int:did>/apply")
@require_role("STUDENT")
def apply(did):
    s=own_student(); d=PlacementDrive.query.filter_by(id=did,status="APPROVED").first_or_404()
    if s.user.is_blacklisted: return fail("Blacklisted students cannot apply",403)
    deadline=d.application_deadline.replace(tzinfo=timezone.utc) if d.application_deadline.tzinfo is None else d.application_deadline
    if deadline < datetime.now(timezone.utc): return fail("Application deadline has passed",409)
    eligibility=drive_json(d,s)
    if not eligibility["eligible"]: return fail("Student is not eligible",409,{"reasons":eligibility["eligibility_reasons"]})
    a=Application(student_id=s.id,drive_id=d.id); db.session.add(a)
    try: db.session.flush(); log("application creation","application",a.id); db.session.commit(); invalidate(); return ok("Application submitted",{"application":app_json(a)},201)
    except IntegrityError: db.session.rollback(); return fail("You have already applied",409)
@api.get("/student/applications")
@require_role("STUDENT")
def student_apps(): return ok(data=page(Application.query.filter_by(student_id=own_student().id),app_json))
@api.get("/student/history")
@require_role("STUDENT")
def history(): return ok(data=page(Application.query.filter_by(student_id=own_student().id).order_by(Application.application_date.desc()),app_json))
@api.post("/student/export")
@require_role("STUDENT")
def export():
    s=own_student(); job=ExportJob(student_id=s.id,status="QUEUED"); db.session.add(job); db.session.flush(); log("CSV export","export",job.id); db.session.commit(); queued=False
    try:
        from redis import Redis
        Redis.from_url(current_app.config["REDIS_URL"],socket_connect_timeout=.2,socket_timeout=.2).ping()
        from celery_worker import export_task
        export_task.delay(job.id); queued=True
    except Exception:
        generate_export(job.id)
    job=db.session.get(ExportJob,job.id); name=os.path.basename(job.file_path) if job.file_path else None
    return ok("Export queued" if queued else "Export completed using local fallback",{"job_id":job.id,"status":job.status,"download_url":f"/api/student/exports/{name}" if name else None},202)
@api.get("/student/exports/<path:name>")
@require_role("STUDENT")
def download(name):
    s=own_student(); safe=secure_filename(name); job=ExportJob.query.filter_by(student_id=s.id,file_path=os.path.join(current_app.config["EXPORT_FOLDER"],safe),status="COMPLETED").first()
    if not job: return fail("Export not found",404)
    return send_from_directory(current_app.config["EXPORT_FOLDER"],safe,as_attachment=True)
@api.get("/student/exports/jobs/<int:job_id>")
@require_role("STUDENT")
def export_status(job_id):
    job=ExportJob.query.filter_by(id=job_id,student_id=own_student().id).first_or_404(); name=os.path.basename(job.file_path) if job.file_path else None
    return ok(data={"job_id":job.id,"status":job.status,"error":job.error_message,"download_url":f"/api/student/exports/{name}" if name else None})
@api.get("/notifications")
@require_role("ADMIN","COMPANY","STUDENT")
def notifications(): return ok(data={"items":[{"id":n.id,"title":n.title,"message":n.message,"type":n.type,"is_read":n.is_read,"created_at":iso(n.created_at)} for n in Notification.query.filter_by(user_id=session["user_id"]).order_by(Notification.created_at.desc()).all()]})
@api.patch("/notifications/<int:nid>/read")
@require_role("ADMIN","COMPANY","STUDENT")
def read_notification(nid): n=Notification.query.filter_by(id=nid,user_id=session["user_id"]).first_or_404(); n.is_read=True; db.session.commit(); return ok("Notification read")
