from big_algo_framework.brokers.ib import *

class IbChild(IB):
    def __init__(self, db, orders_table):
        super().__init__()
        self.db = db
        self.orders_table = orders_table
        self.acc_dict = {}

    def nextValidId(self, orderId):
        super().nextValidId(orderId)

        self.orderId = orderId
        time.sleep(1)

    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)

        good_after_time = 0 if order.goodAfterTime == '' else order.goodAfterTime
        sql_str = f"INSERT INTO {self.orders_table}(order_id, perm_id, client_id, ticker, order_type, action, limit_price, stop_price, quantity, parent_id, time_in_force, good_till_date, good_after_time) " \
                  f"VALUES({orderId}, {order.permId}, {order.clientId}, '{contract.symbol}', '{order.orderType}', '{order.action}', {order.lmtPrice}, {order.auxPrice}, {order.totalQuantity}, {order.parentId}, '{order.tif}', '{order.goodTillDate}', '{good_after_time}') " \
                  f"ON CONFLICT(order_id) " \
                  f"DO UPDATE SET " \
                  f"order_id = {orderId}," \
                  f"perm_id = {order.permId}," \
                  f"client_id = {order.clientId}," \
                  f"ticker = '{contract.symbol}'," \
                  f"order_type = '{order.orderType}'," \
                  f"action = '{order.action}'," \
                  f"limit_price = {order.lmtPrice}," \
                  f"stop_price = {order.auxPrice}," \
                  f"quantity = {order.totalQuantity}," \
                  f"parent_id = {order.parentId}," \
                  f"time_in_force = '{order.tif}'," \
                  f"good_till_date = '{order.goodTillDate}'," \
                  f"good_after_time = '{order.goodAfterTime}';"

        with self.db.connect() as conn:
            conn.execute(sql_str)
            conn.close()
            self.db.dispose()

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId,
                            whyHeld, mktCapPrice)

        why_held = 0 if whyHeld == '' else whyHeld
        sql_str = f"INSERT INTO {self.orders_table}(order_id, order_status, filled, remaining, avg_fill_price, last_fill_price, client_id, why_held, mkt_cap_price) " \
                  f"VALUES({orderId}, '{status}', {filled}, {remaining}, {avgFillPrice}, {lastFillPrice}, {clientId}, '{why_held}', {mktCapPrice}) " \
                  f"ON CONFLICT(order_id) " \
                  f"DO UPDATE SET " \
                  f"order_status = '{status}'," \
                  f"filled = {filled}," \
                  f"remaining = {remaining}," \
                  f"avg_fill_price = {avgFillPrice}," \
                  f"last_fill_price = {lastFillPrice}," \
                  f"client_id = {clientId}," \
                  f"why_held = '{why_held}'," \
                  f"mkt_cap_price = {mktCapPrice};"

        with self.db.connect() as conn:
            conn.execute(sql_str)
            conn.close()
            self.db.dispose()

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)

        sql_str = f"INSERT INTO {self.orders_table}(order_id, exec_id, time, account_no, exchange, side, shares, price, liquidation, cum_qty, avg_price) " \
                  f"VALUES('{execution.orderId}', '{execution.execId}', '{execution.time}', '{execution.acctNumber}', '{execution.exchange}', '{execution.side}', {execution.shares}, {execution.price}, {execution.liquidation}, {execution.cumQty}, {execution.avgPrice}) " \
                  f"ON CONFLICT(order_id) " \
                  f"DO UPDATE SET " \
                  f"exec_id = '{execution.execId}'," \
                  f"time = '{execution.time}'," \
                  f"account_no = '{execution.acctNumber}'," \
                  f"exchange = '{execution.exchange}'," \
                  f"side = '{execution.side}'," \
                  f"shares = {execution.shares}," \
                  f"price = {execution.price}," \
                  f"liquidation = {execution.liquidation}," \
                  f"cum_qty = {execution.cumQty}," \
                  f"avg_price = {execution.avgPrice};"

        with self.db.connect() as conn:
            conn.execute(sql_str)
            conn.close()
            self.db.dispose()

    def commissionReport(self, commissionReport):
        super().commissionReport(commissionReport)

        sql_str = f"INSERT INTO {self.orders_table}(exec_id, commission, currency, realized_pn) " \
                  f"VALUES('{commissionReport.execId}', {commissionReport.commission}, '{commissionReport.currency}', {commissionReport.realizedPNL}) " \
                  f"ON CONFLICT(exec_id) " \
                  f"DO UPDATE SET " \
                  f"commission = {commissionReport.commission}," \
                  f"currency = '{commissionReport.currency}'," \
                  f"realized_pnl = {commissionReport.realizedPNL};"

        with self.db.connect() as conn:
            conn.execute(sql_str)
            conn.close()
            self.db.dispose()

    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)

        self.mintick = contractDetails.minTick
        self.conid = contractDetails.contract.conId

    def updateAccountValue(self, key, val, currency, accountName):
        super().updateAccountValue(key, val, currency, accountName)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        self.acc_dict[tag] = value
