from . import app
from .models import db, User, Questions, Session, Ports

db.init_app(app)

with app.app_context():
    db.create_all()
