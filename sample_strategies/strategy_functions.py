from sqlalchemy import inspect, text
import pandas as pd
import time


class StrategyFunctions():
    def __init__(self, db, ticker, broker):
        self.db = db
        self.ticker = ticker
        self.broker = broker

    def is_exist_positions(self):
        ticker_pos = pd.DataFrame()
        insp = inspect(self.db)
        table_exist = insp.has_table("orders", 'public')

        # Get the order_id from orders table corresponsing to "STP" and "PreSubmitted/Submitted" conditions
        # Check if the order_id exists in the bb_rev dashboard table and get the corresponding tickers
        if table_exist:
            ticker_pos = pd.read_sql_query(
                "select ticker from strat where stoploss_order_id_1 IN (select order_id from orders where order_type='STP' and order_status IN ('PreSubmitted', 'Submitted')) OR "
                "stoploss_order_id_2 IN (select order_id from orders where order_type='STP' and order_status IN ('PreSubmitted', 'Submitted'));",
                con=self.db)

        if self.ticker not in ticker_pos.values:
            return True

        else:
            return False

    def send_entry_sl_tp_order(self, order_dict):
        self.broker.reqIds(1)
        time.sleep(1)

        parent_order_id = self.broker.orderId
        order_dict["slo_order_id"] = parent_order_id
        order_dict["lo_order_id"] = parent_order_id + 1
        order_dict["lo_parent_order_id"] = parent_order_id
        order_dict["so_order_id"] = parent_order_id + 2
        order_dict["so_parent_order_id"] = parent_order_id

        parent_order = self.broker.get_stop_limit_order(order_dict)
        profit_order = self.broker.get_limit_order(order_dict)
        stoploss_order = self.broker.get_stop_order(order_dict)

        self.broker.send_bracket_order(parent_order, profit_order, stoploss_order)

        return order_dict