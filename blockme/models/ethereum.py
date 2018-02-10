import datetime
import settings

from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event
from sqlalchemy.schema import DDL
from sqlalchemy.orm import relationship


# db = create_engine(db_string)
base = declarative_base()


class Block(base):
    """
    A table representation of select fields for an ethereum block

    {
        "number": "0xf4241",
        "hash": "0xcb5cab7266694daa0d28cbf40496c08dd30bf732c41e0455e7ad389c10d79f4f",
        "parentHash": "0x8e38b4dbf6b11fcc3b9dee84fb7986e29ca0a02cecd8977c161ff7333329681e",
        "nonce": "0x9112b8c2b377fbe8",
        "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
        "logsBloom": "0x0",
        "transactionsRoot": "0xc61c50a0a2800ddc5e9984af4e6668de96aee1584179b3141f458ffa7d4ecec6",
        "stateRoot": "0x7dd4aabb93795feba9866821c0c7d6a992eda7fbdd412ea0f715059f9654ef23",
        "receiptRoot": "0xb873ddefdb56d448343d13b188241a4919b2de10cccea2ea573acf8dbc839bef",
        "miner": "0x2a65aca4d5fc5b5c859090a6c34d164135398226",
        "difficulty": "0xb6b4bbd735f",
        "totalDifficulty": "0x63056041aaea71c9",
        "size": "0x292",
        "extraData": "0xd783010303844765746887676f312e352e31856c696e7578",
        "gasLimit": "0x2fefd8",
        "gasUsed": "0x5208",
        "timestamp": "0x56bfb41a",
        "transactions": [...]
    }
    """

    __tablename__ = 'block'
    __table_args__ = {"schema": settings.ETHEREUM_SCHEMA}

    number = Column(BigInteger, primary_key=True, autoincrement=False, index=True)
    block_hash = Column(String(256), unique=True)
    parent_hash = Column(String(256))
    nonce = Column(String(256))
    transactions_root = Column(String(256))
    state_root = Column(String(256))
    receipt_root = Column(String(256))
    miner = Column(String(256))
    difficulty = Column(String(256))
    total_difficulty = Column(String(256))
    size = Column(BigInteger)
    gas_limit = Column(BigInteger)
    gase_used = Column(BigInteger)
    timestamp = Column(DateTime, index=True)
    dt_inserted = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )

    # block_numbers = relationship(
    #     'Transaction',
    #     primaryjoin='Block.number==Transaction.block_number',
    #     foreign_keys='Block.number')
    # block_hashes = relationship(
    #     'Transaction',
    #     primaryjoin='Block.block_hash==Transaction.block_hash',
    #     foreign_keys='Block.block_hash')

class Transaction(base):
    """
    A table representation of select fields for an ethereum transaction

    {
        "hash": "0xefb6c796269c0d1f15fdedb5496fa196eb7fb55b601c0fa527609405519fd581",
        "nonce": "0x2a121",
        "blockHash": "0xcb5cab7266694daa0d28cbf40496c08dd30bf732c41e0455e7ad389c10d79f4f",
        "blockNumber": "0xf4241",
        "transactionIndex": "0x0",
        "from": "0x2a65aca4d5fc5b5c859090a6c34d164135398226",
        "to": "0x819f4b08e6d3baa33ba63f660baed65d2a6eb64c",
        "value": "0xe8e43bc79c88000",
        "gas": "0x15f90",
        "gasPrice": "0xba43b7400",
        "input": "0x"
    }
    """

    __tablename__ = 'transaction'
    __table_args__ = {"schema": settings.ETHEREUM_SCHEMA}

    db_id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_hash = Column(String(256), unique=True)
    block_number = Column(BigInteger, ForeignKey(Block.number), index=True)
    block_hash = Column(String(256), ForeignKey(Block.block_hash))
    nonce = Column(String(256))
    transaction_index = Column(BigInteger)
    sender = Column(String(256), index=True)
    receipt = Column(String(256), index=True)
    value = Column(Numeric(20,10))
    gas = Column(BigInteger)
    gas_price = Column(BigInteger)
    dt_inserted = Column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )

    block_numbers = relationship("Block", foreign_keys='Transaction.block_number')
    block_hashes = relationship("Block", foreign_keys='Transaction.block_hash')


event.listen(
    base.metadata,
    "before_create",
    DDL(f"CREATE SCHEMA IF NOT EXISTS {settings.ETHEREUM_SCHEMA}").execute_if(
        dialect='postgresql'
    )
)

event.listen(
    base.metadata,
    "after_drop",
    DDL(f"DROP SCHEMA IF EXISTS {settings.ETHEREUM_SCHEMA}").execute_if(
        dialect='postgresql'
    )
)
