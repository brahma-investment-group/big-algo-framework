import asyncio
from datetime import date
import polygon
import pytz
import datetime
from big_algo_framework.big.calendar_us import *
import pandas as pd

KEY = ''  # recommend to keep your key in a separate file and import that here

def is_daylight_saving(timestamp, zone_name='America/New_York'):
    final = datetime.datetime.utcfromtimestamp(timestamp / 1000).replace(tzinfo=pytz.utc)

    x = is_mkt_open('NYSE',
                    start_date=final.date(),
                    end_date=final.date(),
                    timestamp=timestamp/1000)

    if  x['mkt_open'] <= final < x['mkt_close']:
        return True

    else:
        return False


def get_hist_data(content, ticker):
    df = pd.DataFrame.from_dict(content['results'])
    df['ticker'] = ticker

    df = df.rename(columns={'v': 'volume',
                            'o': 'open',
                            'c': 'close',
                            'h': 'high',
                            'l': 'low',
                            't': 'date_time',})

    df = df.drop(columns=['vw', 'n'])

    print(df)


async def main(ticker):
    client = polygon.StocksClient(KEY, True)

    content = await client.get_aggregate_bars(symbol=ticker, from_date='2021-11-25', to_date='2021-11-30', timespan='minute',
                                                    multiplier='5', limit=50000)




    streaming_list = []
    for i in range(0, len(content['results'])):
        if is_daylight_saving(content['results'][i]['t']):
            d = {'ticker': ticker,
                 'date_time': content['results'][i]['t'],
                 'open': content['results'][i]['o'],
                 'high': content['results'][i]['h'],
                 'low': content['results'][i]['l'],
                 'close': content['results'][i]['c'],
                 'volume': content['results'][i]['v']
                 }

            streaming_list.append(d)

    dict_o = dict(zip(streaming_list, streaming_list))
    print(dict_o)

    return dict_o


if __name__ == '__main__':
    ticker = 'MSFT'
    content = asyncio.run(main(ticker))

    get_hist_data(content, ticker)