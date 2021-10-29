from big_algo_framework.brokers.abstract_broker import Broker
import time
from datetime import datetime
from ibapi.order import Order
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd

class IB(Broker, EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.orderId = 0

    def init_client(self, client):
        self.client = client

    def get_contract(self, order_dict):
        self.contract = Contract()
        self.contract.symbol = order_dict["ticker"]
        self.contract.secType = order_dict["sec_type"]
        self.contract.currency = order_dict["currency"]
        self.contract.exchange = order_dict["exchange"]
        self.contract.primaryExchange = order_dict["primary_exchange"]

        return self.contract

    def getOrderID(self, client):
        client.reqIds(1)
        time.sleep(1)

    def get_market_order(self, order_dict):
        market_order = Order()
        market_order.orderId = order_dict["mkt_order_id"]
        market_order.action = order_dict["mkt_action"]
        market_order.orderType = 'MKT'
        market_order.totalQuantity = order_dict["mkt_quantity"]
        market_order.parentId = order_dict["mkt_parent_order_id"]
        market_order.transmit = order_dict["mkt_transmit"]

        return market_order

    def get_stop_limit_order(self, order_dict):
        stop_limit_order = Order()
        stop_limit_order.orderId = order_dict["slo_order_id"]
        stop_limit_order.action = order_dict["slo_action"]
        stop_limit_order.orderType = 'STP LMT'
        stop_limit_order.totalQuantity = order_dict["slo_quantity"]
        stop_limit_order.lmtPrice = order_dict["slo_limit_price"]
        stop_limit_order.auxPrice = order_dict["slo_stop_price"]
        stop_limit_order.tif = order_dict["slo_time_in_force"]
        stop_limit_order.goodTillDate = order_dict["slo_good_till_date"]
        stop_limit_order.parentId = order_dict["slo_parent_order_id"]
        stop_limit_order.transmit = order_dict["slo_transmit"]

        return stop_limit_order

    def get_limit_order(self, order_dict):
        limit_order = Order()
        limit_order.orderId = order_dict["lo_order_id"]
        limit_order.action = order_dict["lo_action"]
        limit_order.orderType = 'LMT'
        limit_order.totalQuantity = order_dict["lo_quantity"]
        limit_order.lmtPrice = order_dict["lo_limit_price"]
        limit_order.tif = order_dict["lo_time_in_force"]
        limit_order.goodTillDate = order_dict["lo_good_till_date"]
        limit_order.parentId = order_dict["lo_parent_order_id"]
        limit_order.transmit = order_dict["lo_transmit"]

        return limit_order

    def get_stop_order(self, order_dict):
        stop_order = Order()
        stop_order.orderId = order_dict["so_order_id"]
        stop_order.action = order_dict["so_action"]
        stop_order.orderType = 'STP'
        stop_order.totalQuantity = order_dict["so_quantity"]
        stop_order.auxPrice = order_dict["so_stop_price"]
        stop_order.tif = order_dict["so_time_in_force"]
        stop_order.goodTillDate = order_dict["so_good_till_date"]
        stop_order.parentId = order_dict["so_parent_order_id"]
        stop_order.transmit = order_dict["so_transmit"]

        return stop_order

    def send_bracket_order(self, *orders):
        bracketOrder = []
        for x in orders:
            bracketOrder.append(x)

        for o in bracketOrder:
            self.client.placeOrder(o.orderId, self.contract, o)

    def send_order(self, order_dict, order):
        self.client.placeOrder(order_dict["order_id"], self.contract, order)

    #######################################################################################################
    # IB SPECIFIC CALLBACK FUNCTIONS
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        print(orderId)

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)

    def positionEnd(self):
        super().positionEnd()

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                    whyHeld, mktCapPrice)

    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)

    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
