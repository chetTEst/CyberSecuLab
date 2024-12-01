import pymysql
from flask_sqlalchemy import SQLAlchemy

pymysql.install_as_MySQLdb()
db = SQLAlchemy()

class ShortLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_id = db.Column(db.String(6), unique=True, nullable=False)
    short_id_int = db.Column(db.Integer, unique=False, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)
