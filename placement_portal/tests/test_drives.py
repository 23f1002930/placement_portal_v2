def test_anonymous_drive_access(client): assert client.get('/api/student/drives').status_code==401
