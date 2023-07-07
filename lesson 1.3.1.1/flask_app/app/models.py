import pymysql
from flask_sqlalchemy import SQLAlchemy

pymysql.install_as_MySQLdb()
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Integer, nullable=False) # The role can be 'admin' or 'user'
    active = db.Column(db.Boolean, default=True)  # Add this
    authenticated = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(128))
    two_factor_enter = db.Column(db.Boolean, default=False)
    anonymous = db.Column(db.Boolean, default=False)
    session = db.Column(db.Integer, nullable=False)
    two_factor_enter = db.Column(db.Boolean, default=False)
    first_enter = db.Column(db.Boolean, default=False)
    check_message = db.Column(db.Boolean, default=False)

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

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256), nullable=False)
    permissions = db.relationship('Permission', backref='file', lazy=True)

class Permission(db.Model):
    __tablename__ = 'permissions'

    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    role = db.Column(db.Integer, nullable=False) # The role can be 'admin' or 'user'

class Session(db.Model):
    __tablename__ = 'session'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)