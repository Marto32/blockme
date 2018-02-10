import os


LOGFILE = os.environ.get('LOGFILE')

DEFAULT_USER = os.environ.get('USER')

PG_USERNAME = os.environ.get('PG_USERNAME', DEFAULT_USER)
PG_PASSWORD = os.environ.get('PG_PASSWORD', '')
PG_HOST = os.environ.get('PG_HOST', '127.0.0.1')
PG_PORT = os.environ.get('PG_PORT', 5432)
PG_DATABASE_NAME = os.environ.get('PG_DATABASE_NAME', 'devdb')
PG_DATABASE = f"postgresql://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE_NAME}"

ETHEREUM_SCHEMA = 'ethereum'
