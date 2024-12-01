import pymysql
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

pymysql.install_as_MySQLdb()
db = SQLAlchemy()


class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False, unique=True)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    first_last_name = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True)
    authenticated = db.Column(db.Boolean, default=False)
    anonymous = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    session = db.relationship('Session')
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    uuid_db = db.Column(db.String(36), unique=True, nullable=True)
    reference_uuid_db = db.Column(db.String(36), unique=True, nullable=True)
    q1_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    q1 = db.relationship('Tasks', foreign_keys=[q1_id])
    q2_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    q2 = db.relationship('Tasks', foreign_keys=[q2_id])
    q3_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    q3 = db.relationship('Tasks', foreign_keys=[q3_id])
    q4_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    q4 = db.relationship('Tasks', foreign_keys=[q4_id])
    q5_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    q5 = db.relationship('Tasks', foreign_keys=[q5_id])
    q6_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    q6 = db.relationship('Tasks', foreign_keys=[q6_id])
    q7_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    q7 = db.relationship('Tasks', foreign_keys=[q7_id])
    a1 = db.Column(db.Boolean, default=False)
    a2 = db.Column(db.Boolean, default=False)
    a3 = db.Column(db.Boolean, default=False)
    a4 = db.Column(db.Boolean, default=False)
    a5 = db.Column(db.Boolean, default=False)
    a6 = db.Column(db.Boolean, default=False)
    a7 = db.Column(db.Boolean, default=False)
    check_a3 = db.Column(db.Boolean, default=False)
    check_a4 = db.Column(db.Boolean, default=False)
    check_a5 = db.Column(db.Boolean, default=False)




    @property
    def is_active(self):
        return self.active

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_anonymous(self):
        return self.anonymous


class Tasks(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    reference = db.Column(db.Text, nullable=False)
    chek_reference = db.Column(db.Text, nullable=True)


