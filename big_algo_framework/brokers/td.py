from big_algo_framework.brokers.abstract_broker import Broker
from datetime import datetime
import time
import threading
from sqlalchemy import text
import pandas as pd
from tda.orders.common import OrderType, PriceLinkBasis, PriceLinkType, StopPriceLinkType, first_triggers_second, one_cancels_other
from tda.orders.options import option_buy_to_open_limit, option_sell_to_close_limit, option_sell_to_close_market, option_buy_to_open_market,option_sell_to_open_market, option_buy_to_close_market, option_sell_to_close_limit, option_buy_to_close_limit, option_sell_to_open_limit
from tda.orders.common import Duration, Session
from tda.orders.common import OrderType
from tda.orders.equities import equity_buy_market, equity_buy_limit, equity_sell_market, equity_sell_limit, equity_buy_to_cover_market, equity_sell_short_market, equity_sell_short_limit, equity_buy_to_cover_limit
from tda.orders.generic import OrderBuilder
from tda import auth, orders


class TDA(Broker):
    # Below is the class structure
    # 01. Authentication
    # 02. Asset
    # 03. Prepare/Send Orders
    # 04. Get Orders/Positions
    # 05. Close Orders/Positions
    # 06. Miscellaneous

    def __init__(self, token_path, api_key, redirect_uri, chromedriver_path):
        """Login to TDA"""

        try:
            self.c = auth.client_from_token_file(token_path, api_key)

        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(chromedriver_path) as driver:
                self.c = auth.client_from_login_flow(driver, api_key, redirect_uri, token_path)


    # 01. Authentication
    def connect_broker(self):
        pass


    # 03. Prepare/Send Orders
    def get_market_order(self, order_dict):
        symbol = order_dict["ticker"]
        quantity = order_dict["mkt_quantity"]
        action = order_dict["mkt_action"] # "BUY" or "SELL"
        sec_type = order_dict["mkt_sec_type"] # "STK" or "OPT"
        instruction = order_dict["mkt_instruction"] # "OPEN" or "CLOSE"

        if sec_type == "STK":
            if instruction == "OPEN":
                if action == "BUY":
                    market_order = equity_buy_market(symbol, quantity)
                elif action == "SELL":
                    market_order = equity_sell_short_market(symbol, quantity)
            elif instruction == "CLOSE":
                if action == "BUY":
                    market_order = equity_buy_to_cover_market(symbol, quantity)
                elif action == "SELL":
                     market_order =equity_sell_market(symbol, quantity)

        elif sec_type == "OPT":
            if instruction == "OPEN":
                if action == "BUY":
                    market_order = option_buy_to_open_market(symbol, quantity)
                elif action == "SELL":
                    market_order = option_sell_to_open_market(symbol, quantity)
            elif instruction == "CLOSE":
                if action == "BUY":
                    market_order = option_buy_to_close_market(symbol, quantity)
                elif action == "SELL":
                    market_order = option_sell_to_close_market(symbol, quantity)

        else:
            pass # integrate error handling

        return market_order


    def get_stop_limit_order(self, order_dict):
        symbol = order_dict["ticker"]
        quantity = order_dict["slo_quantity"]
        lmt_price = order_dict["slo_limit_price"]
        stp_price = order_dict["slo_stop_price"]
        tif = order_dict["slo_time_in_force"]
        action = order_dict["slo_action"]
        sec_type = order_dict["slo_sec_type"]
        instruction = order_dict["slo_instruction"]

        if tif == 'GTC':
            tda_tif = orders.common.Duration.GOOD_TILL_CANCEL

        elif tif == 'FOK':
            tda_tif = orders.common.Duration.FILL_OR_KILL

        elif tif == 'DAY':
            tda_tif = orders.common.Duration.DAY

        if sec_type == "STK":
            if instruction == "OPEN":
                if action == "BUY":
                    stop_limit_order = equity_buy_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)
                elif action == "SELL":
                    stop_limit_order = equity_sell_short_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)
            elif instruction == "CLOSE":
                if action == "BUY":
                    stop_limit_order = equity_buy_to_cover_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)
                elif action == "SELL":
                    stop_limit_order = equity_sell_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)

        elif sec_type == "OPT":
            if instruction == "OPEN":
                if action == "BUY":
                    stop_limit_order = option_buy_to_open_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)
                elif action == "SELL":
                    stop_limit_order = option_sell_to_open_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)
            elif instruction == "CLOSE":
                if action == "BUY":
                    stop_limit_order = option_buy_to_close_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)
                elif action == "SELL":
                    stop_limit_order = option_sell_to_close_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).set_stop_price(stp_price).set_duration(tda_tif)

        else:
            pass # integrate error handling

        return stop_limit_order

    def get_limit_order(self, order_dict):
        symbol = order_dict["ticker"]
        quantity = order_dict["lo_quantity"]
        lmt_price = order_dict["lo_limit_price"]
        tif = order_dict["lo_time_in_force"]
        action = order_dict["lo_action"]
        sec_type = order_dict["lo_sec_type"]
        instruction = order_dict["lo_instruction"]

        if tif == 'GTC':
            tda_tif = orders.common.Duration.GOOD_TILL_CANCEL

        elif tif == 'FOK':
            tda_tif = orders.common.Duration.FILL_OR_KILL

        elif tif == 'DAY':
            tda_tif = orders.common.Duration.DAY

        if sec_type == "STK":
            if instruction == "OPEN":
                if action == "BUY":
                    limit_order = equity_buy_limit(symbol, quantity, lmt_price).set_duration(tda_tif)
                elif action == "SELL":
                    limit_order = equity_sell_short_limit(symbol, quantity, lmt_price).set_duration(tda_tif)
            elif instruction == "CLOSE":
                if action == "BUY":
                    limit_order = equity_buy_to_cover_limit(symbol, quantity, lmt_price).set_duration(tda_tif)
                elif action == "SELL":
                    limit_order = equity_sell_limit(symbol, quantity, lmt_price).set_duration(tda_tif)

        elif sec_type == "OPT":
            if instruction == "OPEN":
                if action == "BUY":
                    limit_order = option_buy_to_open_limit(symbol, quantity, lmt_price).set_duration(tda_tif)
                elif action == "SELL":
                    limit_order = option_sell_to_open_limit(symbol, quantity, lmt_price).set_duration(tda_tif)
            elif instruction == "CLOSE":
                if action == "BUY":
                    limit_order = option_buy_to_close_limit(symbol, quantity, lmt_price).set_duration(tda_tif)
                elif action == "SELL":
                    limit_order = option_sell_to_close_limit(symbol, quantity, lmt_price).set_duration(tda_tif)

        else:
            pass # integrate error handling

        return limit_order

    def get_stop_order(self, order_dict):
        pass

    def get_oto_order(self, first_order, second_order):
        oto = first_triggers_second(first_order, second_order)

        return oto

    def get_oco_order(self, first_order, second_order):
        oco = one_cancels_other(first_order, second_order)

        return oco

    #TODO: Naga check how to remove send_oto_order/send_oco_order from abstract class
    def send_oto_order(self):
        pass

    def send_oco_order(self):
        pass

    def send_order(self, order_dict, order):
        try:
            res = self.c.place_order(order_dict["account_no"], order)
                    # HTTP status Code
            print("Status:", res.status_code, "--->", datetime.now())
            try:
                # Actual TDA response. Not applicable to every order
                print(res.json())
            except:
                pass
            if res.status_code == 201:
                print('Order/s Sent!!!')
        except Exception as exc:
            print(f'exception in order: {str(exc)}')

    # 04. Get Orders/Positions
    def get_all_orders(self, order_dict):
        fields = self.c.Account.Fields('orders')
        response = self.c.get_account(order_dict["account_no"], fields = fields)

        return response.json()

    def get_order(self):
        pass


    def get_all_positions(self, order_dict):
        fields = self.c.Account.Fields('positions')
        response = self.c.get_account(order_dict["account_no"], fields = fields)

        return response.json()

    def get_position(self):
        pass

    # 05. Close Orders/Positions
    def cancel_order(self, order_id, order_dict):
        self.c.cancel_order(order_id, order_dict["account_no"])

    def cancel_all_orders(self, order_dict):
        open_orders = self.get_all_orders(order_dict)
        orders = open_orders["securitiesAccount"]["orderStrategies"]

        for i in range(0, len(orders)):
            # print("Ticker: ", orders[i]["orderLegCollection"][0]["instrument"]["symbol"])
            # print("Quantity: ", orders[i]["orderLegCollection"][0]["quantity"])
            order_id = orders[i]["orderId"]
            self.cancel_order(order_id, order_dict)

    def replace_order(self, order_id, order, order_dict):
        self.c.replace_order(order_dict["account_no"], order_id, order)

    def close_position(self, order_dict):
        mkt_order = self.get_market_order(order_dict)
        self.send_order(order_dict, mkt_order)

    def close_all_positions(self, order_dict):
        open_positions = self.get_all_positions(order_dict)
        positions = open_positions["securitiesAccount"]["positions"]

        for i in range(0, len(positions)):
            ticker = positions[i]["instrument"]["symbol"]
            long_quantity = positions[i]["longQuantity"]
            short_quantity = positions[i]["shortQuantity"]

            if long_quantity > 0:
                order_dict =  {"ticker": ticker, "mkt_quantity": long_quantity, "mkt_action":"SELL", "account_no": order_dict["account_no"]}

            if short_quantity > 0:
                order_dict =  {"ticker": ticker, "mkt_quantity": short_quantity, "mkt_action":"BUY", "account_no": order_dict["account_no"]}

            self.close_position(order_dict)

# TODO: Get account balances for position sizing and risk...
# get quotes (STK or OPT Symbols)... Client.get_quotes(symbols)
