from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .models import db
from ..config import path, db_host, db_port, db_user, db_pass, db_name, SECRET_KEY
from os.path import join as pjoin
from os import environ

def create_app():
    app = Flask(__name__)
    if environ.get('FLASK_ENV') == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'universal.db')
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)
    return app

app = create_app()

from . import CreateDb, SetQuestions, routes
