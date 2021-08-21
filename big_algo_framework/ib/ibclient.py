from ibapi.client import EClient
from ibapi.wrapper import EWrapper
import pandas as pd
import time
from big_algo_framework.big.database import createDB
from sqlalchemy import text

class BIGIBClient(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.db = createDB("market_data", "data/config.ini")

    def historicalData(self, reqId, bar):
        print("HistoricalData. ReqId:", reqId, "BarData.", bar)

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)

    def historicalDataUpdate(self, reqId, bar):
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
        data = dict(order_id=orderId,
                    perm_id=order.permId,
                    ticker=contract.symbol,
                    order_type=order.orderType,
                    action=order.action,
                    limit_price=order.lmtPrice,
                    stop_price=order.auxPrice,

                    order_status="",
                    filled=0.0,
                    remaining=0.0,
                    avg_fill_price=0.0,
                    parent_id=0,
                    last_fill_price=0.0,
                    client_id=0,
                    why_held="",

                    execution_time="",
                    order_ref=""
                    )

        df = pd.DataFrame(data=data)
        df.to_sql("orders", self.db, if_exists='append', index=False, method='multi')
        query = text("CREATE INDEX IF NOT EXISTS {} ON {} (order_id);".format("order_id", "orders"))
        with self.db.connect() as conn:
            conn.execute(query)

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        pd.read_sql_query("UPDATE orders SET "
                          "(order_status, filled, remaining, avg_fill_price, parent_id, client_id, why_held) = "
                          "(status, filled, remaining, avgFillPrice, parentId, clientId, whyHeld) "
                          "WHERE order_id = orderId;", con=self.db)

    def contractDetails(self, reqId, contractDetails):
        print("Contract Details: ", reqId, " ", contractDetails, "\n")
        self.mintick = contractDetails.minTick
        self.conid = contractDetails.contract.conId

    def contractDetailsEnd(self, reqId):
        print("\n Contract Details End \n")

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)

        pd.read_sql_query("UPDATE orders SET (execution_time, order_ref) = (execution.time, execution.orderRef) "
                          "WHERE order_id = execution.orderId;", con=self.db)
