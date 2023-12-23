from os import getcwd, environ

path = getcwd()
db_host = environ.get('DB_HOST', 'db_baseTask1')
db_port = environ.get('DB_PORT', '3306')
db_user = environ.get('DB_USER', 'baseTask1')
db_pass = environ.get('PASSWORD', 'baseTask1')
db_name = environ.get('DB_DATABASE', 'baseTask1')