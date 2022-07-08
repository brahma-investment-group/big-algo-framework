import time

import ib_insync.order
# from ib_insync import *
import asyncio
from datetime import datetime, timedelta
# from examples.all_strategy_files.ib.ib_check_order_positions import IbCheckOrderPositions
from examples.all_strategy_files.ib.ib_position_sizing import IbPositionSizing
# from examples.all_strategy_files.ib.ib_send_orders import IbSendOrders
from examples.all_strategy_files.ib.ib_get_action import IbGetAction
from examples.all_strategy_files.ib.ib_filter_options import IbFilterOptions
from big_algo_framework.brokers.ib import IB
from big_algo_framework.strategies.abstract_strategy import *

broker_2 = None

class IBORB(Strategy):
    def __init__(self, order_dict):
        super().__init__()
        self.is_position = True
        self.is_order = True
        self.order_dict = order_dict.copy()

    async def connect_broker(self):
        global broker_2
        if(broker_2 == None) or (not broker_2.isConnected()):
            broker_2 = IB()
            # await broker_2.init_client(broker_2)
            await broker_2.connectAsync('127.0.0.1', 7497, clientId=1)

        self.broker = broker_2
        self.order_dict["broker"] = broker_2

        x = await self.broker.accountSummaryAsync()
        for acc in x:
            if acc.tag == "AvailableFunds":
                self.order_dict["funds"] = acc.value

        self.orders_list = []
        self.pos_list = []

    async def check_open_orders(self):
        for trades in self.broker.trades():
            if trades.orderStatus.status == "PreSubmitted":
                self.orders_list.append(trades.contract.symbol)

        if self.order_dict["ticker"] not in self.orders_list:
            self.is_order = False

    async def check_positions(self):
        for pos in await self.broker.reqPositionsAsync():
            if pos.position != 0:
                self.pos_list.append(pos.contract.symbol)

        if self.order_dict["ticker"] not in self.pos_list:
            self.is_position = False

    async def before_send_orders(self):
        self.order_dict["gtd"] = datetime.fromtimestamp(self.order_dict["mkt_close_time"] / 1000)

        # FILTER OPTIONS
        action = IbGetAction(self.order_dict)
        filter = IbFilterOptions(self.order_dict)
        filter.filter_options()
        action.get_options_action()

        self.order_dict["stock_entry"] = self.order_dict["entry"]
        self.order_dict["stock_sl"] = self.order_dict["sl"]

        self.order_dict["entry"] = self.order_dict["ask"]
        self.order_dict["sl"] = 0

        # IB Position Sizing Class
        ib_pos_size = IbPositionSizing(self.order_dict)
        quantity = ib_pos_size.get_options_quantity()
        self.order_dict["quantity"] = quantity

        # Contract
        self.stock_contract = await self.broker.get_stock_contract(self.order_dict)
        self.option_contract = await self.broker.get_options_contract(self.order_dict)

        # Prepare Orders
        self.x = True if self.order_dict["direction"] == "Bullish" else False
        self.y = False if self.order_dict["direction"] == "Bullish" else True

    async def send_orders(self):
        entry_order = await self.broker.get_market_order(self.order_dict["open_action"], self.order_dict["quantity"], "", "GTD", (self.order_dict["gtd"] + timedelta(minutes=-30)).strftime('%Y%m%d %H:%M:%S'), False)
        p_cond = ib_insync.order.PriceCondition()
        p_cond.conId = self.stock_contract[0].conId
        p_cond.exch = "SMART"
        p_cond.isMore = self.y
        p_cond.price = self.order_dict["stock_entry"]
        p_cond.conjunction = 'o'
        entry_order.conditions = [p_cond]
        entry_trade = self.broker.placeOrder(self.option_contract[0], entry_order)

        sl_order = await self.broker.get_market_order(self.order_dict["close_action"], self.order_dict["quantity"], entry_trade.order.orderId, "", "", False)
        p_cond = ib_insync.order.PriceCondition()
        p_cond.conId = self.stock_contract[0].conId
        p_cond.exch = "SMART"
        p_cond.isMore = self.y
        p_cond.price = self.order_dict["stock_sl"]
        p_cond.conjunction = 'o'
        sl_order.conditions = [p_cond]
        sl_trade = self.broker.placeOrder(self.option_contract[0], sl_order)

        tp_order = await self.broker.get_market_order(self.order_dict["close_action"], self.order_dict["quantity"], entry_trade.order.orderId, "", "",  transmit=True)
        p_cond = ib_insync.order.PriceCondition()
        p_cond.conId = self.stock_contract[0].conId
        p_cond.exch = "SMART"
        p_cond.isMore = self.x
        p_cond.price = self.order_dict["tp1"]
        p_cond.conjunction = 'o'
        t_cond = ib_insync.order.TimeCondition()
        t_cond.time = (self.order_dict["gtd"] + timedelta(minutes=-5)).strftime('%Y%m%d %H:%M:%S')
        tp_order.conditions = [p_cond, t_cond]
        tp_trade = self.broker.placeOrder(self.option_contract[0], tp_order)

    async def start(self):
        await self.connect_broker()

    async def execute(self):
        await self.start()

        if self.order_dict["is_close"] == 0:
            await self.check_positions()
            if not self.is_position:
                await self.check_open_orders()
                if not self.is_order:
                    await self.before_send_orders()

                    if self.order_dict["quantity"] > 0:
                        await self.send_orders()
                        self.after_send_orders()


    # TRADE CLASS OUTPUT!!!!
    # Trade(
    # contract=Stock(conId=270639, symbol='INTC', exchange='SMART', primaryExchange='NASDAQ', currency='USD', localSymbol='INTC', tradingClass='NMS'),
    # order=LimitOrder(orderId=104, clientId=1, permId=1405222075, action='SELL', totalQuantity=1.0, lmtPrice=1.11, auxPrice=0.0),
    # orderStatus=OrderStatus(orderId=104, status='PreSubmitted', filled=0.0, remaining=1.0, avgFillPrice=0.0, permId=1405222075, parentId=0, lastFillPrice=0.0, clientId=1, whyHeld='', mktCapPrice=0.0),
    # fills=[],
    # log=[TradeLogEntry(time=datetime.datetime(2022, 6, 18, 23, 7, 29, 87606, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='', errorCode=0),
    # TradeLogEntry(time=datetime.datetime(2022, 6, 18, 23, 7, 29, 120600, tzinfo=datetime.timezone.utc), status='PreSubmitted', message='', errorCode=0)]),


    # POSITIONS OUTPUT
    # [Position(account='U3584554',
    #           contract=Stock(conId=344439802, symbol='TME', exchange='NYSE', currency='USD', localSymbol='TME', tradingClass='TME'),
    #           position=1.0, avgCost=5.2227)]

# async def main():
#     broker_2 = IB()
#     await broker_2.connectAsync('127.0.0.1', 7497, clientId=1)
#
#     order_dict = {"ticker": "BABA", "broker": broker_2}
#     await run_ibinsync(order_dict)
#
# if __name__ == "__main__":
#     asyncio.run(main())
