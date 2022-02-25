from datetime import timedelta, timezone, datetime
from random import randint
from dateutil import tz

from big_algo_framework.big.position_sizing import PositionSizing
from big_algo_framework.strategies.abstract_strategy import *
from strategies.all_strategy_files.child_classes.brokers_ib_child import *
from strategies.all_strategy_files.all_strategies.strategy_functions import *
from strategies.all_strategy_files.data.get_options_data import *
from strategies.ib_orb import config

from ibapi.order_condition import PriceCondition
import time

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
        self.open_action = ""
        self.close_action = ""
        self.con = ()

        self.broker = self.order_dict["broker"]
        self.db = self.order_dict["db"]
        self.ticker = self.order_dict["ticker"]
        self.time_frame = self.order_dict["time_frame"]
        self.entry_time = self.order_dict["entry_time"]
        self.entry = self.order_dict["entry"]
        self.sl = self.order_dict["sl"]
        self.tp1 = self.order_dict["tp1"]
        self.tp2 = self.order_dict["tp2"]
        self.risk = self.order_dict["risk"]
        self.direction = self.order_dict["direction"]

        self.is_close = self.order_dict["is_close"]
        self.sec_type = self.order_dict["sec_type"]
        self.option_action = self.order_dict["option_action"]
        self.option_range = self.order_dict["option_range"]
        self.option_strikes = self.order_dict["option_strikes"]
        self.option_expiry_days = self.order_dict["option_expiry_days"]
        self.currency = self.order_dict["currency"]
        self.exchange = self.order_dict["exchange"]
        self.primary_exchange = self.order_dict["primary_exchange"]
        self.orders_table = self.order_dict["orders_table"]
        self.strategy_table = self.order_dict["strategy_table"]

        self.function = StrategyFunctions(self.db, self.ticker, self.broker, self.order_dict, self.orders_table, self.strategy_table)

    def check_positions(self):
        if self.function.is_exist_positions():
            self.is_position = True

    def check_open_orders(self):
        self.is_order = True

    def before_send_orders(self):
        # Derive gtd time
        entry_time = datetime.datetime.fromtimestamp(self.entry_time/1000).astimezone(tz.gettz('America/New_York'))
        self.gtd = datetime.datetime(year=entry_time.year, month=entry_time.month, day=entry_time.day, hour=11, minute=00, second=0)

        # If we want to trade OPTIONS or else skip!
        if self.sec_type == "OPT":
            options_dict = {
                "days_forward": 10,
                "ticker": self.ticker,
                "strike_count": '',
                "include_quotes": "FALSE",
                "strategy": "SINGLE",
                "interval": '',
                "strike": '',
                "range": self.option_range,
                "volatility": '',
                "underlying_price": '',
                "interest_rate": '',
                "days_to_expiration": '',
                "exp_month": "ALL",
                "option_type": "ALL"
            }

            # Based on the direction, derive the option price and build the order_dict
            if self.direction == "Bullish" and self.option_action == "BUY":
                options_dict["contract_type"] = "CALL"
                options_df = getOptions1(options_dict)

                if self.option_range == "OTM":
                    df = options_df.loc[(options_df['strikePrice'] >= self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                elif self.option_range == "ITM":
                    df = options_df.loc[(options_df['strikePrice'] < self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
                dff = dff.sort_values(by='strikePrice', ascending=True if self.option_range == "OTM" else False)

                self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[self.option_strikes-1]["expirationDate"].strftime("%Y%m%d")
                self.order_dict["strike"] = dff.iloc[self.option_strikes-1]["strikePrice"]
                self.order_dict["right"] = 'C'
                self.order_dict["delta"] = dff.iloc[self.option_strikes-1]["call_delta"]
                self.order_dict["multiplier"] = dff.iloc[-self.option_strikes]["call_multiplier"]

            elif self.direction == "Bullish" and self.option_action == "SELL":
                options_dict["contract_type"] = "PUT"
                options_df = getOptions1(options_dict)

                if self.option_range == "OTM":
                    df = options_df.loc[(options_df['strikePrice'] <= self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                elif self.option_range == "ITM":
                    df = options_df.loc[(options_df['strikePrice'] > self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
                dff = dff.sort_values(by='strikePrice', ascending=False if self.option_range == "OTM" else True)

                self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[self.option_strikes - 1]["expirationDate"].strftime("%Y%m%d")
                self.order_dict["strike"] = dff.iloc[self.option_strikes - 1]["strikePrice"]
                self.order_dict["right"] = 'P'
                self.order_dict["delta"] = dff.iloc[self.option_strikes - 1]["put_delta"]
                self.order_dict["multiplier"] = dff.iloc[-self.option_strikes]["put_multiplier"]

            elif self.direction == "Bearish" and self.option_action == "BUY":
                options_dict["contract_type"] = "PUT"
                options_df = getOptions1(options_dict)

                if self.option_range == "OTM":
                    df = options_df.loc[(options_df['strikePrice'] <= self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                elif self.option_range == "ITM":
                    df = options_df.loc[(options_df['strikePrice'] > self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
                dff = dff.sort_values(by='strikePrice', ascending=True if self.option_range == "OTM" else False)

                self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[-self.option_strikes]["expirationDate"].strftime("%Y%m%d")
                self.order_dict["strike"] = dff.iloc[-self.option_strikes]["strikePrice"]
                self.order_dict["right"] = 'P'
                self.order_dict["delta"] = dff.iloc[-self.option_strikes]["put_delta"]
                self.order_dict["multiplier"] = dff.iloc[-self.option_strikes]["put_multiplier"]

            elif self.direction == "Bearish" and self.option_action == "SELL":
                options_dict["contract_type"] = "CALL"
                options_df = getOptions1(options_dict)

                if self.option_range == "OTM":
                    df = options_df.loc[(options_df['strikePrice'] >= self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                elif self.option_range == "ITM":
                    df = options_df.loc[(options_df['strikePrice'] < self.entry) & (options_df['daysToExpiration'] >= self.option_expiry_days)]
                dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
                dff = dff.sort_values(by='strikePrice', ascending=False if self.option_range == "OTM" else True)

                self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[-self.option_strikes]["expirationDate"].strftime("%Y%m%d")
                self.order_dict["strike"] = dff.iloc[-self.option_strikes]["strikePrice"]
                self.order_dict["right"] = 'C'
                self.order_dict["delta"] = dff.iloc[-self.option_strikes]["call_delta"]
                self.order_dict["multiplier"] = dff.iloc[-self.option_strikes]["call_multiplier"]

            # Build order_dict and get the contract
            self.order_dict["primary_exchange"] = ""
            self.open_action = self.option_action
            self.close_action = "SELL" if self.open_action=="BUY" else "BUY"

        if self.sec_type == "STK":
            if self.direction == "Bullish":
                self.open_action = "BUY"
                self.close_action = "SELL"
            elif self.direction == "Bearish":
                self.open_action = "SELL"
                self.close_action = "BUY"

        # Request the contract for the asset that we are trading
        self.con = self.broker.get_contract(self.order_dict)
        time.sleep(1)

        # Form the dictionary for the underlying and get the contract
        stock_dict = {"ticker": self.ticker,
                      "sec_type": "STK",
                      "currency": self.currency,
                      "exchange": self.exchange,
                      "primary_exchange": self.primary_exchange,
                      "lastTradeDateOrContractMonth": "",
                      "strike": "",
                      "right": "",
                      "multiplier": ""}
        stock_contract = self.broker.get_contract(stock_dict)
        time.sleep(1)
        # Using the underlying contract, request details like mintick
        self.broker.reqContractDetails(randint(0, 10000), stock_contract)
        time.sleep(1)
        stocks_min_tick = self.broker.mintick

        # Adjust the entry/sl/tp to take into account the mintick
        self.entry = self.entry - (self.entry % stocks_min_tick)
        self.tp1 = self.tp1 - (self.tp1 % stocks_min_tick)
        self.tp2 = self.tp2 - (self.tp2 % stocks_min_tick)
        self.sl = self.sl - (self.sl % stocks_min_tick)

        # Position Sizing
        self.order_dict["available_capital"] = float(self.broker.acc_dict["AvailableFunds"])

        if self.sec_type == "OPT":
            self.order_dict["risk_unit"] = abs((self.entry - self.sl) * self.order_dict["delta"])*self.order_dict["multiplier"]
            print("DELTA: ", self.order_dict["delta"])
            print("RISK/CONT: ", self.order_dict["risk_unit"])

            position = PositionSizing(self.order_dict)
            quantity = position.options_quantity(self.order_dict)
        if self.sec_type == "STK":
            self.order_dict["risk_unit"] = abs(self.entry - self.sl)

            position = PositionSizing(self.order_dict)
            quantity = position.stock_quantity(self.order_dict)
        self.quantity1 = quantity

        print("This is the stock conid: ", self.broker.conid)
        # Price/Time conditions
        x = True if self.direction == "Bullish" else False
        y = False if self.direction == "Bullish" else True
        self.parent_order_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, self.broker.conid, stock_contract.exchange, y, self.entry)
        self.sl_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, self.broker.conid, stock_contract.exchange, y, self.sl)
        self.tp_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, self.broker.conid, stock_contract.exchange, x, self.tp1)
        time.sleep(1)

    def check_trailing_stop(self):
        pass

    def start(self):
        self.broker.init_client(self.broker)
        self.function.set_strategy_status()

        if self.is_close == 1:
            print("Closing Period")
            self.function.closeAllPositions()

    def send_orders(self):
        # Parent Order for Order 1
        config.orb_oid = config.orb_oid + 1

        self.order_dict["order_id"] = config.orb_oid
        self.order_dict["mkt_order_id"] = config.orb_oid
        parent_id = self.order_dict["mkt_order_id"]
        self.dashboard_dict[1]["parent_order_id"] = self.order_dict["order_id"]

        self.order_dict["mkt_action"] = self.open_action
        self.order_dict["mkt_quantity"] = self.quantity1
        self.order_dict["mkt_parent_order_id"] = ""
        self.order_dict["mkt_time_in_force"] = "GTD"
        self.order_dict["mkt_good_till_date"] = self.gtd.strftime('%Y%m%d %H:%M:%S')
        self.order_dict["mkt_transmit"] = False

        order = self.broker.get_market_order(self.order_dict)
        order.conditions.append(self.parent_order_price_condition)
        self.broker.send_order(self.order_dict, self.con, order)

        # Stoploss Order for Order 1
        config.orb_oid = config.orb_oid + 1

        self.order_dict["order_id"] = config.orb_oid
        self.order_dict["mkt_order_id"] = config.orb_oid
        self.order_dict["mkt_parent_order_id"] = parent_id
        self.dashboard_dict[1]["stoploss_order_id"] = self.order_dict["order_id"]

        self.order_dict["mkt_action"] = self.close_action
        self.order_dict["mkt_quantity"] = self.quantity1
        self.order_dict["mkt_time_in_force"] = "GTC"
        self.order_dict["mkt_good_till_date"] = ""
        self.order_dict["mkt_transmit"] = False

        order = self.broker.get_market_order(self.order_dict)
        order.conditions.append(self.sl_price_condition)
        self.broker.send_order(self.order_dict, self.con, order)

        # Profit Order for Order 1
        config.orb_oid = config.orb_oid + 1

        self.order_dict["order_id"] = config.orb_oid
        self.order_dict["mkt_order_id"] = config.orb_oid
        self.order_dict["mkt_parent_order_id"] = parent_id
        self.dashboard_dict[1]["profit_order_id"] = self.order_dict["order_id"]

        self.order_dict["mkt_action"] = self.close_action
        self.order_dict["mkt_quantity"] = self.quantity1
        self.order_dict["mkt_time_in_force"] = "GTC"
        self.order_dict["mkt_good_till_date"] = ""
        self.order_dict["mkt_transmit"] = True

        order = self.broker.get_market_order(self.order_dict)
        order.conditions.append(self.tp_price_condition)
        self.broker.send_order(self.order_dict, self.con, order)

    def after_send_orders(self):
        data_list = []
        for x in range(1, 2):
            data = dict(parent_order_id=self.dashboard_dict[x]["parent_order_id"],
                        profit_order_id=self.dashboard_dict[x]["profit_order_id"],
                        stoploss_order_id=self.dashboard_dict[x]["stoploss_order_id"],
                        entry_price=self.entry,
                        sl_price=self.sl,
                        tp1_price=self.tp1,
                        tp2_price=self.tp2,
                        risk_share=self.risk,
                        cont_ticker=self.ticker,

                        timeframe=self.time_frame,
                        date_time=self.entry_time/1000,

                        sec_type=self.sec_type,
                        cont_currency=self.currency,
                        cont_exchange=self.exchange,
                        primary_exchange=self.primary_exchange,
                        stock_conid=self.broker.conid,
                        cont_date=self.order_dict["lastTradeDateOrContractMonth"],
                        strike=self.order_dict["strike"],
                        opt_right=self.order_dict["right"],
                        multiplier=self.order_dict["multiplier"],
                        status='Open')

            data_list.append(data)

        if data_list:
            df = pd.DataFrame(data=data_list)
            df.to_sql(self.strategy_table, self.db, if_exists='append', index=False, method='multi')

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
