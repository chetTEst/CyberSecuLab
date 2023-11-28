import pymysql
from flask_sqlalchemy import SQLAlchemy


pymysql.install_as_MySQLdb()
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(128), unique=True, nullable=False)
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
    flag = db.Column(db.String(128), unique=False, nullable=False)
    
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



class Ports(db.Model):
    __tablename__ = 'ports'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)
    isDanger = db.Column(db.Boolean, default=False, nullable=False)
    isAnswer = db.Column(db.Boolean, default=False, nullable=False)

