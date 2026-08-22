from conftest import login, student, company
def test_registration_login_logout(client):
    assert student(client).status_code==201; assert company(client).status_code==201
    assert login(client,'stu','secret1').status_code==200
    assert client.get('/api/admin/dashboard').status_code==403
    assert client.post('/api/auth/logout').status_code==200
    assert login(client,'stu','wrong').status_code==401
def test_admin_login(client): assert login(client,'admin','Admin123').status_code==200

