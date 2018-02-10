# Blockme

NOTE: While not a direct fork, this was inspired by and derived from [Alex Miller's](https://github.com/alex-miller-0) [ethereum blockchain parser](https://github.com/alex-miller-0/Ethereum_Blockchain_Parser). If you enjoy this, or find it useful, please go ahead and give him a star as well.

# Installation

## Prerequisites

This has been built and tested on [python 3.6](https://www.python.org/downloads/release/python-360/). Please ensure you have the latest version.

It his highly recommended that you use a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) to ensure that anything installed doesn't conflict with your standard environment.

We use `PostgreSQL` as our relational database of choice. `blockme` uses [SQL Alchemy](https://www.sqlalchemy.org/) so if you prefer to use another database, ensure it's compatabily with `sqlalchemy` and enter the credentials (and modify the url in the `settings` file) as needed. You can install postgres using your preferred package manager (`brew`, `apt`, etc.) or from source [here](https://www.postgresql.org/download/).

Ensure you have [`geth`](https://github.com/ethereum/go-ethereum/wiki/geth) installed. `blockme` makes use of the JSON-RPC endpoint to parse the ethereum blockchain. You can read more about the JSON-RPC endpoint [here](https://github.com/ethereum/wiki/wiki/JSON-RPC#json-rpc-endpoint).

**WARNING** if you run this on a geth client containing an account that has ether in it, make sure you put a firewall 8545 or whatever port you run geth RPC on.

## Setup

Clone this repo and install the requirements using your preferred package manager (ideally you're using a virtualenv):

```shell
git clone https://github.com/Marto32/blockme.git
cd blockme
pip install -r requirements.txt
```

## Launch

Launch postgresql.

Launch geth using the following command:

```shell
geth --rpc
```

More `geth` CLI options may be found [here](https://github.com/ethereum/go-ethereum/wiki/Command-Line-Options).

Set environment variables (or use defaults for local development):

```shell
export PG_USERNAME='your_database_username'        # Defaults to $USER env var
export PG_PASSWORD='your_database_user_password'   # Defaults to ''
export PG_HOST='database_host'                     # Defaults to localhost
export PG_PORT=5432                                # Defaults to the 5432
export PG_DATABASE_NAME='blockme_db'               # Defaults to 'devdb'
```

Additional configuration options can be found in the `settings.py` file.

Run blockme

```shell
python runner.py
```

## Analysis

The data will now be available for querying in the database. To get an idea of the schema, take a look at the objects in the `blockme/models` directory.

# Moving forward

Bitcoin and other chain support is planned as future work.

# Contributing

If you've found a bug, or want to contribute, please feel free to create an issue or PR.
