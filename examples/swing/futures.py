from big_algo_framework.strategies.abstract_strategy import *
from big_algo_framework.brokers.ib import IB
from big_algo_framework.data.td import TDData
from big_algo_framework.big.options import filter_option_contract
from big_algo_framework.big.position_sizing import PositionSizing
from datetime import datetime, timedelta
import asyncio
import datetime
import numpy as np
import time
import config

broker = None

class LongCallVeticalSpread(Strategy):
    def __init__(self):
        super().__init__()

        self.ip_address = config.ib_account["ip_address"]
        self.port = config.ib_account["port"]
        self.ib_client = config.ib_account["ib_client"]
        self.account_no = config.ib_account["account_no"]
        self.currency = "USD"

        self.ticker = "MES"
        self.local_symbol = "MESZ2"
        self.exchange = "GLOBEX"
        self.quantity = 1

        self.expiry_date = 16
        self.expiry_month = 12
        self.expiry_year = 2022
        self.entry_time = "20220926 09:45:00"

    async def connect_broker(self):
        global broker
        if(broker == None) or (not broker.isConnected()):
            broker = IB()
            await broker.connectAsync(self.ip_address, self.port, self.ib_client)
        self.broker = broker
        self.account_dict = await self.broker.get_account()

    async def before_send_orders(self):
        self.contract = await self.broker.get_futures_contract(symbol=self.ticker,
                                                             expiry_date=self.expiry_date,
                                                             expiry_month=self.expiry_month,
                                                             expiry_year=self.expiry_year,
                                                             local_symbol=self.local_symbol,
                                                             exchange=self.exchange,
                                                             currency=self.currency,
                                                             multiplier="5")

    async def send_orders(self):
        entry_order = await self.broker.get_market_order(action="BUY",
                                                         quantity=self.quantity,
                                                         account_no=self.account_no,
                                                         duration="GTC",
                                                         transmit=True,
                                                         sec_type="",
                                                         symbol="")
        entry_trade = await self.broker.send_order(self.contract[0], "", entry_order)

    async def start(self):
        await self.connect_broker()

    async def execute(self):
        await self.start()
        await self.before_send_orders()

        if self.quantity > 0:
            await self.send_orders()
            self.after_send_orders()

if __name__ == "__main__":
    x = LongCallVeticalSpread()
    asyncio.run(x.execute())
