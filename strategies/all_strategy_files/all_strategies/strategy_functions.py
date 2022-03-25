from sqlalchemy import text
import pandas as pd
from ibapi.order_condition import PriceCondition

class StrategyFunctions():
    def __init__(self, db, ticker, broker, order_dict, orders_table, strategy_table):
        self.db = db
        self.ticker = ticker
        self.broker = broker
        self.order_dict = order_dict
        self.strategy_table = strategy_table
        self.orders_table = orders_table

    def set_strategy_status(self):
        strategy_order_ids = pd.read_sql_query(f"select parent_order_id, profit_order_id, stoploss_order_id from {self.strategy_table} where status IN (' ', 'Open', 'In Progress') ;", con=self.db)

        closed_status = ['PendingCancel', 'ApiCancelled', 'Cancelled', 'Inactive']
        open_status = ['ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted']
        filled_status = ['Filled']

        for i in range (0, len(strategy_order_ids)):
            row = strategy_order_ids.iloc[i]

            parent_order_id = row['parent_order_id']
            profit_order_id = row['profit_order_id']
            stoploss_order_id = row['stoploss_order_id']

            parent_order_status = pd.read_sql_query(f"select order_status from {self.orders_table} WHERE order_id = {parent_order_id};", con=self.db)
            stoploss_order_status = pd.read_sql_query(f"select order_status from {self.orders_table} WHERE order_id = {stoploss_order_id};", con=self.db)
            profit_order_status = pd.read_sql_query(f"select order_status from {self.orders_table} WHERE order_id = {profit_order_id};", con=self.db)

            if (parent_order_status.values in filled_status) and (stoploss_order_status.values in open_status or profit_order_status.values in open_status):
                query = text(f"UPDATE {self.strategy_table} SET status = 'In Progress' WHERE parent_order_id = {parent_order_id};")

            elif (parent_order_status.values in filled_status) and (stoploss_order_status.values in filled_status or profit_order_status.values in filled_status):
                query = text(f"UPDATE {self.strategy_table} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif (parent_order_status.values in filled_status) and (stoploss_order_status.values in closed_status or profit_order_status.values in closed_status):
                query = text(f"UPDATE {self.strategy_table} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in closed_status:
                query = text(f"UPDATE {self.strategy_table} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in open_status:
                query = text(f"UPDATE {self.strategy_table} SET status = 'Open' WHERE parent_order_id = {parent_order_id};")

            else:
                query = text(f"UPDATE {self.strategy_table} SET status = ' ' WHERE parent_order_id = {parent_order_id};")

            with self.db.connect() as conn:
                conn.execute(query)
                conn.close()
                self.db.dispose()

    def is_exist_positions(self):
        ticker_pos = pd.read_sql_query(f"select cont_ticker from {self.strategy_table} where status IN ('Open', 'In Progress');", con=self.db)

        if self.ticker not in ticker_pos.values:
            return True

        else:
            return False

    def close_all_positions(self):
        # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders
        open_orders = pd.read_sql_query(f"select parent_order_id from {self.strategy_table} WHERE status IN ('Open');", con=self.db)

        for ind in open_orders.index:
            order_id = open_orders['parent_order_id'][ind]
            self.broker.cancelOrder(order_id)

        # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
        open_positions = pd.read_sql_query(
            f"select * from {self.orders_table} LEFT OUTER JOIN {self.strategy_table} ON {self.strategy_table}.profit_order_id = order_id WHERE {self.strategy_table}.status IN ('In Progress');", con=self.db)

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
                "account_no": self.order_dict["account_no"],
                "mkt_transmit": True,

                "order_id": order_id
            }

            # x = True if opt_right == "C" else False
            # price = 0 if opt_right == "C" else 99999

            pos_con = self.broker.get_contract(pos_order_dict)

            # tp_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, stock_conid, cont_exchange, x, price)
            mkt_order = self.broker.get_market_order(pos_order_dict)
            # mkt_order.conditions.append(tp_price_condition)

            self.broker.send_order(pos_order_dict, pos_con, mkt_order)

    def close_all_positions_underlying(self):
        # TODO: This function is exactly the same as above function, except few lines. Maybe we can do something in order to avoid repeating the code
        # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders
        open_orders = pd.read_sql_query(f"select parent_order_id from {self.strategy_table} WHERE status IN ('Open');", con=self.db)

        for ind in open_orders.index:
            order_id = open_orders['parent_order_id'][ind]
            self.broker.cancelOrder(order_id)

        # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
        open_positions = pd.read_sql_query(
            f"select * from {self.orders_table} LEFT OUTER JOIN {self.strategy_table} ON {self.strategy_table}.profit_order_id = order_id WHERE {self.strategy_table}.status IN ('In Progress');", con=self.db)

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
                "account_no": self.order_dict["account_no"],
                "mkt_transmit": True,

                "order_id": order_id
            }

            # TODO: Make below lines general for stocks and options (For options, take into consideration both opt_right and direction)
            x = True if opt_right == "C" else False
            price = 0 if opt_right == "C" else 99999

            pos_con = self.broker.get_contract(pos_order_dict)

            tp_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, stock_conid, cont_exchange, x, price)
            mkt_order = self.broker.get_market_order(pos_order_dict)
            mkt_order.conditions.append(tp_price_condition)

            self.broker.send_order(pos_order_dict, pos_con, mkt_order)