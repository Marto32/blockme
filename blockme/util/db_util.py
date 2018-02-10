import settings

from collections import deque

from sqlalchemy import create_engine   
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils.functions import database_exists, create_database
from sqlalchemy.sql.expression import func

from blockme.util.parser_util import convert_base_16_unix_time_to_datetime
from blockme.models.ethereum import Block, Transaction, base
from blockme.util.logging_util import get_blockme_file_logger


class BaseDatabaseException(Exception):
    pass


class SessionDoesNotExist(BaseDatabaseException):
    pass


class AbstractDatabaseHelper(object):

    def __init__(self):
        self.logger = get_blockme_file_logger()
        self.session = self.create_database_session()

    def get_latest_block_in_database(self):
        """
        Obtains the datetime (in UTC) of the most recent
        block in the database. Returns blocktime.
        """
        results = self.session.query(func.max(Block.timestamp)).all()
        return results[0][0]

    def get_earliest_block_in_database(self):
        """
        Obtains the datetime (in UTC) of the earliest
        block in the database. Returns blocktime.
        """
        results = self.session.query(func.min(Block.timestamp)).all()
        return results[0][0]

    def get_block_queue(self):
        """
        Returns a list of block numbers already in the database.
        """
        queue = deque()
        results = self.session.query(Block.number).distinct()
        for r in results:
            queue.append(r[0])
        return queue

    def create_database_session(self):
        """
        Obtains a database engine and creates one if it doesn't exist.
        """
        db_string = settings.PG_DATABASE
        db = create_engine(db_string)

        self.logger.info("Checking if database exists...")
        if not database_exists(db.url):
            self.logger.info(f"The db doesn't exist. Creating the "
                "database: {settings.PG_DATABASE_NAME}...")
            create_database(db.url)
            base.metadata.create_all(db)
            self.logger.info(f"{settings.PG_DATABASE_NAME} created.")
        else:
            self.logger.info("Database exists.")

        Session = sessionmaker(db)
        session = Session()
        return session


class EthereumDatabaseHelper(AbstractDatabaseHelper):

    def insert_blocks(self, block_list):
        """
        Inserts blocks to the initialized database.

        block_list :: a list of json-decoded block objects
        """
        if self.session is None:
            raise SessionDoesNotExist(
                'There is no database session created. Initialize a session first.'
            )

        blocks_to_insert = []

        self.logger.info(f'Parsing {len(block_list)} blocks...')
        for b in block_list:
            block = {}
            block['number'] = int(b['number'], 16)
            block['block_hash'] = int(b['hash'], 16)
            block['parent_hash'] = b['parentHash']
            block['nonce'] = b['nonce']
            block['transactions_root'] = b['transactionsRoot']
            block['state_root'] = b['stateRoot']
            block['receipt_root'] = b['receiptsRoot']
            block['miner'] = b['miner']
            block['difficulty'] = b['difficulty']
            block['total_difficulty'] = b['totalDifficulty']
            block['size'] = int(b['size'], 16)
            block['gas_limit'] = int(b['gasLimit'], 16)
            block['gase_used'] = int(b['gasUsed'], 16)
            block['timestamp'] = convert_base_16_unix_time_to_datetime(b['timestamp'])

            blocks_to_insert.append(Block(**block))

        num_blocks = len(blocks_to_insert)
        self.logger.info(f'Inserting {num_blocks} blocks to the database.')
        self.session.bulk_save_objects(blocks_to_insert)
        self.session.commit()
        self.logger.info(f'{num_blocks} blocks inserted.')

    def insert_transactions(self, transaction_list):
        """
        Inserts transactions to the initialized database.

        transaction_list :: a list of json-decoded transaction objects
        """
        if self.session is None:
            raise SessionDoesNotExist(
                'There is no database session created. Initialize a session first.'
            )

        transactions_to_insert = []

        self.logger.info(f'Parsing {len(transaction_list)} transactions...')
        for t in transaction_list:
            transaction = {}
            transaction['transaction_hash'] = int(t['hash'], 16)
            transaction['block_number'] = int(t['blockNumber'], 16)
            transaction['block_hash'] = t['blockHash']
            transaction['nonce'] = t['nonce']
            transaction['transaction_index'] = t['transactionsIndex']
            transaction['sender'] = t['from']
            transaction['receipt'] = t['to']
            transaction['value'] = int(t['value'], 16)/1000000000000000000.
            transaction['gas'] = int(t['gas'], 16)
            transaction['gas_price'] = int(t['gasPrice'], 16)

            transactions_to_insert.append(Transaction(**transaction))

        num_transactions = len(transactions_to_insert)
        self.logger.info(f'Inserting {num_transactions} transactions to the database.')
        self.session.bulk_save_objects(transactions_to_insert)
        self.session.commit()
        self.logger.info(f'{num_transactions} transactions inserted.')
