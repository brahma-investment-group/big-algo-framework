from ibapi.order import Order
import time
from datetime import datetime

class BIGOrders():
    def __init__(self):
        pass

    def getOrderID(self, client):
        client.reqIds(1)
        time.sleep(1)

    def open_order(self, client, contract, order_id, order):
        now = datetime.now().strftime('%Y%m%d, %H:%M:%S')
        print(now, " : order opened")
        client.placeOrder(order_id, contract, order)
        time.sleep(2)

    def marketOrder(self, orderId, action, quantity, parent_orderId, transmit):
        main_order = Order()
        main_order.orderId = orderId
        main_order.action = action
        main_order.orderType = 'MKT'
        main_order.totalQuantity = quantity
        main_order.parentId = parent_orderId
        main_order.transmit = transmit

        return main_order

    def stopLimitOrder(self, orderId, action, quantity, stopPrice, limitPrice, timeInForce, goodTillDate, parent_orderId, transmit):
        main_order = Order()
        main_order.orderId = orderId
        main_order.action = action
        main_order.orderType = 'STP LMT'
        main_order.totalQuantity = quantity
        main_order.lmtPrice = limitPrice
        main_order.auxPrice = stopPrice
        main_order.tif = timeInForce
        main_order.goodTillDate = goodTillDate
        main_order.parentId = parent_orderId
        main_order.transmit = transmit

        return main_order

    def limitOrder(self, orderId, action, quantity, limitPrice, timeInForce, goodTillDate, parent_orderId, transmit):
        main_order = Order()
        main_order.orderId = orderId
        main_order.action = action
        main_order.orderType = 'LMT'
        main_order.totalQuantity = quantity
        main_order.lmtPrice = limitPrice
        main_order.tif = timeInForce
        main_order.goodTillDate = goodTillDate
        main_order.parentId = parent_orderId
        main_order.transmit = transmit

        return main_order

    def stopOrder(self, orderId, action, quantity, stopPrice, timeInForce, goodTillDate, parent_orderId, transmit):
        main_order = Order()
        main_order.orderId = orderId
        main_order.action = action
        main_order.orderType = 'STP'
        main_order.totalQuantity = quantity
        main_order.auxPrice = stopPrice
        main_order.tif = timeInForce
        main_order.goodTillDate = goodTillDate
        main_order.parentId = parent_orderId
        main_order.transmit = transmit

        return main_order

    def sendBracketOrder(self, client, contract, order_dict, parentOrderId, profitOrderId, stopLossOrderId):
        parent = self.stopLimitOrder(orderId= parentOrderId,
                                     action= order_dict["action"],
                                     quantity= order_dict["quantity"],
                                     stopPrice= order_dict["entryPrice"],
                                     limitPrice= order_dict["entryPrice"],
                                     timeInForce= order_dict["entryTIF"],
                                     goodTillDate= order_dict["entryGoodTillDate"],
                                     parent_orderId= "",
                                     transmit= False)

        takeProfit = self.limitOrder(orderId = profitOrderId,
                                     action= order_dict["reverseAction"],
                                     quantity= order_dict["quantity"],
                                     limitPrice= order_dict["profitPrice"],
                                     timeInForce= "GTC",
                                     goodTillDate= "",
                                     parent_orderId= parentOrderId,
                                     transmit= False)

        stopLoss = self.stopOrder(orderId= stopLossOrderId,
                                  action= order_dict["reverseAction"],
                                  quantity= order_dict["quantity"],
                                  stopPrice= order_dict["stopLossPrice"],
                                  timeInForce= "GTC",
                                  goodTillDate= "",
                                  parent_orderId= parentOrderId,
                                  transmit= True)

        bracketOrder = [parent, takeProfit, stopLoss]

        for o in bracketOrder:
            client.placeOrder(o.orderId, contract, o)

        print(order_dict)

    def ModifyStopLoss(self, client, contract, order_dict):
        parent = self.stopOrder(order_dict["orderId"],
                                    action = order_dict["action"],
                                    quantity = order_dict["quantity"],
                                    stopPrice = order_dict["stopLossPrice"],
                                    timeInForce = order_dict["entryTIF"],
                                    goodTillDate = order_dict["entryGoodTillDate"],
                                    parent_orderId = "",
                                    transmit = True)


        client.placeOrder(order_dict["orderId"], contract, parent)

    def ModifyTakeProfit(self, client, contract, order_dict):
        parent = self.limitOrder(orderId = order_dict["orderId"],
                                    action = order_dict["action"],
                                    quantity = order_dict["quantity"],
                                    limitPrice = order_dict["profitPrice"],
                                    timeInForce = order_dict["entryTIF"],
                                    goodTillDate = order_dict["entryGoodTillDate"],
                                    parent_orderId = "",
                                    transmit = True)

        client.placeOrder(order_dict["orderId"], contract, parent)

    def ModifyMarketOrder(self, client, contract, order_dict):
        parent = self.marketOrder(orderId = order_dict["orderId"],
                                    action = order_dict["action"],
                                    quantity = order_dict["quantity"],
                                    parent_orderId = "",
                                    transmit = True)

        client.placeOrder(order_dict["orderId"], contract, parent)
