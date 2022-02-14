import queue

from fastapi import FastAPI
from pydantic import BaseModel
import traceback
import threading
import datetime
from ibapi.account_summary_tags import AccountSummaryTags
from strategies.all_strategy_files.child_classes.brokers_ib_child import *
from strategies.all_strategy_files.database.database import createDB
from strategies.orb.strategy import ORB
from strategies.orb import config
from strategies.orb.twitter import send_alert

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
sec_type = config.contract["sec_type"]
currency = config.contract["currency"]
exchange = config.contract["exchange"]

db = createDB(database_name)
time.sleep(1)

broker = IbChild(db, orders_table)
broker.connect(ip_address, port, ib_client)
time.sleep(1)
broker.reqPositions()
time.sleep(1)
broker.reqOpenOrders()
time.sleep(1)
broker.reqAccountSummary(9001, "All", AccountSummaryTags.AllTags)
time.sleep(1)

def websocket_con():
    broker.run()

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(30) #NEED 30 seconds to make sure broker starts to run before going through tickers!!!

broker.reqIds(1)
time.sleep(1)
config.OID = broker.orderId

app = FastAPI()
q = queue.Queue()

def run_queue():
    while True:
        webhook_message = q.get()

        if webhook_message.passphrase != config.webhook["passphrase"]:
            return {
                "status": "fail",
                "code": "401",
                "message": "Invalid passphrase"
            }

        try:
            print("Webhook Recieved:", webhook_message.dict())

            order_dict = {"broker": broker,
                          "db": db,
                          "ticker": webhook_message.ticker,
                          "primary_exchange": webhook_message.exchange,
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
                          "sec_type": sec_type,
                          "currency": currency,
                          "exchange": exchange,
                          "lastTradeDateOrContractMonth": "",
                          "strike": 0.0,
                          "right": "",
                          "multiplier": 0,
                          "ask_price": 0.0,
                          "orders_table": orders_table,
                          "strategy_table": strategy_table,
                          "account_no": account_no,
                          "total_risk": total_risk,
                          "total_risk_units": total_risk_units,
                          }

            print(datetime.datetime.now(), ": ", order_dict["ticker"])
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

        q.task_done()

queue_thread = threading.Thread(target=run_queue, daemon=True)
queue_thread.start()

class webhook_message(BaseModel):
    ticker: str
    exchange: str
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

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post('/orb/options')
async def orb_options(webhook_message: webhook_message):
    q.put(webhook_message)

@app.post('/twitter')
def webhook(webhook_message: webhook_message):

    if webhook_message.passphrase != config.webhook["passphrase"]:
        return {
            "status": "fail",
            "code": "401",
            "message": "Invalid passphrase"
        }

    try:
        time.sleep(1800)
        send_alert(webhook_message)

    except Exception as e:
        print("[X]", "Error:\n>", e)
        return "Error", 400