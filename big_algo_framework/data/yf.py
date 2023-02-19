from big_algo_framework.data.abstract_data import Data
import datetime
import pandas as pd
import requests
import time
import json
import yfinance as yf

class YFData(Data):
    def __init__(self, 
                 symbol = "", 
                 period_type = "mo",
                 period = "1", 
                 frequency_type = "d",
                 frequency = "1",
                 start = None,
                 end = None):

        self.symbol = symbol
        self.period_type = period_type
        self.period = period
        self.frequency_type = frequency_type
        self.frequency = frequency
        self.start = start
        self.end = end
        self.yfHist = ""
#   def get_historic_stock_data(self, symbol, period_type, period, frequency_type, frequency, extended_hours_data='false'):
    def get_historic_stock_data(self):
        """
        :Parameters:
            period_type : str
                Valid periods_types: d, mo, y
                Either Use period parameters or use start and end
            period : str
                Valid periods: 1,5 (d), 1,3,6 (mo), 1,2,5,10 (y), ytd, max
                Either Use period parameters or use start and end
            frequency_type : str
                Valid frequency_type: m, h, d, wk, mo
                Intraday data cannot exceed last 60 days 
            frequency : str
                Valid intervals: 1,2,5,15,30,60,90 (m),1 (h), 1,5 (d), 1 (wk), 1,3 (mo)
                Intraday data cannot exceed last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
        """
        period = self.period + self.period_type
        interval = self.frequency + self.frequency_type

        yfTkr = yf.Ticker(self.symbol)
        self.yfHist = yfTkr.history(period = period, interval = interval, start = self.start, end = self.end)
        return self.yfHist
        

    def get_historic_option_data(self, symbol, contract_type, strike_count="", include_quotes="False", strategy="SINGLE",
                                 interval="", strike="", range="", volatility="", underlying_price="", interest_rate="",
                                 days_to_expiration="", exp_month="ALL", option_type="ALL", days_forward=10):
            pass
