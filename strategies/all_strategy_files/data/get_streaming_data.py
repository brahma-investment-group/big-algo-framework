from strategies.all_strategy_files.database.database import createDB
from strategies.all_strategy_files.child_classes.data_td_child import TdChild
from tickers import tickers
import configparser

historic_data_table = "us_equity_historic_data"
streaming_data_table = "us_equity_streaming_data"

config = configparser.ConfigParser()
config.read("config.ini")
tda_api = config['TDA_API']
api_key = tda_api["api_key"]
account_id = tda_api["account_id"]
redirect_uri = tda_api["redirect_uri"]

db = createDB("market_data", "config.ini")

act = TdChild(ticker=tickers,
              api_key=api_key,
              account_id=account_id,
              redirect_uri=redirect_uri,
              db=db,
              streaming_data_table=streaming_data_table)

act.get_streaming_equity_data()
