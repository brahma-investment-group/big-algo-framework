import tda
from tda.streaming import StreamClient
import asyncio
from datetime import datetime
import configparser

class tdTimeSaleDataStreaming:
    def __init__(self, db, tickers, streaming_data_table, queue_size=1, credentials_path='./ameritrade-credentials.json'):
        config = configparser.ConfigParser()
        config.read("config.ini")
        tda_api = config['TDA_API']

        self.db = db
        self.api_key = tda_api["api_key"]
        self.account_id = tda_api["account_id"]
        self.redirect_uri = tda_api["redirect_uri"]
        self.credentials_path = credentials_path
        self.tda_client = None
        self.stream_client = None
        self.tickers = tickers
        self.streaming_data_table = streaming_data_table

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
        if self.queue.full():
            await self.queue.get()
        await self.queue.put(msg)

    async def handle_queue(self):
        """
        Here we pull messages off the queue and process them.
        """
        while True:
            msg = await self.queue.get()
            table = self.db[self.streaming_data_table]

            for content in msg['content']:
                print("Price for ", content['key'], "is: ", content['LAST_PRICE'], "occured at: ", datetime.fromtimestamp(content['TRADE_TIME']/1000), "volume is: ", content['LAST_SIZE'])
                data = dict(datetime=datetime.fromtimestamp(content['TRADE_TIME']/1000),
                            ticker = content['key'],
                            price=content['LAST_PRICE'],
                            volume=content['LAST_SIZE'])

                table.insert(data)
