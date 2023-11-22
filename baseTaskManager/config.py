from os import getcwd, environ

path = getcwd()
db_host = environ.get('DB_HOST', 'db_lesson')
db_port = environ.get('DB_PORT', 'lesson1311')
db_user = environ.get('DB_USER', 'lesson1311')
db_pass = environ.get('PASSWORD', 'lesson1311')
db_name = environ.get('DB_DATABASE', 'lesson1311')