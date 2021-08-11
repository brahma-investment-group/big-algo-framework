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
                        call_options = call_options.append({
                                                            'strikePrice': data["strikePrice"],
                                                            'expirationDate': data["expirationDate"],
                                                            'daysToExpiration': data["daysToExpiration"],
                                                            'call': data["putCall"],
                                                            'call_bid': data["bid"],
                                                            'call_ask': data["ask"],
                                                            'call_last': data["last"],
                                                            'call_mark': data["mark"],
                                                            'call_bidSize': data["bidSize"],
                                                            'call_askSize': data["askSize"],
                                                            'call_bidAskSize': data["bidAskSize"],
                                                            'call_lastSize': data["lastSize"],
                                                            'call_highPrice': data["highPrice"],
                                                            'call_lowPrice': data["lowPrice"],
                                                            'call_openPrice': data["openPrice"],
                                                            'call_closePrice': data["closePrice"],
                                                            'call_totalVolume': data["totalVolume"],
                                                            'call_tradeDate': data["tradeDate"],
                                                            'call_tradeTimeInLong': data["tradeTimeInLong"],
                                                            'call_quoteTimeInLong': data["quoteTimeInLong"],
                                                            'call_netChange': data["netChange"],
                                                            'call_volatility': data["volatility"],
                                                            'call_delta': data["delta"],
                                                            'call_gamma': data["gamma"],
                                                            'call_theta': data["theta"],
                                                            'call_vega': data["vega"],
                                                            'call_rho': data["rho"],
                                                            'call_openInterest': data["openInterest"],
                                                            'call_timeValue': data["timeValue"],
                                                            'call_theoreticalOptionValue': data["theoreticalOptionValue"],
                                                            'call_theoreticalVolatility': data["theoreticalVolatility"],
                                                            'call_optionDeliverablesList': data["optionDeliverablesList"],
                                                            'call_expirationType': data["expirationType"],
                                                            'call_lastTradingDay': data["lastTradingDay"],
                                                            'call_multiplier': data["multiplier"],
                                                            'call_percentChange': data["percentChange"],
                                                            'call_markChange': data["markChange"],
                                                            'call_markPercentChange': data["markPercentChange"]},
                                                           ignore_index=True)

            for date in content["putExpDateMap"]:
                for strike in content["putExpDateMap"][date]:
                    for data in content["putExpDateMap"][date][strike]:
                        put_options = put_options.append({
                                                          'strikePrice': data["strikePrice"],
                                                          'expirationDate': data["expirationDate"],
                                                          'daysToExpiration': data["daysToExpiration"],
                                                          'put': data["putCall"],
                                                          'put_bid': data["bid"],
                                                          'put_ask': data["ask"],
                                                          'put_last': data["last"],
                                                          'put_mark': data["mark"],
                                                          'put_bidSize': data["bidSize"],
                                                          'put_askSize': data["askSize"],
                                                          'put_bidAskSize': data["bidAskSize"],
                                                          'put_lastSize': data["lastSize"],
                                                          'put_highPrice': data["highPrice"],
                                                          'put_lowPrice': data["lowPrice"],
                                                          'put_openPrice': data["openPrice"],
                                                          'put_closePrice': data["closePrice"],
                                                          'put_totalVolume': data["totalVolume"],
                                                          'put_tradeDate': data["tradeDate"],
                                                          'put_tradeTimeInLong': data["tradeTimeInLong"],
                                                          'put_quoteTimeInLong': data["quoteTimeInLong"],
                                                          'put_netChange': data["netChange"],
                                                          'put_volatility': data["volatility"],
                                                          'put_delta': data["delta"],
                                                          'put_gamma': data["gamma"],
                                                          'put_theta': data["theta"],
                                                          'put_vega': data["vega"],
                                                          'put_rho': data["rho"],
                                                          'put_openInterest': data["openInterest"],
                                                          'put_timeValue': data["timeValue"],
                                                          'put_theoreticalOptionValue': data["theoreticalOptionValue"],
                                                          'put_theoreticalVolatility': data["theoreticalVolatility"],
                                                          'put_optionDeliverablesList': data["optionDeliverablesList"],
                                                          'put_expirationType': data["expirationType"],
                                                          'put_lastTradingDay': data["lastTradingDay"],
                                                          'put_multiplier': data["multiplier"],
                                                          'put_percentChange': data["percentChange"],
                                                          'put_markChange': data["markChange"],
                                                          'put_markPercentChange': data["markPercentChange"]},
                                                         ignore_index=True)

            self.options_chain = pd.merge(call_options, put_options, how='outer', on=['strikePrice', 'expirationDate', 'daysToExpiration'], suffixes=("_call", "_put"))
            self.options_chain['expirationDate'] = pd.to_datetime(self.options_chain['expirationDate'], unit = "ms")

            self.options_chain["call_put_volume"] = self.options_chain["call_totalVolume"] / self.options_chain["put_totalVolume"]
            self.options_chain["call_put_oi"] = self.options_chain["call_openInterest"] / self.options_chain["put_openInterest"]
            self.options_chain["call_volume_oi"] = self.options_chain["call_totalVolume"] / self.options_chain["call_openInterest"]

            self.options_chain["put_call_volume"] = self.options_chain["put_totalVolume"] / self.options_chain["call_totalVolume"]
            self.options_chain["put_call_oi"] = self.options_chain["put_openInterest"] / self.options_chain["call_openInterest"]
            self.options_chain["put_volume_oi"] = self.options_chain["put_totalVolume"] / self.options_chain["put_openInterest"]

            self.options_chain["ticker"] = self.ticker

            self.options_chain = self.options_chain.replace(np.nan, 0)
            self.options_chain = self.options_chain.replace([np.inf, -np.inf], 999999)

            return self.options_chain

        else:
            return call_options