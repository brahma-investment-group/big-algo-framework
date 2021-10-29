from big_algo_framework.data.td import TD, tdTimeSaleDataStreaming
import asyncio
from datetime import datetime
import pandas as pd
from sqlalchemy import text
import threading
from big_algo_framework.big.calendar_us import *
from pytz import timezone

class TdChild(TD):
    def __init__(self, ticker, api_key, account_id, redirect_uri, db, streaming_data_table, credentials_path='./ameritrade-credentials.json'):
        super().__init__(ticker, api_key, account_id, redirect_uri, credentials_path='./ameritrade-credentials.json')

        self.db = db
        self.streaming_data_table = streaming_data_table

    def get_streaming_equity_data(self):
        async def main():
            consumer = tdTimeSaleDataStreamingChild(self.ticker, self.api_key, self.account_id, self.redirect_uri, self.db, self.streaming_data_table)
            consumer.initialize()
            await consumer.stream()

        asyncio.run(main())

class tdTimeSaleDataStreamingChild(tdTimeSaleDataStreaming):
    def __init__(self, tickers, api_key, account_id, redirect_uri, db, streaming_data_table, queue_size=0, credentials_path='./ameritrade-credentials.json'):
        super().__init__(tickers, api_key, account_id, redirect_uri, queue_size=0, credentials_path='./ameritrade-credentials.json')

        self.db = db
        self.streaming_data_table = streaming_data_table

    def write_db(self, msg):
        df = pd.DataFrame()
        streaming_list = []

        local_tz = 'US/Eastern'
        tz = timezone(local_tz)

        if msg.get('content'):
            for content in msg['content']:
                cal = is_mkt_open('NYSE')

                if cal["is_mkt_open"]:
                    date_time = datetime.datetime.fromtimestamp(int(content['TRADE_TIME'] / 1000))
                    date_time = date_time.replace(tzinfo=tz)

                    if cal["mkt_open"].astimezone(local_tz) <= date_time <= cal["mkt_close"].astimezone(local_tz):
                        d = {'ticker': content['key'],
                             'date_time': content['TRADE_TIME'],
                             'price': content['LAST_PRICE'],
                             'volume': content['LAST_SIZE']}

                        streaming_list.append(d)

        if streaming_list:
            df = pd.DataFrame(data=streaming_list)
            df.to_sql(self.streaming_data_table, self.db, if_exists='append', index=False, method='multi')

    async def handle_queue(self):
        """
        Here we pull messages off the queue and process them.
        """
        while True:
                msg = await self.queue.get()
                con_thread = threading.Thread(target=self.write_db(msg), daemon=True)
                con_thread.start()
