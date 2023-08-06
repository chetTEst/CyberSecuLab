from . import app
from .models import db, User, Session, IPs

db.init_app(app)

with app.app_context():
    db.create_all()
