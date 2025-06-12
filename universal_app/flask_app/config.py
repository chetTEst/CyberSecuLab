from os import getcwd, environ

path = getcwd()
db_host = environ.get('DB_HOST', 'localhost')
db_port = environ.get('DB_PORT', '3306')
db_user = environ.get('DB_USER', 'universal')
db_pass = environ.get('DB_PASSWORD', 'universal')
db_name = environ.get('DB_DATABASE', 'universal')
SECRET_KEY = environ.get('SECRET_KEY', 'secret')
