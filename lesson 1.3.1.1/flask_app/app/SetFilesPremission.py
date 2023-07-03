import random
import string
from werkzeug.security import generate_password_hash
from .models import db, User, File, Permission
from . import app

with app.app_context():
    # Create permissions for the files
    for i in range(1, 11):
        file = File(path=f'file{i}.docx')
        db.session.add(file)
    for i in range(1, 6):
        permission = Permission(file_id=i, role=0)
        db.session.add(permission)

    for i in range(6, 11):
        permission = Permission(file_id=i, role=1)
        db.session.add(permission)

    # Commit the new Permission objects to the database
    db.session.commit()