import threading
import os
from ibapi.account_summary_tags import AccountSummaryTags

from strategies.orb import options_specifics
from strategies.all_strategy_files.child_classes.brokers_ib_child import *
from strategies.all_strategy_files.database.database import createDB
from strategies.orb.tv_orb import ORB
from strategies.orb import tickers


ib_connection = 3

db = createDB("market_data", "../all_strategy_files/database/config.ini")
time.sleep(1)

broker = IbChild(db)
broker.connect('127.0.0.1', 7497, ib_connection)
time.sleep(1)
broker.reqPositions()
time.sleep(1)
broker.reqOpenOrders()
time.sleep(1)

# broker.reqAccountUpdates(True, '')

# broker.reqAccountSummary(9001, "All", AccountSummaryTags.AllTags)
# time.sleep(1)

def websocket_con():
    broker.run()

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(30) #NEED 30 seconds to make sure broker starts to run before going through tickers!!!

def start_main(webhook_message):
    order_dict = dict()
    dashboard_dict = dict()

    ticker = webhook_message['ticker']
    time_frame = webhook_message['time_frame']
    entry_time = webhook_message['entry_time']

    entry = webhook_message['entry']
    sl = webhook_message['sl']
    tp1 = webhook_message['tp1']
    tp2 = webhook_message['tp2']
    risk = webhook_message['risk']

    direction = webhook_message['direction']
    open_action = webhook_message['open_action']   # "BUY"/ "SELL"
    close_action = webhook_message['close_action']


    order_dict = {"ticker": ticker,
                  "time_frame": time_frame,
                  "entry_time": entry_time,

                  "entry": entry,
                  "sl": sl,
                  "tp1": tp1,
                  "tp2": tp2,
                  "risk": risk,

                  "direction": direction,
                  "open_action": open_action,
                  "close_action": close_action,

                  "sec_type": options_specifics.sec_type,
                  "currency": options_specifics.currency,
                  "exchange": options_specifics.exchange,
                  "primary_exchange": tickers.ticker_universe[ticker]["primary_exchange"],
                  }

    print(datetime.now(), ": ", ticker)
    x = ORB(broker, ticker, db, order_dict)
    x.execute()

def run_start():
    order_dict = dict()
    ticker = ""

    y = ORB(broker, ticker, db, order_dict)
    y.start()