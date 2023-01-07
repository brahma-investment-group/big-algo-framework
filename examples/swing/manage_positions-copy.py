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

class managePositions(Strategy):
    def __init__(self):
        super().__init__()

        self.ip_address = config.ib_account["ip_address"]
        self.port = config.ib_account["port"]
        self.ib_client = config.ib_account["ib_client"]
        self.account_no = config.ib_account["account_no"]
        # self.currency = "USD"
        # self.exchange = "SMART"

    async def connect_broker(self):
        global broker
        if(broker == None) or (not broker.isConnected()):
            broker = IB()
            await broker.connectAsync(self.ip_address, self.port, self.ib_client)
        self.broker = broker
        self.account_dict = await self.broker.get_account()

    async def before_send_orders(self):
        pass

    async def send_orders(self):
        while 1:
            time.sleep(5)
            print("************")
            self.quantity = 1
            self.ticker = "DKNG"
            self.exchange = "SMART"
            self.primary_exchange = "NASDAQ"
            self.currency = "USD"
            self.expiration_date = "20221209"
            self.strike = 14
            self.right = "P"
            self.multiplier = 100
            self.avg_price = 0.50

            self.year = self.expiration_date[0: 4: 1]
            self.month = self.expiration_date[4: 6: 1]
            self.date = self.expiration_date[6: 8: 1]

            self.open_orders = await self.broker.get_order_by_symbol(self.ticker, self.account_no)

            if (self.quantity > 0) and (not self.open_orders):
                self.contract = await self.broker.get_options_contract(symbol=self.ticker,
                                                                       expiry_date=int(self.date),
                                                                       expiry_month=int(self.month),
                                                                       expiry_year=int(self.year),
                                                                       strike=self.strike,
                                                                       right=self.right,
                                                                       exchange=self.exchange,
                                                                       multiplier="100",
                                                                       currency=self.currency)

                sl_order = await self.broker.get_stop_order(action="SELL",
                                                            quantity=int(self.quantity),
                                                            stop_price=0.5*self.avg_price,
                                                            parent_id=0,
                                                            account_no=self.account_no,
                                                            duration="GTC",
                                                            transmit=True,
                                                            sec_type="",
                                                            symbol="")
                sl_order.eTradeOnly = None
                sl_order.firmQuoteOnly = None
                # await self.broker.send_order(self.contract[0], "", sl_order)
                # ***********************************************************************************************************

                tp_order = await self.broker.get_limit_order(action="SELl",
                                                             quantity=int(self.quantity),
                                                             parent_id=0,
                                                             limit_price=1.3*self.avg_price,
                                                             account_no=self.account_no,
                                                             duration="GTC",
                                                             transmit=True,
                                                             sec_type="",
                                                             symbol="")
                tp_order.eTradeOnly = None
                tp_order.firmQuoteOnly = None
                # await self.broker.send_order(self.contract[0], "", tp_order)

                orders = [sl_order, tp_order]
                oco_order = await self.broker.get_oco_order(orders, oca_group_name=self.ticker, oca_group_type="REDUCE_WITH_BLOCK")

                for order in oco_order:
                    print(order)
                    await self.broker.send_order(self.contract[0], "", order)

    async def start(self):
        await self.connect_broker()

    async def execute(self):
        await self.start()
        await self.before_send_orders()
        await self.send_orders()
        self.after_send_orders()

if __name__ == "__main__":
    x = managePositions()
    asyncio.run(x.execute())
