from abstract_data import Data
import v20
import json

class Oanda(Data):
    def __init__(self):
        API = "api-fxtrade.oanda.com"
        STREAM_API = "stream-fxtrade.oanda.com"
        ACCESS_TOKEN = None
        ACCOUNT_ID = None

        self.api = v20.Context(hostname=API, token=ACCESS_TOKEN, port=443)
        self.stream_api = v20.Context(hostname=STREAM_API, token=ACCESS_TOKEN, port=443)

    def get_hist_equity_data(self):
        """Fetch historic equity data from TDA client"""
        ACCOUNT_ID = None

        response = self.api.pricing.get(accountID=ACCOUNT_ID, instruments="USD_CAD")

        print(response.json())
        # json.loads(response.body["prices"][0].json())

        return response.json()

    def get_streaming_equity_data(self):
        pass

    def get_hist_options_data(self):
        """Fetch historic options data from TDA client"""
        pass

    def get_streaming_options_data(self):
        pass


x = Oanda()
print(x.get_hist_equity_data())
