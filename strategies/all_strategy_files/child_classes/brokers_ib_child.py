from big_algo_framework.brokers.ib import *

class IbChild(IB):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.acc_dict = {}

    def nextValidId(self, orderId):
        super().nextValidId(orderId)

        self.orderId = orderId
        # print(orderId)
        time.sleep(1)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)

        sql_str = """INSERT INTO orders(order_id, perm_id, client_id, ticker, order_type, action, limit_price, stop_price, quantity, parent_id, time_in_force, oca_group, oca_type, trigger, rth, good_till_date, good_after_time)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT(order_id)
                        DO UPDATE SET
                            order_id = %s,
                            perm_id = %s,
                            client_id = %s,
                            ticker = %s,
                            order_type = %s,
                            action = %s,
                            limit_price = %s,
                            stop_price = %s,
                            quantity = %s,
                            parent_id = %s,
                            time_in_force = %s,
                            oca_group = %s,
                            oca_type = %s,
                            trigger = %s,
                            rth = %s,
                            good_till_date = %s,
                            good_after_time = %s;"""

        with self.db.connect() as conn:
            conn.execute(sql_str, (orderId, order.permId, order.clientId, contract.symbol, order.orderType, order.action, order.lmtPrice, order.auxPrice, order.totalQuantity, order.parentId, order.tif, order.ocaGroup, order.ocaType, order.triggerMethod, order.outsideRth, order.goodTillDate, order.goodAfterTime,
                                   orderId, order.permId, order.clientId, contract.symbol, order.orderType, order.action, order.lmtPrice, order.auxPrice, order.totalQuantity, order.parentId, order.tif, order.ocaGroup, order.ocaType, order.triggerMethod, order.outsideRth, order.goodTillDate, order.goodAfterTime))
            conn.close()
            self.db.dispose()

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                            whyHeld, mktCapPrice)

        sql_str = """INSERT INTO orders(order_id, order_status, filled, remaining, avg_fill_price, last_fill_price, client_id, why_held, mkt_cap_price)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT(order_id)
                DO UPDATE SET
                    order_status = %s, 
                    filled = %s, 
                    remaining = %s, 
                    avg_fill_price = %s, 
                    last_fill_price = %s, 
                    client_id = %s, 
                    why_held = %s, 
                    mkt_cap_price = %s;"""

        with self.db.connect() as conn:
            conn.execute(sql_str, (orderId, status, filled, remaining, avgFillPrice, lastFillPrice, clientId, whyHeld, mktCapPrice,
                                   status, filled, remaining, avgFillPrice, lastFillPrice, clientId, whyHeld, mktCapPrice))
            conn.close()
            self.db.dispose()

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)

        sql_str = """INSERT INTO orders(order_id, exec_id, time, account_no, exchange, side, shares, price, liquidation, cum_qty, avg_price)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT(order_id)
        DO UPDATE SET
            exec_id = %s,
            time = %s,
            account_no = %s,
            exchange = %s,
            side = %s,
            shares = %s,
            price = %s,
            liquidation = %s,
            cum_qty = %s,
            avg_price = %s;"""

        with self.db.connect() as conn:
            conn.execute(sql_str, (execution.orderId, execution.execId, execution.time, execution.acctNumber, execution.exchange, execution.side, execution.shares, execution.price, execution.liquidation, execution.cumQty, execution.avgPrice,
                                   execution.execId, execution.time, execution.acctNumber, execution.exchange, execution.side, execution.shares, execution.price, execution.liquidation, execution.cumQty, execution.avgPrice))
            conn.close()
            self.db.dispose()

    def commissionReport(self, commissionReport):
        super().commissionReport(commissionReport)

        sql_str = """INSERT INTO orders(exec_id, commission, currency, realized_pnl)
                VALUES(%s, %s, %s, %s)
                ON CONFLICT(exec_id)
                DO UPDATE SET
                    commission = %s,
                    currency = %s,
                    realized_pnl = %s;"""

        with self.db.connect() as conn:
            conn.execute(sql_str, (commissionReport.execId, commissionReport.commission, commissionReport.currency, commissionReport.realizedPNL,
                                   commissionReport.commission, commissionReport.currency, commissionReport.realizedPNL))
            conn.close()
            self.db.dispose()

    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)

        self.mintick = contractDetails.minTick
        self.conid = contractDetails.contract.conId

        print("Min tick: ", self.mintick)

    def updateAccountValue(self, key, val, currency, accountName):
        super().updateAccountValue(key, val, currency, accountName)
        # print("UpdateAccountValue. Key:", key, "Value:", val,
        # "Currency:", currency, "AccountName:", accountName)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        # print("AccountSummary. ReqId:", reqId, "Account:", account,
        # "Tag: ", tag, "Value:", value, "Currency:", currency)

        self.acc_dict[tag] = value


