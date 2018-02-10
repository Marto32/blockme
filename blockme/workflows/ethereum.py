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
import tqdm

from blockme.util.db_util import EthereumDatabaseHelper
from blockme.util import crawler_util
from blockme.util.logging_util import get_blockme_logger


class Crawler(object):
    """
    A client to migrate blockchain from geth to mongo.

    Description:
    ------------
    Before starting, make sure geth is running in RPC (port 8545 by default).
    Initializing a Crawler object will automatically scan the blockchain from
    the last block saved in mongo to the most recent block in geth.

    Parameters:
    -----------
    rpc_port: <int> default 8545 	# The port on which geth RPC can be called
    host: <string> default "http://localhost" # The geth host
    start: <bool> default True		# Create the graph upon instantiation

    Usage:
    ------
    Default behavior:
        crawler = Crawler()

    Interactive mode:
        crawler = Crawler(start=False)

    Get the data from a particular block:
        block = crawler.getBlock(block_number)

    Save the block to mongo. This will fail if the block already exists:
        crawler.saveBlock(block)

    """

    def __init__(
        self,
        start=True,
        rpc_port=8545,
        host="http://127.0.0.1",
        delay=0.0001
    ):
        """Initialize the Crawler."""
        self.logger = get_blockme_logger()
        self.logger.debug("Starting Crawler")
        self.url = "{}:{}".format(host, rpc_port)
        self.headers = {"content-type": "application/json"}


        self.blocks_to_insert = []
        self.transactions_to_insert = []

        # Initializes to default host/port = localhost/27017
        self.database_client = EthereumDatabaseHelper(logger=self.logger)

        # The max block number that is in the database
        self.max_block_db = None

        # The max block number in the public blockchain
        self.max_block_geth = None

        # Record errors for inserting block data into the database
        self.insertion_errors = []

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
        self.logger.info(f'Obtaining block {n} from the chain')
        data = self._rpcRequest("eth_getBlockByNumber", [n, True], "result")
        block, transactions = crawler_util.decode_block(data)
        return block, transactions

    def highest_block_eth(self):
        """Find the highest numbered block in geth."""
        num_hex = self._rpcRequest("eth_blockNumber", [], "result")
        return int(num_hex, 16)

    def save_blocks_and_transactions_to_database(self):
        """Insert a given parsed block into database."""
        self.database_client.insert_blocks(self.blocks_to_insert)
        self.database_client.insert_transactions(self.transactions_to_insert)

    def highest_block_database(self):
        """Find the highest numbered block in the database."""
        highest_block = self.database_client.get_latest_block_in_database()
        self.logger.info(f"Highest block found in database: {highest_block}")
        return highest_block

    def collect_block_and_transactions(self, n):
        """Prepare blocks and transactions to add to database"""
        block, transactions = self.get_block_and_associated_transactions(n)
        
        if block:
            self.blocks_to_insert.append(block)
            time.sleep(0.001)
        
        if transactions:
            self.transactions_to_insert.extend(transactions)
            time.sleep(0.001)

    def run(self):
        """
        Run the process.

        Iterate through the blockchain on geth and fill up db
        with block data.
        """
        start_time = datetime.datetime.utcnow()
        self.logger.debug("Processing geth blockchain:")
        self.logger.info("Highest block found as: {}".format(self.max_block_geth))
        self.logger.info("Number of blocks to process: {}".format(
            len(self.block_queue)))

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
                        self.collect_block_and_transactions(n)
                        self.block_queue.appendleft(_n)
                        self.logger.info("Added block {}".format(n))

        # Get all new blocks
        self.logger.info("Processing remainder of the blockchain...")
        for n in tqdm.tqdm(range(self.max_block_db, self.max_block_geth)):
            self.collect_block_and_transactions(n)

        self.save_blocks_and_transactions_to_database()
        end_time = datetime.datetime.utcnow()
        self.logger.info("===============================")
        self.logger.info("Processing complete.")
        runtime = (end_time - start_time).seconds
        self.logger.info(f'Runtime: {runtime} seconds.')
        self.logger.info("===============================")
