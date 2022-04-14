from datetime import datetime
from dateutil import tz
import pandas as pd

from examples.all_strategy_files.ib.ib_check_order_positions import IbCheckOrderPositions
from examples.all_strategy_files.ib.ib_position_sizing import IbPositionSizing
from examples.all_strategy_files.ib.ib_send_orders import IbSendOrders
from examples.all_strategy_files.ib.ib_get_action import IbGetAction
from big_algo_framework.strategies.abstract_strategy import *

class IBORB(Strategy):
    def __init__(self, order_dict):
        super().__init__()
        self.is_position = False
        self.is_order = False

        self.order_dict = order_dict.copy()
        self.order_dict1 = order_dict.copy()
        self.dashboard_dict = {}
        self.dashboard_dict[1] = {}
        self.dashboard_dict[2] = {}
        self.order_dict["open_action"] = ""
        self.order_dict["close_action"] = ""
        self.order_dict["con"] = ()

    def check_positions(self):
        # IB Check Order Position Class
        pos = IbCheckOrderPositions(self.order_dict)
        self.is_position = pos.check_ib_positions()
        self.is_order = pos.check_ib_orders()

    def before_send_orders(self):
        # Derive gtd time
        entry_time = datetime.fromtimestamp(self.order_dict["entry_time"]/1000).astimezone(tz.gettz('America/New_York'))
        self.order_dict["gtd"] = datetime(year=entry_time.year, month=entry_time.month, day=entry_time.day, hour=11, minute=00, second=0)

        # IB Action Class
        action = IbGetAction(self.order_dict)
        if self.order_dict["sec_type"] == "STK":
            action.get_stocks_action()
        if self.order_dict["sec_type"] == "OPT":
            action.get_options_action()

        # If we are trading options, then overwrite the entry/sl/tp parameters taking into consideration whether we are buying/selling options
        if self.order_dict["sec_type"] == "OPT":
            self.order_dict["entry"] = self.order_dict["ask"]
            if self.order_dict["option_action"] == "BUY":
                self.order_dict["sl"] = self.order_dict["entry"] * 0.90
                self.order_dict["tp1"] = self.order_dict["entry"] * 1.20
            if self.order_dict["option_action"] == "SELL":
                self.order_dict["tp1"] = self.order_dict["entry"] * 0.90
                self.order_dict["sl"] = self.order_dict["entry"] * 1.20

        # IB Position Sizing Class
        ib_pos_size = IbPositionSizing(self.order_dict)
        if self.order_dict["sec_type"] == "STK":
            quantity = ib_pos_size.get_stocks_quantity()
        if self.order_dict["sec_type"] == "OPT":
            quantity = ib_pos_size.get_options_quantity()
        self.order_dict["quantity"] = quantity

    def check_trailing_stop(self):
        # TODO: Code the trailing stop based on amount/percentage
        pass

    def start(self):
        # KEEP THIS HERE, SINCE THIS MIGHT BE DIFFERENT FOR EACH STRATEGY!!!!
        self.order_dict["broker"].init_client(self.order_dict["broker"], self.order_dict)
        self.order_dict["broker"].set_strategy_status(self.order_dict)

        if self.order_dict["is_close"] == 1:
            print("Closing Period")
            self.order_dict["broker"].close_all_positions(self.order_dict, underlying=False)

    def send_orders(self):
        # IB Send Orders Class
        send_order = IbSendOrders(self.order_dict, self.dashboard_dict[1])
        send_order.send_lmt_stp_order()

    def after_send_orders(self):
        data_list = []
        for x in range(1, 2):
            data = dict(parent_order_id=self.dashboard_dict[x]["parent_order_id"],
                        profit_order_id=self.dashboard_dict[x]["profit_order_id"],
                        stoploss_order_id=self.dashboard_dict[x]["stoploss_order_id"],
                        entry_price=self.order_dict["entry"],
                        sl_price=self.order_dict["sl"],
                        tp1_price=self.order_dict["tp1"],
                        tp2_price=self.order_dict["tp2"],
                        risk_share=self.order_dict["risk"],
                        cont_ticker=self.order_dict["ticker"],
                        direction=self.order_dict["direction"],

                        timeframe=self.order_dict["time_frame"],
                        date_time=self.order_dict["entry_time"]/1000,

                        sec_type=self.order_dict["sec_type"],
                        cont_currency=self.order_dict["currency"],
                        cont_exchange=self.order_dict["exchange"],
                        primary_exchange=self.order_dict["primary_exchange"],
                        stock_conid=self.order_dict["broker"].conid,
                        cont_date=self.order_dict["lastTradeDateOrContractMonth"],
                        strike=self.order_dict["strike"],
                        opt_right=self.order_dict["right"],
                        opt_action=self.order_dict["option_action"],
                        multiplier=self.order_dict["multiplier"],
                        status='Open')

            data_list.append(data)

        if data_list:
            df = pd.DataFrame(data=data_list)
            df.to_sql(self.order_dict["strategy_table"], self.order_dict["db"], if_exists='append', index=False, method='multi')

    def execute(self):
        self.start()

        if self.order_dict["is_close"] == 0:
            self.check_positions()
            if self.is_position:
                self.check_open_orders()
                if self.is_order:
                    self.before_send_orders()

                    if self.order_dict["quantity"] > 0:
                        self.send_orders()
                        self.after_send_orders()
