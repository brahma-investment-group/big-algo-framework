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
from strategies.orb.twitter_bot import send_twitter_alerts
from strategies.orb.discord_bot import send_discord_alerts

broker_2 = None

def websocket_con(broker):
    broker.run()

def connect_ib(broker, ip_address, port, ib_client):
    # Connects to interactive brokers with the specified port/client and returns the last order ID.
    broker.connect(ip_address, port, ib_client)
    time.sleep(1)
    broker.reqPositions()
    time.sleep(1)
    broker.reqOpenOrders()
    time.sleep(1)
    broker.reqAccountSummary(9001, "All", AccountSummaryTags.AllTags)
    time.sleep(1)

    con_thread = threading.Thread(target=websocket_con, args=(broker,), daemon=True)
    con_thread.start()
    time.sleep(1)

    broker.reqIds(1)
    time.sleep(1)

    return broker.orderId

app = FastAPI()
q = queue.Queue()

def run_queue():
    while True:
        webhook_message = q.get()

        if webhook_message.passphrase != config.webhook["orb_passphrase"]:
            return {
                "status": "fail",
                "code": "401",
                "message": "Invalid passphrase"
            }

        try:
            print("Webhook Recieved:", webhook_message.dict())

            # CONFIG INPUTS
            database_name = config.database["database_name"]
            orders_table = config.database["orders_table"]
            strategy_table = config.database["orb_strategy_table"]
            account_no = config.ib_account["orb_account_no"]
            ip_address = config.ib_account["orb_ip_address"]
            port = config.ib_account["orb_port"]
            ib_client = config.ib_account["orb_ib_client"]
            total_risk = config.risk_param["orb_total_risk"]
            total_risk_units = config.risk_param["orb_total_risk_units"]
            sec_type = config.contract["orb_sec_type"]
            currency = config.contract["orb_currency"]
            exchange = config.contract["orb_exchange"]

            db = createDB(database_name)
            time.sleep(1)

            global broker_2
            if (broker_2 == None) or (not broker_2.isConnected()):
                broker_2 = IbChild(db, orders_table)
                config.orb_oid = connect_ib(broker_2, ip_address, port, ib_client)

            order_dict = {"broker": broker_2,
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
    await send_discord_alerts(webhook_message)
    await send_twitter_alerts(webhook_message)
