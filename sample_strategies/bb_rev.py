from big_algo_framework.strategies.abstract_strategy import *
from strategies.ib_child import *
import threading
from datetime import timedelta, datetime
from big_algo_framework.big.resample_price_indicators import resample
from big_algo_framework.big.database import createDB
from big_algo_framework.big.indicators import *
import pytz
from strategies.strategy_functions import *

class TestStrategy1(Strategy):
    def __init__(self, broker, ticker, db, historic_data_table, streaming_data_table, order_dict):
        super().__init__()

        self.is_position = False
        self.is_order = False

        self.check_long = False
        self.check_short = False

        self.trade_long = False
        self.trade_short = False

        self.send_trade = False

        self.broker = broker
        self.indi = BIGIndicators()
        self.db = db
        self.ticker = ticker
        self.historic_data_table = historic_data_table
        self.streaming_data_table = streaming_data_table
        self.order_dict = order_dict
        self.order_dict1 = order_dict

        self.function = StrategyFunctions(self.db, self.ticker, self.broker)


        self.tf_props = {
            "1 min": {'base_timeframe': '1 min', 'rule': '1min', 'is_origin': True},
            "3 mins": {'base_timeframe': '1 min', 'rule': '3min', 'is_origin': True},
            "10 mins": {'base_timeframe': '1 min', 'rule': '10min', 'is_origin': True},
            "15 mins": {'base_timeframe': '1 min', 'rule': '15min', 'is_origin': True},
            "20 mins": {'base_timeframe': '1 min', 'rule': '20min', 'is_origin': True},
            "30 mins": {'base_timeframe': '30 mins', 'rule': '30min', 'is_origin': True},
            "90 mins": {'base_timeframe': '30 mins', 'rule': '90min', 'is_origin': True},
            "1 hour": {'base_timeframe': '30 mins', 'rule': '1H', 'is_origin': True},
            "2 hours": {'base_timeframe': '30 mins', 'rule': '2H', 'is_origin': True},
            "4 hours": {'base_timeframe': '30 mins', 'rule': '4H', 'is_origin': True},
            "1 day": {'base_timeframe': '1 day', 'rule': '24H', 'is_origin': False},
            "2 days": {'base_timeframe': '1 day', 'rule': '2B', 'is_origin': True},
            "3 days": {'base_timeframe': '1 day', 'rule': '72H', 'is_origin': True},
            "1 week": {'base_timeframe': '1 day', 'rule': 'W', 'is_origin': True},
            "1 month": {'base_timeframe': '1 day', 'rule': 'MS', 'is_origin': True},
            "1 quarter": {'base_timeframe': '1 day', 'rule': 'QS', 'is_origin': True},
            "1 year": {'base_timeframe': '1 day', 'rule': 'AS-JAN', 'is_origin': True},
        }

        self.entry_conditions = [
            {
                "lowerSampleTimeFrame": "1 hour",
                "FTFC": ["1 day", "1 week", "1 month"],
                "timeDelta": [0, 1, 0, 0],  # Minutes, hours, days, weeks
            }
        ]

    def check_positions(self):
        if self.function.is_exist_positions():
            self.is_position = True

    def check_open_orders(self):
        self.is_order = True

    def check_high_level_market_conditons(self):
        self.check_long = True
        self.check_short = True

    def check_conditions(self, direction):
        trade_permission = False

        for i in range(len(self.entry_conditions)):
            ltf_tf = self.entry_conditions[i]["lowerSampleTimeFrame"]
            ltf_resample = resample(self.db,
                                    [self.ticker],
                                    self.tf_props[ltf_tf]["base_timeframe"],
                                    ltf_tf,
                                    self.tf_props[ltf_tf]["rule"],
                                    self.historic_data_table,
                                    self.streaming_data_table,
                                    self.tf_props[self.tf_props[ltf_tf]["base_timeframe"]]["rule"],
                                    self.tf_props[ltf_tf]["is_origin"])
            ltf_df = ltf_resample.resample_price()

            if len(ltf_df) >= 21:
                # Get Bollinger Bands
                bb_df = ltf_df.ta.bbands(length=20, std=2, mamode="sma")

                bb_df = bb_df.rename(columns={"BBL_20_2.0": "LBB",
                                      "BBM_20_2.0": "MBB",
                                      "BBU_20_2.0": "UBB",
                                      "BBB_20_2.0": "BBW",
                                      "BBP_20_2.0": "BBP"})

                if direction == "Bullish":
                    if ltf_df["low"].iloc[-2] < bb_df["LBB"].iloc[-2]:
                        entry = ltf_df["high"].iloc[-2]
                        sl = ltf_df["low"].iloc[-2]
                        risk = abs(entry - sl)
                        tp1 = entry + (1 * risk)
                        tp2 = entry + (3 * risk)
                        open_action = "BUY"
                        close_action = "SELL"

                        trade_permission = True

                if direction == "Bearish":
                    if ltf_df["high"].iloc[-2] > bb_df["UBB"].iloc[-2]:
                        entry = ltf_df["low"].iloc[-2]
                        sl = ltf_df["high"].iloc[-2]
                        risk = abs(entry - sl)
                        tp1 = entry - (1 * risk)
                        tp2 = entry - (3 * risk)
                        open_action = "SELL"
                        close_action = "BUY"

                        trade_permission = True

                if trade_permission == True:
                    dt_1 = ltf_df["date_time"].iloc[-1]
                    tz = pytz.timezone('UTC')
                    dt_2 = tz.localize(dt_1, is_dst=None)
                    print(dt_1)
                    print(dt_2)
                    eastern = pytz.timezone("US/Eastern")
                    dt_3 = dt_2.astimezone(eastern)
                    print(dt_3)

                    gtd = dt_3 + timedelta(minutes=float(self.entry_conditions[i]["timeDelta"][0]),
                                           hours=float(self.entry_conditions[i]["timeDelta"][1]),
                                           days=float(self.entry_conditions[i]["timeDelta"][2]),
                                           weeks=float(self.entry_conditions[i]["timeDelta"][3]))

                    self.order_dict = {"slo_action": open_action,
                                       "slo_quantity": 10,
                                       "slo_limit_price": entry,
                                       "slo_stop_price": entry,
                                       "slo_time_in_force": "GTD",
                                       "slo_good_till_date": gtd.strftime('%Y%m%d %H:%M:%S'),
                                       "slo_parent_order_id": "",
                                       "slo_transmit": False,

                                       "lo_action": close_action,
                                       "lo_quantity": 10,
                                       "lo_limit_price": tp1,
                                       "lo_time_in_force": "GTC",
                                       "lo_good_till_date": "",
                                       "lo_transmit": False,

                                       "so_action": close_action,
                                       "so_quantity": 10,
                                       "so_stop_price": sl,
                                       "so_time_in_force": "GTC",
                                       "so_good_till_date": "",
                                       "so_transmit": True,
                                  }

                    self.order_dict1 = {"slo_action": open_action,
                                       "slo_quantity": 10,
                                       "slo_limit_price": entry,
                                       "slo_stop_price": entry,
                                       "slo_time_in_force": "GTD",
                                       "slo_good_till_date": gtd.strftime('%Y%m%d %H:%M:%S'),
                                       "slo_parent_order_id": "",
                                       "slo_transmit": False,

                                       "lo_action": close_action,
                                       "lo_quantity": 10,
                                       "lo_limit_price": tp2,
                                       "lo_time_in_force": "GTC",
                                       "lo_good_till_date": "",
                                       "lo_transmit": False,

                                       "so_action": close_action,
                                       "so_quantity": 10,
                                       "so_stop_price": sl,
                                       "so_time_in_force": "GTC",
                                       "so_good_till_date": "",
                                       "so_transmit": True,
                                       }

                    if direction == "Bullish":
                        self.trade_long = True

                    elif direction == "Bearish":
                        self.trade_short = True

    def check_long_conditions(self):
        self.check_conditions("Bullish")

    def check_short_conditions(self):
        self.check_conditions("Bearish")

    def start(self):
        self.broker.initialize(self.broker, self.order_dict)
        self.broker.get_contract()

    def send_orders(self):
        self.function.send_entry_sl_tp_order(self.order_dict)
        self.function.send_entry_sl_tp_order(self.order_dict1)

    def execute(self):
        self.start()

        self.check_positions()
        if self.is_position:
            self.check_open_orders()
            if self.is_order:
                self.check_high_level_market_conditons()

                if self.check_long:
                    self.check_long_conditions()
                    if self.trade_long:
                        self.send_trade = True

                if self.check_short:
                    self.check_short_conditions()
                    if self.trade_short:
                        self.send_trade = True

                if self.send_trade:
                    self.send_orders()

###############################################################################################################

historic_data_table = "us_equity_historic_data"
streaming_data_table = "us_equity_streaming_data"
db = createDB("market_data", "data/config.ini")
time.sleep(2)

tickers = ['A', 'ABM', 'AAON', 'AAP', 'AAU', 'AAWW', 'AAXJ']
broker = IbChild(db)

broker.connect('127.0.0.1', 7497, 2)
time.sleep(3)
broker.reqPositions()
time.sleep(3)
broker.reqOpenOrders()
time.sleep(3)

def websocket_con():
    broker.run()

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(3)

for ticker in tickers:
    order_dict = dict()
    order_dict = {"ticker": ticker,
                  "sec_type": "STK",
                  "currency": "USD",
                  "exchange": "SMART",
                  "primary_exchange": "SMART"}

    print(ticker)
    x = TestStrategy1(broker, ticker, db, historic_data_table, streaming_data_table, order_dict)
    x.execute()
