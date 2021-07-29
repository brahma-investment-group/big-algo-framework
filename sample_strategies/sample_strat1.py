from big_algo_framework.ib.ibclient import *
import threading
import time

from strategies.strat import Strat

db = createDB("market_data", "data/config.ini")
time.sleep(2)

app = BIGIBClient()
app.connect('127.0.0.1', 7497, 1)
time.sleep(3)

app.reqPositions()
time.sleep(3)

app.reqOpenOrders()
time.sleep(3)

def websocket_con():
    app.run()

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(3)

def start_main(tickers):
    while True:
        for ticker in tickers:
            dashboard_dict = {}
            strat = Strat(app, ticker, db)
            strat.checkTradeConditions("Bullish", dashboard_dict)
