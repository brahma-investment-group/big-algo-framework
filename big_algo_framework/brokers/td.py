from big_algo_framework.brokers.abstract_broker import Broker
from big_algo_framework.big.helper import truncate
from datetime import datetime
from tda.orders.common import StopPriceLinkType, StopPriceLinkBasis, first_triggers_second, one_cancels_other, OrderType, Duration
from tda.orders.options import option_buy_to_open_limit, option_sell_to_close_limit, option_sell_to_close_market, option_buy_to_open_market,option_sell_to_open_market, option_buy_to_close_market, option_buy_to_close_limit, option_sell_to_open_limit
from tda.orders.equities import equity_buy_market, equity_buy_limit, equity_sell_market, equity_sell_limit, equity_buy_to_cover_market, equity_sell_short_market, equity_sell_short_limit, equity_buy_to_cover_limit
from tda.auth import client_from_token_file, client_from_login_flow

class TDA(Broker):
    def __init__(self, token_path, api_key, redirect_uri, chromedriver_path):
        try:
            self.c = client_from_token_file(token_path, api_key)

        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(chromedriver_path) as driver:
                self.c = client_from_login_flow(driver, api_key, redirect_uri, token_path)

    # Authentication
    def connect_broker(self):
        pass

    # Prepare/Send Orders
    def get_market_order(self, order_dict):
        symbol = order_dict["ticker"]
        quantity = order_dict["mkt_quantity"]
        action = order_dict["mkt_action"]
        sec_type = order_dict["mkt_sec_type"]
        instruction = order_dict["mkt_instruction"]

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

        return market_order

    def get_stop_limit_order(self, order_dict, digits=2):
        symbol = order_dict["ticker"]
        quantity = order_dict["slo_quantity"]
        lmt_price = truncate(order_dict["slo_limit_price"], digits)
        stp_price = order_dict["slo_stop_price"]
        tif = order_dict["slo_time_in_force"]
        action = order_dict["slo_action"]
        sec_type = order_dict["slo_sec_type"]
        instruction = order_dict["slo_instruction"]

        if tif == 'GTC':
            tda_tif = Duration.GOOD_TILL_CANCEL
        elif tif == 'FOK':
            tda_tif = Duration.FILL_OR_KILL
        elif tif == 'DAY':
            tda_tif = Duration.DAY

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

        return stop_limit_order

    def get_limit_order(self, order_dict, digits=2):
        symbol = order_dict["ticker"]
        quantity = order_dict["lo_quantity"]
        lmt_price = truncate(order_dict["lo_limit_price"], digits)
        tif = order_dict["lo_time_in_force"]
        action = order_dict["lo_action"]
        sec_type = order_dict["lo_sec_type"]
        instruction = order_dict["lo_instruction"]

        if tif == 'GTC':
            tda_tif = Duration.GOOD_TILL_CANCEL
        elif tif == 'FOK':
            tda_tif = Duration.FILL_OR_KILL
        elif tif == 'DAY':
            tda_tif = Duration.DAY

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

        return limit_order

    def get_stop_order(self, order_dict):
        pass

    def get_trailing_stop_order(self, order_dict, digits=2):
        symbol = order_dict["ticker"]
        quantity = order_dict["tr_stop_quantity"]
        tif = order_dict["tr_stop_time_in_force"]
        action = order_dict["tr_stop_action"]
        sec_type = order_dict["tr_stop_sec_type"]
        instruction = order_dict["tr_stop_instruction"]

        if str.upper(order_dict["price_link_type"]) == "PERCENT":
            price_link = StopPriceLinkType.PERCENT
            offset = truncate(order_dict["tr_stop_percent"], 1)
        elif str.upper(order_dict["price_link_type"]) == "VALUE":
            price_link = StopPriceLinkType.VALUE
            offset = truncate(order_dict["tr_stop_price"], digits)

        if tif == 'GTC':
            tda_tif = Duration.GOOD_TILL_CANCEL
        elif tif == 'FOK':
            tda_tif = Duration.FILL_OR_KILL
        elif tif == 'DAY':
            tda_tif = Duration.DAY
        if tif == 'GTC':
            tda_tif = Duration.GOOD_TILL_CANCEL

        if sec_type == "STK":
            if instruction == "OPEN":
                if action == "BUY":
                    trailing_stop_order = equity_buy_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)
                elif action == "SELL":
                    trailing_stop_order = equity_sell_short_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)
            elif instruction == "CLOSE":
                if action == "BUY":
                    trailing_stop_order = equity_buy_to_cover_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)
                elif action == "SELL":
                    trailing_stop_order = equity_sell_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)

        elif sec_type == "OPT":
            if instruction == "OPEN":
                if action == "BUY":
                    trailing_stop_order = option_buy_to_open_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)
                elif action == "SELL":
                    trailing_stop_order = option_sell_to_open_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)
            elif instruction == "CLOSE":
                if action == "BUY":
                    trailing_stop_order = option_buy_to_close_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)
                elif action == "SELL":
                    trailing_stop_order = option_sell_to_close_market(symbol, quantity).set_order_type(OrderType.TRAILING_STOP).set_stop_price_link_basis(StopPriceLinkBasis.MARK).set_stop_price_link_type(price_link).set_stop_price_offset(offset).set_duration(tda_tif)

        return trailing_stop_order

    def get_oto_order(self, first_order, second_order):
        oto = first_triggers_second(first_order, second_order)
        return oto

    def get_oco_order(self, first_order, second_order):
        oco = one_cancels_other(first_order, second_order)
        return oco

    def send_order(self, order_dict, order):
        try:
            res = self.c.place_order(order_dict["account_no"], order)
            print("Status:", res.status_code, "--->", datetime.now())

            try:
                print(res.json())
            except:
                pass

            if res.status_code == 201:
                print('Order/s Sent!!!')

        except Exception as exc:
            print(f'exception in order: {str(exc)}')

    # Get Orders/Positions
    def get_order_by_ticker(self, order_dict):
        all_orders = self.get_all_orders(order_dict)
        open_orders = []

        for i in all_orders['securitiesAccount']['orderStrategies']:
            open_status_list = ['AWAITING_PARENT_ORDER', 'AWAITING_CONDITION', 'AWAITING_MANUAL_REVIEW', 'ACCEPTED',
                   'AWAITING_UR_OUT', 'PENDING_ACTIVATION', 'QUEUED', 'WORKING']

            try:
                symbol = i['orderLegCollection'][0]['instrument']['symbol']
                underlying_symbol = symbol.split("_")
                status = i['status']

                if underlying_symbol[0] == order_dict["ticker"] and status in open_status_list:
                    open_orders.append(i['orderLegCollection'][0])
            except:
                print("ERROR in get_order_by_ticker()")

        return open_orders

    def get_all_orders(self, order_dict):
        fields = self.c.Account.Fields('orders')
        response = self.c.get_account(order_dict["account_no"], fields = fields)
        return response.json()

    def get_position_by_ticker(self, order_dict):
        all_positions = self.get_all_positions(order_dict)
        open_positions = []

        for i in all_positions['securitiesAccount']['positions']:
            try:
                symbol = i['instrument']['symbol']
                underlying_symbol = symbol.split("_")

                if underlying_symbol[0] == order_dict["ticker"]:
                    open_positions.append(i['instrument'])

            except:
                print("ERROR in get_position_by_ticker()")

        return open_positions

    def get_all_positions(self, order_dict):
        fields = self.c.Account.Fields('positions')
        response = self.c.get_account(order_dict["account_no"], fields = fields)
        return response.json()

    # Cancel Orders/Close Positions
    def cancel_order(self, order_id, order_dict):
        self.c.cancel_order(order_id, order_dict["account_no"])

    def cancel_all_orders(self, order_dict):
        open_orders = self.get_all_orders(order_dict)
        orders = open_orders["securitiesAccount"]["orderStrategies"]

        for i in range(0, len(orders)):
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
            sec_type = positions[i]["instrument"]["assetType"]
            long_quantity = positions[i]["longQuantity"]
            short_quantity = positions[i]["shortQuantity"]

            if sec_type == "EQUITY":
                sec_type = "STK"
            elif sec_type == "OPTION":
                sec_type = "OPT"

            if long_quantity > 0:
                position_dict =  {"ticker": ticker, "mkt_sec_type": sec_type, "mkt_quantity": long_quantity, "mkt_action":"SELL", "mkt_instruction": "CLOSE", "account_no": order_dict["account_no"]}

            if short_quantity > 0:
                position_dict =  {"ticker": ticker, "mkt_sec_type": sec_type, "mkt_quantity": short_quantity, "mkt_action":"BUY", "mkt_instruction": "CLOSE", "account_no": order_dict["account_no"]}

            self.close_position(position_dict)


