from os import getcwd, environ

TOKEN_API_KEY = environ.get('TOKEN_API_KEY', 'token')
path = getcwd()
db_host = environ.get('DB_HOST', 'db_lesson13134')
db_port = environ.get('DB_PORT', '3306')
db_user = environ.get('DB_USER', 'lesson13134')
db_pass = environ.get('DB_PASSWORD', 'lesson13134')
db_name = environ.get('DB_DATABASE', 'lesson13134')
PROD_STATE = environ.get('FLASK_DEBUG', '')
SECRET_KEY = environ.get('SECRET_KEY', 'secret')