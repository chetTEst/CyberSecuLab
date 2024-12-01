from os import getcwd, environ

TOKEN_API_KEY = environ.get('TOKEN_API_KEY', 'token')
path = getcwd()
JOBE_SERVER_URL = environ.get('JOBE_SERVER_URL', '0.0.0.0')
X_API_KEY = environ.get('X_API_KEY', 'token')
db_host = environ.get('DB_HOST', 'db_lesson213')
db_port = environ.get('DB_PORT', '3306')
db_user = environ.get('DB_USER', 'lesson213')
db_pass = environ.get('DB_PASSWORD', 'lesson213')
db_name = environ.get('DB_DATABASE', 'lesson213')
PROD_STATE = environ.get('FLASK_DEBUG', '')
SECRET_KEY = environ.get('SECRET_KEY', 'secret')
