import queue
import traceback
import datetime
import threading
import time
from big_algo_framework.brokers.ib import IB
from big_algo_framework.big.create_db import create_db
from examples.ib_orb import config
from examples.ib_orb.strategy import IBORB

ib_orb_queue = queue.Queue()
broker_2 = None

def run_ib_orb():
    while True:
        webhook_message = ib_orb_queue.get()

        if webhook_message.passphrase != config.webhook["passphrase"]:
            return {
                "status": "fail",
                "code": "401",
                "message": "Invalid passphrase"
            }

        try:
            print("Webhook Recieved:", webhook_message.dict())

            # CONFIG INPUTS
            database_host = config.database["host"]
            database_user = config.database["user"]
            database_password = config.database["password"]
            database_port = config.database["port"]
            database_name = config.database["database_name"]
            orders_table = config.database["orders_table"]
            strategy_table = config.database["strategy_table"]
            account_no = config.ib_account["account_no"]
            ip_address = config.ib_account["ip_address"]
            port = config.ib_account["port"]
            ib_client = config.ib_account["ib_client"]
            funds = config.risk_param["funds"]
            total_risk = config.risk_param["total_risk"]
            total_risk_units = config.risk_param["total_risk_units"]
            max_position_percent = config.risk_param["max_position_percent"]
            sec_type = config.contract["sec_type"]
            option_action = config.contract["option_action"]
            option_range = config.contract["option_range"]
            option_strikes = config.contract["option_strikes"]
            option_expiry_days = config.contract["option_expiry_days"]
            currency = config.contract["currency"]
            exchange = config.contract["exchange"]
            tda_api = config.tda["api"]

            db = create_db(database_name, database_host, database_user, database_password, database_port)
            time.sleep(1)

            global broker_2
            if (broker_2 == None) or (not broker_2.isConnected()):
                broker_2 = IB()
                config.ib_order_id = broker_2.connect_broker(broker_2, ip_address, port, ib_client)

            order_dict = {"broker": broker_2,
                          "db": db,
                          "order_id": config.ib_order_id,
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
                          "is_close": webhook_message.is_close,
                          "sec_type": sec_type,
                          "option_action": option_action,
                          "option_range": option_range,
                          "option_strikes": option_strikes,
                          "option_expiry_days": option_expiry_days,
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
                          "funds": funds,
                          "total_risk": total_risk,
                          "total_risk_units": total_risk_units,
                          "max_position_percent": max_position_percent,
                          "tda_api": tda_api
                          }

            print(datetime.datetime.now(), ": ", order_dict["ticker"])
            x = IBORB(order_dict)
            x.execute()

        except Exception as exc:
            traceback.print_exc()
            print(f'exception in orb_options: {str(exc)}')

            return {
                "status": "error",
                "code": "500",
                "message": f"{str(Exception)}"
            }

        ib_orb_queue.task_done()

ib_orb_thread = threading.Thread(target=run_ib_orb, daemon=True)
ib_orb_thread.start()