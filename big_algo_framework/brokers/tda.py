from big_algo_framework.brokers.abstract_broker import Broker
import time
import threading
from sqlalchemy import text
import pandas as pd
from tda import auth, orders
from tda.orders.common import OrderType, PriceLinkBasis, PriceLinkType, StopPriceLinkType, first_triggers_second, one_cancels_other
from tda.orders.options import option_buy_to_open_limit, option_sell_to_close_limit, option_sell_to_close_market
from tda.orders.common import Duration, Session
from tda.orders.common import OrderType
from tda.orders.equities import equity_buy_market, equity_buy_limit, equity_sell_market, equity_sell_limit
from tda.orders.generic import OrderBuilder


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


    # Authentication
    def connect_broker(self):
        pass


    # Prepare Orders
    def get_market_order(self, order_dict):
        symbol = order_dict["ticker"]
        quantity = order_dict["mkt_quantity"]
        action = order_dict["mkt_action"]

        if action == 'BUY':
            market_order = equity_buy_market(symbol, quantity)

        else:
            market_order = equity_sell_market(symbol, quantity)

        return market_order


    def get_stop_limit_order(self, order_dict):
        symbol = order_dict["ticker"]
        quantity = order_dict["slo_quantity"]
        lmt_price = order_dict["slo_limit_price"]
        stp_price = order_dict["slo_stop_price"]
        tif = order_dict["slo_time_in_force"]
        action = order_dict["slo_action"]

        if tif == 'GTC':
            tda_tif = orders.common.Duration.GOOD_TILL_CANCEL

        elif tif == 'FOK':
            tda_tif = orders.common.Duration.FILL_OR_KILL

        else:
            tda_tif = orders.common.Duration.DAY

        if action == 'BUY':
            stop_limit_order = equity_buy_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).clear_price().set_stop_price(stp_price).set_duration(tda_tif)

        else:
            stop_limit_order = equity_sell_limit(symbol, quantity, lmt_price).set_order_type(OrderType.STOP_LIMIT).clear_price().set_stop_price(stp_price).set_duration(tda_tif)

        return stop_limit_order

    def get_limit_order(self, order_dict):
        symbol = order_dict["ticker"]
        quantity = order_dict["lo_quantity"]
        lmt_price = order_dict["lo_limit_price"]
        tif = order_dict["lo_time_in_force"]
        action = order_dict["lo_action"]

        if tif == 'GTC':
            tda_tif = orders.common.Duration.GOOD_TILL_CANCEL

        elif tif == 'FOK':
            tda_tif = orders.common.Duration.FILL_OR_KILL

        else:
            tda_tif = orders.common.Duration.DAY

        if action == 'BUY':
            limit_order = equity_buy_limit(symbol, quantity, lmt_price).set_duration(tda_tif)

        else:
            limit_order = equity_sell_limit(symbol, quantity, lmt_price).set_duration(tda_tif)


        return limit_order

    def get_stop_order(self, order_dict):
        pass

    # Send Orders
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
        self.c.place_order(order_dict["account_no"], order)

    # Get Orders/Positions
    def get_all_order(self, order_dict):
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

    # Cancel Orders/Close Positions
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
        self.send_order(mkt_order)

    def close_all_positions(self, order_dict):
        open_positions = self.get_all_positions(order_dict)
        positions = open_positions["securitiesAccount"]["positions"]

        for i in range(0, len(positions)):
            ticker = positions[i]["instrument"]["symbol"]
            long_quantity = positions[i]["longQuantity"]
            short_quantity = positions[i]["shortQuantity"]

            if long_quantity > 0:
                order_dict =  {"ticker": ticker, "quantity": long_quantity}

            if short_quantity > 0:
                order_dict =  {"ticker": ticker, "quantity": short_quantity}

            self.close_position(order_dict)
