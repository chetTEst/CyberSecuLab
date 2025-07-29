from os import getcwd, environ
from secrets import token_hex


def generate_salt(length=16):
    return token_hex(length)


path = getcwd()

TOKEN_API_KEY = environ.get('TOKEN_API_KEY','token_api_key')

db_host = environ.get('DB_HOST', 'db_test_uts')
db_port = environ.get('DB_PORT', '3306')
db_user = environ.get('DB_USER', 'universal')
db_pass = environ.get('DB_PASSWORD', 'universal')
db_name = environ.get('DB_DATABASE', 'universal')

prod_state_str = environ.get('FLASK_DEBUG', '')
PROD_STATE = prod_state_str.lower() == 'production'

SECRET_KEY = environ.get('SECRET_KEY', 'secret')
SUBDOMAIN = environ.get('SUBDOMAIN', 'test')
DOMAIN = environ.get('DOMAIN', 'ctfclass.ru')
GIFT_FILE = environ.get("GIFT_FILE", "questions.gift")
SK_PASERK = environ.get("SK_PASERK", "k4.secret")
PK_PASERK = environ.get("PK_PASERK", "k4.public.")
SALT = environ.get('SALT', generate_salt())
TOLLERANCE = environ.get('TOLLERANCE', 0.01)

random_in_variants_str = environ.get('RANDOM_IN_VARIANTS', 'False')
RANDOM_IN_VARIANTS = random_in_variants_str.lower() == 'true'

REDIS_URL = environ.get('REDIS_URL', 'redis://redis:6379/0')
REDIS_CACHE_TTL = int(environ.get('REDIS_CACHE_TTL', '3600'))  # 1 час
