import time
import pandas as pd
from big_algo_framework.big.database import createDB
from big_algo_framework.big.indicators import *
from datetime import datetime
import pytz
from zoneinfo import ZoneInfo

class strategyRules():
    def __init__(self, ticker, df):
        self.indi = BIGIndicators()
        self.ticker = ticker
        self.df = df

    def becomes_ftfc_at_price(self, price):
        open1 = self.df['open'].iloc[-1]

        if price >= open1:
            return "Bullish"

        if price <= open1:
            return "Bearish"

    def is_not_ib(self, higher_price, lower_price):
        close1 = self.df['close'].iloc[-1]

        if close1 > higher_price or close1 < lower_price:
            return True
        else:
            return False
