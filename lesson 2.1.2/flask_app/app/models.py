import pymysql
from flask_sqlalchemy import SQLAlchemy

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
    password = db.Column(db.String(256), nullable=False)
    active = db.Column(db.Boolean, default=True)  # Add this
    authenticated = db.Column(db.Boolean, default=False)
    anonymous = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    session = db.relationship('Session')
    q1_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q1 = db.relationship('IPs', foreign_keys=[q1_id])
    q2_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q2 = db.relationship('IPs', foreign_keys=[q2_id])
    q3_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q3 = db.relationship('IPs', foreign_keys=[q3_id])
    q4_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q4 = db.relationship('IPs', foreign_keys=[q4_id])
    q5_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q5 = db.relationship('IPs', foreign_keys=[q5_id])
    q6_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q6 = db.relationship('IPs', foreign_keys=[q6_id])
    q7_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q7 = db.relationship('IPs', foreign_keys=[q7_id])
    q8_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q8 = db.relationship('IPs', foreign_keys=[q8_id])
    q9_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q9 = db.relationship('IPs', foreign_keys=[q9_id])
    q10_id = db.Column(db.Integer, db.ForeignKey('ips.id'), nullable=False)
    q10 = db.relationship('IPs', foreign_keys=[q10_id])
    a1 = db.Column(db.Boolean, default=False)

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


class IPs(db.Model):
    __tablename__ = 'ips'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Text, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    isDanger = db.Column(db.Boolean, default=False, nullable=False)

