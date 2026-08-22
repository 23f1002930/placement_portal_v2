import os, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import User

app=create_app()
with app.app_context():
    db.create_all()
    admins=User.query.filter_by(role="ADMIN").all()
    if not admins:
        admin=User(username=os.getenv("ADMIN_USERNAME","admin"),email=os.getenv("ADMIN_EMAIL","admin@placement.local"),password_hash=generate_password_hash(os.getenv("ADMIN_PASSWORD","Admin@123")),role="ADMIN")
        db.session.add(admin); db.session.commit(); print("Database initialized; admin created.")
    else: print(f"Database initialized; existing admin: {admins[0].username}")

