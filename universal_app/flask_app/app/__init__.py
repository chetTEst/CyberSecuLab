from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from pyseto import Key
from os.path import join as pjoin

from config import path, db_host, db_port, db_user, db_pass, db_name, SECRET_KEY, GIFT_FILE, PROD_STATE
from .models import db, Question

from os import environ


app = Flask(__name__, static_folder='static')
if PROD_STATE == 'production':
    app.logger.setLevel('WARNING')
else:
    app.logger.setLevel('DEBUG')
db = SQLAlchemy()
socketio = SocketIO()  # Инициализируем SocketIO


def create_app() -> Flask:
    if PROD_STATE == 'production':
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'universal.db')
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['POOL_SIZE'] = 0
    app.config["QUESTIONS_BY_POOL"] = dict()
    with open('private.pem', 'rb') as f:
        app.config['PRIVATE_KEY'] = Key.new(version=4, purpose="public", key=f.read()).to_paserk()
    with open('public.pem', 'rb') as f:
        app.config['PUBLIC_KEY'] = Key.new(version=4, purpose="public", key=f.read()).to_paserk()
    return app


app = create_app()

from . import CreateDb, routes