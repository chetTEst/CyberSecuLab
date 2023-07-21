import pymysql
from flask_sqlalchemy import SQLAlchemy

pymysql.install_as_MySQLdb()
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True)  # Add this
    authenticated = db.Column(db.Boolean, default=False)
    anonymous = db.Column(db.Boolean, default=False)
    session = db.Column(db.Integer, db.ForeignKey('session.number'), nullable=False)
    session_obj = db.relationship('Session', foreign_keys=[session])
    q1 = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q1_obj = db.relationship('Questions', foreign_keys=[q1])
    q2 = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q2_obj = db.relationship('Questions', foreign_keys=[q2])
    q3 = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q3_obj = db.relationship('Questions', foreign_keys=[q3])
    q4 = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q4_obj = db.relationship('Questions', foreign_keys=[q4])
    a1 = db.Column(db.Boolean, default=False)
    a2 = db.Column(db.Boolean, default=False)
    a3 = db.Column(db.Boolean, default=False)
    a4 = db.Column(db.Boolean, default=False)

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


class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)

class CipherType(db.Model):
    __tablename__ = 'cipher_type'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16), unique=True, nullable=False)

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, db.ForeignKey('cipher_type.id'), nullable=False)
    type_obj = db.relationship('CipherType', foreign_keys=[type])
    text = db.Column(db.String(1024), nullable=False)
    answer = db.Column(db.String(32), nullable=False)

