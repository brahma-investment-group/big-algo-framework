from big_algo_framework.data.abstract_data import Data
import tda
from tda.streaming import StreamClient
import asyncio
from datetime import datetime, timedelta
import pytz
import pandas as pd
from sqlalchemy import text
import time
import multiprocessing
import threading
from big_algo_framework.data.multiawait import multi_await

class TD(Data):
    def __init__(self, ticker, api_key, account_id, redirect_uri, credentials_path='./ameritrade-credentials.json'):
        self.api_key = api_key
        self.account_id =account_id
        self.redirect_uri = redirect_uri
        self.credentials_path = credentials_path
        self.ticker = ticker

        try:
            self.tda_client = tda.auth.client_from_token_file(self.credentials_path, self.api_key)

        except FileNotFoundError:
            from selenium import webdriver
            # path = "C:/Users/nagab/Desktop/v2/big-algo-framework/strategies/all_strategy_files/data/chromedriver.exe"
            # with webdriver.Chrome(path) as driver:
            with webdriver.Chrome() as driver:
                self.tda_client = tda.auth.client_from_login_flow(driver, self.api_key, self.redirect_uri, self.credentials_path)

    def get_hist_equity_data(self, period_type=None, period=None, frequency_type=None, frequency=None,
                             start_dt=None, end_dt=None, extended_hours=False):
        """Fetch historic equity data from TDA client"""
        response = self.tda_client.get_price_history(symbol=self.ticker[0],
                                                     period_type=period_type ,
                                                     period=period,
                                                     frequency_type=frequency_type,
                                                     frequency=frequency,
                                                     start_datetime=start_dt,
                                                     end_datetime=end_dt,
                                                     need_extended_hours_data=extended_hours)

        return response.json()

    def get_streaming_equity_data(self):
        async def main():
            consumer = tdTimeSaleDataStreaming(self.ticker, self.api_key, self.account_id, self.redirect_uri)
            consumer.initialize()
            await consumer.stream()

        asyncio.run(main())

    def get_hist_options_data(self, contract_type=None, strike_count=None, include_quotes=None, strategy=None, interval=None,
                              strike=None, strike_range=None, from_date=None, to_date=None, volatility=None,
                              underlying_price=None, interest_rate=None, days_to_expiration=None, exp_month=None,
                              option_type=None):
        """Fetch historic options data from TDA client"""
        response = self.tda_client.get_option_chain(symbol=self.ticker[0],
                                                    contract_type=contract_type,
                                                    strike_count=strike_count,
                                                    include_quotes=include_quotes,
                                                    strategy=strategy,
                                                    interval=interval,
                                                    strike=strike,
                                                    strike_range=strike_range,
                                                    from_date=from_date,
                                                    to_date=to_date,
                                                    volatility=volatility,
                                                    underlying_price=underlying_price,
                                                    interest_rate=interest_rate,
                                                    days_to_expiration=days_to_expiration,
                                                    exp_month=exp_month,
                                                    option_type=option_type)

        return response.json()

    def get_streaming_options_data(self):
        pass

class tdTimeSaleDataStreaming:
    def __init__(self, tickers, api_key, account_id, redirect_uri, queue_size=0, credentials_path='./ameritrade-credentials.json'):
        self.api_key = api_key
        self.account_id = account_id
        self.redirect_uri = redirect_uri
        self.credentials_path = credentials_path
        self.tda_client = None
        self.stream_client = None
        self.tickers = tickers

        # Create a queue so we can queue up work gathered from the client
        self.queue = asyncio.Queue(queue_size)

    def initialize(self):
        """
        Create the clients and log in. Using easy_client, we can get new creds
        from the user via the web browser if necessary
        """
        try:
            self.tda_client = tda.auth.client_from_token_file(self.credentials_path, self.api_key)

        except FileNotFoundError:
            from selenium import webdriver

            with webdriver.Chrome() as driver:
                self.tda_client = tda.auth.client_from_login_flow(driver, self.api_key, self.redirect_uri, self.credentials_path)

        self.stream_client = StreamClient(
            self.tda_client, account_id=self.account_id)

        # The streaming client wants you to add a handler for every service type
        self.stream_client.add_timesale_equity_handler(
            self.handle_timesale_equity)

    async def stream(self):
        await self.stream_client.login()  # Log into the streaming service
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        await self.stream_client.timesale_equity_subs(self.tickers)

        # Kick off our handle_queue function as an independent coroutine
        asyncio.ensure_future(self.handle_queue())

        # Continuously handle inbound messages
        while True:
            await self.stream_client.handle_message()

    async def handle_timesale_equity(self, msg):
        """
        This is where we take msgs from the streaming client and put them on a
        queue for later consumption. We use a queue to prevent us from wasting
        resources processing old data, and falling behind.
        """
        # if the queue is full, make room
        if self.queue.full():  # This won't happen if the queue doesn't have a max size
            print('Handler queue is full. Awaiting to make room... Some messages might be dropped')
            await self.queue.get()
        await self.queue.put(msg)

    async def handle_queue(self):
        """
        Here we pull messages off the queue and process them.
        """
        while True:
            await self.queue.get()

