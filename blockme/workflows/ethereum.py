"""
A client to interact with ethereum and write data
to a specified database.

NOTE: This file was modified from its original version
created by Alex Miller: https://github.com/alex-miller-0/Ethereum_Blockchain_Parser
"""
import requests
import json
import os
import time
import datetime
import sys
import tqdm

import settings

from blockme.util.db_util import EthereumDatabaseHelper
from blockme.util import crawler_util
from blockme.util.logging_util import get_blockme_console_logger, \
    get_insertion_error_file_logger


class Crawler(object):
    """
    A client to migrate blockchain from geth to a database.
    """

    def __init__(
        self,
        start=True,
        rpc_port=settings.ETHEREUM_JSON_RPC_PORT,
        host="http://127.0.0.1",
        delay=0.0001,
        chunk_size=10000
    ):
        """Initialize the Crawler."""
        self.logger = get_blockme_console_logger()
        self.logger.debug("Starting Crawler")
        self.url = "{}:{}".format(host, rpc_port)
        self.headers = {"content-type": "application/json"}

        self.chunk_size = chunk_size

        # Initializes to default host/port = localhost/27017
        self.database_client = EthereumDatabaseHelper()

        # The max block number that is in the database
        self.max_block_db = None

        # The max block number in the public blockchain
        self.max_block_geth = None

        # Record errors for inserting block data into the database
        self.insertion_error_logger = get_insertion_error_file_logger()

        # Make a stack of block numbers that are in the database
        self.block_queue = self.database_client.get_block_queue()

        # The delay between requests to geth
        self.delay = delay

        if start:
            self.max_block_db = self.database_client.get_latest_block_in_database()
            self.max_block_geth = self.highest_block_eth()
            self.run()

    def _rpcRequest(self, method, params, key):
        """Make an RPC request to geth on port 8545."""
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0
        }
        time.sleep(self.delay)
        res = requests.post(
              self.url,
              data=json.dumps(payload),
              headers=self.headers).json()
        return res[key]

    def get_block_and_associated_transactions(self, n):
        """Get a specific block from the blockchain and filter the data."""
        data = self._rpcRequest("eth_getBlockByNumber", [hex(n), True], "result")
        block, transactions = crawler_util.decode_block(data)
        return block, transactions

    def highest_block_eth(self):
        """Find the highest numbered block in geth."""
        self.logger.info("Obtaining highst block on geth.")
        num_hex = int(self._rpcRequest("eth_blockNumber", [], "result"), 16)
        self.logger.info(f"Highest block found: {num_hex}.")
        return num_hex

    def save_blocks_and_transactions_to_database(self, blocks, transactions):
        """Insert a given parsed block into database."""
        try:
            self.database_client.insert_blocks(blocks)
        except:
            the_type, the_value, the_traceback = sys.exc_info()
            message = f'\n------\n{the_type}\n{the_value}\n{the_traceback}\n------'
            self.insertion_error_logger.error(message)
        try:
            self.database_client.insert_transactions(transactions)
        except:
            message = f'\n------\n{the_type}\n{the_value}\n{the_traceback}\n------'
            self.insertion_error_logger.error(message)

    def highest_block_database(self):
        """Find the highest numbered block in the database."""
        highest_block = self.database_client.get_latest_block_in_database()
        self.logger.info(f"Highest block found in database: {highest_block}")
        return highest_block

    def collect_block_and_transactions(self, n):
        """Prepare blocks and transactions to add to database"""
        block, transactions = self.get_block_and_associated_transactions(n)
        blocks_to_insert = []
        transactions_to_insert = []
        
        if block:
            blocks_to_insert.append(block)
            time.sleep(0.001)
        
        if transactions:
            transactions_to_insert = transactions
            time.sleep(0.001)

        return blocks_to_insert, transactions_to_insert

    def chunk(self, l, n):
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def run(self):
        """
        Run the process.

        Iterate through the blockchain on geth and fill up db
        with block data.
        """
        start_time = datetime.datetime.utcnow()
        self.logger.debug("Processing geth blockchain:")
        self.logger.info("Highest block found as: {}".format(self.max_block_geth))
        self.logger.info(f"Number of blocks to process: {len(self.block_queue)}")

        # Make sure the database isn't missing any blocks up to this point
        self.logger.debug("Verifying that the database isn't missing any blocks...")
        self.max_block_db = 1
        if len(self.block_queue) > 0:
            self.logger.info("Looking for missing blocks...")
            self.max_block_db = self.block_queue.pop()
            for n in tqdm.tqdm(range(1, self.max_block_db)):
                if len(self.block_queue) == 0:
                    # If we have reached the max index of the queue,
                    # break the loop
                    break
                else:
                    # -If a block with number = current index is not in
                    # the queue, add it to the database.
                    # -If the lowest block number in the queue (_n) is
                    # not the current running index (n), then _n > n
                    # and we must add block n to the database. After doing so,
                    # we will add _n back to the queue.
                    _n = self.block_queue.popleft()
                    if n != _n:
                        blocks, transactions = self.collect_block_and_transactions(n)
                        self.block_queue.appendleft(_n)

        # Get all new blocks
        self.logger.info("Processing remainder of the blockchain...")
        blocks_to_pull = range(self.max_block_db, self.max_block_geth)
        chunked_blocks = self.chunk(blocks_to_pull, self.chunk_size)
        total = len([i for i in self.chunk(blocks_to_pull, self.chunk_size)])
        for i,chunk in enumerate(chunked_blocks):
            self.logger.info(f'Processing chunk {i} of {total}')
            for n in tqdm.tqdm(chunk):
                blocks, transactions = self.collect_block_and_transactions(n)
                self.save_blocks_and_transactions_to_database(
                    blocks, transactions)

        end_time = datetime.datetime.utcnow()
        self.logger.info("===============================")
        self.logger.info("Processing complete.")
        self.logger.info(f"Identified {len(self.insertion_errors)} insertion errors.")
        self.logger.info(
            f"These can be viewed in {settings.INSERTION_ERROR_FILE}")
        runtime = time.strftime(
            '%H:%M:%S',
            time.gmtime((end_time - start_time).seconds)
        )
        self.logger.info('----------')
        self.logger.info(f'Runtime (HH:MM:SS): {runtime}')
        self.logger.info("===============================")
