from big_algo_framework.strategies.abstract_strategy import *
from strategies.all_strategy_files.child_classes.brokers_ib_child import *
import threading
from datetime import timedelta, datetime
from big_algo_framework.big.resample_price_indicators import resample
from strategies.all_strategy_files.database.database import createDB
from big_algo_framework.big.indicators import *
import pytz
from strategies.all_strategy_files.strategy_functions import *
import math
from big_algo_framework.big.calendar_us import *
from ibapi.account_summary_tags import AccountSummaryTags
from tickers import *
from big_algo_framework.big.position_sizing import PositionSizing

class BbRev(Strategy):
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

        self.dashboard_dict = {}
        self.dashboard_dict[1] = {}
        self.dashboard_dict[2] = {}
        self.con = ()

        self.no_bb = 21
        self.min_candles_ltf = max(1, self.no_bb)


        self.function = StrategyFunctions(self.db, self.ticker, self.broker)

        self.tf_props = {
            "1 min": {'base_timeframe': '1 min', 'rule': '1min', 'is_origin': True},
            "3 mins": {'base_timeframe': '1 min', 'rule': '3min', 'is_origin': True},
            "5 mins": {'base_timeframe': '1 min', 'rule': '5min', 'is_origin': True},
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

        self.entry_conditions = {
            0: {
                "lowerSampleTimeFrame": "5 mins",
                "FTFC": ["15 mins", "1 hour"],
                "timeDelta": [5, 0, 0, 0],  # Minutes, hours, days, weeks
            },

            1: {
                "lowerSampleTimeFrame": "15 mins",
                "FTFC": ["1 hour", "4 hours"],
                "timeDelta": [15, 0, 0, 0],  # Minutes, hours, days, weeks
            },

            2: {
                "lowerSampleTimeFrame": "30 mins",
                "FTFC": ["2 hours", "1 day"],
                "timeDelta": [30, 0, 0, 0],  # Minutes, hours, days, weeks
            },

            3: {
                "lowerSampleTimeFrame": "1 hour",
                "FTFC": ["4 hours", "2 days"],
                "timeDelta": [0, 1, 0, 0],  # Minutes, hours, days, weeks
            },

            4: {
                "lowerSampleTimeFrame": "1 day",
                "FTFC": ["1 week", "1 month"],
                "timeDelta": [0, 0, 1, 0],  # Minutes, hours, days, weeks
            },

        }

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

            if len(ltf_df) >= self.min_candles_ltf:
                # Get Bollinger Bands
                bb_df = ltf_df.ta.bbands(length=20, std=2, mamode="sma")

                bb_df = bb_df.rename(columns={"BBL_20_2.0": "LBB",
                                      "BBM_20_2.0": "MBB",
                                      "BBU_20_2.0": "UBB",
                                      "BBB_20_2.0": "BBW",
                                      "BBP_20_2.0": "BBP"})

                if direction == "Bullish":
                    bullish_creteria = [ltf_df["low"].iloc[-2] < bb_df["LBB"].iloc[-2]]

                if direction == "Bearish":
                    bearish_creteria = [ltf_df["high"].iloc[-2] > bb_df["UBB"].iloc[-2]]

                if direction == "Bullish":
                    if all(bullish_creteria):
                        entry = ltf_df["high"].iloc[-2]
                        sl = ltf_df["low"].iloc[-2]
                        risk = abs(entry - sl)
                        tp1 = entry + (1 * risk)
                        tp2 = entry + (3 * risk)
                        open_action = "BUY"
                        close_action = "SELL"

                        trade_permission = True

                if direction == "Bearish":
                    if all(bearish_creteria):
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

                    self.broker.reqContractDetails(12, self.con)
                    time.sleep(1)

                    entry = entry - (entry % self.broker.mintick)
                    tp1 = tp1 - (tp1 % self.broker.mintick)
                    tp2 = tp2 - (tp2 % self.broker.mintick)
                    sl = sl - (sl % self.broker.mintick)

                    self.order_dict["available_capital"] = float(self.broker.acc_dict["AvailableFunds"]) #Need to convert to floar
                    self.order_dict["total_risk"] = 2                       #Later, put as input
                    self.order_dict["total_risk_units"] = "percent"         #Later, put as input
                    self.order_dict["risk_share"] = risk

                    position = PositionSizing()
                    quantity = position.stock_quantity(self.order_dict)
                    quantity1 = quantity - int(quantity/2)
                    quantity2 = int(quantity/2)

                    if entry > 1:
                        self.order_dict["slo_action"] = open_action
                        self.order_dict["slo_quantity"] = quantity1
                        self.order_dict["slo_limit_price"] = entry
                        self.order_dict["slo_stop_price"] = entry
                        self.order_dict["slo_time_in_force"] = "GTD"
                        self.order_dict["slo_good_till_date"] = gtd.strftime('%Y%m%d %H:%M:%S')
                        self.order_dict["slo_parent_order_id"] = ""
                        self.order_dict["slo_transmit"] = True

                        self.order_dict["lo_action"] = close_action
                        self.order_dict["lo_quantity"] = quantity1
                        self.order_dict["lo_limit_price"] = tp1
                        self.order_dict["lo_time_in_force"] = "GTC"
                        self.order_dict["lo_good_till_date"] = ""
                        self.order_dict["lo_transmit"] = True

                        self.order_dict["so_action"] = close_action
                        self.order_dict["so_quantity"] = quantity1
                        self.order_dict["so_stop_price"] = sl
                        self.order_dict["so_time_in_force"] = "GTC"
                        self.order_dict["so_good_till_date"] = ""
                        self.order_dict["so_transmit"] = True

                        #ORDER DICT 1....
                        self.order_dict1["slo_action"] = open_action
                        self.order_dict1["slo_quantity"] = quantity2
                        self.order_dict1["slo_limit_price"] = entry
                        self.order_dict1["slo_stop_price"] = entry
                        self.order_dict1["slo_time_in_force"] = "GTD"
                        self.order_dict1["slo_good_till_date"] = gtd.strftime('%Y%m%d %H:%M:%S')
                        self.order_dict1["slo_parent_order_id"] = ""
                        self.order_dict1["slo_transmit"] = True

                        self.order_dict1["so_action"] = close_action
                        self.order_dict1["so_quantity"] = quantity2
                        self.order_dict1["so_stop_price"] = sl
                        self.order_dict1["so_time_in_force"] = "GTC"
                        self.order_dict1["so_good_till_date"] = ""
                        self.order_dict1["so_transmit"] = True

                        if direction == "Bullish":
                            self.trade_long = True

                        elif direction == "Bearish":
                            self.trade_short = True

                        now = datetime.datetime.now()
                        self.dashboard_dict[1]["ticker"] = self.ticker
                        self.dashboard_dict[1]["timeframe"] = ltf_tf
                        self.dashboard_dict[1]["date_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
                        self.dashboard_dict[1]["risk_share"] = risk
                        self.dashboard_dict[1]["entry"] = entry

            if trade_permission == True:
                break   #Using break so that it doesnt loop through the remaining time frames, after sending order on a time frame

    def check_long_conditions(self):
        self.check_conditions("Bullish")

    def check_short_conditions(self):
        self.check_conditions("Bearish")

    def check_trailing_stop(self):
        order_results_df = pd.read_sql_query(
            "SELECT * FROM orders JOIN bb_rev ON ((orders.order_id = bb_rev.stoploss_order_id) AND bb_rev.status = 'In Progress');", con=self.db)

        order_results_dict = order_results_df.to_dict("records")

        for dic in order_results_dict:
            order_id = dic["order_id"]
            ticker = dic["ticker"]
            current_sl = dic['stop_price']
            action = dic['action']
            order_tf = dic['timeframe']
            entryPrice = dic['entry_price']
            riskPerShare = dic['risk_share']
            quantity = dic['remaining']
            parent_id = dic['parent_id']

            direction = ""
            if action == "SELL":
                direction = "Bullish"
            elif action == "BUY":
                direction = "Bearish"

            order_resample = resample(self.db, [ticker], self.tf_props[order_tf]["base_timeframe"], order_tf, self.tf_props[order_tf]["rule"], self.historic_data_table, self.streaming_data_table, self.tf_props[self.tf_props[order_tf]["base_timeframe"]]["rule"], self.tf_props[order_tf]["is_origin"])
            order_df = order_resample.resample_price()
            currentPrice = order_df["close"].iloc[-1]

            primary_exchange = BIG_LIST_TICKERS[ticker]["primary_exchange"]
            sl_order_dict = {"ticker": ticker,
                          "sec_type": "STK",
                          "currency": "USD",
                          "exchange": "SMART",
                          "primary_exchange": primary_exchange}

            sl_con = self.broker.get_contract(sl_order_dict)
            time.sleep(1)
            self.broker.reqContractDetails(11, sl_con)
            time.sleep(1)

            if direction == "Bullish":
                currentProfit = currentPrice - entryPrice
                rr = currentProfit / riskPerShare
                x = math.floor(rr) - 1
                new_SL = entryPrice + (x * riskPerShare)
                new_SL = (new_SL) - (new_SL % self.broker.mintick)

                if current_sl < new_SL:
                    #Modify the order
                    sl_order_dict = {"order_id": order_id,
                                     "so_order_id": order_id,
                                     "so_action": action,
                                     "so_quantity": quantity,
                                     "so_stop_price": new_SL,
                                     "so_time_in_force": "GTC",
                                     "so_good_till_date": "",
                                     "so_parent_order_id": parent_id,
                                     "so_transmit": True
                                  }

                    stoploss_order = self.broker.get_stop_order(sl_order_dict)
                    self.broker.send_order(sl_order_dict, stoploss_order)

            if direction == "Bearish":
                currentProfit = entryPrice - currentPrice
                rr = currentProfit / riskPerShare
                x = math.floor(rr) - 1
                new_SL = entryPrice - (x * riskPerShare)
                new_SL = (new_SL) - (new_SL % self.broker.mintick)

                if current_sl > new_SL:
                    #Modify the order
                    sl_order_dict = {"order_id": order_id,
                                     "so_order_id": order_id,
                                     "so_action": action,
                                     "so_quantity": quantity,
                                     "so_stop_price": new_SL,
                                     "so_time_in_force": "GTC",
                                     "so_good_till_date": "",
                                     "so_parent_order_id": parent_id,
                                     "so_transmit": True
                                  }

                    stoploss_order = self.broker.get_stop_order(sl_order_dict)
                    self.broker.send_order(sl_order_dict, stoploss_order)

    def start(self):
        self.broker.init_client(self.broker)
        self.con = self.broker.get_contract(self.order_dict)
        self.function.set_strategy_status()
        self.check_trailing_stop()

    def send_orders(self):
        # self.function.send_entry_sl_tp_order(self.order_dict)
        # self.dashboard_dict[1]["parent_order_id"] = self.order_dict["slo_order_id"]
        # self.dashboard_dict[1]["profit_order_id"] = self.order_dict["lo_order_id"]
        # self.dashboard_dict[1]["stoploss_order_id"] = self.order_dict["so_order_id"]
        #
        # self.function.send_entry_sl_order(self.order_dict1)
        # self.dashboard_dict[2]["parent_order_id"] = self.order_dict1["slo_order_id"]
        # self.dashboard_dict[2]["profit_order_id"] = -1
        # self.dashboard_dict[2]["stoploss_order_id"] = self.order_dict1["so_order_id"]

        # Parent Order for Order 1
        self.broker.reqIds(1)
        time.sleep(1)
        self.order_dict["order_id"] = self.broker.orderId
        self.order_dict["slo_order_id"] = self.broker.orderId
        self.dashboard_dict[1]["parent_order_id"] = self.order_dict["order_id"]
        order = self.broker.get_stop_limit_order(self.order_dict)
        self.broker.send_order(self.order_dict, order)

        # Stoploss Order for Order 1
        self.broker.reqIds(1)
        time.sleep(1)
        self.order_dict["order_id"] = self.broker.orderId
        self.order_dict["so_order_id"] = self.broker.orderId
        self.order_dict["so_parent_order_id"] = self.order_dict["slo_order_id"]
        self.dashboard_dict[1]["stoploss_order_id"] = self.order_dict["order_id"]
        order = self.broker.get_stop_order(self.order_dict)
        self.broker.send_order(self.order_dict, order)

        # Profit Order for Order 1
        self.broker.reqIds(1)
        time.sleep(1)
        self.order_dict["order_id"] = self.broker.orderId
        self.order_dict["lo_order_id"] = self.broker.orderId
        self.order_dict["lo_parent_order_id"] = self.order_dict["slo_order_id"]
        self.dashboard_dict[1]["profit_order_id"] = self.order_dict["order_id"]
        order = self.broker.get_limit_order(self.order_dict)
        self.broker.send_order(self.order_dict, order)

        time.sleep(1)  # Adding 1 second sleep before sending in another order!!!

        # Parent Order for Order 2
        self.broker.reqIds(1)
        time.sleep(1)
        self.order_dict1["order_id"] = self.broker.orderId
        self.order_dict1["slo_order_id"] = self.broker.orderId
        self.dashboard_dict[2]["parent_order_id"] = self.order_dict1["order_id"]
        order = self.broker.get_stop_limit_order(self.order_dict1)
        self.broker.send_order(self.order_dict1, order)

        # Stoploss Order for Order 2
        self.broker.reqIds(1)
        time.sleep(1)
        self.order_dict1["order_id"] = self.broker.orderId
        self.order_dict1["so_order_id"] = self.broker.orderId
        self.order_dict1["so_parent_order_id"] = self.order_dict1["slo_order_id"]
        self.dashboard_dict[2]["stoploss_order_id"] = self.order_dict1["order_id"]
        order = self.broker.get_stop_order(self.order_dict1)
        self.broker.send_order(self.order_dict1, order)

        self.dashboard_dict[2]["profit_order_id"] = -1

    def after_send_orders(self):
        data_list = []
        for x in range(1,3):
            data = dict(parent_order_id=self.dashboard_dict[x]["parent_order_id"],
                        profit_order_id=self.dashboard_dict[x]["profit_order_id"],
                        stoploss_order_id=self.dashboard_dict[x]["stoploss_order_id"],
                        entry_price=self.dashboard_dict[1]["entry"],
                        risk_share=self.dashboard_dict[1]["risk_share"],
                        ticker=self.dashboard_dict[1]["ticker"],
                        timeframe=self.dashboard_dict[1]["timeframe"],
                        date_time=self.dashboard_dict[1]["date_time"],
                        status='Open')

            data_list.append(data)

        if data_list:
            df = pd.DataFrame(data=data_list)
            df.to_sql("bb_rev", self.db, if_exists='append', index=False, method='multi')

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
                    self.after_send_orders()

###############################################################################################################

historic_data_table = "us_equity_historic_data"
streaming_data_table = "us_equity_streaming_data"
db = createDB("market_data", "../all_strategy_files/data/config.ini")
time.sleep(1)

broker = IbChild(db)
broker.connect('127.0.0.1', 7497, 2)
time.sleep(1)
broker.reqPositions()
time.sleep(1)
broker.reqOpenOrders()
time.sleep(1)

# broker.reqAccountUpdates(True, '')

broker.reqAccountSummary(9001, "All", AccountSummaryTags.AllTags)
time.sleep(1)


def websocket_con():
    broker.run()

con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(30) #NEED 30 seconds to make sure broker starts to run before going through tickers!!!

def start_main(tickers):
    i = 0
    while True:
        if i == 0:
            time.sleep(10)   #REMOVE THIS AND TRY!!!

        for key in tickers:
            ticker = key
            primary_exchange = tickers[key]["primary_exchange"]

            if is_mkt_open('NYSE'):
                order_dict = dict()
                dashboard_dict = dict()
                order_dict = {"ticker": ticker,
                              "sec_type": "STK",
                              "currency": "USD",
                              "exchange": "SMART",
                              "primary_exchange": primary_exchange}

                now = datetime.datetime.now()
                print(now, ": ", ticker)
                x = BbRev(broker, ticker, db, historic_data_table, streaming_data_table, order_dict)
                x.execute()
                i = i+1

            else:
                pass

# def function_to_run_in_thread(tickers: list):
#     start_main(tickers)

# THREADS = []
# BIG_LIST_TICKERS = ['A', 'AA', 'AAIC', 'AAL', 'AAN', 'AAOI', 'AAON', 'AAP', 'AAPL', 'AAT', 'AAU', 'AAWW', 'AAXJ', 'AB', 'ABB', 'ABBV', 'ABC', 'ABCB', 'ABCL', 'ABEO', 'ABEV', 'ABG', 'ABIO', 'ABM', 'ABMD', 'ABNB', 'ABR', 'ABST', 'ABT', 'ABTX', 'ABUS', 'ACA', 'ACAD', 'ACB', 'ACC', 'ACCD', 'ACCO', 'ACEL', 'ACER', 'ACES', 'ACET', 'ACEV', 'ACGL', 'ACH', 'ACHC', 'ACI', 'ACIC', 'ACIU', 'ACIW', 'ACLS', 'ACM', 'ACMR', 'ACN', 'ACOR', 'ACR', 'ACRE', 'ACRS', 'ACRX', 'ACTG', 'ACVA', 'ACWI', 'ACWV', 'ACWX', 'ADAP', 'ADBE', 'ADC', 'ADCT', 'ADI', 'ADM', 'ADMA', 'ADMP', 'ADMS', 'ADN', 'ADNT', 'ADP', 'ADPT', 'ADS', 'ADSK', 'ADT', 'ADTN', 'ADTX', 'ADUS', 'ADV', 'ADVM', 'AEE', 'AEG', 'AEHR', 'AEIS', 'AEL', 'AEM', 'AEMD', 'AEO', 'AEP', 'AER', 'AERI', 'AES', 'AEVA', 'AEZS', 'AFG', 'AFI', 'AFIB', 'AFIN', 'AFL', 'AFMD', 'AFRM', 'AFTY', 'AFYA', 'AG', 'AGC', 'AGCB', 'AGCO', 'AGEN', 'AGFS', 'AGG', 'AGI', 'AGIO', 'AGL', 'AGLE', 'AGM', 'AGNC', 'AGO', 'AGQ', 'AGR', 'AGRO', 'AGRX', 'AGS', 'AGTC', 'AGX', 'AGYS', 'AGZ', 'AHAC', 'AHCO', 'AHH', 'AHT', 'AI', 'AIA', 'AIG', 'AIMC', 'AIN', 'AINV', 'AIQ', 'AIR', 'AIRC', 'AIRG', 'AIRR', 'AIT', 'AIV', 'AIZ', 'AJAX', 'AJG', 'AJRD', 'AJX', 'AKAM', 'AKBA', 'AKR', 'AKRO', 'AKTS', 'AKUS', 'AL', 'ALB', 'ALBO', 'ALC', 'ALDX', 'ALE', 'ALEC', 'ALEX', 'ALFA', 'ALG', 'ALGM', 'ALGN', 'ALGS', 'ALGT', 'ALHC', 'ALIT', 'ALK', 'ALKS', 'ALL', 'ALLE', 'ALLK', 'ALLO', 'ALLT', 'ALLY', 'ALNY', 'ALPN', 'ALRM', 'ALSN', 'ALT', 'ALTG', 'ALTO', 'ALTR', 'ALTU', 'ALTY', 'ALV', 'ALVR', 'ALXO', 'ALZN', 'AM', 'AMAT', 'AMBA', 'AMBC', 'AMC', 'AMCR', 'AMCX', 'AMD', 'AME', 'AMED', 'AMEH', 'AMG', 'AMGN', 'AMH', 'AMJ', 'AMKR', 'AMLP', 'AMN', 'AMNB', 'AMOT', 'AMP', 'AMPE', 'AMPH', 'AMPY', 'AMR', 'AMRC', 'AMRN', 'AMRS', 'AMRX', 'AMSC', 'AMSF', 'AMSWA', 'AMT', 'AMTI', 'AMTX', 'AMWD', 'AMWL', 'AMX', 'AMZA', 'AMZN', 'AN', 'ANAB', 'ANAT', 'ANDE', 'ANET', 'ANF', 'ANGI', 'ANGL', 'ANGO', 'ANIK', 'ANIP', 'ANIX', 'ANPC', 'ANSS', 'ANTE', 'ANTM', 'AON', 'AOS', 'AOSL', 'AOUT', 'AP', 'APA', 'APAM', 'APD', 'APDN', 'APEI', 'APEN', 'APG', 'APH', 'API', 'APLE', 'APLS', 'APLT', 'APO', 'APOG', 'APP', 'APPF', 'APPH', 'APPN', 'APPS', 'APRE', 'APRN', 'APT', 'APTO', 'APTS', 'APTV', 'APTX', 'APYX', 'AQB', 'AQMS', 'AQN', 'AQST', 'AQUA', 'AR', 'ARAV', 'ARAY', 'ARC', 'ARCB', 'ARCC', 'ARCH', 'ARCO', 'ARCT', 'ARD', 'ARDX', 'ARE', 'AREC', 'ARES', 'ARGT', 'ARGX', 'ARI', 'ARKF', 'ARKG', 'ARKK', 'ARKO', 'ARKQ', 'ARKW', 'ARKX', 'ARLO', 'ARLP', 'ARMK', 'ARNA', 'ARNC', 'AROC', 'AROW', 'ARQT', 'ARR', 'ARRY', 'ARVL', 'ARVN', 'ARW', 'ARWR', 'ASA', 'ASAI', 'ASAN', 'ASB', 'ASC', 'ASEA', 'ASGN', 'ASH', 'ASHR', 'ASHS', 'ASIX', 'ASLN', 'ASMB', 'ASML', 'ASND', 'ASO', 'ASPN', 'ASPS', 'ASPU', 'ASR', 'ASRT', 'ASRV', 'ASTE', 'ASTR', 'ASTS', 'ASUR', 'ASX', 'ASXC', 'ASYS', 'ATAI', 'ATAX', 'ATCO', 'ATCX', 'ATEC', 'ATEN', 'ATER', 'ATEX', 'ATGE', 'ATH', 'ATHA', 'ATHM', 'ATHX', 'ATI', 'ATIP', 'ATKR', 'ATLC', 'ATMP', 'ATNF', 'ATNI', 'ATNM', 'ATNX', 'ATO', 'ATOM', 'ATOS', 'ATR', 'ATRA', 'ATRC', 'ATRO', 'ATRS', 'ATSG', 'ATUS', 'ATVI', 'AU', 'AUB', 'AUD', 'AUDC', 'AUMN', 'AUPH', 'AUTL', 'AUTO', 'AUY', 'AVA', 'AVAH', 'AVAV', 'AVB', 'AVCT', 'AVD', 'AVDL', 'AVEO', 'AVGO', 'AVID', 'AVIR', 'AVLR', 'AVNS', 'AVNT', 'AVNW', 'AVO', 'AVPT', 'AVRO', 'AVT', 'AVTR', 'AVXL', 'AVY', 'AVYA', 'AWAY', 'AWH', 'AWI', 'AWK', 'AWR', 'AWRE', 'AX', 'AXAS', 'AXDX', 'AXGN', 'AXL', 'AXLA', 'AXNX', 'AXON', 'AXP', 'AXS', 'AXSM', 'AXTA', 'AXTI', 'AXU', 'AY', 'AYI', 'AYRO', 'AYTU', 'AYX', 'AZEK', 'AZN', 'AZO', 'AZPN', 'AZUL', 'AZZ', 'B', 'BA', 'BAB', 'BABA', 'BAC', 'BAH', 'BAL', 'BALY', 'BAM', 'BANC', 'BAND', 'BANF', 'BANR', 'BAP', 'BARK', 'BATRA', 'BATRK', 'BATT', 'BAX', 'BB', 'BBAR', 'BBAX', 'BBBY', 'BBCA', 'BBCP', 'BBD', 'BBDC', 'BBEU', 'BBH', 'BBIG', 'BBIN', 'BBIO', 'BBJP', 'BBL', 'BBSI', 'BBU', 'BBVA', 'BBW', 'BBY', 'BC', 'BCAB', 'BCBP', 'BCC', 'BCDA', 'BCE', 'BCEI', 'BCEL', 'BCI', 'BCLI', 'BCM', 'BCO', 'BCOR', 'BCOV', 'BCPC', 'BCRX', 'BCS', 'BCSF', 'BCYC', 'BDC', 'BDN', 'BDRY', 'BDSI', 'BDSX', 'BDTX', 'BDX', 'BE', 'BEAM', 'BECN', 'BEEM', 'BEKE', 'BELFB', 'BEN', 'BEP', 'BEPC', 'BERY', 'BEST', 'BETZ', 'BF.A', 'BF.B', 'BFAM', 'BFI', 'BFLY', 'BFOR', 'BG', 'BGCP', 'BGFV', 'BGNE', 'BGRY', 'BGS', 'BHC', 'BHE', 'BHF', 'BHG', 'BHLB', 'BHP', 'BHR', 'BHVN', 'BIB', 'BIDU', 'BIG', 'BIGC', 'BIIB', 'BIL', 'BILI', 'BILL', 'BIO', 'BIOC', 'BIOX', 'BIP', 'BIPC', 'BIS', 'BITF', 'BITQ', 'BIV', 'BIZD', 'BJ', 'BJK', 'BJRI', 'BK', 'BKCC', 'BKD', 'BKE', 'BKEP', 'BKF', 'BKH', 'BKI', 'BKLN', 'BKNG', 'BKR', 'BKU', 'BKYI', 'BL', 'BLCN', 'BLD', 'BLDE', 'BLDP', 'BLDR', 'BLFS', 'BLI', 'BLK', 'BLKB', 'BLL', 'BLMN', 'BLNK', 'BLOK', 'BLRX', 'BLU', 'BLUE', 'BLV', 'BLX', 'BMA', 'BMBL', 'BMI', 'BMO', 'BMRA', 'BMRN', 'BMTC', 'BMTX', 'BMY', 'BND', 'BNDX', 'BNED', 'BNFT', 'BNGO', 'BNL', 'BNO', 'BNS', 'BNTC', 'BNTX', 'BOCH', 'BODY', 'BOH', 'BOIL', 'BOKF', 'BOND', 'BOOM', 'BOOT', 'BOTZ', 'BOWX', 'BOX', 'BP', 'BPMC', 'BPMP', 'BPOP', 'BPT', 'BQ', 'BR', 'BRBR', 'BRC', 'BREZ', 'BRF', 'BRFS', 'BRG', 'BRK.B', 'BRKL', 'BRKR', 'BRKS', 'BRMK', 'BRO', 'BRP', 'BRSP', 'BRX', 'BRY', 'BRZU', 'BSAC', 'BSBR', 'BSCL', 'BSET', 'BSGM', 'BSIG', 'BSM', 'BSMX', 'BSQR', 'BSRR', 'BSV', 'BSX', 'BSY', 'BTAI', 'BTAQ', 'BTBT', 'BTCM', 'BTG', 'BTI', 'BTN', 'BTNB', 'BTRS', 'BTTR', 'BTU', 'BTWN', 'BTX', 'BUD', 'BUG', 'BUR', 'BURL', 'BUSE', 'BUZZ', 'BV', 'BVN', 'BW', 'BWA', 'BWAC', 'BWEN', 'BWX', 'BWXT', 'BX', 'BXC', 'BXMT', 'BXP', 'BXRX', 'BXS', 'BYD', 'BYND', 'BYSI', 'BZH', 'BZQ', 'BZUN', 'C', 'CAAP', 'CAAS', 'CABA', 'CAC', 'CACC', 'CACI', 'CADE', 'CAE', 'CAF', 'CAG', 'CAH', 'CAI', 'CAJ', 'CAKE', 'CAL', 'CALA', 'CALM', 'CALX', 'CAMP', 'CAMT', 'CAN', 'CANE', 'CANO', 'CAP', 'CAPE', 'CAPL', 'CAPR', 'CAR', 'CARA', 'CARG', 'CARR', 'CARS', 'CASA', 'CASH', 'CASS', 'CASY', 'CAT', 'CATB', 'CATH', 'CATO', 'CATY', 'CB', 'CBAT', 'CBAY', 'CBB', 'CBD', 'CBIO', 'CBLI', 'CBOE', 'CBRE', 'CBRL', 'CBSH', 'CBT', 'CBU', 'CBZ', 'CC', 'CCAC', 'CCCC', 'CCEP', 'CCI', 'CCJ', 'CCK', 'CCL', 'CCLP', 'CCMP', 'CCNE', 'CCO', 'CCOI', 'CCRN', 'CCS', 'CCV', 'CCXI', 'CD', 'CDAK', 'CDAY', 'CDE', 'CDEV', 'CDK', 'CDLX', 'CDMO', 'CDNA', 'CDNS', 'CDR', 'CDTX', 'CDW', 'CDXC', 'CDXS', 'CDZI', 'CE', 'CECE', 'CEIX', 'CELH', 'CELJF', 'CELU', 'CEMB', 'CEMI', 'CENT', 'CENTA', 'CENX', 'CEQP', 'CERC', 'CERE', 'CERN', 'CERS', 'CERT', 'CEVA', 'CEW', 'CF', 'CFA', 'CFAC', 'CFB', 'CFFN', 'CFG', 'CFLT', 'CFR', 'CFRX', 'CFX', 'CG', 'CGA', 'CGAU', 'CGBD', 'CGC', 'CGEN', 'CGNT', 'CGNX', 'CGRN', 'CGW', 'CHAD', 'CHAU', 'CHCO', 'CHD', 'CHDN', 'CHE', 'CHEF', 'CHGG', 'CHH', 'CHIC', 'CHIK', 'CHIQ', 'CHIX', 'CHK', 'CHKP', 'CHMA', 'CHMI', 'CHNG', 'CHPT', 'CHRA', 'CHRS', 'CHRW', 'CHS', 'CHT', 'CHTR', 'CHUY', 'CHWY', 'CHX', 'CI', 'CIA', 'CIB', 'CIBR', 'CIEN', 'CIG', 'CIGI', 'CIM', 'CINF', 'CIO', 'CIR', 'CIT', 'CIVB', 'CIXX', 'CKPT', 'CL', 'CLAR', 'CLB', 'CLBK', 'CLBS', 'CLDR', 'CLDT', 'CLDX', 'CLF', 'CLFD', 'CLH', 'CLI', 'CLIR', 'CLLS', 'CLMT', 'CLNE', 'CLOU', 'CLOV', 'CLPS', 'CLPT', 'CLR', 'CLS', 'CLSD', 'CLSK', 'CLSN', 'CLVR', 'CLVS', 'CLVT', 'CLW', 'CLX', 'CLXT', 'CM', 'CMA', 'CMC', 'CMCM', 'CMCO', 'CMCSA', 'CME', 'CMG', 'CMI', 'CMO', 'CMP', 'CMPR', 'CMPS', 'CMRE', 'CMRX', 'CMS', 'CMTL', 'CNA', 'CNBS', 'CNC', 'CNCE', 'CNDT', 'CNET', 'CNHI', 'CNI', 'CNK', 'CNMD', 'CNNE', 'CNO', 'CNOB', 'CNP', 'CNQ', 'CNR', 'CNRG', 'CNS', 'CNSL', 'CNTY', 'CNX', 'CNXC', 'CNXN', 'CNXT', 'CNYA', 'CO', 'CODI', 'CODX', 'COF', 'COG', 'COGT', 'COHR', 'COHU', 'COIN', 'COLB', 'COLD', 'COLL', 'COLM', 'COMM', 'COMP', 'COMS', 'COMT', 'CONE', 'CONN', 'CONX', 'COO', 'COOP', 'COP', 'COPX', 'COR', 'CORE', 'CORN', 'CORR', 'CORT', 'COST', 'COTY', 'COUP', 'COUR', 'COW', 'COWN', 'COWZ', 'CP', 'CPA', 'CPB', 'CPE', 'CPER', 'CPF', 'CPG', 'CPK', 'CPLG', 'CPLP', 'CPNG', 'CPRI', 'CPRT', 'CPRX', 'CPS', 'CPSH', 'CPSI', 'CPSS', 'CPT', 'CPUH', 'CQP', 'CQQQ', 'CR', 'CRAI', 'CRBN', 'CRBP', 'CRC', 'CRCT', 'CRD.A', 'CRDF', 'CREE', 'CRESY', 'CRH', 'CRHC', 'CRI', 'CRIS', 'CRK', 'CRL', 'CRM', 'CRMD', 'CRMT', 'CRNC', 'CRNT', 'CRNX', 'CROC', 'CRON', 'CROX', 'CRS', 'CRSP', 'CRSR', 'CRTD', 'CRTO', 'CRTX', 'CRU', 'CRUS', 'CRVL', 'CRVS', 'CRWD', 'CRWS', 'CRY', 'CS', 'CSAN', 'CSBR', 'CSCO', 'CSD', 'CSGP', 'CSGS', 'CSII', 'CSIQ', 'CSL', 'CSLT', 'CSOD', 'CSPR', 'CSR', 'CSTE', 'CSTL', 'CSTM', 'CSV', 'CSWC', 'CSX', 'CTAS', 'CTBI', 'CTEC', 'CTG', 'CTIC', 'CTLP', 'CTLT', 'CTMX', 'CTOS', 'CTRE', 'CTRM', 'CTRN', 'CTS', 'CTSH', 'CTSO', 'CTT', 'CTVA', 'CTXR', 'CTXS', 'CUBE', 'CUBI', 'CUE', 'CUK', 'CULP', 'CURE', 'CURI', 'CURO', 'CUT', 'CUTR', 'CUZ', 'CVA', 'CVAC', 'CVBF', 'CVCO', 'CVCY', 'CVE', 'CVEO', 'CVET', 'CVGI', 'CVGW', 'CVI', 'CVLG', 'CVLT', 'CVM', 'CVNA', 'CVS', 'CVX', 'CVY', 'CW', 'CWB', 'CWCO', 'CWEB', 'CWEN', 'CWEN.A', 'CWH', 'CWI', 'CWK', 'CWST', 'CWT', 'CX', 'CXDC', 'CXM', 'CXP', 'CXSE', 'CXW', 'CYB', 'CYBE', 'CYBR', 'CYCC', 'CYCN', 'CYD', 'CYH', 'CYRX', 'CYTK', 'CYTO', 'CZNC', 'CZR', 'D', 'DAC', 'DADA', 'DAKT', 'DAL', 'DALN', 'DAN', 'DAO', 'DAR', 'DASH', 'DB', 'DBA', 'DBB', 'DBC', 'DBD', 'DBE', 'DBEF', 'DBEU', 'DBI', 'DBJP', 'DBO', 'DBP', 'DBRG', 'DBS', 'DBV', 'DBVT', 'DBX', 'DCBO', 'DCI', 'DCO', 'DCOM', 'DCP', 'DCPH', 'DCRC', 'DCT', 'DD', 'DDD', 'DDG', 'DDM', 'DDOG', 'DDS', 'DE', 'DEA', 'DECK', 'DEEP', 'DEH', 'DEI', 'DELL', 'DEM', 'DEN', 'DENN', 'DEO', 'DES', 'DESP', 'DFAU', 'DFE', 'DFEN', 'DFH', 'DFIN', 'DFJ', 'DFNS', 'DFS', 'DG', 'DGICA', 'DGII', 'DGL', 'DGLY', 'DGNR', 'DGNS', 'DGRO', 'DGRW', 'DGS', 'DGX', 'DHC', 'DHI', 'DHR', 'DHS', 'DHT', 'DHX', 'DIA', 'DIDI', 'DIG', 'DIN', 'DIOD', 'DIS', 'DISCA', 'DISCK', 'DISH', 'DIV', 'DIVO', 'DJP', 'DK', 'DKL', 'DKNG', 'DKS', 'DLB', 'DLHC', 'DLN', 'DLNG', 'DLO', 'DLPN', 'DLR', 'DLS', 'DLTH', 'DLTR', 'DLX', 'DM', 'DMAC', 'DMLP', 'DMRC', 'DMTK', 'DMYI', 'DNB', 'DNLI', 'DNMR', 'DNN', 'DNOW', 'DNUT', 'DOC', 'DOCN', 'DOCS', 'DOCU', 'DOG', 'DOMO', 'DON', 'DOOO', 'DOOR', 'DORM', 'DOV', 'DOW', 'DOX', 'DOYU', 'DPST', 'DPW', 'DPZ', 'DQ', 'DRD', 'DRE', 'DRH', 'DRI', 'DRIO', 'DRIP', 'DRIV', 'DRN', 'DRNA', 'DRQ', 'DRRX', 'DRTT', 'DRV', 'DRVN', 'DS', 'DSEY', 'DSGX', 'DSI', 'DSKE', 'DSL', 'DSPC', 'DSPG', 'DSX', 'DT', 'DTE', 'DTEA', 'DTEC', 'DTIL', 'DTM', 'DTN', 'DUG', 'DUK', 'DUSL', 'DUST', 'DV', 'DVA', 'DVAX', 'DVN', 'DVY', 'DVYE', 'DWAS', 'DWX', 'DX', 'DXC', 'DXCM', 'DXD', 'DXJ', 'DXJS', 'DXPE', 'DXYN', 'DY', 'DYAI', 'DYN', 'DZSI', 'E', 'EA', 'EAF', 'EAR', 'EARN', 'EAT', 'EB', 'EBAY', 'EBC', 'EBF', 'EBIX', 'EBIZ', 'EBND', 'EBON', 'EBS', 'EBSB', 'EC', 'ECH', 'ECHO', 'ECL', 'ECNS', 'ECOL', 'ECOM', 'ECON', 'ECPG', 'ED', 'EDAP', 'EDC', 'EDIT', 'EDIV', 'EDOC', 'EDR', 'EDU', 'EDV', 'EDZ', 'EEFT', 'EELV', 'EEM', 'EEMA', 'EEMV', 'EES', 'EET', 'EEV', 'EEX', 'EFA', 'EFAV', 'EFC', 'EFG', 'EFSC', 'EFV', 'EFX', 'EFZ', 'EGAN', 'EGBN', 'EGHT', 'EGLX', 'EGO', 'EGP', 'EGRX', 'EGY', 'EH', 'EHC', 'EHTH', 'EIDO', 'EIG', 'EIGR', 'EINC', 'EIX', 'EKSO', 'EL', 'ELAN', 'ELD', 'ELDN', 'ELF', 'ELMD', 'ELMS', 'ELOX', 'ELP', 'ELS', 'ELVT', 'ELY', 'ELYS', 'EMAN', 'EMB', 'EME', 'EMKR', 'EMLC', 'EMLP', 'EMN', 'EMQQ', 'EMR', 'EMX', 'EMXC', 'ENB', 'ENBL', 'ENDP', 'ENG', 'ENIA', 'ENIC', 'ENLC', 'ENLV', 'ENOB', 'ENPH', 'ENR', 'ENS', 'ENSG', 'ENTA', 'ENTG', 'ENTX', 'ENV', 'ENVA', 'ENVX', 'ENZ', 'ENZL', 'EOG', 'EOLS', 'EOSE', 'EPAC', 'EPAM', 'EPAY', 'EPC', 'EPD', 'EPHY', 'EPI', 'EPM', 'EPP', 'EPR', 'EPRT', 'EPS', 'EPV', 'EPZM', 'EQ', 'EQC', 'EQH', 'EQIX', 'EQNR', 'EQOS', 'EQR', 'EQT', 'EQX', 'ERF', 'ERIC', 'ERIE', 'ERII', 'ERJ', 'ERTH', 'ERX', 'ERY', 'ES', 'ESCA', 'ESE', 'ESGC', 'ESGE', 'ESGU', 'ESI', 'ESNT', 'ESPO', 'ESPR', 'ESRT', 'ESS', 'ESSC', 'ESTA', 'ESTC', 'ESTE', 'ESXB', 'ET', 'ETH', 'ETN', 'ETNB', 'ETON', 'ETR', 'ETRN', 'ETSY', 'ETWO', 'EUFN', 'EUM', 'EUO', 'EURL', 'EURN', 'EVA', 'EVBG', 'EVC', 'EVER', 'EVFM', 'EVGN', 'EVGO', 'EVH', 'EVLO', 'EVLV', 'EVOK', 'EVOP', 'EVR', 'EVRG', 'EVRI', 'EVTC', 'EVX', 'EW', 'EWA', 'EWBC', 'EWC', 'EWD', 'EWG', 'EWH', 'EWI', 'EWJ', 'EWK', 'EWL', 'EWM', 'EWN', 'EWP', 'EWQ', 'EWRE', 'EWS', 'EWT', 'EWU', 'EWV', 'EWW', 'EWX', 'EWY', 'EWZ', 'EXAS', 'EXC', 'EXEL', 'EXK', 'EXLS', 'EXP', 'EXPD', 'EXPE', 'EXPI', 'EXPO', 'EXPR', 'EXR', 'EXTN', 'EXTR', 'EYE', 'EYEN', 'EYES', 'EYPT', 'EZA', 'EZJ', 'EZM', 'EZPW', 'EZU', 'F', 'FAF', 'FALN', 'FAN', 'FANG', 'FANH', 'FARM', 'FARO', 'FAS', 'FAST', 'FATE', 'FAZ', 'FB', 'FBC', 'FBHS', 'FBIO', 'FBIZ', 'FBK', 'FBNC', 'FBP', 'FBRX', 'FBT', 'FC', 'FCA', 'FCBC', 'FCEL', 'FCF', 'FCFS', 'FCG', 'FCN', 'FCOM', 'FCPT', 'FCRD', 'FCX', 'FDD', 'FDIS', 'FDL', 'FDLO', 'FDMO', 'FDMT', 'FDN', 'FDNI', 'FDP', 'FDRR', 'FDS', 'FDUS', 'FDVV', 'FDX', 'FE', 'FELE', 'FEM', 'FENC', 'FENG', 'FENY', 'FEP', 'FEX', 'FEYE', 'FEZ', 'FF', 'FFBC', 'FFIC', 'FFIE', 'FFIN', 'FFIV', 'FFNW', 'FFTY', 'FGD', 'FGEN', 'FHB', 'FHI', 'FHLC', 'FHN', 'FI', 'FIBK', 'FICO', 'FIDI', 'FIDU', 'FIGS', 'FINV', 'FINX', 'FIS', 'FISI', 'FISV', 'FITB', 'FIVE', 'FIVG', 'FIVN', 'FIW', 'FIX', 'FIXD', 'FIXX', 'FIZZ', 'FL', 'FLBR', 'FLDM', 'FLEX', 'FLGT', 'FLIC', 'FLL', 'FLMN', 'FLNT', 'FLO', 'FLOT', 'FLOW', 'FLQL', 'FLR', 'FLRN', 'FLS', 'FLT', 'FLUX', 'FLWS', 'FLXN', 'FLY', 'FM', 'FMAC', 'FMAT', 'FMBI', 'FMC', 'FMNB', 'FMS', 'FMTX', 'FMX', 'FN', 'FNB', 'FNCL', 'FND', 'FNDA', 'FNDC', 'FNDE', 'FNDF', 'FNDX', 'FNF', 'FNGS', 'FNHC', 'FNKO', 'FNLC', 'FNV', 'FOA', 'FOCS', 'FOE', 'FOLD', 'FOR', 'FORM', 'FORR', 'FOSL', 'FOUR', 'FOX', 'FOXA', 'FOXF', 'FPAC', 'FPE', 'FPH', 'FPI', 'FPX', 'FPXI', 'FQAL', 'FR', 'FRAK', 'FRBK', 'FRC', 'FREE', 'FREL', 'FREQ', 'FREY', 'FRG', 'FRGI', 'FRHC', 'FRI', 'FRME', 'FRO', 'FROG', 'FRPT', 'FRSX', 'FRT', 'FRTA', 'FSK', 'FSLR', 'FSLY', 'FSM', 'FSMD', 'FSP', 'FSR', 'FSS', 'FST', 'FSTA', 'FSTR', 'FSTX', 'FSV', 'FTAG', 'FTAI', 'FTC', 'FTCH', 'FTCS', 'FTCV', 'FTDR', 'FTEC', 'FTEK', 'FTFT', 'FTGC', 'FTI', 'FTK', 'FTNT', 'FTRI', 'FTS', 'FTSL', 'FTSM', 'FTV', 'FTXN', 'FTXO', 'FTXR', 'FUBO', 'FUL', 'FULC', 'FULT', 'FUN', 'FUSE', 'FUSN', 'FUTU', 'FUTY', 'FUV', 'FV', 'FVAL', 'FVD', 'FVE', 'FVRR', 'FWONA', 'FWONK', 'FWRD', 'FXA', 'FXB', 'FXC', 'FXD', 'FXE', 'FXF', 'FXG', 'FXH', 'FXI', 'FXL', 'FXN', 'FXO', 'FXP', 'FXR', 'FXU', 'FXY', 'FXZ', 'FYBR', 'FYX', 'G', 'GABC', 'GAIA', 'GAIN', 'GALT', 'GAMR', 'GAN', 'GASS', 'GATO', 'GATX', 'GAU', 'GAZ', 'GB', 'GBCI', 'GBDC', 'GBIO', 'GBOX', 'GBT', 'GBUG', 'GBX', 'GCI', 'GCO', 'GCP', 'GD', 'GDDY', 'GDEN', 'GDOT', 'GDRX', 'GDS', 'GDX', 'GDXJ', 'GDYN', 'GE', 'GEF', 'GEL', 'GEM', 'GENE', 'GENI', 'GENN', 'GENY', 'GEO', 'GEOS', 'GERM', 'GERN', 'GES', 'GEVO', 'GFF', 'GFI', 'GFL', 'GGAL', 'GGB', 'GGG', 'GH', 'GHL', 'GHM', 'GHYB', 'GIB', 'GIC', 'GIFI', 'GIGB', 'GII', 'GIII', 'GIL', 'GILD', 'GILT', 'GINN', 'GIS', 'GKOS', 'GL', 'GLAD', 'GLBS', 'GLCN', 'GLD', 'GLDD', 'GLIN', 'GLL', 'GLMD', 'GLNG', 'GLOB', 'GLOP', 'GLP', 'GLPG', 'GLPI', 'GLRE', 'GLT', 'GLTO', 'GLW', 'GLYC', 'GM', 'GMAB', 'GMBL', 'GMDA', 'GME', 'GMED', 'GMF', 'GMRE', 'GMS', 'GMTX', 'GNCA', 'GNE', 'GNK', 'GNL', 'GNLN', 'GNOG', 'GNOM', 'GNPK', 'GNPX', 'GNR', 'GNRC', 'GNRS', 'GNSS', 'GNTX', 'GNUS', 'GNW', 'GO', 'GOCO', 'GOED', 'GOEV', 'GOEX', 'GOGL', 'GOGO', 'GOL', 'GOLD', 'GOLF', 'GOOD', 'GOOG', 'GOOGL', 'GOOS', 'GORO', 'GOSS', 'GOTU', 'GOVT', 'GOVZ', 'GP', 'GPC', 'GPI', 'GPK', 'GPL', 'GPMT', 'GPN', 'GPP', 'GPRE', 'GPRK', 'GPRO', 'GPS', 'GPX', 'GRA', 'GRAY', 'GRBK', 'GRC', 'GREK', 'GRFS', 'GRID', 'GRMN', 'GRN', 'GROW', 'GROY', 'GRPN', 'GRSV', 'GRTS', 'GRUB', 'GRWG', 'GS', 'GSAH', 'GSAT', 'GSBC', 'GSBD', 'GSEW', 'GSG', 'GSHD', 'GSIE', 'GSIT', 'GSK', 'GSKY', 'GSL', 'GSLC', 'GSM', 'GSP', 'GSS', 'GSY', 'GT', 'GTBP', 'GTE', 'GTES', 'GTHX', 'GTIM', 'GTLS', 'GTN', 'GTS', 'GTTN', 'GTX', 'GTY', 'GTYH', 'GUNR', 'GURU', 'GUSH', 'GVA', 'GVI', 'GVIP', 'GWAC', 'GWB', 'GWRE', 'GWRS', 'GWW', 'GWX', 'GXC', 'GXG', 'GXTG', 'GYLD', 'H', 'HA', 'HAAC', 'HACK', 'HAE', 'HAFC', 'HAIL', 'HAIN', 'HAL', 'HALL', 'HALO', 'HAP', 'HARP', 'HAS', 'HASI', 'HAYN', 'HAYW', 'HBAN', 'HBI', 'HBIO', 'HBM', 'HBNC', 'HBP', 'HCA', 'HCAT', 'HCC', 'HCCI', 'HCHC', 'HCI', 'HCKT', 'HCM', 'HCSG', 'HD', 'HDB', 'HDEF', 'HDGE', 'HDSN', 'HDV', 'HE', 'HEAR', 'HEDJ', 'HEES', 'HEFA', 'HEI', 'HEI.A', 'HELE', 'HEP', 'HEPA', 'HERO', 'HES', 'HESM', 'HEWG', 'HEWJ', 'HEXO', 'HEZU', 'HFC', 'HFWA', 'HGEN', 'HGV', 'HHC', 'HI', 'HIBB', 'HIBL', 'HIBS', 'HIG', 'HII', 'HIL', 'HIMS', 'HIMX', 'HITI', 'HIW', 'HJLI', 'HL', 'HLF', 'HLI', 'HLIO', 'HLIT', 'HLMN', 'HLNE', 'HLT', 'HLX', 'HMC', 'HMHC', 'HMLP', 'HMN', 'HMST', 'HMTV', 'HMY', 'HNDL', 'HNGR', 'HNI', 'HNP', 'HNST', 'HOFT', 'HOFV', 'HOG', 'HOLI', 'HOLX', 'HOMB', 'HOMZ', 'HON', 'HONE', 'HOOK', 'HOPE', 'HP', 'HPE', 'HPP', 'HPQ', 'HQY', 'HR', 'HRB', 'HRC', 'HRI', 'HRL', 'HRMY', 'HROW', 'HRTG', 'HRTX', 'HRZN', 'HSBC', 'HSC', 'HSIC', 'HSII', 'HSKA', 'HST', 'HSTM', 'HSY', 'HT', 'HTA', 'HTBI', 'HTBK', 'HTBX', 'HTGC', 'HTH', 'HTHT', 'HTLD', 'HTLF', 'HTOO', 'HUBB', 'HUBG', 'HUBS', 'HUGE', 'HUM', 'HUN', 'HURN', 'HUT', 'HUYA', 'HVT', 'HWC', 'HWKN', 'HWM', 'HXL', 'HY', 'HYBB', 'HYD', 'HYFM', 'HYG', 'HYGH', 'HYLB', 'HYLD', 'HYLN', 'HYLV', 'HYMB', 'HYMC', 'HYRE', 'HYS', 'HYXU', 'HYZN', 'HZN', 'HZNP', 'HZO', 'HZON', 'IAA', 'IAC', 'IAG', 'IAGG', 'IAI', 'IART', 'IAT', 'IAU', 'IBB', 'IBCP', 'IBIO', 'IBKR', 'IBM', 'IBN', 'IBOC', 'IBP', 'IBRX', 'IBTX', 'IBUY', 'ICAD', 'ICE', 'ICF', 'ICFI', 'ICHR', 'ICL', 'ICLK', 'ICLN', 'ICLR', 'ICMB', 'ICON', 'ICPT', 'ICSH', 'ICUI', 'ICVT', 'IDA', 'IDCC', 'IDEV', 'IDEX', 'IDLV', 'IDN', 'IDNA', 'IDRA', 'IDRV', 'IDT', 'IDU', 'IDV', 'IDXX', 'IDYA', 'IEA', 'IEC', 'IEF', 'IEFA', 'IEI', 'IEMG', 'IEO', 'IEP', 'IETC', 'IEUR', 'IEV', 'IEX', 'IEZ', 'IFF', 'IFGL', 'IFN', 'IFRA', 'IFRX', 'IGAC', 'IGC', 'IGE', 'IGF', 'IGIB', 'IGLB', 'IGM', 'IGMS', 'IGN', 'IGOV', 'IGSB', 'IGT', 'IGV', 'IHAK', 'IHDG', 'IHE', 'IHF', 'IHI', 'IHRT', 'IHY', 'III', 'IIIN', 'IIIV', 'IIN', 'IIPR', 'IIVI', 'IJH', 'IJJ', 'IJK', 'IJR', 'IJS', 'IJT', 'ILF', 'ILMN', 'ILPT', 'IMAB', 'IMAX', 'IMBI', 'IMGN', 'IMH', 'IMKTA', 'IMLP', 'IMMP', 'IMMR', 'IMNM', 'IMO', 'IMOS', 'IMTM', 'IMTX', 'IMUX', 'IMV', 'IMVT', 'IMXI', 'INCO', 'INCY', 'INDA', 'INDB', 'INDI', 'INDL', 'INDY', 'INFI', 'INFL', 'INFN', 'INFO', 'INFU', 'INFY', 'ING', 'INGN', 'INGR', 'INMB', 'INMD', 'INN', 'INO', 'INOD', 'INOV', 'INSE', 'INSG', 'INSM', 'INSP', 'INSW', 'INT', 'INTC', 'INTF', 'INTT', 'INTU', 'INTZ', 'INVA', 'INVE', 'INVH', 'INVZ', 'IO', 'IONS', 'IOO', 'IOSP', 'IOVA', 'IP', 'IPA', 'IPAR', 'IPAY', 'IPFF', 'IPG', 'IPGP', 'IPI', 'IPO', 'IPOD', 'IPOF', 'IQ', 'IQDF', 'IQDG', 'IQLT', 'IQV', 'IR', 'IRBO', 'IRBT', 'IRDM', 'IRIX', 'IRM', 'IRT', 'IRTC', 'IRWD', 'IS', 'ISBC', 'ISEE', 'ISRA', 'ISRG', 'ISTB', 'ISUN', 'IT', 'ITA', 'ITB', 'ITCI', 'ITEQ', 'ITGR', 'ITI', 'ITM', 'ITOT', 'ITP', 'ITRI', 'ITRN', 'ITT', 'ITUB', 'ITW', 'IUSB', 'IUSG', 'IUSV', 'IVAC', 'IVC', 'IVE', 'IVLU', 'IVOL', 'IVR', 'IVV', 'IVW', 'IVZ', 'IWB', 'IWC', 'IWD', 'IWF', 'IWFH', 'IWL', 'IWM', 'IWN', 'IWO', 'IWP', 'IWR', 'IWS', 'IWV', 'IWX', 'IWY', 'IXC', 'IXG', 'IXJ', 'IXN', 'IXP', 'IXUS', 'IYC', 'IYE', 'IYF', 'IYG', 'IYH', 'IYJ', 'IYK', 'IYM', 'IYR', 'IYT', 'IYW', 'IYY', 'IYZ', 'IZEA', 'IZRL', 'J', 'JACK', 'JAGX', 'JAMF', 'JAX', 'JAZZ', 'JBGS', 'JBHT', 'JBI', 'JBL', 'JBLU', 'JBSS', 'JBT', 'JCI', 'JCOM', 'JD', 'JDST', 'JEF', 'JELD', 'JEPI', 'JETS', 'JFIN', 'JG', 'JHG', 'JHML', 'JJA', 'JJC', 'JJE', 'JJG', 'JJM', 'JJN', 'JJP', 'JJS', 'JJSF', 'JJT']
# BIG_LIST_TICKERS = ['A', 'AA', 'AAIC', 'AAL', 'AAN', 'AAOI', 'AAON', 'AAP', 'AAPL', 'AAT', 'AAU', 'AAWW', 'AAXJ', 'AB', 'ABB', 'ABBV', 'ABC', 'ABCB', 'ABCL', 'ABEO', 'ABEV', 'ABG', 'ABIO', 'ABM', 'ABMD', 'ABNB', 'ABR', 'ABST', 'ABT', 'ABTX', 'ABUS', 'ACA', 'ACAD', 'ACB', 'ACC', 'ACCD', 'ACCO', 'ACEL', 'ACER', 'ACES', 'ACET', 'ACEV', 'ACGL', 'ACH', 'ACHC', 'ACI', 'ACIC', 'ACIU', 'ACIW', 'ACLS', 'ACM', 'ACMR', 'ACN', 'ACOR', 'ACR', 'ACRE', 'ACRS', 'ACRX', 'ACTG', 'ACVA', 'ACWI', 'ACWV', 'ACWX', 'ADAP', 'ADBE', 'ADC', 'ADCT', 'ADI', 'ADM', 'ADMA', 'ADMP', 'ADMS', 'ADN', 'ADNT', 'ADP', 'ADPT', 'ADS', 'ADSK', 'ADT', 'ADTN', 'ADTX', 'ADUS', 'ADV', 'ADVM', 'AEE', 'AEG', 'AEHR', 'AEIS', 'AEL', 'AEM', 'AEMD', 'AEO', 'AEP', 'AER', 'AERI', 'AES', 'AEVA', 'AEZS', 'AFG', 'AFI', 'AFIB', 'AFIN', 'AFL', 'AFMD', 'AFRM', 'AFTY', 'AFYA', 'AG', 'AGC', 'AGCB', 'AGCO', 'AGEN', 'AGFS', 'AGG', 'AGI', 'AGIO', 'AGL', 'AGLE', 'AGM', 'AGNC', 'AGO', 'AGQ', 'AGR', 'AGRO', 'AGRX', 'AGS', 'AGTC', 'AGX', 'AGYS', 'AGZ', 'AHCO', 'AHH', 'AHT', 'AI', 'AIA', 'AIG', 'AIMC', 'AIN', 'AINV', 'AIQ', 'AIR', 'AIRC', 'AIRG', 'AIRR', 'AIT', 'AIV', 'AIZ', 'AJAX', 'AJG', 'AJRD', 'AJX', 'AKAM', 'AKBA', 'AKR', 'AKRO', 'AKTS', 'AKUS', 'AL', 'ALB', 'ALBO', 'ALC', 'ALDX', 'ALE', 'ALEC', 'ALEX', 'ALFA', 'ALG', 'ALGM', 'ALGN', 'ALGS', 'ALGT', 'ALHC', 'ALIT', 'ALK', 'ALKS', 'ALL', 'ALLE', 'ALLK', 'ALLO', 'ALLT', 'ALLY', 'ALNY', 'ALPN', 'ALRM', 'ALSN', 'ALT', 'ALTG', 'ALTO', 'ALTR', 'ALTU', 'ALTY', 'ALV', 'ALVR', 'ALXO', 'ALZN', 'AM', 'AMAT', 'AMBA', 'AMBC', 'AMC', 'AMCR', 'AMCX', 'AMD', 'AME', 'AMED', 'AMEH', 'AMG', 'AMGN', 'AMH', 'AMJ', 'AMKR', 'AMLP', 'AMN', 'AMNB', 'AMOT', 'AMP', 'AMPE', 'AMPH', 'AMPY', 'AMR', 'AMRC', 'AMRN', 'AMRS', 'AMRX', 'AMSC', 'AMSF', 'AMSWA', 'AMT', 'AMTI', 'AMTX', 'AMWD', 'AMWL', 'AMX', 'AMZA', 'AMZN', 'AN', 'ANAB', 'ANAT', 'ANDE', 'ANET', 'ANF', 'ANGI', 'ANGL', 'ANGO', 'ANIK', 'ANIP', 'ANIX', 'ANPC', 'ANSS', 'ANTE', 'ANTM', 'AON', 'AOS', 'AOSL', 'AOUT', 'AP', 'APA', 'APAM', 'APD', 'APDN', 'APEI', 'APEN', 'APG', 'APH', 'API', 'APLE', 'APLS', 'APLT', 'APO', 'APOG', 'APP', 'APPF', 'APPH', 'APPN', 'APPS', 'APRE', 'APRN', 'APT', 'APTO', 'APTS', 'APTV', 'APTX', 'APYX', 'AQB', 'AQMS', 'AQN', 'AQST', 'AQUA', 'AR', 'ARAV', 'ARAY', 'ARC', 'ARCB', 'ARCC', 'ARCH', 'ARCO', 'ARCT', 'ARD', 'ARDX', 'ARE', 'AREC', 'ARES', 'ARGT', 'ARGX', 'ARI', 'ARKF', 'ARKG', 'ARKK', 'ARKO', 'ARKQ', 'ARKW', 'ARKX', 'ARLO', 'ARLP', 'ARMK', 'ARNA', 'ARNC', 'AROC', 'AROW', 'ARQT', 'ARR', 'ARRY', 'ARVL', 'ARVN', 'ARW', 'ARWR', 'ASA', 'ASAI', 'ASAN', 'ASB', 'ASC', 'ASEA', 'ASGN', 'ASH', 'ASHR', 'ASHS', 'ASIX', 'ASLN', 'ASMB', 'ASML', 'ASND', 'ASO', 'ASPN', 'ASPS', 'ASPU', 'ASR', 'ASRT', 'ASRV', 'ASTE', 'ASTR', 'ASTS', 'ASUR', 'ASX', 'ASXC', 'ASYS', 'ATAI', 'ATAX', 'ATCO', 'ATCX', 'ATEC', 'ATEN', 'ATER', 'ATEX', 'ATGE', 'ATH', 'ATHA', 'ATHM', 'ATHX', 'ATI', 'ATIP', 'ATKR', 'ATLC', 'ATMP', 'ATNF', 'ATNI', 'ATNM', 'ATNX', 'ATO', 'ATOM', 'ATOS', 'ATR', 'ATRA', 'ATRC', 'ATRO', 'ATRS', 'ATSG', 'ATUS', 'ATVI', 'AU', 'AUB', 'AUD', 'AUDC', 'AUMN', 'AUPH', 'AUTL', 'AUTO', 'AUY', 'AVA', 'AVAH', 'AVAV', 'AVB', 'AVCT', 'AVD', 'AVDL', 'AVEO', 'AVGO', 'AVID', 'AVIR', 'AVLR', 'AVNS', 'AVNT', 'AVNW', 'AVO', 'AVPT', 'AVRO', 'AVT', 'AVTR', 'AVXL', 'AVY', 'AVYA', 'AWAY', 'AWH', 'AWI', 'AWK', 'AWR', 'AWRE', 'AX', 'AXAS', 'AXDX', 'AXGN', 'AXL', 'AXLA', 'AXNX', 'AXON', 'AXP', 'AXS', 'AXSM', 'AXTA', 'AXTI', 'AXU', 'AY', 'AYI', 'AYRO', 'AYTU', 'AYX', 'AZEK', 'AZN', 'AZO', 'AZPN', 'AZUL', 'AZZ', 'B', 'BA', 'BAB', 'BABA', 'BAC', 'BAH', 'BAL', 'BALY', 'BAM', 'BANC', 'BAND', 'BANF', 'BANR', 'BAP', 'BARK', 'BATRA', 'BATRK', 'BATT', 'BAX', 'BB', 'BBAR', 'BBAX', 'BBBY', 'BBCA', 'BBCP', 'BBD', 'BBDC', 'BBEU', 'BBH', 'BBIG', 'BBIN', 'BBIO', 'BBJP', 'BBL', 'BBSI', 'BBU', 'BBVA', 'BBW', 'BBY', 'BC', 'BCAB', 'BCBP', 'BCC', 'BCDA', 'BCE', 'BCEI', 'BCEL', 'BCI', 'BCLI', 'BCM', 'BCO', 'BCOR', 'BCOV', 'BCPC', 'BCRX', 'BCS', 'BCSF', 'BCYC', 'BDC', 'BDN', 'BDRY', 'BDSI', 'BDSX', 'BDTX', 'BDX', 'BE', 'BEAM', 'BECN', 'BEEM', 'BEKE', 'BELFB', 'BEN', 'BEP', 'BEPC', 'BERY', 'BEST', 'BETZ', 'BF.A', 'BF.B', 'BFAM', 'BFI', 'BFLY', 'BFOR', 'BG', 'BGCP', 'BGFV', 'BGNE', 'BGRY', 'BGS', 'BHC', 'BHE', 'BHF', 'BHG', 'BHLB', 'BHP']




# for group in iter_utils.grouper(BIG_LIST_TICKERS, 2500):
#     thread = threading.Thread(target=function_to_run_in_thread, args=(group,))
#     THREADS.append(thread)
#     thread.start()

# if __name__ == "__main__":

start_main(BIG_LIST_TICKERS)