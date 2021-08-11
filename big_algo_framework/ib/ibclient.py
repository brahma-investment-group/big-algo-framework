from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import pandas as pd
import time
from big_algo_framework.big.database import createDB

class BIGIBClient(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}
        self.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType',
                                    'Currency', 'Position', 'Avg cost'])
        self.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId',
                                          'Account', 'Symbol', 'SecType',
                                          'Exchange', 'Action', 'OrderType',
                                          'TotalQty', 'CashQty', 'LmtPrice',
                                          'AuxPrice', 'Status'])

        self.orderStatus_df = pd.DataFrame(columns=['OrderStatus. Id', 'Status', 'Filled', 'Remaining',
                                                    'AvgFillPrice', 'PermId', 'ParentId', 'LastFillPrice', 'ClientId',
                                                    'WhyHeld', 'MktCapPrice'])

        self.db = createDB("market_data", "data/config.ini")


    def historicalData(self, reqId, bar):
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)

    def historicalDataEnd(self, reqId, start, end):
        print("THIS ISSS:", reqId)
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    def historicalDataUpdate(self, reqId, bar):
        print("THIS IS:", reqId)
        print("HistoricalDataUpdate. ReqId:", reqId, "BarData.", bar)

    def nextValidId(self, orderId):
        self.orderId = orderId
        time.sleep(1)

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        dictionary = {"Account":account, "Symbol": contract.symbol, "SecType": contract.secType,
                      "Currency": contract.currency, "Position": position, "Avg cost": avgCost}
        self.pos_df = self.pos_df.append(dictionary, ignore_index=True)

    def positionEnd(self):
        print("Latest position data extracted")

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        print("OPEN ORDERS")
        dictionary = {"PermId":order.permId, "ClientId": order.clientId, "OrderId": orderId,
                      "Symbol": contract.symbol,"Action": order.action, "OrderType": order.orderType,
                      "LmtPrice": order.lmtPrice, "AuxPrice": order.auxPrice, "Status": orderState.status}
        self.order_df = self.order_df.append(dictionary, ignore_index=True)

        table = self.db["orders"]

        data = dict(orderId=orderId,
                    permId=order.permId,
                    ticker=contract.symbol,
                    orderType=order.orderType,
                    action=order.action,
                    limitPrice=order.lmtPrice,
                    stopPrice=order.auxPrice,
                    )

        table.upsert(data, ['orderId'])

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        Statusdictionary = {"OrderId": orderId,
              "Status": status,
              "Filled": filled,
              "Remaining": remaining,
              "AvgFillPrice": avgFillPrice,
              "PermId": permId,
              "ParentId": parentId,
              "LastFillPrice": lastFillPrice,
              "ClientId": clientId,
              "WhyHeld": whyHeld,
              "MktCapPrice": mktCapPrice}

        self.orderStatus_df = self.orderStatus_df.append(Statusdictionary, ignore_index=True)

        table = self.db["orders"]

        data = dict(orderId=orderId,
                    status=status,
                    filled=filled,
                    remaining=remaining,
                    avgFillPrice=avgFillPrice,
                    parentId=parentId,
                    clientId=clientId,
                    whyHeld=whyHeld)

        table.upsert(data, ['orderId'])

    def contractDetails(self, reqId, contractDetails):
        print("Contract Details: ", reqId, " ", contractDetails, "\n")

        self.mintick = contractDetails.minTick
        self.conid = contractDetails.contract.conId

    def contractDetailsEnd(self, reqId):
        print("\n Contract Details End \n")

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        print("ExecDetails. ReqId:", reqId, "Symbol:", contract.symbol, "SecType:", contract.secType, "Currency:",
              contract.currency, execution, "Order Ref: ", execution.orderRef)

        table = self.db["orders"]

        data = dict(orderId=execution.orderId,
                    Executiontime=execution.time,
                    orderRef = execution.orderRef)

        table.upsert(data, ['orderId'])
