from . import app
from .models import db, User, Session, CipherType, Questions

db.init_app(app)

with app.app_context():
    db.create_all()
