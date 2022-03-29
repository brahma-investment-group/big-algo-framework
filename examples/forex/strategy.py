from big_algo_framework.brokers.mt5 import MT
from examples.forex import config
from big_algo_framework.big.position_sizing import PositionSizing
from big_algo_framework.strategies.abstract_strategy import *
from datetime import timedelta, timezone, datetime

deviation = 2
magic = 21051987

class OrbForex(Strategy):
    def __init__(self, order_dict):
        super().__init__()
        self.is_position = False
        self.is_order = False

        self.order_dict = order_dict.copy()
        self.order_dict1 = order_dict.copy()

        # self.db = self.order_dict["db"]
        # self.time_frame = self.order_dict["time_frame"]
        # self.tp2 = self.order_dict["tp2"]
        # self.orders_table = self.order_dict["orders_table"]
        # self.strategy_table = self.order_dict["strategy_table"]

        self.ticker = "EURUSD"
        self.broker = MT()
        # self.entry_time = self.order_dict["entry_time"]
        self.entry = 1.05
        self.sl = 0.99
        self.tp1 = 2.00
        self.risk = 0.06
        self.direction = "Bullish"
        self.open_action = "BUY"
        self.close_action = "SELL"
        self.is_close = 0

        # self.ticker = self.order_dict["ticker"]
        # self.broker = self.order_dict["broker"]
        # self.entry_time = self.order_dict["entry_time"]
        # self.entry = self.order_dict["entry"]
        # self.sl = self.order_dict["sl"]
        # self.tp1 = self.order_dict["tp1"]
        # self.risk = self.order_dict["risk"]
        # self.direction = self.order_dict["direction"]
        # self.open_action = self.order_dict["open_action"]
        # self.close_action = self.order_dict["close_action"]
        # self.is_close = self.order_dict["is_close"]



    def check_positions(self):
        if not self.broker.is_exist_positions():
            self.is_position = True

    def check_open_orders(self):
        if not self.broker.is_exist_orders():
            self.is_order = True

    def before_send_orders(self):
        # Derive gtd time
        # entry_time = datetime.datetime.fromtimestamp(self.entry_time/1000).astimezone(tz.gettz('America/New_York'))
        # self.gtd = datetime.datetime(year=entry_time.year, month=entry_time.month, day=entry_time.day, hour=11, minute=00, second=0)


        # Adjust the entry/sl/tp to take into account the mintick
        # self.entry = self.entry - (self.entry % self.broker.mintick)
        # self.tp1 = self.tp1 - (self.tp1 % self.broker.mintick)
        # self.tp2 = self.tp2 - (self.tp2 % self.broker.mintick)
        # self.sl = self.sl - (self.sl % self.broker.mintick)

        # Position Sizing
        # self.order_dict["available_capital"] = float(self.broker.acc_dict["AvailableFunds"])
        # position = PositionSizing()
        # self.order_dict["risk_share"] = abs(self.entry-self.sl)
        # quantity = position.stock_quantity(self.order_dict)
        self.quantity1 = 0.1



        self.order_dict["magic"] = magic
        self.order_dict["order_id"] = 0
        self.order_dict["ticker"] = self.ticker
        self.order_dict["lo_quantity"] = self.quantity1
        self.order_dict["lo_price"] = self.entry
        self.order_dict["lo_sl"] = self.sl
        self.order_dict["lo_tp"] = self.tp1
        self.order_dict["deviation"] = deviation
        self.order_dict["lo_type"] = mt5.ORDER_TYPE_BUY_LIMIT
        self.order_dict["lo_time_in_force"] = mt5.ORDER_TIME_SPECIFIED_DAY
        self.order_dict["expiration"] = 10000
        self.order_dict["comment"] = ""
        self.order_dict["position_id"] = 0
        self.order_dict["position_by"] = 0

    def check_trailing_stop(self):
        pass

    def start(self):
        self.broker.init_client(config.mt_account["account"], config.mt_account["server"], config.mt_account["password"])

        if self.is_close == 1:
            print("Closing Period")
            self.broker.closeAllPositions()

    def send_orders(self):
        order = self.broker.get_limit_order(self.order_dict)
        res = self.broker.send_order(order)


    def after_send_orders(self):
        pass

    def execute(self):
        self.start()

        if self.is_close == 0:
            self.check_positions()
            if self.is_position:
                self.check_open_orders()
                if self.is_order:
                    self.before_send_orders()

                    if self.quantity1 > 0:
                        self.send_orders()
                        self.after_send_orders()
