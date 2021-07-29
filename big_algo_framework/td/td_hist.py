import tda
import time
import pprint
import configparser

class tdHist:
    def __init__(self, ticker, db, period, periodType, freq, freqType, timeframe, start_dt, end_dt, credentials_path='./ameritrade-credentials.json'):
        config = configparser.ConfigParser()
        config.read("config.ini")
        tda_api = config['TDA_API']

        self.api_key = tda_api["api_key"]
        self.redirect_uri = tda_api["redirect_uri"]
        self.credentials_path = credentials_path
        self.ticker = ticker
        self.db = db
        self.period = period
        self.periodType = periodType
        self.freq = freq
        self.freqType = freqType
        self.timeframe = timeframe
        self.start_dt = start_dt
        self.end_dt = end_dt

        try:
            self.tda_client = tda.auth.client_from_token_file(self.credentials_path, self.api_key)

        except FileNotFoundError:
            from selenium import webdriver

            with webdriver.Chrome() as driver:
                self.tda_client = tda.auth.client_from_login_flow(driver, self.api_key, self.redirect_uri, self.credentials_path)

    def get_hist(self):
        """
            Fetch historic data from TDA client
        """
        response = self.tda_client.get_price_history(self.ticker[0],
                                                     period_type=self.periodType,
                                                     period=self.period,
                                                     frequency_type=self.freqType,
                                                     frequency=self.freq,
                                                     need_extended_hours_data=False,
                                                     start_datetime=self.start_dt,
                                                     end_datetime=self.end_dt)
        return response.json()