class tdChartEquityDataStreaming:
    def __init__(self, tickers, api_key, account_id, redirect_uri, queue_size=0, credentials_path='./ameritrade-credentials.json'):
        self.api_key = api_key
        self.account_id = account_id
        self.redirect_uri = redirect_uri
        self.credentials_path = credentials_path
        self.tda_client = None
        self.stream_client = None
        self.tickers = tickers

        # Create a queue so we can queue up work gathered from the client
        self.queue = asyncio.Queue(queue_size)

    def initialize(self):
        """
        Create the clients and log in. Using easy_client, we can get new creds
        from the user via the web browser if necessary
        """
        try:
            self.tda_client = tda.auth.client_from_token_file(self.credentials_path, self.api_key)

        except FileNotFoundError:
            from selenium import webdriver

            with webdriver.Chrome() as driver:
                self.tda_client = tda.auth.client_from_login_flow(driver, self.api_key, self.redirect_uri, self.credentials_path)

        self.stream_client = StreamClient(
            self.tda_client, account_id=self.account_id)

        # The streaming client wants you to add a handler for every service type
        self.stream_client.add_chart_equity_handler(
            self.handle_chart_equity)

    async def stream(self):
        await self.stream_client.login()  # Log into the streaming service
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.EXPRESS)
        await self.stream_client.chart_equity_subs(self.tickers)

        # Kick off our handle_queue function as an independent coroutine
        asyncio.ensure_future(self.handle_queue())

        # Continuously handle inbound messages
        while True:
            await self.stream_client.handle_message()

    async def handle_chart_equity(self, msg):
        """
        This is where we take msgs from the streaming client and put them on a
        queue for later consumption. We use a queue to prevent us from wasting
        resources processing old data, and falling behind.
        """
        # if the queue is full, make room
        if self.queue.full():  # This won't happen if the queue doesn't have a max size
            print('Handler queue is full. Awaiting to make room... Some messages might be dropped')
            await self.queue.get()
        await self.queue.put(msg)

    async def handle_queue(self):
        """
        Here we pull messages off the queue and process them.
        """
        while True:
            await self.queue.get()

import os

import asyncio
import time
from queue import Queue

# ----------------------------------------------
from tda import auth, client
from tda.streaming import StreamClient
from tda.contrib.util import HeuristicJsonDecoder
# ---------------------------------------------



class DataListener():

    def init_credentials(self, api_key, account_id, credentials_path='./ameritrade-credentials.json'):
        self.api_key = api_key
        self.account_id = account_id
        self.stream_client = None
        self.credentials_path = credentials_path

        self.queue_fast_data = asyncio.Queue(maxsize=1000)
        self.queue_mins_data = asyncio.Queue(maxsize=100)

    def initialize(self, account_id, all_symbols, mins_symbols):

        self.symbols = all_symbols
        self.mins_symbols = mins_symbols

        # token_path = os.path.join(os.path.dirname(__file__), '../configlib', 'token')
        self.auth_client = tda.auth.client_from_token_file(self.credentials_path, self.api_key)
        # self.auth_client = auth.client_from_token_file(token_path, self.api_key)

        self.stream_client = StreamClient(self.auth_client, account_id=self.account_id)

        self.stream_client.set_json_decoder(HeuristicJsonDecoder())

        self.stream_client.add_chart_equity_handler(self.handle_minutes_data)
        self.stream_client.add_level_one_equity_handler(self.handle_fast_data)

        asyncio.ensure_future(self.stream())

    def get_auth_client(self):
        return self.auth_client

    def get_account_id(self):
        return self.account_id

    async def stream(self):
        await self.stream_client.login()
        await self.stream_client.quality_of_service(StreamClient.QOSLevel.FAST)

        if len(self.mins_symbols) > 0:
            await self.stream_client.chart_equity_subs(self.mins_symbols)
        await self.stream_client.level_one_equity_subs(self.symbols)

        while True:
            await self.stream_client.handle_message()

    async def handle_minutes_data(self, msg):
        await self.queue_mins_data.put(msg)

    async def handle_fast_data(self, msg):
        await  self.queue_fast_data.put(msg)

    async def fast_message_handler(self):
        async with multi_await() as m:
            m.add(self.queue_fast_data.get)
            m.add(self.queue_mins_data.get)

            done = False
            while not done:
                completed, failures = await m.get()
                fast_msg, slow_msg = completed
                if fast_msg is None:
                    fast_msg = {"content": []}
                if slow_msg is None:
                    slow_msg = {"content": []}
                done = True
                return fast_msg, slow_msg
