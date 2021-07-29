import requests
import pandas as pd
import time
import json
import numpy as np
from mysql.connector import Error

class tdOptions(object):
    def __init__(self, ticker, key):
        self.ticker = ticker
        self.key = key

    def get_options_data(self, from_date, to_date, range="None"):
        """
            Request tdOptions data from TD
        """
        base_url = 'https://api.tdameritrade.com/v1/marketdata/chains?&symbol={stock_ticker}&fromDate={startdate}&toDate={enddate}&range={range}'
        endpoint = base_url.format(stock_ticker=self.ticker, startdate=from_date, enddate=to_date, range=range)

        page = requests.get(url=endpoint, params={'apikey': self.key})
        time.sleep(1)
        content = json.loads(page.content)

        call_options = pd.DataFrame()
        put_options = pd.DataFrame()

        if content["putExpDateMap"] and content["callExpDateMap"]:
            for date in content["callExpDateMap"]:
                for strike in content["callExpDateMap"][date]:
                    for data in content["callExpDateMap"][date][strike]:
                        call_options = call_options.append({'call': data["putCall"],
                                                            'date': date,
                                                            'strike': data["strikePrice"],
                                                            'call_volume': data["totalVolume"],
                                                            'call_oi': data["openInterest"]},
                                                           ignore_index=True)

            for date in content["putExpDateMap"]:
                for strike in content["putExpDateMap"][date]:
                    for data in content["putExpDateMap"][date][strike]:
                        put_options = put_options.append({'put': data["putCall"],
                                                          'date': date,
                                                          'strike': data["strikePrice"],
                                                          'put_volume': data["totalVolume"],
                                                          'put_oi': data["openInterest"]},
                                                         ignore_index=True)

            self.options_chain = pd.merge(call_options, put_options, how='outer', on=['strike', 'date'], suffixes=("_call", "_put"))

            self.options_chain['date'] = self.options_chain['date'].str.split(':', 1).str[0]
            self.options_chain['date'] = pd.to_datetime(self.options_chain['date'])

            self.options_chain["call_put_volume"] = self.options_chain["call_volume"] / self.options_chain["put_volume"]
            self.options_chain["call_put_oi"] = self.options_chain["call_oi"] / self.options_chain["put_oi"]
            self.options_chain["call_volume_oi"] = self.options_chain["call_volume"] / self.options_chain["call_oi"]

            self.options_chain["put_call_volume"] = self.options_chain["put_volume"] / self.options_chain["call_volume"]
            self.options_chain["put_call_oi"] = self.options_chain["put_oi"] / self.options_chain["call_oi"]
            self.options_chain["put_volume_oi"] = self.options_chain["put_volume"] / self.options_chain["put_oi"]

            self.options_chain["ticker"] = self.ticker

            self.options_chain = self.options_chain.replace(np.nan, 0)
            self.options_chain = self.options_chain.replace([np.inf, -np.inf], 999999)

            column_names = ["ticker",
                            "date",
                            "strike",
                            "call",
                            "call_volume",
                            "call_oi",
                            "put",
                            "put_volume",
                            "put_oi",
                            "call_put_volume",
                            "call_put_oi",
                            "call_volume_oi",
                            "put_call_volume",
                            "put_call_oi",
                            "put_volume_oi"]

            #Reorganize columns
            self.options_chain = self.options_chain.reindex(columns=column_names)
            return self.options_chain

        else:
            return call_options