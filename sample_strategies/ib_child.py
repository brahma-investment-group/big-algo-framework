from big_algo_framework.brokers.ib import *

class IbChild(IB):
    def __init__(self, db):
        super().__init__()

        self.db = db

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

        df = pd.DataFrame(data=data, index=[0])
        o_id = pd.read_sql_query("select order_id from orders where order_id = {};".format(orderId), con=self.db)

        if orderId not in o_id.values:
            df.to_sql("orders", self.db, if_exists='append', index=False, method='multi')

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                            whyHeld, mktCapPrice)

        sql_str = """UPDATE orders SET order_status = %s, filled = %s, remaining = %s, avg_fill_price = %s, parent_id = %s, client_id = %s, why_held = %s WHERE order_id = %s;"""
        with self.db.connect() as conn:
            conn.execute(sql_str, (status, filled, remaining, avgFillPrice, parentId, clientId, whyHeld, orderId))
            conn.close()
            self.db.dispose()

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)

        sql_str = """UPDATE orders SET execution_time = %s, order_ref = %s WHERE order_id = %s;"""
        with self.db.connect() as conn:
            conn.execute(sql_str, (execution.time, execution.orderRef, execution.orderId))
            conn.close()
            self.db.dispose()
