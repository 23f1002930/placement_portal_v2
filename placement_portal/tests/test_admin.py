from conftest import login, company
def test_approve_and_reject_company(client):
    company(client); login(client,'admin','Admin123'); x=client.get('/api/admin/companies').get_json()['data']['items'][0]; assert client.patch(f"/api/admin/companies/{x['company_id']}/approve").status_code==200; assert client.patch(f"/api/admin/companies/{x['company_id']}/reject").status_code==200
