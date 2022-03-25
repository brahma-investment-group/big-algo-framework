from big_algo_framework.brokers.abstract_broker import Broker
import time
from sqlalchemy import text
import pandas as pd
from ibapi.order import Order
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order_condition import PriceCondition

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
        self.contract.primaryExchange = order_dict["primary_exchange"] #For options leave blank
        self.contract.lastTradeDateOrContractMonth = order_dict["lastTradeDateOrContractMonth"]
        self.contract.strike = order_dict["strike"]
        self.contract.right = order_dict["right"]
        self.contract.multiplier = order_dict["multiplier"]

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
        market_order.tif = order_dict["mkt_time_in_force"]
        market_order.goodTillDate = order_dict["mkt_good_till_date"]
        market_order.account = order_dict["account_no"]
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
        stop_limit_order.account = order_dict["account_no"]
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
        limit_order.account = order_dict["account_no"]
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
        stop_order.account = order_dict["account_no"]
        stop_order.transmit = order_dict["so_transmit"]

        return stop_order

    def send_bracket_order(self, *orders):
        bracketOrder = []
        for x in orders:
            bracketOrder.append(x)

        for o in bracketOrder:
            self.client.placeOrder(o.orderId, self.contract, o)

    def send_order(self, order_dict, contract, order):
        self.client.placeOrder(order_dict["order_id"], contract, order)
        time.sleep(1)

    def set_strategy_status(self, order_dict):
        strategy_order_ids = pd.read_sql_query(f"select parent_order_id, profit_order_id, stoploss_order_id from {order_dict['strategy_table']} where status IN (' ', 'Open', 'In Progress') ;", con=order_dict['db'])

        closed_status = ['PendingCancel', 'ApiCancelled', 'Cancelled', 'Inactive']
        open_status = ['ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted']
        filled_status = ['Filled']

        for i in range (0, len(strategy_order_ids)):
            row = strategy_order_ids.iloc[i]

            parent_order_id = row['parent_order_id']
            profit_order_id = row['profit_order_id']
            stoploss_order_id = row['stoploss_order_id']

            parent_order_status = pd.read_sql_query(f"select order_status from {order_dict['orders_table']} WHERE order_id = {parent_order_id};", con=order_dict['db'])
            stoploss_order_status = pd.read_sql_query(f"select order_status from {order_dict['orders_table']} WHERE order_id = {stoploss_order_id};", con=order_dict['db'])
            profit_order_status = pd.read_sql_query(f"select order_status from {order_dict['orders_table']} WHERE order_id = {profit_order_id};", con=order_dict['db'])

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

    def is_exist_positions(self, order_dict):
        ticker_pos = pd.read_sql_query(f"select cont_ticker from {order_dict['strategy_table']} where status IN ('Open', 'In Progress');", con=order_dict['db'])

        if order_dict['ticker'] not in ticker_pos.values:
            return True

        else:
            return False

    def close_all_positions(self, order_dict):
        # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders
        open_orders = pd.read_sql_query(f"select parent_order_id from {order_dict['strategy_table']} WHERE status IN ('Open');", con=order_dict['db'])

        for ind in open_orders.index:
            order_id = open_orders['parent_order_id'][ind]
            order_dict['broker'].cancelOrder(order_id)

        # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
        open_positions = pd.read_sql_query(
            f"select * from {order_dict['orders_table']} LEFT OUTER JOIN {order_dict['strategy_table']} ON {order_dict['strategy_table']}.profit_order_id = order_id WHERE {order_dict['strategy_table']}.status IN ('In Progress');", con=order_dict['db'])

        for ind in open_positions.index:
            cont_ticker = open_positions.iloc[ind]['cont_ticker']
            sec_type = open_positions.iloc[ind]['sec_type']
            cont_currency = open_positions.iloc[ind]['cont_currency']
            cont_exchange = open_positions.iloc[ind]['cont_exchange']
            primary_exchange = open_positions.iloc[ind]['primary_exchange']
            stock_conid = open_positions.iloc[ind]['stock_conid']

            order_id = open_positions.iloc[ind]['order_id']
            remaining = open_positions.iloc[ind]['remaining']
            action = open_positions.iloc[ind]['action']

            cont_date = open_positions.iloc[ind]['cont_date']
            strike = open_positions.iloc[ind]['strike']
            opt_right = open_positions.iloc[ind]['opt_right']
            multiplier = open_positions.iloc[ind]['multiplier']

            pos_order_dict = {
                "ticker": cont_ticker,
                "sec_type": sec_type,
                "currency": cont_currency,
                "exchange": cont_exchange,
                "primary_exchange": primary_exchange,

                "lastTradeDateOrContractMonth": cont_date,
                "strike": strike,
                "right": opt_right,
                "multiplier": multiplier,

                "mkt_order_id": order_id,
                "mkt_action": action,
                "mkt_quantity": remaining,
                "mkt_parent_order_id": "",
                "mkt_time_in_force": "",
                "mkt_good_till_date": "",
                "account_no": order_dict['account_no'],
                "mkt_transmit": True,

                "order_id": order_id
            }

            pos_con = order_dict['broker'].get_contract(pos_order_dict)
            mkt_order = order_dict['broker'].get_market_order(pos_order_dict)
            order_dict['broker'].send_order(pos_order_dict, pos_con, mkt_order)

    def close_all_positions_underlying(self, order_dict):
        # TODO: This function is exactly the same as above function, except few lines. Maybe we can do something in order to avoid repeating the code
        # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders
        open_orders = pd.read_sql_query(f"select parent_order_id from {order_dict['strategy_table']} WHERE status IN ('Open');", con=order_dict['db'])

        for ind in open_orders.index:
            order_id = open_orders['parent_order_id'][ind]
            order_dict['broker'].cancelOrder(order_id)

        # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
        open_positions = pd.read_sql_query(
            f"select * from {order_dict['orders_table']} LEFT OUTER JOIN {order_dict['strategy_table']} ON {order_dict['strategy_table']}.profit_order_id = order_id WHERE {order_dict['strategy_table']}.status IN ('In Progress');", con=order_dict['db'])

        for ind in open_positions.index:
            cont_ticker = open_positions.iloc[ind]['cont_ticker']
            sec_type = open_positions.iloc[ind]['sec_type']
            cont_currency = open_positions.iloc[ind]['cont_currency']
            cont_exchange = open_positions.iloc[ind]['cont_exchange']
            primary_exchange = open_positions.iloc[ind]['primary_exchange']
            stock_conid = open_positions.iloc[ind]['stock_conid']

            order_id = open_positions.iloc[ind]['order_id']
            remaining = open_positions.iloc[ind]['remaining']
            action = open_positions.iloc[ind]['action']

            cont_date = open_positions.iloc[ind]['cont_date']
            strike = open_positions.iloc[ind]['strike']
            opt_right = open_positions.iloc[ind]['opt_right']
            multiplier = open_positions.iloc[ind]['multiplier']

            pos_order_dict = {
                "ticker": cont_ticker,
                "sec_type": sec_type,
                "currency": cont_currency,
                "exchange": cont_exchange,
                "primary_exchange": primary_exchange,

                "lastTradeDateOrContractMonth": cont_date,
                "strike": strike,
                "right": opt_right,
                "multiplier": multiplier,

                "mkt_order_id": order_id,
                "mkt_action": action,
                "mkt_quantity": remaining,
                "mkt_parent_order_id": "",
                "mkt_time_in_force": "",
                "mkt_good_till_date": "",
                "account_no": order_dict['account_no'],
                "mkt_transmit": True,

                "order_id": order_id
            }

            # TODO: Make below lines general for stocks and options (For options, take into consideration both opt_right and direction)
            x = True if opt_right == "C" else False
            price = 0 if opt_right == "C" else 99999

            pos_con = order_dict['broker'].get_contract(pos_order_dict)

            tp_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, stock_conid, cont_exchange, x, price)
            mkt_order = order_dict['broker'].get_market_order(pos_order_dict)
            mkt_order.conditions.append(tp_price_condition)

            order_dict['broker'].send_order(pos_order_dict, pos_con, mkt_order)

    #######################################################################################################
    # IB SPECIFIC CALLBACK FUNCTIONS
    def nextValidId(self, orderId):
        super().nextValidId(orderId)

    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)

    def positionEnd(self):
        super().positionEnd()

    def positionMulti(self, reqId, account, modelCode, contract, pos, avgCost):
        super().positionMulti(reqId, account, modelCode, contract, pos, avgCost)
        print("PositionMulti. RequestId:", reqId, "Account:", account,
        "ModelCode:", modelCode, "Symbol:", contract.symbol, "SecType:",
        contract.secType, "Currency:", contract.currency, ",Position:",
        pos, "AvgCost:", avgCost)

    def positionMultiEnd(self, reqId: int):
        super().positionMultiEnd(reqId)
        print("PositionMultiEnd. RequestId:", reqId)

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
