import pymysql
from flask_sqlalchemy import SQLAlchemy


pymysql.install_as_MySQLdb()
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)  # Add this
    authenticated = db.Column(db.Boolean, default=True)
    anonymous = db.Column(db.Boolean, default=True)
    q1_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q1 = db.relationship('Ports', foreign_keys=[q1_id])
    q2_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q2 = db.relationship('Ports', foreign_keys=[q2_id])
    q3_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q3 = db.relationship('Ports', foreign_keys=[q3_id])
    q4_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q4 = db.relationship('Ports', foreign_keys=[q4_id])
    q5_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q5 = db.relationship('Ports', foreign_keys=[q5_id])
    q6_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q6 = db.relationship('Ports', foreign_keys=[q6_id])
    q7_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q7 = db.relationship('Ports', foreign_keys=[q7_id])
    q8_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    q8 = db.relationship('Ports', foreign_keys=[q8_id])
    a1 = db.Column(db.Boolean, default=False)
    a2 = db.Column(db.Boolean, default=False)
    a3 = db.Column(db.Boolean, default=False)
    a4 = db.Column(db.Boolean, default=False)
    a5 = db.Column(db.Boolean, default=False)
    a6 = db.Column(db.Boolean, default=False)
    a7 = db.Column(db.Boolean, default=False)
    a8 = db.Column(db.Boolean, default=False)
    a9 = db.Column(db.Boolean, default=False)
    
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



class Emails(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(128), nullable=False)
    from_label = db.Column(db.String(50), nullable=False)
    to_label = db.Column(db.String(50), nullable=False)
    email_body = db.Column(db.String(1024), nullable=False)
    attach = db.Column(db.String(16), nullable=False, default="нет")
    isDanger = db.Column(db.Boolean, default=False, nullable=False)
    isSpam = db.Column(db.Boolean, default=False, nullable=False)
