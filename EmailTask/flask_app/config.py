from os import getcwd, environ

path = getcwd()
db_host = environ.get('DB_HOST', 'db_baseEmailTask')
db_port = environ.get('DB_PORT', '3306')
db_user = environ.get('DB_USER', 'baseEmailTask')
db_pass = environ.get('PASSWORD', 'baseEmailTask')
db_name = environ.get('DB_DATABASE', 'baseEmailTask')