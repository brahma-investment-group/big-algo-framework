from big_algo_framework.data.abstract_data import Data
import configparser
import datetime
import pandas as pd
import numpy as np
import requests
import time
import json

class TDData(Data):
    def __init__(self):
        pass

    def get_options_data(self, options_dict, api_key):
        from_date = datetime.date.today()
        to_date = from_date + datetime.timedelta(days=options_dict["days_forward"])

        endpoint = f'https://api.tdameritrade.com/v1/marketdata/chains?' \
                   f'&symbol={options_dict["ticker"]}&' \
                   f'contractType={options_dict["contract_type"]}&' \
                   f'strikeCount={options_dict["strike_count"]}&'\
                   f'includeQuotes={options_dict["include_quotes"]}&' \
                   f'strategy={options_dict["strategy"]}&' \
                   f'interval={options_dict["interval"]}&' \
                   f'strike={options_dict["strike"]}&' \
                   f'range={options_dict["range"]}&' \
                   f'fromDate={from_date}&' \
                   f'toDate={to_date}&' \
                   f'volatility={options_dict["volatility"]}&' \
                   f'underlyingPrice={options_dict["underlying_price"]}&' \
                   f'interestRate={options_dict["interest_rate"]}&' \
                   f'daysToExpiration={options_dict["days_to_expiration"]}&' \
                   f'expMonth={options_dict["exp_month"]}&' \
                   f'optionType={options_dict["option_type"]}' \

        page = requests.get(url = endpoint, params={'apikey': api_key})
        time.sleep(1)
        content = json.loads(page.content)

        call_options = pd.DataFrame()
        put_options = pd.DataFrame()

        if options_dict["contract_type"] == "CALL" and content["callExpDateMap"]:
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

            call_options['expirationDate'] = pd.to_datetime(call_options['expirationDate'], unit="ms")
            return call_options

        if options_dict["contract_type"] == "PUT" and content["putExpDateMap"]:
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

            put_options['expirationDate'] = pd.to_datetime(put_options['expirationDate'], unit="ms")
            return put_options

        else:
            return call_options
