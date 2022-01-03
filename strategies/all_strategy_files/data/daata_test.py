from big_algo_framework.data.td import DataListener
import configparser
import asyncio
import threading
from datetime import datetime
from big_algo_framework.big.calendar_us import *
from pytz import timezone
import pandas as pd
from strategies.all_strategy_files.database.database import createDB

config = configparser.ConfigParser()
config.read("config.ini")
tda_api = config['TDA_API']
api_key = tda_api["api_key"]
account_id = tda_api["account_id"]
redirect_uri = tda_api["redirect_uri"]
is_running = True

streaming_data_table = "us_equity_streaming_data"
db = createDB("market_data", "config.ini")

loop = asyncio.new_event_loop()

def data_func():
    symbols = ['SPY', 'MSFT', 'GOOG', 'AAPL', 'NFLX']

    asyncio.set_event_loop(loop)

    datalistener = DataListener()
    datalistener.init_credentials(api_key, account_id)
    datalistener.initialize(account_id, symbols, symbols)

    local_tz = 'US/Eastern'
    tz = timezone(local_tz)

    while is_running:
        try:
            mins_msg = []
            fast_msg, mins_msg = loop.run_until_complete(datalistener.fast_message_handler())

            df = pd.DataFrame()
            streaming_list = []

            if len(mins_msg['content']) > 0:
                for content in mins_msg['content']:
                    now = datetime.datetime.now()
                    print(now, ": ", content)
                    cal = is_mkt_open('NYSE')

                    date_time = datetime.datetime.fromtimestamp(int(content['CHART_TIME'] / 1000))
                    date_time = timezone(local_tz).localize(date_time)

                    if cal["mkt_open"].astimezone(local_tz) <= date_time <= cal["mkt_close"].astimezone(local_tz):
                        d = {'ticker': content['key'],
                             'date_time': content['CHART_TIME'],
                             'open': content['OPEN_PRICE'],
                             'high': content['HIGH_PRICE'],
                             'low': content['LOW_PRICE'],
                             'close': content['CLOSE_PRICE'],
                             'volume': content['VOLUME']}

                        streaming_list.append(d)
                        print(streaming_list)


                if streaming_list:
                    df = pd.DataFrame(data=streaming_list)
                    print(df)
                    df.to_sql(streaming_data_table, db, if_exists='append', index=False, method='multi')

        except:
            print("NOOOOOOOO")

    loop.close()  # dont know where this should be


if __name__ == "__main__":
    data_thread = threading.Thread(target=data_func, daemon=True)
    data_thread.start()

    while is_running:
        pass
    data_thread.join()