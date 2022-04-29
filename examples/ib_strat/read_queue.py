import queue
import traceback
import datetime
import threading
import time
from big_algo_framework.brokers.ib import IB
from big_algo_framework.big.create_db import create_db
from examples.ib_strat import config
from examples.ib_strat.strategy import IBSTRAT

ib_strat_queue = queue.Queue()
broker_3 = None

def run_ib_strat():
    while True:
        webhook_message = ib_strat_queue.get()

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
            orders_table = config.database["strat_orders_table"]
            strategy_table = config.database["strat_strategy_table"]
            account_no = config.ib_account["orb_account_no"]
            ip_address = config.ib_account["orb_ip_address"]
            port = config.ib_account["orb_port"]
            ib_client = config.ib_account["strat_ib_client"]
            funds = config.risk_param["orb_funds"]
            total_risk = config.risk_param["orb_total_risk"]
            total_risk_units = config.risk_param["orb_total_risk_units"]
            max_position_percent = config.risk_param["orb_max_position_percent"]
            sec_type = config.contract["orb_sec_type"]
            option_action = config.contract["orb_option_action"]
            option_range = config.contract["orb_option_range"]
            option_strikes = config.contract["orb_option_strikes"]
            option_expiry_days = config.contract["orb_option_expiry_days"]
            currency = config.contract["orb_currency"]
            exchange = config.contract["orb_exchange"]

            db = create_db(database_name, "examples/all_strategy_files/config.ini")
            time.sleep(1)

            global broker_3
            if (broker_3 == None) or (not broker_3.isConnected()):
                broker_3 = IB()
                config.strat_oid = broker_3.connect_broker(broker_3, ip_address, port, ib_client)

            order_dict = {"broker": broker_3,
                          "db": db,
                          "order_id": config.strat_oid,
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
                          }

            print(datetime.datetime.now(), ": ", order_dict["ticker"])
            x = IBSTRAT(order_dict)
            x.execute()

        except Exception as exc:
            traceback.print_exc()
            print(f'exception in orb_options: {str(exc)}')

            return {
                "status": "error",
                "code": "500",
                "message": f"{str(Exception)}"
            }

        ib_strat_queue.task_done()

ib_strat_thread = threading.Thread(target=run_ib_strat, daemon=True)
ib_strat_thread.start()