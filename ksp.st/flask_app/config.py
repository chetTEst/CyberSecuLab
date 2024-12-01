from os import getcwd, environ
from icecream import ic

ic.disable()

TOKEN_API_KEY = environ.get('TOKEN_API_KEY', 'token')
path = getcwd()
db_host = ic(environ.get('DB_HOST', 'db_lesson'))
db_port = ic(environ.get('DB_PORT', 'lesson1311'))
db_user = ic(environ.get('DB_USER', 'lesson1311'))
db_pass = ic(environ.get('DB_PASSWORD', 'lesson1311'))
db_name = ic(environ.get('DB_DATABASE', 'lesson1311'))
PROD_STATE = ic(environ.get('FLASK_DEBUG', ''))
