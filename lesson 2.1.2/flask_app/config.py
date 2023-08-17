from os import getcwd, environ

path = getcwd()
db_host = environ.get('DB_HOST', 'db_lesson212')
db_port = environ.get('DB_PORT', 'lesson212')
db_user = environ.get('DB_USER', 'lesson212')
db_pass = environ.get('PASSWORD', 'lesson212')
db_name = environ.get('DB_DATABASE', 'lesson212')