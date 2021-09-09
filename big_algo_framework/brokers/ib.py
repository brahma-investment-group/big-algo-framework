from big_algo_framework.brokers.abstract_broker import Broker
import time
from datetime import datetime
from ibapi.order import Order
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class IB(Broker, EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def initialize(self, client, order_dict):
        self.client = client
        self.order_dict = order_dict

        self.contract = Contract()
        self.contract.symbol = self.order_dict["ticker"]
        self.contract.secType = self.order_dict["sec_type"]
        self.contract.currency = self.order_dict["currency"]
        self.contract.exchange = self.order_dict["exchange"]
        self.contract.primaryExchange = self.order_dict["primary_exchange"]

    def getOrderID(self, client):
        client.reqIds(1)
        time.sleep(1)

    # def open_order(self, client, contract, order_id, order):
    #     now = datetime.now().strftime('%Y%m%d, %H:%M:%S')
    #     self.client.placeOrder(order_id, contract, order)
    #     time.sleep(2)

    def get_market_order(self, order_id):
        market_order = Order()
        market_order.orderId = order_id
        market_order.action = self.order_dict["action"]
        market_order.orderType = 'MKT'
        market_order.totalQuantity = self.order_dict["quantity"]
        market_order.parentId = self.order_dict["parent_order_id"]
        market_order.transmit = self.order_dict["transmit"]

        # self.client.placeOrder(self.order_dict["order_id"], self.contract, market_order)
        return market_order

    def get_stop_limit_order(self, order_id):
        stop_limit_order = Order()
        stop_limit_order.orderId = order_id
        stop_limit_order.action = self.order_dict["action"]
        stop_limit_order.orderType = 'STP LMT'
        stop_limit_order.totalQuantity = self.order_dict["quantity"]
        stop_limit_order.lmtPrice = self.order_dict["limit_price"]
        stop_limit_order.auxPrice = self.order_dict["stop_price"]
        stop_limit_order.tif = self.order_dict["time_in_force"]
        stop_limit_order.goodTillDate = self.order_dict["good_till_date"]
        stop_limit_order.parentId = self.order_dict["parent_order_id"]
        stop_limit_order.transmit = self.order_dict["transmit"]

        # self.client.placeOrder(self.order_dict["order_id"], self.contract, stop_limit_order)
        return stop_limit_order

    def get_limit_order(self, order_id):
        limit_order = Order()
        limit_order.orderId = order_id
        limit_order.action = self.order_dict["action"]
        limit_order.orderType = 'LMT'
        limit_order.totalQuantity = self.order_dict["quantity"]
        limit_order.lmtPrice = self.order_dict["limit_price"]
        limit_order.tif = self.order_dict["time_in_force"]
        limit_order.goodTillDate = self.order_dict["good_till_date"]
        limit_order.parentId = self.order_dict["parent_order_id"]
        limit_order.transmit = self.order_dict["transmit"]

        # self.client.placeOrder(self.order_dict["order_id"], self.contract, limit_order)
        return limit_order

    def get_stop_order(self, order_id):
        stop_order = Order()
        stop_order.orderId = order_id
        stop_order.action = self.order_dict["action"]
        stop_order.orderType = 'STP'
        stop_order.totalQuantity = self.order_dict["quantity"]
        stop_order.auxPrice = self.order_dict["stop_price"]
        stop_order.tif = self.order_dict["time_in_force"]
        stop_order.goodTillDate = self.order_dict["good_till_date"]
        stop_order.parentId = self.order_dict["parent_order_id"]
        stop_order.transmit = self.order_dict["transmit"]

        # self.client.placeOrder(self.order_dict["order_id"], self.contract, stop_order)
        return stop_order

    def send_bracket_order(self, parent_order, profit_order, stoploss_order):
        bracketOrder = [parent_order, profit_order, stoploss_order]

        for o in bracketOrder:
            self.client.placeOrder(o.orderId, self.contract, o)

    def send_order(self, order):
        self.client.placeOrder(self.order_dict["orderId"], self.contract, order)

    def ib_callback_open_order(self):
        pass

    #######################################################################################################
    # IB SPECIFIC CALLBACK FUNCTIONS
    def nextValidId(self, orderId):
        self.orderId = orderId
        time.sleep(1)

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)

    def positionEnd(self):
        super().positionEnd()

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        self.ib_callback_open_order()

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
