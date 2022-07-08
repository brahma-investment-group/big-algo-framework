import ib_insync
import asyncio

from big_algo_framework.brokers.abstract_broker import Broker
from big_algo_framework.big.helper import truncate
import time
import threading
from sqlalchemy import text
import pandas as pd

class IB(Broker, ib_insync.IB):
    def __init__(self):
        ib_insync.IB.__init__(self)



    # # Authentication

    def connect_broker(self, broker, ip_address, port, ib_client):
        pass

    # Asset
    async def get_stock_contract(self, order_dict):
        stock_contract = ib_insync.Stock(symbol=order_dict["ticker"],
                               currency=order_dict["currency"],
                               exchange=order_dict["exchange"],
                               primaryExchange=order_dict["primary_exchange"])
        x = await order_dict["broker"].qualifyContractsAsync(stock_contract)
        return x

    async def get_options_contract(self, order_dict):
        option_contract = ib_insync.Option(symbol=order_dict["ticker"],
                                 currency=order_dict["currency"],
                                 exchange=order_dict["exchange"],
                                 lastTradeDateOrContractMonth=order_dict["lastTradeDateOrContractMonth"],
                                 strike=order_dict["strike"],
                                 right=order_dict["right"],
                                 multiplier=order_dict["multiplier"],
                                 )
        return await order_dict["broker"].qualifyContractsAsync(option_contract)

    # Prepare/Send Orders
    async def get_market_order(self, action, quantity, parent_id, tif, gtd, transmit):
        return ib_insync.MarketOrder(
            action=action,
            totalQuantity=quantity,
            parentId=parent_id,
            tif=tif,
            goodTillDate=gtd,
            transmit=transmit)

    def get_stop_limit_order(self, order_dict, digits=2):
        pass


    def get_limit_order(self, order_dict, digits=2):
        pass

    def get_stop_order(self, order_dict, digits=2):
        pass

    def get_trailing_stop_order(self, orders, trail_type, trail_amount, trail_stop, digits=2):
       pass

    def get_oto_order(self, orders):
        pass

    def get_oco_order(self, orders, oca_group_name, oca_group_type):
        pass

    def send_order(self, order_id, contract, order):
        pass

    # Get Orders/Positions
    def get_order_by_ticker(self, order_dict):
        pass

    def get_all_orders(self, order_dict):
        pass

    def get_position_by_ticker(self, order_dict):
        pass

    def get_all_positions(self, order_dict):
        pass

    # Cancel Orders/Close Positions
    def cancel_order(self, order_dict, order_id):
        pass

    def cancel_all_orders(self, order_dict):
        pass

    def close_position(self, pos_order_dict, underlying=False):
        pass

    def close_all_positions(self, order_dict, underlying=False):
        pass