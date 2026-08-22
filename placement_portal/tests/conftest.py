import sys
from pathlib import Path
import pytest
from werkzeug.security import generate_password_hash
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from app import create_app
from app.extensions import db
from app.models import User

class TestConfig:
    TESTING=True; SECRET_KEY="test"; SQLALCHEMY_DATABASE_URI="sqlite:///:memory:"; SQLALCHEMY_TRACK_MODIFICATIONS=False
    UPLOAD_FOLDER=str(ROOT/"uploads"); EXPORT_FOLDER=str(ROOT/"exports"); REPORT_FOLDER=str(ROOT/"reports"); CELERY={"broker_url":"memory://","result_backend":"cache+memory://"}

@pytest.fixture
def app():
    a=create_app(TestConfig)
    with a.app_context():
        db.create_all(); db.session.add(User(username="admin",email="admin@test.local",password_hash=generate_password_hash("Admin123"),role="ADMIN")); db.session.commit(); yield a; db.session.remove(); db.drop_all()
@pytest.fixture
def client(app): return app.test_client()

def login(c,u,p): return c.post('/api/auth/login',json={'username':u,'password':p})
def student(c,name='stu',reg='R1',cgpa=8.5): return c.post('/api/auth/register/student',json={'username':name,'email':name+'@test.local','password':'secret1','full_name':'Student One','register_number':reg,'department':'CSE','year':4,'cgpa':cgpa})
def company(c,name='co'): return c.post('/api/auth/register/company',json={'username':name,'email':name+'@test.local','password':'secret1','company_name':'Acme','hr_name':'HR','hr_email':'hr@acme.test'})

