import time

from fastapi import FastAPI
from pydantic import BaseModel
import traceback
import threading
import datetime
from ibapi.account_summary_tags import AccountSummaryTags
from strategies.all_strategy_files.child_classes.brokers_ib_child import *
from strategies.all_strategy_files.database.database import createDB
from strategies.orb.strategy import ORB
from strategies.all_strategy_files.all_strategies import tickers
from strategies.orb import config

# CONFIG INPUTS
orders_table = config.database["orders_table"]
strategy_table = config.database["strategy_table"]
database_name = config.database["database_name"]
account_no = config.ib_account["account_no"]
ip_address = config.ib_account["ip_address"]
port = config.ib_account["port"]
ib_client = config.ib_account["ib_client"]
total_risk = config.risk_param["total_risk"]
total_risk_units = config.risk_param["total_risk_units"]

db = createDB(database_name)
time.sleep(1)

broker = IbChild(db, orders_table)
broker.connect(ip_address, port, ib_client)
time.sleep(1)
broker.reqPositions()
time.sleep(1)
broker.reqOpenOrders()
time.sleep(1)

# broker.reqAccountUpdates(True, account_no)

broker.reqAccountSummary(9001, "All", AccountSummaryTags.AllTags)
time.sleep(1)

def websocket_con():
    broker.run()

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(30) #NEED 30 seconds to make sure broker starts to run before going through tickers!!!

class webhook_message(BaseModel):
    ticker: str
    time_frame: float
    entry_time: int
    entry: float
    sl: float
    tp1: float
    tp2: float
    risk: float
    direction: str
    open_action: str
    close_action: str
    passphrase: str
    is_close: int

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/orb/options')
async def orb_options(webhook_message: webhook_message):
    print("Webhook Recieved:", webhook_message.dict())

    if webhook_message.passphrase != config.webhook["passphrase"]:
        return {
            "status": "fail",
            "code": "401",
            "message": "Invalid passphrase"
        }

    try:
        ticker = webhook_message.ticker

        order_dict = {"broker": broker,
                      "db": db,
                      "ticker": ticker,
                      "time_frame": webhook_message.time_frame,
                      "entry_time": webhook_message.entry_time,
                      "entry": webhook_message.entry,
                      "sl": webhook_message.sl,
                      "tp1": webhook_message.tp1,
                      "tp2": webhook_message.tp2,
                      "risk": webhook_message.risk,
                      "direction": webhook_message.direction,
                      "open_action": webhook_message.open_action,
                      "close_action": webhook_message.close_action,
                      "is_close": webhook_message.is_close,
                      "sec_type": config.contract["sec_type"],
                      "currency": config.contract["currency"],
                      "exchange": config.contract["exchange"],
                      "primary_exchange": tickers.ticker_universe[ticker]["primary_exchange"],
                      "orders_table": orders_table,
                      "strategy_table": strategy_table,
                      "account_no": account_no,
                      "total_risk": total_risk,
                      "total_risk_units": total_risk_units,
                      }

        print(datetime.datetime.now(), ": ", ticker)
        x = ORB(order_dict)
        x.execute()

    except Exception as exc:
        traceback.print_exc()
        print(f'exception in orb_options: {str(exc)}')

        return {
            "status": "error",
            "code": "500",
            "message": f"{str(Exception)}"
        }
