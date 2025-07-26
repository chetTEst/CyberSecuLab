from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from pyseto import Key

from os.path import join as pjoin
from os import environ as env

from config import (path, db_host, db_port, db_user, db_pass, db_name, SECRET_KEY, PROD_STATE, SUBDOMAIN,
                    DOMAIN, REDIS_URL, REDIS_CACHE_TTL)

from .RedisCacheLib import RedisCache

db = SQLAlchemy()
redis_cache = RedisCache(redis_url=REDIS_URL, ttl=REDIS_CACHE_TTL)


def get_real_ip():
    """
    Получение реального IP клиента через цепочку прокси
    Порядок проверки заголовков важен!
    """
    # Проверяем заголовки в порядке приоритета
    headers_to_check = [
        'X-Forwarded-For',      # Основной заголовок для прокси
        'X-Real-IP',            # Nginx Proxy Manager может использовать этот
        'X-Original-Forwarded-For',  # Дополнительный заголовок
        'CF-Connecting-IP',     # Cloudflare
        'True-Client-IP',       # Другие CDN
    ]

    for header in headers_to_check:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For может содержать несколько IP через запятую
            # Берем первый (самый левый) - это оригинальный клиент
            if ',' in ip:
                ip = ip.split(',')[0].strip()
            
            # Проверяем, что это не внутренний IP
            if not ip.startswith(('127.', '10.', '172.', '192.168.')):
                return ip
            
            # Если это внутренний IP, но он не наш прокси - возвращаем его
            if ip != '192.168.100.81':
                return ip

    # Если ничего не найдено, возвращаем remote_addr
    return request.remote_addr or 'unknown'

def create_app_for_db() -> Flask:
    app = Flask(__name__, static_folder='./static')
    if PROD_STATE:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'universal.db')
    
    app.config['SECRET_KEY'] = SECRET_KEY

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['REDIS_URL'] = REDIS_URL
    app.config['REDIS_CACHE_TTL'] = REDIS_CACHE_TTL

    return app

def create_app() -> Flask:
    app = Flask(__name__, static_folder='./static')
    app.logger.debug("========== create_app ==========")
    if PROD_STATE:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'universal.db')
    
    app.config['SECRET_KEY'] = SECRET_KEY

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['REDIS_URL'] = REDIS_URL
    app.config['REDIS_CACHE_TTL'] = REDIS_CACHE_TTL

    with open('private.pem', 'rb') as f:
        app.config['PRIVATE_KEY'] = Key.new(version=4, purpose="public", key=f.read()).to_paserk()
    with open('public.pem', 'rb') as f:
        app.config['PUBLIC_KEY'] = Key.new(version=4, purpose="public", key=f.read()).to_paserk()

    # Инициализируем расширения с приложением
    db.init_app(app)
    
        # Получаем настройки из переменных окружения
    redis_url = env.get('REDIS_URL', 'redis://redis:6379')
    async_mode = env.get('SOCKETIO_ASYNC_MODE', 'eventlet')
    ping_timeout = int(env.get('WEBSOCKET_PING_TIMEOUT', '60'))
    ping_interval = int(env.get('WEBSOCKET_PING_INTERVAL', '25'))
    
    socketio = SocketIO(app,
        async_mode=async_mode,
        # message_queue=f'{redis_url}/1',
        # Ограничьте CORS только необходимыми доменами в продакшене
        cors_allowed_origins="*" if not PROD_STATE else ['192.168.100.81',
                                                         f'https://{SUBDOMAIN}.{DOMAIN}',
                                                         f'http://{SUBDOMAIN}.{DOMAIN}'],
        # Отключите логирование в продакшене
        engineio_logger=(not PROD_STATE),
        logger=(not PROD_STATE),
        # Добавьте настройки для лучшей производительности
        ping_timeout=ping_timeout,
        ping_interval=ping_interval,
        transports=['websocket', 'polling'],
        allow_upgrades=True
    )
    
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Добавьте исключение для путей Socket.IO
    @csrf.exempt
    def csrf_exempt_socketio():
        if request.path.startswith('socket.io'):
            return True
        return False  # Это значение не используется как HTTP-ответ
   
    
    csrf.exempt(csrf_exempt_socketio)

    limiter = Limiter(
        default_limits=["600 per minute"],
        storage_uri=f'{redis_url}/2',
        storage_options={"socket_connect_timeout": 30},
        strategy="fixed-window",
        key_func=get_real_ip
    )
    limiter.init_app(app)
    
    # Регистрируем маршруты
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)
        @app.errorhandler(400)
        def bad_request(error):
            return str(error.description), 400


        @app.errorhandler(401)
        @app.errorhandler(404)
        @app.errorhandler(405)
        @app.errorhandler(500)
        def handle_error(error):
            app.logger.debug(f"====== handle_error =======")
            requested_url = request.url
            return routes.error_do(requested_url)

        @app.errorhandler(429)
        def ratelimit_handler(e):
            return f"Лимит запросов превышен, попробуйте через {e.description}", 429
        
        global redis_cache
        redis_cache.init_app(app)
        
        from .RedisCacheLib import refresh_all_cache, get_all_cache_status, build_and_cache_questions_by_pool, build_and_cache_correct_answers

        all_cache_status = get_all_cache_status(redis_cache)
        if not all(all_cache_status.values()):
            try:
                refresh_all_cache(redis_cache) 
            except Exception as e:
                app.logger.error(f"Error initializing cache: {e}")
            
        from . import socket_handlers
        socket_handlers.init_socketio(socketio)
    
    if PROD_STATE:
        app.logger.setLevel('WARNING')
    else:
        app.logger.setLevel('DEBUG')

    # Инициализация кэша при старте приложения
       
        
    return app, socketio
    

app, socketio = create_app()

