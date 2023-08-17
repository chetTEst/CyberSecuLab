from os import getcwd, environ

path = getcwd()
db_host = environ.get('DB_HOST', 'db_lesson13134')
db_port = environ.get('DB_PORT', 'lesson13134')
db_user = environ.get('DB_USER', 'lesson13134')
db_pass = environ.get('PASSWORD', 'lesson13134')
db_name = environ.get('DB_DATABASE', 'lesson13134')