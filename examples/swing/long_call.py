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

class LongCall(Strategy):
    def __init__(self):
        super().__init__()

        self.ip_address = config.ib_account["ip_address"]
        self.port = config.ib_account["port"]
        self.ib_client = config.ib_account["ib_client"]
        self.account_no = config.ib_account["account_no"]
        self.currency = "USD"
        self.exchange = "SMART"

        self.ticker = "GM"
        self.primary_exchange = "NYSE"
        self.stock_stp_entry = 40.18
        self.stock_lmt_entry = 1.001 * self.stock_stp_entry
        self.stock_sl = 38.39
        self.stock_tp = 47.00
        self.strike = 41
        self.quantity = 2

        self.strike_date = "20220916" #YYYYMMDD
        self.entry_time = "20220908 09:45:00"

    async def connect_broker(self):
        global broker
        if(broker == None) or (not broker.isConnected()):
            broker = IB()
            await broker.connectAsync(self.ip_address, self.port, self.ib_client)
        self.broker = broker
        self.account_dict = await self.broker.get_account()

    async def before_send_orders(self):
        self.stock_contract = await self.broker.get_stock_contract(self.ticker, self.exchange, self.currency,
                                                                   self.primary_exchange)
        self.contract = await self.broker.get_options_contract(symbol=self.ticker,
                                                               expiration_date=self.strike_date,
                                                               strike=self.strike,
                                                               right='C',
                                                               exchange=self.exchange,
                                                               multiplier="100",
                                                               currency=self.currency)

    async def send_orders(self):
        entry_order = await self.broker.get_market_order(action="BUY",
                                                         quantity=self.quantity,
                                                         account_no=self.account_no,
                                                         duration="GTC",
                                                         transmit=False,
                                                         sec_type="",
                                                         symbol="")
        stp_price_cond = await self.broker.get_price_condition(conjunction='a',
                                                               is_more=True,
                                                               price=self.stock_stp_entry,
                                                               contract_id=self.stock_contract[0].conId,
                                                               exchange="SMART")
        lmt_price_cond = await self.broker.get_price_condition(conjunction='a',
                                                               is_more=False,
                                                               price=self.stock_lmt_entry,
                                                               contract_id=self.stock_contract[0].conId,
                                                               exchange="SMART")
        time_cond = await self.broker.get_time_condition(time = self.entry_time,
                                                         conjunction= 'a',
                                                         is_more= True)
        entry_order.conditions = [stp_price_cond, lmt_price_cond, time_cond]
        entry_trade = await self.broker.send_order(self.contract[0], "", entry_order)
        # ***********************************************************************************************************

        sl_order = await self.broker.get_market_order(action="SELL",
                                                      quantity=self.quantity,
                                                      parent_id=entry_trade.order.orderId,
                                                      account_no=self.account_no,
                                                      duration="GTC",
                                                      transmit=False,
                                                      sec_type="",
                                                      symbol="")
        p_cond = await self.broker.get_price_condition(conjunction='o',
                                                       is_more=False,
                                                       price=self.stock_sl,
                                                       contract_id=self.stock_contract[0].conId,
                                                       exchange="SMART")
        sl_order.conditions = [p_cond]
        await self.broker.send_order(self.contract[0], "", sl_order)
        # ***********************************************************************************************************

        tp_order = await self.broker.get_market_order(action="SELl",
                                                      quantity=self.quantity,
                                                      parent_id=entry_trade.order.orderId,
                                                      account_no=self.account_no,
                                                      duration="GTC",
                                                      transmit=True,
                                                      sec_type="",
                                                      symbol="")
        p_cond = await self.broker.get_price_condition(conjunction='o',
                                                       is_more=True,
                                                       price=self.stock_tp,
                                                       contract_id=self.stock_contract[0].conId,
                                                       exchange="SMART")
        tp_order.conditions = [p_cond]
        await self.broker.send_order(self.contract[0], "", tp_order)

    async def start(self):
        await self.connect_broker()

    async def execute(self):
        await self.start()
        await self.before_send_orders()

        if self.quantity > 0:
            await self.send_orders()
            self.after_send_orders()

if __name__ == "__main__":
    x = LongCall()
    asyncio.run(x.execute())