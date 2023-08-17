from os import getcwd, environ

path = getcwd()
db_host = environ.get('DB_HOST', 'db_lesson132')
db_port = environ.get('DB_PORT', 'lesson132')
db_user = environ.get('DB_USER', 'lesson132')
db_pass = environ.get('PASSWORD', 'lesson132')
db_name = environ.get('DB_DATABASE', 'lesson132')