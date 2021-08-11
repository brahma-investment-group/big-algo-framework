import requests
import pandas as pd
import time
import configparser

class FinnHubData():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("data/config.ini")
        finnhub = config['FINNHUB']

        self.key = finnhub["api_key"]
        self.earning = dict()

    def get_earnings_data(self, from_date, to_date):
        r = requests.get(f'https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&token={self.key}')
        time.sleep(1)
        self.earning = pd.DataFrame(r.json()['earningsCalendar'])
