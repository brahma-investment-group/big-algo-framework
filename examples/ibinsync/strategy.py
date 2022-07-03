import time

import ib_insync.order
from ib_insync import *
import asyncio
from datetime import datetime, timedelta
from examples.all_strategy_files.ib.ib_check_order_positions import IbCheckOrderPositions
from examples.all_strategy_files.ib.ib_position_sizing import IbPositionSizing
from examples.all_strategy_files.ib.ib_send_orders import IbSendOrders
from examples.all_strategy_files.ib.ib_get_action import IbGetAction
from examples.all_strategy_files.ib.ib_filter_options import IbFilterOptions

async def run_ibinsync(order_dict):
    ticker = order_dict["ticker"]
    ib = order_dict["broker"]

    x = await ib.accountSummaryAsync()
    for acc in x:
        if acc.tag == "AvailableFunds":
            order_dict["funds"] = acc.value

    orders_list = []
    pos_list = []

    for trades in ib.trades():
        if trades.orderStatus.status == "PreSubmitted":
            orders_list.append(trades.contract.symbol)

    for pos in await ib.reqPositionsAsync():
        if pos.position != 0:
            pos_list.append(pos.contract.symbol)

    if (ticker not in orders_list) and (ticker not in pos_list):
        order_dict["gtd"] = datetime.fromtimestamp(order_dict["mkt_close_time"] / 1000)

        # FILTER OPTIONS
        action = IbGetAction(order_dict)
        filter = IbFilterOptions(order_dict)
        filter.filter_options()
        action.get_options_action()

        order_dict["stock_entry"] = order_dict["entry"]
        order_dict["stock_sl"] = order_dict["sl"]

        order_dict["entry"] = order_dict["ask"]
        order_dict["sl"] = 0

        # IB Position Sizing Class
        ib_pos_size = IbPositionSizing(order_dict)
        quantity = ib_pos_size.get_options_quantity()
        order_dict["quantity"] = quantity

        # Contract
        stock_contract = Stock(symbol=ticker,
                               currency='USD',
                               exchange='SMART',
                               primaryExchange=order_dict["primary_exchange"])
        await ib.qualifyContractsAsync(stock_contract)

        option_contract = Option(symbol=ticker,
                                 currency='USD',
                                 exchange='SMART',
                                 lastTradeDateOrContractMonth=order_dict["lastTradeDateOrContractMonth"],
                                 strike=order_dict["strike"],
                                 right=order_dict["right"],
                                 multiplier=order_dict["multiplier"],
                                 )
        await ib.qualifyContractsAsync(option_contract)

        # Prepare Orders
        x = True if order_dict["direction"] == "Bullish" else False
        y = False if order_dict["direction"] == "Bullish" else True

        entry_order = MarketOrder(order_dict["open_action"], order_dict["quantity"], tif="GTD", goodTillDate= (order_dict["gtd"] + timedelta(minutes=-30)).strftime('%Y%m%d %H:%M:%S'), transmit=False)
        p_cond = ib_insync.order.PriceCondition()
        p_cond.conId = stock_contract.conId
        p_cond.exch = "SMART"
        p_cond.isMore = y
        p_cond.price = order_dict["stock_entry"]
        p_cond.conjunction = 'o'
        entry_order.conditions = [p_cond]
        entry_trade = ib.placeOrder(option_contract, entry_order)

        sl_order = MarketOrder(order_dict["close_action"], order_dict["quantity"], parentId=entry_trade.order.orderId, transmit=False)
        p_cond = ib_insync.order.PriceCondition()
        p_cond.conId = stock_contract.conId
        p_cond.exch = "SMART"
        p_cond.isMore = y
        p_cond.price = order_dict["stock_sl"]
        p_cond.conjunction = 'o'
        sl_order.conditions = [p_cond]
        sl_trade = ib.placeOrder(option_contract, sl_order)

        tp_order = MarketOrder(order_dict["close_action"], order_dict["quantity"], parentId=entry_trade.order.orderId, transmit=True)
        p_cond = ib_insync.order.PriceCondition()
        p_cond.conId = stock_contract.conId
        p_cond.exch = "SMART"
        p_cond.isMore = x
        p_cond.price = order_dict["tp1"]
        p_cond.conjunction = 'o'
        t_cond = ib_insync.order.TimeCondition()
        t_cond.time = (order_dict["gtd"] + timedelta(minutes=-5)).strftime('%Y%m%d %H:%M:%S')
        tp_order.conditions = [p_cond, t_cond]
        tp_trade = ib.placeOrder(option_contract, tp_order)


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
