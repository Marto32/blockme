import os


LOGFILE = os.environ.get('LOGFILE', 'logs/file_logger.log')
INSERTION_ERROR_FILE = os.environ.get(
    'INSERTION_ERROR_FILE', 'logs/insertion_errors.log')

DEFAULT_USER = os.environ.get('USER')

PG_USERNAME = os.environ.get('PG_USERNAME', DEFAULT_USER)
PG_PASSWORD = os.environ.get('PG_PASSWORD', '')
PG_HOST = os.environ.get('PG_HOST', 'localhost')
PG_PORT = os.environ.get('PG_PORT', 5432)
PG_DATABASE_NAME = os.environ.get('PG_DATABASE_NAME', 'dev')
PG_DATABASE = f"postgresql://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE_NAME}"

ETHEREUM_SCHEMA = 'ethereum'

ETHEREUM_JSON_RPC_PORT = os.environ.get('RPC_PORT', 8545)
