# from datetime import datetime
# import pandas as pd

# import config
# import os, sys
# sys.path.append(os.path.abspath('C:/Users/Owner/Desktop/Projects/big-algo'))
# #from big_algo_framework.brokers.tda import *
# from big_algo_framework.strategies.abstract_strategy import *
# from dateutil import tz
# from big_algo_framework.brokers import td



# class TDA_SQZMOM(Strategy):
#     def __init__(self, order_dict):
#         super().__init__()
#         self.is_position = False
#         self.is_order = False

#         self.order_dict = order_dict.copy()
#         self.order_dict["is_close"] = 0
#         # self.order_dict["open_action"] = ""
#         # self.order_dict["close_action"] = ""

#     def check_positions(self):
#         # TD Check Order Position Class
#         self.is_position = True
#         self.is_order = True
#         # pos = IbCheckOrderPositions(self.order_dict)
#         # self.is_position = pos.check_ib_positions()
#         # self.is_order = pos.check_ib_orders()

#     def before_send_orders(self):
#        self.order_dict["ticker"] = "TSLA_050622P875" #ticker symbol or option symbol (option format = ticker_mmddyyCstrike)
#        self.order_dict["mkt_quantity"] = 1
#        self.order_dict["mkt_action"] = "BUY"
#        self.order_dict["quantity"] = self.order_dict["mkt_quantity"]
#        self.order_dict["mkt_sec_type"] = "OPT" # "STK" or "OPT"
#        self.order_dict["mkt_instruction"] = "OPEN" # "OPEN" or "CLOSE"
#        self.order_dict["lo_quantity"] = 1
#        self.order_dict["lo_limit_price"] = 42.10
#        self.order_dict["lo_time_in_force"] = "GTC"
#        self.order_dict["lo_action"] = "BUY"
#        self.order_dict["lo_sec_type"] = "OPT" # "STK" or "OPT"
#        self.order_dict["lo_instruction"] = "OPEN" # "OPEN" or "CLOSE"
#        self.order_dict["slo_quantity"] = 1
#        self.order_dict["slo_limit_price"] = 42.20
#        self.order_dict["slo_stop_price"] = 42.30
#        self.order_dict["slo_time_in_force"] = "GTC"
#        self.order_dict["slo_action"] = "BUY"
#        self.order_dict["slo_sec_type"] = "OPT" # "STK" or "OPT"
#        self.order_dict["slo_instruction"] = "OPEN" # "OPEN" or "CLOSE"
#         # # Derive gtd time
#         # entry_time = datetime.fromtimestamp(self.order_dict["entry_time"]/1000).astimezone(tz.gettz('America/New_York'))
#         # self.order_dict["gtd"] = datetime(year=entry_time.year, month=entry_time.month, day=entry_time.day, hour=11, minute=00, second=0)

#         # # IB Action Class
#         # action = IbGetAction(self.order_dict)
#         # if self.order_dict["sec_type"] == "STK":
#         #     action.get_stocks_action()
#         # if self.order_dict["sec_type"] == "OPT":
#         #     action.get_options_action()

#         # # If we are trading options, then overwrite the entry/sl/tp parameters
#         # if self.order_dict["sec_type"] == "OPT":
#         #     self.order_dict["entry"] = self.order_dict["ask"]
#         #     self.order_dict["sl"] = self.order_dict["entry"] * 0.90
#         #     self.order_dict["tp1"] = self.order_dict["entry"] * 1.10

#         # # IB Position Sizing Class
#         # ib_pos_size = IbPositionSizing(self.order_dict)
#         # if self.order_dict["sec_type"] == "STK":
#         #     quantity = ib_pos_size.get_stocks_quantity()
#         # if self.order_dict["sec_type"] == "OPT":
#         #     quantity = ib_pos_size.get_options_quantity()
#         # self.order_dict["quantity"] = quantity

#     def check_trailing_stop(self):
#         # TODO: Code the trailing stop based on amount/percentage
#         pass

#     def start(self):
#         token_path = config.td_account["token_path"]
#         api_key = config.td_account["api_key"]
#         redirect_uri = config.td_account["redirect_uri"]
#         chromedriver_path = config.td_account["chromedriver_path"]

#         self.td = td.TDA(token_path, api_key, redirect_uri, chromedriver_path)
#         # # KEEP THIS HERE, SINCE THIS MIGHT BE DIFFERENT FOR EACH STRATEGY!!!!
#         # self.order_dict["broker"].init_client(self.order_dict["broker"], self.order_dict)
#         # self.order_dict["broker"].set_strategy_status(self.order_dict)

#         # if self.order_dict["is_close"] == 1:
#         #     print("Closing Period")
#         #     self.order_dict["broker"].close_all_positions(self.order_dict, underlying=False)

#     def send_orders(self):
#         self.order_dict["account_no"] = config.td_account["account_no"]
#         """Market Order"""
#         mkt_order = self.td.get_market_order(self.order_dict)
#         """Limtit Order"""
#         lmt_order = self.td.get_limit_order(self.order_dict)
#         """Stop_Limit Order"""
#         stlmt_order = self.td.get_stop_limit_order(self.order_dict)
#         """OCO Order"""
#         oco_order = self.td.get_oco_order(lmt_order, stlmt_order)
#         """Trigger Order"""
#         trigger_order = self.td.get_oto_order(mkt_order, oco_order) #can be used to trigger oco
#         """Replace Order"""
#         #self.td.replace_order(8151146909, lmt_order, self.order_dict)
#         """Send Order"""
#         self.td.send_order(self.order_dict, trigger_order)
#         """Cancel All Orders"""
#         #self.td.cancel_all_orders(self.order_dict)
#         """Close All Positions"""
#         #self.td.close_all_positions(self.order_dict)

#     def execute(self):
#         self.start()

#         if self.order_dict["is_close"] == 0:
#             self.check_positions()
#             if self.is_position:
#                 self.check_open_orders()
#                 if self.is_order:
#                     self.before_send_orders()

#                     if self.order_dict["quantity"] > 0:
#                         self.send_orders()
#         #print(self.order_dict)

# order_dict = {}
# strat = TDA_SQZMOM(order_dict)
# strat.execute()
