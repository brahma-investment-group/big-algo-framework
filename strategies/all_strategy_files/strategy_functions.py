from sqlalchemy import inspect, text
import pandas as pd
import time

class StrategyFunctions():
    def __init__(self, db, ticker, broker):
        self.db = db
        self.ticker = ticker
        self.broker = broker

    def get_child_order_id(self, parent_id):
        child_order_id = pd.read_sql_query(
            f"select order_id from orders where parent_id = {parent_id};",
            con=self.db)
        return child_order_id.values

    def set_strategy_status(self):
        #If its present, then set status to as per following
            #parent_order absent, child_order absent --> Open (DEFAULT WHEN INSERTING ROW)
            #parent_order present, child_order absent --> In Progress
            #parent_order present, child_order present --> Closed

        exec_order_ids = pd.read_sql_query("select order_id from orders;", con=self.db)
        strategy_order_ids = pd.read_sql_query("select parent_order_id, profit_order_id, stoploss_order_id from bb_rev where status IN ('Open', 'In Progress') ;", con=self.db)


        closed_status = ['PendingCancel', 'ApiCancelled', 'Cancelled', 'Inactive']
        open_status = ['ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted']
        filled_status = ['Filled']

        for i in range (0, len(strategy_order_ids)):
            query = ""
            row = strategy_order_ids.iloc[i]

            parent_order_id = row['parent_order_id']
            profit_order_id = row['profit_order_id']
            stoploss_order_id = row['stoploss_order_id']

            parent_order_status = pd.read_sql_query(f"select order_status from orders WHERE order_id = {parent_order_id};", con=self.db)
            stoploss_order_status = pd.read_sql_query(f"select order_status from orders WHERE order_id = {stoploss_order_id};", con=self.db)
            profit_order_status = pd.read_sql_query(f"select order_status from orders WHERE order_id = {profit_order_id};", con=self.db)

            if (parent_order_status.values in filled_status) and (stoploss_order_status.values in open_status or profit_order_status.values in open_status):
                query = text(f"UPDATE bb_rev SET status = 'In Progress' WHERE parent_order_id = {parent_order_id};")

            elif (parent_order_status.values in filled_status) and (stoploss_order_status.values in filled_status or profit_order_status.values in filled_status):
                query = text(f"UPDATE bb_rev SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in closed_status:
                query = text(f"UPDATE bb_rev SET status = 'Closed' WHERE parent_order_id = {parent_order_id};")

            elif parent_order_status.values in open_status:
                query = text(f"UPDATE bb_rev SET status = 'Open' WHERE parent_order_id = {parent_order_id};")

            else:
                query = text(f"UPDATE bb_rev SET status = ' ' WHERE parent_order_id = {parent_order_id};")
                # if (parent_order_id not in exec_order_ids.values) and (profit_order_id not in exec_order_ids.values and stoploss_order_id not in exec_order_ids.values):
                #     query = text("UPDATE bb_rev SET status = 'Open' WHERE parent_order_id = {};".format("parent_order_id"))
                #
                # elif (parent_order_id in exec_order_ids.values) and (profit_order_id not in exec_order_ids.values and stoploss_order_id not in exec_order_ids.values):
                #     query = text("UPDATE bb_rev SET status = 'In Progress' WHERE parent_order_id = {};".format("parent_order_id"))
                #
                # elif (parent_order_id in exec_order_ids.values) and (profit_order_id in exec_order_ids.values or stoploss_order_id in exec_order_ids.values):
                #     query = text("UPDATE bb_rev SET status = 'Closed' WHERE parent_order_id = {};".format("parent_order_id"))

            with self.db.connect() as conn:
                # print(query)
                conn.execute(query)
                conn.close()
                self.db.dispose()

    def is_exist_positions(self):
        ticker_pos = pd.DataFrame()
        ticker_pos = pd.read_sql_query(
            "select ticker from bb_rev where status IN ('Open', 'In Progress') AND stoploss_order_id IN (select order_id from orders where order_type='STP' and remaining > 0);",
            con=self.db)

        if self.ticker not in ticker_pos.values:
            return True

        else:
            return False

    #NOT USING ANYMORE... SENDING INDIVIDUAL ORDERS
    # def send_entry_sl_tp_order(self, order_dict):
    #     self.broker.reqIds(1)
    #     time.sleep(1)
    #
    #     parent_order_id = self.broker.orderId
    #     order_dict["slo_order_id"] = parent_order_id
    #     order_dict["lo_order_id"] = parent_order_id + 1
    #     order_dict["lo_parent_order_id"] = parent_order_id
    #     order_dict["so_order_id"] = parent_order_id + 2
    #     order_dict["so_parent_order_id"] = parent_order_id
    #
    #     parent_order = self.broker.get_stop_limit_order(order_dict)
    #     profit_order = self.broker.get_limit_order(order_dict)
    #     stoploss_order = self.broker.get_stop_order(order_dict)
    #
    #     self.broker.send_bracket_order(parent_order, profit_order, stoploss_order)
    #     return order_dict

    # NOT USING ANYMORE... SENDING INDIVIDUAL ORDERS
    # def send_entry_sl_order(self, order_dict):
    #     self.broker.reqIds(1)
    #     time.sleep(1)
    #
    #     parent_order_id = self.broker.orderId
    #     order_dict["slo_order_id"] = parent_order_id
    #     order_dict["so_order_id"] = parent_order_id + 1
    #     order_dict["so_parent_order_id"] = parent_order_id
    #
    #     parent_order = self.broker.get_stop_limit_order(order_dict)
    #     stoploss_order = self.broker.get_stop_order(order_dict)
    #
    #     self.broker.send_bracket_order(parent_order, stoploss_order)
    #     return order_dict

