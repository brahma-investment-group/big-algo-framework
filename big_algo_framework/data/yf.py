from big_algo_framework.data.abstract_data import Data
import datetime
import pandas as pd
import requests
import time
import json
import yfinance as yf

class YFData(Data):
    def __init__(self, 
                 symbol: str = "",
                 period_type: str = "mo",
                 period: str = "1",
                 frequency_type: str = "d",
                 frequency: str = "1",
                 start: str = None,
                 end: str = None):
        """
            Creates and returns a YFData object.

            :param symbol: The symbol.
            :param period_type: Possible values are "d", "mo", "y. Either Use period parameters or use start and end.
            :param period: Possible values are  "1","5" (d), "1","3","6" (mo), "1","2","5","10" (y), "ytd", "max". Either Use period parameters or use start and end.
            :param frequency_type: Possible values are "m", "h", "d", "wk", "mo". Intraday data cannot exceed last 60 days
            :param frequency: Possible values are "1","2","5","15","30","60","90" (m), "1" (h), "1","5" (d), "1" (wk), "1","3" (mo). Intraday data cannot exceed last 60 days
            :param start: Download start date string (YYYY-MM-DD) or _datetime. Default is 1900-01-01
            :param end: Download end date string (YYYY-MM-DD) or _datetime. Default is now
        """

        self.symbol = symbol
        self.period_type = period_type
        self.period = period
        self.frequency_type = frequency_type
        self.frequency = frequency
        self.start = start
        self.end = end

    def get_historic_stock_data(self):
        period = self.period + self.period_type
        interval = self.frequency + self.frequency_type

        yfTkr = yf.Ticker(self.symbol)
        yfDF = yfTkr.history(period = period, interval = interval, start = self.start, end = self.end)
        yfHist = yfDF.to_json(orient='records')

        return yfHist

    def get_historic_option_data(self, symbol, contract_type, strike_count="", include_quotes="False", strategy="SINGLE",
                                 interval="", strike="", range="", volatility="", underlying_price="", interest_rate="",
                                 days_to_expiration="", exp_month="ALL", option_type="ALL", days_forward=10):
            pass
