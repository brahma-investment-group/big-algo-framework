from datetime import datetime
import pandas as pd
from dateutil import tz

import os, sys
sys.path.append(os.path.abspath('C:/Users/Owner/Desktop/Projects/big/big-algo-framework'))

from examples.tda_sqzmom import config
from big_algo_framework.strategies.abstract_strategy import *
from big_algo_framework.brokers import td
from big_algo_framework.data.td import TDData
from big_algo_framework.big.options import filter_option_contract
from big_algo_framework.big.helper import truncate

class TDA_SQZMOM(Strategy):
    def __init__(self, order_dict):
        super().__init__()
        self.is_position = False
        self.is_order = False
        self.order_dict = order_dict.copy()

    def check_positions(self):
        # TD Check Order Position Class
        pos = self.td.get_position_by_ticker(self.order_dict)
        orders = self.td.get_order_by_ticker(self.order_dict)

        if pos:
            self.is_position = True
            print("Existing Position Found:", self.order_dict['ticker'])

        if orders:
            self.is_order = True
            print("Existing Order Found:", self.order_dict['ticker'])

    def before_send_orders(self):
       self.order_dict["option_range"] = 'OTM'

       if self.order_dict["putcall"] == "CALL":
           self.order_dict['direction'] = "Bullish"
       else:
           self.order_dict['direction'] = "Bearish"

       self.order_dict["option_action"] = "BUY"
       self.order_dict["option_expiry_days"] = self.order_dict["dte"]
       self.order_dict["option_strikes"] = 1
       self.order_dict["entry"] = self.order_dict["u_price"]

       options_dict = {
            "days_forward": 10,
            "ticker": self.order_dict["ticker"],
            "strike_count": '',
            "include_quotes": "FALSE",
            "strategy": "SINGLE",
            "interval": '',
            "strike": '',
            "range": self.order_dict["option_range"],
            "volatility": '',
            "underlying_price": '',
            "interest_rate": '',
            "days_to_expiration": '',
            "exp_month": "ALL",
            "option_type": "ALL",
            "contract_type": self.order_dict["putcall"]
        }

       data = TDData()
       options_df = data.get_options_data(options_dict, "examples/tda_sqzmom/config.ini")
       filter_option_contract(self.order_dict, options_df)

       self.order_dict["ticker"] = self.order_dict["symbol"]
       price = (self.order_dict["ask"] + self.order_dict["bid"]) / 2

       self.order_dict["lo_quantity"] = self.order_dict["quantity"]
       self.order_dict["lo_limit_price"] = price
       self.order_dict["lo_time_in_force"] = "GTC"
       self.order_dict["lo_action"] = "BUY"
       self.order_dict["lo_instruction"] = "OPEN"
       self.order_dict["lo_sec_type"] = "OPT" # "STK" or "OPT""

       self.order_dict1 = self.order_dict.copy()
       self.order_dict1["lo_limit_price"] = price + (price * .30)
       self.order_dict1["lo_action"] = "SELL"
       self.order_dict1["lo_instruction"] = "CLOSE"

       self.order_dict["slo_quantity"] = self.order_dict["quantity"]
       self.order_dict["slo_limit_price"] = price - (price * .20)
       self.order_dict["slo_stop_price"] = price - (price * .18)
       self.order_dict["slo_time_in_force"] = "GTC"
       self.order_dict["slo_action"] = "SELL"
       self.order_dict["slo_sec_type"] = "OPT" # "STK" or "OPT"
       self.order_dict["slo_instruction"] = "CLOSE" # "OPEN" or "CLOSE"

       self.order_dict["tr_stop_quantity"] = self.order_dict["quantity"]
       self.order_dict["price_link_type"] = "PERCENT"
       self.order_dict["tr_stop_percent"] = 10
       self.order_dict["tr_stop_price"] = 10.00
       self.order_dict["tr_stop_time_in_force"] = "GTC"
       self.order_dict["tr_stop_action"] = "SELL"
       self.order_dict["tr_stop_sec_type"] = "OPT" # "STK" or "OPT"
       self.order_dict["tr_stop_instruction"] = "CLOSE" # "OPEN" or "CLOSE"

    def start(self):
        self.order_dict["account_no"] = config.td_account["account_no"]
        token_path = config.td_account["token_path"]
        api_key = config.td_account["api_key"]
        redirect_uri = config.td_account["redirect_uri"]
        chromedriver_path = config.td_account["chromedriver_path"]

        self.td = td.TDA(token_path, api_key, redirect_uri, chromedriver_path)

    def send_orders(self):

        entry_order = self.td.get_limit_order(self.order_dict)
        tp_order = self.td.get_limit_order(self.order_dict1)
        sl_order = self.td.get_stop_limit_order(self.order_dict)

        tr_stop_order = self.td.get_trailing_stop_order(self.order_dict)

        oco_order = self.td.get_oco_order(tr_stop_order, sl_order)
        trigger_order = self.td.get_oto_order(entry_order, oco_order)

        self.td.send_order(self.order_dict, trigger_order)

    def execute(self):
        self.start()

        self.check_positions()
        if not self.is_position:
            self.check_open_orders()
            if not self.is_order:
                self.before_send_orders()

                if self.order_dict["quantity"] > 0:
                    self.send_orders()
