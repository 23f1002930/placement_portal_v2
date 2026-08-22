def test_anonymous_application_access(client): assert client.get('/api/student/applications').status_code==401
