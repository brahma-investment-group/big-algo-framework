from big_algo_framework.brokers.abstract_broker import Broker
from big_algo_framework.big.helper import truncate
import time
import threading
from sqlalchemy import text
import pandas as pd
from ibapi.order import Order
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import PriceCondition
from ibapi.account_summary_tags import AccountSummaryTags

class IB(Broker, EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.orderId = 0
        self.acc_dict = {}

    # Authentication
    def init_client(self, client, order_dict):
        self.client = client
        self.orders_table = order_dict['orders_table']
        self.db = order_dict['db']

    def websocket_con(self, broker):
        broker.run()

    def connect_broker(self, broker, ip_address, port, ib_client):
        # Connects to interactive brokers with the specified port/client and returns the last order ID.
        broker.connect(ip_address, port, ib_client)
        time.sleep(1)
        broker.reqPositions()
        time.sleep(1)
        broker.reqOpenOrders()
        time.sleep(1)
        broker.reqAccountSummary(9001, "All", AccountSummaryTags.AllTags)
        time.sleep(1)

        con_thread = threading.Thread(target=self.websocket_con, args=(broker,), daemon=True)
        con_thread.start()
        time.sleep(1)

        broker.reqIds(1)
        time.sleep(1)

        return broker.orderId

    # Asset
    def get_contract(self, order_dict):
        self.contract = Contract()
        self.contract.symbol = order_dict["ticker"]
        self.contract.secType = order_dict["sec_type"]
        self.contract.currency = order_dict["currency"]
        self.contract.exchange = order_dict["exchange"]
        self.contract.primaryExchange = order_dict["primary_exchange"] #For options leave blank
        self.contract.lastTradeDateOrContractMonth = order_dict["lastTradeDateOrContractMonth"]
        self.contract.strike = order_dict["strike"]
        self.contract.right = order_dict["right"]
        self.contract.multiplier = order_dict["multiplier"]

        return self.contract

    # Prepare/Send Orders
    def get_market_order(self, order_dict):
        market_order = Order()
        market_order.orderId = order_dict["mkt_order_id"]
        market_order.action = order_dict["mkt_action"]
        market_order.orderType = 'MKT'
        market_order.totalQuantity = order_dict["mkt_quantity"]
        market_order.tif = order_dict["mkt_time_in_force"]
        market_order.goodTillDate = order_dict["mkt_good_till_date"]
        market_order.goodAfterTime = order_dict["mkt_good_after_date"]
        market_order.account = order_dict["account_no"]
        market_order.transmit = order_dict["mkt_transmit"]

        return market_order

    def get_stop_limit_order(self, order_dict, digits=2):
        stop_limit_order = Order()
        stop_limit_order.orderId = order_dict["slo_order_id"]
        stop_limit_order.action = order_dict["slo_action"]
        stop_limit_order.orderType = 'STP LMT'
        stop_limit_order.totalQuantity = order_dict["slo_quantity"]
        stop_limit_order.lmtPrice = truncate(order_dict["slo_limit_price"], digits)
        stop_limit_order.auxPrice = truncate(order_dict["slo_stop_price"], digits)
        stop_limit_order.tif = order_dict["slo_time_in_force"]
        stop_limit_order.goodTillDate = order_dict["slo_good_till_date"]
        stop_limit_order.goodAfterTime = order_dict["slo_good_after_date"]
        stop_limit_order.account = order_dict["account_no"]
        stop_limit_order.transmit = order_dict["slo_transmit"]

        return stop_limit_order

    def get_limit_order(self, order_dict, digits=2):
        limit_order = Order()
        limit_order.orderId = order_dict["lo_order_id"]
        limit_order.action = order_dict["lo_action"]
        limit_order.orderType = 'LMT'
        limit_order.totalQuantity = order_dict["lo_quantity"]
        limit_order.lmtPrice = truncate(order_dict["lo_limit_price"], digits)
        limit_order.tif = order_dict["lo_time_in_force"]
        limit_order.goodTillDate = order_dict["lo_good_till_date"]
        limit_order.goodAfterTime = order_dict["lo_good_after_date"]
        limit_order.account = order_dict["account_no"]
        limit_order.transmit = order_dict["lo_transmit"]

        return limit_order

    def get_stop_order(self, order_dict, digits=2):
        stop_order = Order()
        stop_order.orderId = order_dict["so_order_id"]
        stop_order.action = order_dict["so_action"]
        stop_order.orderType = 'STP'
        stop_order.totalQuantity = order_dict["so_quantity"]
        stop_order.auxPrice = truncate(order_dict["so_stop_price"], digits)
        stop_order.tif = order_dict["so_time_in_force"]
        stop_order.goodTillDate = order_dict["so_good_till_date"]
        stop_order.goodAfterTime = order_dict["so_good_after_date"]
        stop_order.account = order_dict["account_no"]
        stop_order.transmit = order_dict["so_transmit"]

        return stop_order

    def get_trailing_stop_order(self, orders, trail_type, trail_amount, trail_stop, digits=2):
       for o in orders:
           o.orderType = "TRAIL"
           o.trailStopPrice = truncate(trail_stop, digits)

           if str.upper(trail_type) == "AMOUNT":
               o.auxPrice = truncate(trail_amount, digits)

           elif str.upper(trail_type) == "PERCENTAGE":
               o.auxPrice = ""
               o.trailingPercent = trail_amount

       return o

    def get_oto_order(self, orders):
        parent_order_id = orders[0].orderId
        for o in orders:
            o.parentId = parent_order_id

        return o

    def get_oco_order(self, orders, oca_group_name, oca_group_type):
        for o in orders:
            o.ocaGroup = oca_group_name
            o.ocaType = oca_group_type

        return o

    def send_order(self, order_id, contract, order):
        self.client.placeOrder(order_id, contract, order)
        time.sleep(1)

    # Get Orders/Positions
    def get_order_by_ticker(self, order_dict):
        all_orders = self.get_all_orders(order_dict)
        return all_orders[all_orders['cont_ticker'] == order_dict["ticker"]]

    def get_all_orders(self, order_dict):
        return pd.read_sql_query(f"select * from {order_dict['strategy_table']} where status IN ('Open');", con=order_dict['db'])

    def get_position_by_ticker(self, order_dict):
        all_positions = self.get_all_positions(order_dict)
        return all_positions[all_positions['cont_ticker'] == order_dict["ticker"]]

    def get_all_positions(self, order_dict):
        return pd.read_sql_query(f"select cont_ticker from {order_dict['strategy_table']} where status IN ('In Progress');", con = order_dict['db'])

    # Cancel Orders/Close Positions
    def cancel_order(self, order_dict, order_id):
        order_dict['broker'].cancelOrder(order_id)

    def cancel_all_orders(self, order_dict):
        open_orders = self.get_all_orders(order_dict)

        for ind in open_orders.index:
            order_id = open_orders['parent_order_id'][ind]
            self.cancel_order(order_dict, order_id)

    def close_position(self, pos_order_dict, underlying=False):
        broker = pos_order_dict['broker']
        sec_type = pos_order_dict['sec_type']
        direction = pos_order_dict['direction']
        opt_right = pos_order_dict['right']
        stock_conid = pos_order_dict['stock_conid']
        cont_exchange = pos_order_dict['exchange']

        pos_con = broker.get_contract(pos_order_dict)
        mkt_order = broker.get_market_order(pos_order_dict)

        if underlying:
            if sec_type == "STK":
                is_greater_than = True if direction == "Bullish" else False
                price = 0 if direction == "Bullish" else 99999

            if sec_type == "OPT":
                if opt_right == "C" and direction == "Bullish":
                    is_greater_than = True
                    price = 0

                elif opt_right == "C" and direction == "Bearish":
                    is_greater_than = False
                    price = 99999

                elif opt_right == "P" and direction == "Bullish":
                    is_greater_than = False
                    price = 99999

                elif opt_right == "P" and direction == "Bearish":
                    is_greater_than = True
                    price = 0

            tp_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, stock_conid, cont_exchange, is_greater_than, price)
            mkt_order.conditions.append(tp_price_condition)

        broker.send_order(pos_order_dict["order_id"], pos_con, mkt_order)

    def close_all_positions(self, order_dict, underlying=False):
        open_positions = pd.read_sql_query(
            f"select * from {order_dict['orders_table']} LEFT OUTER JOIN {order_dict['strategy_table']} ON {order_dict['strategy_table']}.profit_order_id = order_id WHERE {order_dict['strategy_table']}.status IN ('In Progress');", con = order_dict['db'])

        for ind in open_positions.index:
            pos_order_dict = {
                "ticker": open_positions.iloc[ind]['cont_ticker'],
                "sec_type": open_positions.iloc[ind]['sec_type'],
                "currency": open_positions.iloc[ind]['cont_currency'],
                "exchange": open_positions.iloc[ind]['cont_exchange'],
                "primary_exchange": open_positions.iloc[ind]['primary_exchange'],
                "stock_conid": open_positions.iloc[ind]['stock_conid'],
                "direction": open_positions.iloc[ind]['direction'],

                "lastTradeDateOrContractMonth": open_positions.iloc[ind]['cont_date'],
                "strike": open_positions.iloc[ind]['strike'],
                "right": open_positions.iloc[ind]['opt_right'],
                "multiplier": open_positions.iloc[ind]['multiplier'],

                "mkt_order_id": open_positions.iloc[ind]['order_id'],
                "mkt_action": open_positions.iloc[ind]['action'],
                "mkt_quantity": open_positions.iloc[ind]['remaining'],
                "mkt_parent_order_id": "",
                "mkt_time_in_force": "",
                "mkt_good_till_date": "",
                "account_no": order_dict['account_no'],
                "mkt_transmit": True,

                "order_id": open_positions.iloc[ind]['order_id'],
                "broker": order_dict['broker']
            }

            self.close_position(pos_order_dict, underlying)

    # Miscellaneous
    def getOrderID(self, client):
        client.reqIds(1)
        time.sleep(1)

    def set_strategy_status(self, order_dict):
        strategy_order_ids = pd.read_sql_query(f"select parent_order_id, profit_order_id, stoploss_order_id from {order_dict['strategy_table']} where status IN (' ', 'Open', 'In Progress') ;", con = order_dict['db'])

        closed_status = ['PendingCancel', 'ApiCancelled', 'Cancelled', 'Inactive']
        open_status = ['ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted']
        filled_status = ['Filled']

        for i in range (0, len(strategy_order_ids)):
            row = strategy_order_ids.iloc[i]

            parent_order_id = row['parent_order_id']
            profit_order_id = row['profit_order_id']
            stoploss_order_id = row['stoploss_order_id']

            parent_order_status = pd.read_sql_query(f"select order_status from {order_dict['orders_table']} WHERE order_id = {parent_order_id};", con = order_dict['db'])
            stoploss_order_status = pd.read_sql_query(f"select order_status from {order_dict['orders_table']} WHERE order_id = {stoploss_order_id};", con = order_dict['db'])
            profit_order_status = pd.read_sql_query(f"select order_status from {order_dict['orders_table']} WHERE order_id = {profit_order_id};", con = order_dict['db'])

            if (parent_order_status.values in filled_status) and (stoploss_order_status.values in open_status or profit_order_status.values in open_status):
                query = text(f"UPDATE {order_dict['strategy_table']} SET status = 'In Progress' WHERE parent_order_id = {parent_order_id};")

            elif (parent_order_status.values in filled_status) and (stoploss_order_status.values in filled_status or profit_order_status.values in filled_status):
                query = text(f"UPDATE {order_dict['strategy_table']} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif (parent_order_status.values in filled_status) and (stoploss_order_status.values in closed_status or profit_order_status.values in closed_status):
                query = text(f"UPDATE {order_dict['strategy_table']} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in closed_status:
                query = text(f"UPDATE {order_dict['strategy_table']} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in open_status:
                query = text(f"UPDATE {order_dict['strategy_table']} SET status = 'Open' WHERE parent_order_id = {parent_order_id};")

            else:
                query = text(f"UPDATE {order_dict['strategy_table']} SET status = ' ' WHERE parent_order_id = {parent_order_id};")

            with order_dict['db'].connect() as conn:
                conn.execute(query)
                conn.close()
                order_dict['db'].dispose()

    # IB SPECIFIC CALLBACK FUNCTIONS
    def nextValidId(self, orderId):
        super().nextValidId(orderId)

        self.orderId = orderId
        time.sleep(1)

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)

    def positionEnd(self):
        super().positionEnd()

    def positionMulti(self, reqId, account, modelCode, contract, pos, avgCost):
        super().positionMulti(reqId, account, modelCode, contract, pos, avgCost)

    def positionMultiEnd(self, reqId: int):
        super().positionMultiEnd(reqId)

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
        super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)

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

    def contractDetails(self, reqId, contractDetails):
        super().contractDetails(reqId, contractDetails)

        self.mintick = contractDetails.minTick
        self.conid = contractDetails.contract.conId

    def contractDetailsEnd(self, reqId):
        super().contractDetailsEnd(reqId)

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

        sql_str = f"INSERT INTO {self.orders_table}(exec_id, commission, currency, realized_pnl) " \
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

    def updateAccountValue(self, key, val, currency, accountName):
        super().updateAccountValue(key, val, currency, accountName)

    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        self.acc_dict[tag] = value
