from sample_strategies.data.data import *
from big_algo_framework.big.database import createDB

db = createDB("market_data", "config.ini")
tickers = ["PEP", "LMT"]
historic_data_table = "historic_data"
streaming_data_table = "streaming_data"

data = getData(db, tickers, historic_data_table, streaming_data_table)

data.get_historic_data()