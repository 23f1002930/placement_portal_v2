from conftest import login, student
def test_profile_access(client): student(client); login(client,'stu','secret1'); assert client.get('/api/student/profile').status_code==200
