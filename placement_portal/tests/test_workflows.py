from datetime import datetime, timedelta, timezone
from conftest import login, student, company

def setup_drive(c):
    company(c); student(c); login(c,'admin','Admin123'); co=c.get('/api/admin/companies').get_json()['data']['items'][0]; c.patch(f"/api/admin/companies/{co['company_id']}/approve"); c.post('/api/auth/logout'); login(c,'co','secret1')
    future=datetime.now(timezone.utc)+timedelta(days=5); later=future+timedelta(days=2)
    r=c.post('/api/company/drives',json={'job_title':'Engineer','job_description':'Build things','eligible_department':'CSE','minimum_cgpa':8,'eligible_year':4,'application_deadline':future.isoformat(),'drive_date':later.isoformat()}); assert r.status_code==201
    c.post('/api/auth/logout'); login(c,'admin','Admin123'); d=c.get('/api/admin/drives').get_json()['data']['items'][0]; c.patch(f"/api/admin/drives/{d['id']}/approve"); return d['id']

def test_complete_workflow(client):
    did=setup_drive(client); client.post('/api/auth/logout'); login(client,'stu','secret1'); assert len(client.get('/api/student/drives').get_json()['data']['items'])==1
    assert client.post(f'/api/student/drives/{did}/apply').status_code==201; assert client.post(f'/api/student/drives/{did}/apply').status_code==409
    aid=client.get('/api/student/applications').get_json()['data']['items'][0]['id']; client.post('/api/auth/logout'); login(client,'co','secret1'); assert client.patch(f'/api/company/applications/{aid}/shortlist').status_code==200
    assert client.patch(f'/api/company/applications/{aid}/interview',json={'interview_date':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat(),'interview_mode':'Online'}).status_code==200
    assert client.patch(f'/api/company/applications/{aid}/select').status_code==200
    offer=client.post(f'/api/company/applications/{aid}/offer-letter'); assert offer.status_code==200; assert offer.mimetype=='application/pdf'; assert offer.data.startswith(b'%PDF-')
    client.post('/api/auth/logout'); login(client,'stu','secret1'); assert client.get('/api/student/history').get_json()['data']['total']==1
    export=client.post('/api/student/export'); assert export.status_code==202; assert export.get_json()['data']['status'] in ('QUEUED','COMPLETED')

def test_ineligible_student(client):
    did=setup_drive(client); client.post('/api/auth/logout'); login(client,'stu','secret1'); client.put('/api/student/profile',json={'cgpa':4}); assert client.post(f'/api/student/drives/{did}/apply').status_code==409
