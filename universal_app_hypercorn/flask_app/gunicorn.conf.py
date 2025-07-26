import multiprocessing
import os

# Основные настройки
bind = "0.0.0.0:8000"
worker_class = "eventlet" #geventwebsocket.gunicorn.workers.GeventWebSocketWorker"
worker_connections = 1000
# Для разработки - более детальные логи
if os.getenv('FLASK_DEBUG') == 'test':
  loglevel = "debug"
  workers = 2
  reload = True
else:
  reload = False
  workers = multiprocessing.cpu_count() * 2 + 1

# Настройки для разработки
reload_extra_files = [
  '/app/app/',
  '/app/config.py',
  '/app/wsgi.py',
  '/app/gunicorn.conf.py'
]

# Логирование
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Настройки для WebSocket
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
timeout = 30