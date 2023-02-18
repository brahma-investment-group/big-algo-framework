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
                 period = "1mo", 
                 interval = "1d",
                 start = None,
                 end = None):
        self.symbol = symbol
        self.period = period
        self.interval = interval
        self.start = start
        self.end = end

    def get_historic_stock_data(self):
        """
        :Parameters:
            period : str
                Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                Either Use period parameter or use start and end
            interval : str
                Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                Intraday data cannot extend last 60 days
            start: str
                Download start date string (YYYY-MM-DD) or _datetime.
                Default is 1900-01-01
            end: str
                Download end date string (YYYY-MM-DD) or _datetime.
                Default is now
            prepost : bool
                Include Pre and Post market data in results?
                Default is False
            auto_adjust: bool
                Adjust all OHLC automatically? Default is True
            back_adjust: bool
                Back-adjusted data to mimic true historical prices
            repair: bool or "silent"
                Detect currency unit 100x mixups and attempt repair.
                If True, fix & print summary. If "silent", just fix.
                Default is False
            keepna: bool
                Keep NaN rows returned by Yahoo?
                Default is False
            proxy: str
                Optional. Proxy server URL scheme. Default is None
            rounding: bool
                Round values to 2 decimal places?
                Optional. Default is False = precision suggested by Yahoo!
            timeout: None or float
                If not None stops waiting for a response after given number of
                seconds. (Can also be a fraction of a second e.g. 0.01)
                Default is 10 seconds.
            debug: boolstart
                If passed as False, will suppress
                error message printing to console.
            raise_errors: bool
                If True, then raise errors as
                exceptions instead of printing to console.
        """
        yfTkr = yf.Ticker(self.symbol)
        yfHist = yfTkr.history(self.period, self.interval, self.start, self.end)

        return yfHist

    def get_historic_option_data(self, symbol, contract_type, strike_count="", include_quotes="False", strategy="SINGLE",
                                 interval="", strike="", range="", volatility="", underlying_price="", interest_rate="",
                                 days_to_expiration="", exp_month="ALL", option_type="ALL", days_forward=10):
            call_options = "not working"
            return call_options
