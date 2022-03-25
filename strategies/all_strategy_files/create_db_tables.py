from big_algo_framework.big.create_db_tables import CreateTables
from big_algo_framework.big.database import createDB

db = createDB("market_data", "config.ini")

table = CreateTables(db)
table.create_orders(["orb_orders", "dummy_orders"])
table.create_dashboard(["orb_strategy", "dummy_strat"])
