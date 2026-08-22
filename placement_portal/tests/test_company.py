from conftest import login, company
def test_unapproved_company_cannot_create_drive(client):
    company(client); login(client,'co','secret1'); assert client.post('/api/company/drives',json={}).status_code==403
