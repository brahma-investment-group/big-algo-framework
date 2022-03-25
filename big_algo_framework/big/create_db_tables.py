from big_algo_framework.big.database import *

class CreateTables():
    def __init__(self, db):
        self.db = db

    def create_dashboard(self, tables):
        for i in range(0, len(tables)):
            query1 = text("CREATE TABLE IF NOT EXISTS {}("
                          "parent_order_id BIGINT UNIQUE,"
                          "profit_order_id BIGINT,"
                          "stoploss_order_id BIGINT,"
                          "entry_price DOUBLE PRECISION,"
                          "sl_price DOUBLE PRECISION,"
                          "tp1_price DOUBLE PRECISION,"
                          "tp2_price DOUBLE PRECISION,"
                          "risk_share DOUBLE PRECISION,"
                          "cont_ticker CHARACTER VARYING,"
                          "timeframe CHARACTER VARYING,"
                          "date_time BIGINT,"
                          "sec_type CHARACTER VARYING,"
                          "cont_currency CHARACTER VARYING,"
                          "cont_exchange CHARACTER VARYING,"
                          "primary_exchange CHARACTER VARYING,"
                          "stock_conid BIGINT,"
                          "cont_date CHARACTER VARYING,"
                          "strike DOUBLE PRECISION,"
                          "opt_right CHARACTER VARYING,"
                          "multiplier BIGINT,"
                          "status CHARACTER VARYING);".format(tables[i]))

            query2 = text("CREATE INDEX IF NOT EXISTS {} ON {} (parent_order_id);".format("parent_order_id", tables[i]))

            with self.db.connect() as conn:
                conn.execute(query1)
                conn.execute(query2)
                conn.close()
                self.db.dispose()

    def create_orders(self, tables):
        for i in range(0, len(tables)):
            query1 = text("CREATE TABLE IF NOT EXISTS {}("
                          "order_id BIGINT UNIQUE,"
                          "perm_id BIGINT,"
                          "client_id BIGINT,"
                          "ticker CHARACTER VARYING,"
                          "order_type CHARACTER VARYING,"
                          "action CHARACTER VARYING,"
                          "limit_price DOUBLE PRECISION,"
                          "stop_price DOUBLE PRECISION,"
                          "quantity DOUBLE PRECISION,"
                          "parent_id BIGINT,"
                          "time_in_force CHARACTER VARYING,"
                          "good_till_date CHARACTER VARYING,"
                          "good_after_time CHARACTER VARYING,"
    
                          "order_status CHARACTER VARYING,"
                          "filled DOUBLE PRECISION,"
                          "remaining DOUBLE PRECISION,"
                          "avg_fill_price DOUBLE PRECISION,"
                          "last_fill_price DOUBLE PRECISION,"
                          "why_held CHARACTER VARYING,"
                          "mkt_cap_price DOUBLE PRECISION,"
                          
                          "exec_id CHARACTER VARYING UNIQUE,"
                          "time CHARACTER VARYING,"
                          "account_no CHARACTER VARYING,"
                          "exchange CHARACTER VARYING,"
                          "side CHARACTER VARYING,"
                          "shares DOUBLE PRECISION,"
                          "price DOUBLE PRECISION,"
                          "liquidation BIGINT,"
                          "cum_qty DOUBLE PRECISION,"
                          "avg_price DOUBLE PRECISION,"
                          
                          "commission DOUBLE PRECISION,"
                          "currency CHARACTER VARYING,"
                          "realized_pnl DOUBLE PRECISION);".format(tables[i]))

            query2 = text("CREATE INDEX IF NOT EXISTS {} ON {} (order_id);".format("order_id", tables[i]))

            with self.db.connect() as conn:
                conn.execute(query1)
                conn.execute(query2)
                conn.close()
                self.db.dispose()
