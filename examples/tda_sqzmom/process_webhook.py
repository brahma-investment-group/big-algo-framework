import os, sys
sys.path.append(os.path.abspath('C:/Users/Owner/Desktop/Projects/big/big-algo-framework'))
from examples.tda_sqzmom import config
from examples.tda_sqzmom.strategy import TDA_SQZMOM
import datetime

def process_webhook(webhook_message):
    if webhook_message.passphrase != config.webhook["passphrase"]:
        return {
            "status": "fail",
            "code": "401",
            "message": "Invalid passphrase"
        }
    try:
        order_dict = {
            "u_price": webhook_message.close,
            "quantity": webhook_message.quantity,
            "ticker": webhook_message.ticker,
            "instruction": webhook_message.instruction,
            "putcall": webhook_message.callput,
            "dte": webhook_message.dte
        }

        print(datetime.datetime.now(), ": ", order_dict["ticker"])
        x = TDA_SQZMOM(order_dict)
        x.execute()

    except Exception as exc:
        print(f'exception in option_order: {str(exc)}')
        return {
            "status": "error",
            "code": "500",
            "message": f"{str(Exception)}"
        }
