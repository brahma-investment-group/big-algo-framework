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
        self.is_position = False
        self.is_order = False

    def before_send_orders(self):
        pass

    def start(self):
        self.order_dict["account_no"] = config.td_account["account_no"]
        token_path = config.td_account["token_path"]
        api_key = config.td_account["api_key"]
        redirect_uri = config.td_account["redirect_uri"]
        chromedriver_path = config.td_account["chromedriver_path"]

        self.td = td.TDA(token_path, api_key, redirect_uri, chromedriver_path)

    def send_orders(self):
        pass

    def execute(self):
        self.start()

        self.check_positions()
        if not self.is_position:
            self.check_open_orders()
            if not self.is_order:
                self.before_send_orders()

                if self.order_dict["quantity"] > 0:
                    self.send_orders()
