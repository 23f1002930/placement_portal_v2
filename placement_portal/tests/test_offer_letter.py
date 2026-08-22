from conftest import company, login
from test_workflows import setup_drive

def selected_application(client):
    did=setup_drive(client); client.post('/api/auth/logout'); login(client,'stu','secret1')
    application=client.post(f'/api/student/drives/{did}/apply').get_json()['data']['application']; aid=application['id']
    client.post('/api/auth/logout'); login(client,'co','secret1'); client.patch(f'/api/company/applications/{aid}/shortlist'); client.patch(f'/api/company/applications/{aid}/select')
    return aid

def test_selected_offer_is_real_dynamic_pdf(client):
    aid=selected_application(client); response=client.post(f'/api/company/applications/{aid}/offer-letter')
    assert response.status_code==200
    assert response.mimetype=='application/pdf'
    assert response.data.startswith(b'%PDF-') and b'%%EOF' in response.data[-20:]
    assert response.headers['Content-Disposition'].startswith('attachment;')
    assert '.pdf' in response.headers['Content-Disposition'].lower()
    assert b'Student One' in response.data and b'Acme' in response.data and b'Engineer' in response.data

def test_offer_letter_access_and_status_rules(client):
    assert client.post('/api/company/applications/1/offer-letter').status_code==401
    did=setup_drive(client); client.post('/api/auth/logout'); login(client,'stu','secret1')
    aid=client.post(f'/api/student/drives/{did}/apply').get_json()['data']['application']['id']
    assert client.post(f'/api/company/applications/{aid}/offer-letter').status_code==403
    client.post('/api/auth/logout'); login(client,'co','secret1')
    assert client.post(f'/api/company/applications/{aid}/offer-letter').status_code==409
    assert client.post('/api/company/applications/99999/offer-letter').status_code==404

def test_company_cannot_generate_another_company_offer(client):
    aid=selected_application(client); client.post('/api/auth/logout'); company(client,'otherco'); login(client,'admin','Admin123')
    companies=client.get('/api/admin/companies').get_json()['data']['items']; other=next(x for x in companies if x['company_name']=='Acme' and x['username']=='otherco')
    client.patch(f"/api/admin/companies/{other['company_id']}/approve"); client.post('/api/auth/logout'); login(client,'otherco','secret1')
    assert client.post(f'/api/company/applications/{aid}/offer-letter').status_code==403
