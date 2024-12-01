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
    active = db.Column(db.Boolean, default=True)  # Add this
    authenticated = db.Column(db.Boolean, default=False)
    anonymous = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    session = db.relationship('Session')
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    q1_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q1 = db.relationship('Questions', foreign_keys=[q1_id])
    q2_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q2 = db.relationship('Questions', foreign_keys=[q2_id])
    q3_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q3 = db.relationship('Questions', foreign_keys=[q3_id])
    q4_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q4 = db.relationship('Questions', foreign_keys=[q4_id])
    q5_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q5 = db.relationship('Questions', foreign_keys=[q5_id])
    q6_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q6 = db.relationship('Questions', foreign_keys=[q6_id])
    q7_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q7 = db.relationship('Questions', foreign_keys=[q7_id])
    q8_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    q8 = db.relationship('Questions', foreign_keys=[q8_id])
    q9_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q9 = db.relationship('Ports', foreign_keys=[q9_id])
    q10_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q10 = db.relationship('Ports', foreign_keys=[q10_id])
    q11_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q11 = db.relationship('Ports', foreign_keys=[q11_id])
    q12_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q12 = db.relationship('Ports', foreign_keys=[q12_id])
    q13_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q13 = db.relationship('Ports', foreign_keys=[q13_id])
    q14_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q14 = db.relationship('Ports', foreign_keys=[q14_id])
    q15_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q15 = db.relationship('Ports', foreign_keys=[q15_id])
    q16_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q16 = db.relationship('Ports', foreign_keys=[q16_id])
    a1 = db.Column(db.Boolean, default=False)
    a2 = db.Column(db.Boolean, default=False)

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


class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    hash = db.Column(db.Text, nullable=False)
    isVirus = db.Column(db.Boolean, default=False, nullable=False)


class Ports(db.Model):
    __tablename__ = 'ports'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)
    isDanger = db.Column(db.Boolean, default=False, nullable=False)

