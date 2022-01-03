from sqlalchemy import inspect, text
import pandas as pd
import time
from ibapi.order_condition import PriceCondition
from random import randint


class StrategyFunctions():
    def __init__(self, db, ticker, broker, strategy):
        self.db = db
        self.ticker = ticker
        self.broker = broker
        self.strategy = strategy

    # def get_child_order_id(self, parent_id):
    #     child_order_id = pd.read_sql_query(
    #         f"select order_id from orders where parent_id = {parent_id};",
    #         con=self.db)
    #     return child_order_id.values

    def set_strategy_status(self):
        #If its present, then set status to as per following
            #parent_order absent, child_order absent --> Open (DEFAULT WHEN INSERTING ROW)
            #parent_order present, child_order absent --> In Progress
            #parent_order present, child_order present --> Closed

        strategy_order_ids = pd.read_sql_query(f"select parent_order_id, profit_order_id, stoploss_order_id from {self.strategy} where status IN (' ', 'Open', 'In Progress') ;", con=self.db)

        closed_status = ['PendingCancel', 'ApiCancelled', 'Cancelled', 'Inactive']
        open_status = ['ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted']
        filled_status = ['Filled']

        for i in range (0, len(strategy_order_ids)):
            row = strategy_order_ids.iloc[i]

            parent_order_id = row['parent_order_id']
            profit_order_id = row['profit_order_id']
            stoploss_order_id = row['stoploss_order_id']

            parent_order_status = pd.read_sql_query(f"select order_status from orders WHERE order_id = {parent_order_id};", con=self.db)
            stoploss_order_status = pd.read_sql_query(f"select order_status from orders WHERE order_id = {stoploss_order_id};", con=self.db)
            profit_order_status = pd.read_sql_query(f"select order_status from orders WHERE order_id = {profit_order_id};", con=self.db)

            if (parent_order_status.values in filled_status) and (stoploss_order_status.values in open_status or profit_order_status.values in open_status):
                query = text(f"UPDATE {self.strategy} SET status = 'In Progress' WHERE parent_order_id = {parent_order_id};")

            elif (parent_order_status.values in filled_status) and (stoploss_order_status.values in filled_status or profit_order_status.values in filled_status):
                query = text(f"UPDATE {self.strategy} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif (parent_order_status.values in filled_status) and (stoploss_order_status.values in closed_status or profit_order_status.values in closed_status):
                query = text(f"UPDATE {self.strategy} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in closed_status:
                query = text(f"UPDATE {self.strategy} SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in open_status:
                query = text(f"UPDATE {self.strategy} SET status = 'Open' WHERE parent_order_id = {parent_order_id};")

            else:
                query = text(f"UPDATE {self.strategy} SET status = ' ' WHERE parent_order_id = {parent_order_id};")

            with self.db.connect() as conn:
                conn.execute(query)
                conn.close()
                self.db.dispose()

    def is_exist_positions(self):
        ticker_pos = pd.read_sql_query(f"select cont_ticker from {self.strategy} where status IN ('Open', 'In Progress');", con=self.db)

        if self.ticker not in ticker_pos.values:
            return True

        else:
            return False

    def closeAllPositions(self):
        # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders
        open_orders = pd.read_sql_query(f"select parent_order_id from {self.strategy} WHERE status IN ('Open');", con=self.db)

        for ind in open_orders.index:
            order_id = open_orders['parent_order_id'][ind]
            self.broker.cancelOrder(order_id)

        # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
        open_positions = pd.read_sql_query(
            f"select * from orders LEFT OUTER JOIN orb ON {self.strategy}.profit_order_id = order_id WHERE {self.strategy}.status IN ('In Progress');", con=self.db)

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
                "mkt_transmit": True,

                "order_id": order_id
            }

            x = True if opt_right == "C" else False

            pos_con = self.broker.get_contract(pos_order_dict)

            tp_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, stock_conid, cont_exchange, x, "")
            mkt_order = self.broker.get_market_order(pos_order_dict)
            mkt_order.conditions.append(tp_price_condition)

            self.broker.send_order(pos_order_dict, pos_con, mkt_order)
