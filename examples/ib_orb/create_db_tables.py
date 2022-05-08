from big_algo_framework.big.create_db_tables import CreateTables
from big_algo_framework.big.create_db import create_db
from examples.ib_orb import config

database_host = config.database["host"]
database_user = config.database["user"]
database_password = config.database["password"]
database_port = config.database["port"]

db = create_db("market_data", database_host, database_user, database_password, database_port)

table = CreateTables(db)
table.create_orders(["orb_orders"])
table.create_strategy(["orb_strategy"])
