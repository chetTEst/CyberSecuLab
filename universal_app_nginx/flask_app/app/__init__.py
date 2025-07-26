from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from pyseto import Key

from os.path import join as pjoin
from os import environ as env

from config import path, db_host, db_port, db_user, db_pass, db_name, SECRET_KEY, PROD_STATE, SUBDOMAIN, DOMAIN


def get_real_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)


def create_app() -> Flask:
    app = Flask(__name__, static_folder='static')
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
    
    # Инициализируем расширения с приложением
    db.init_app(app)
    
    return app



db = SQLAlchemy()
app = create_app()
# Инициализируем SocketIO только один раз здесь
socketio = SocketIO(
    app,
    async_mode='gevent',
    # Ограничьте CORS только необходимыми доменами в продакшене
    cors_allowed_origins="*" if PROD_STATE != 'production' else [f"https://{SUBDOMAIN}.{DOMAIN}"],
    path="socket.io",
    # Отключите логирование в продакшене
    engineio_logger=PROD_STATE != 'production',
    logger=PROD_STATE != 'production',
    # Добавьте настройки для лучшей производительности
    ping_timeout=60,
    ping_interval=25
)

if PROD_STATE == 'production':
    app.logger.setLevel('WARNING')
else:
    app.logger.setLevel('DEBUG')


# Импортируем маршруты и другие необходимые модули
csrf = CSRFProtect()
csrf.init_app(app)

redis_url = env.get('REDIS_URL', 'redis://redis:6379')

limiter = Limiter(
    default_limits=["200 per minute"],
    storage_uri=redis_url,
    storage_options={"socket_connect_timeout": 30},
    strategy="fixed-window",  # или "moving-window" для более точного отслеживания
    key_func=get_real_ip
)
limiter.init_app(app)

from . import CreateDb, routes