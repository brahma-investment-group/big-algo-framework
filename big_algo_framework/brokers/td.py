from big_algo_framework.brokers.abstract_broker import Broker
from big_algo_framework.big.helper import truncate
from datetime import datetime
from tda.orders.generic import OrderBuilder
from tda.orders.common import first_triggers_second, one_cancels_other
from tda.auth import client_from_token_file, client_from_login_flow

class TDA(Broker):
    def __init__(self, token_path, api_key, redirect_uri, chromedriver_path):
        try:
            self.c = client_from_token_file(token_path, api_key)

        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(chromedriver_path) as driver:
                self.c = client_from_login_flow(driver, api_key, redirect_uri, token_path)

    # Prepare/Send Orders
    def get_market_order(self, symbol: str, quantity: int, sec_type, action: str = 'BUY', session: str = 'NORMAL', duration: str = 'DAY'):
        if sec_type == "STK":
            return OrderBuilder(enforce_enums=False)\
                .set_order_type('MARKET') \
                .set_session(session.upper()) \
                .set_duration(duration.upper()) \
                .set_order_strategy_type('SINGLE') \
                .add_equity_leg(action.upper(), symbol.upper(), quantity)

        elif sec_type == "OPT":
            pass

    def get_stop_limit_order(self, symbol: str, quantity: int, sec_type, stop_price: float, limit_price: float, instr: str = 'BUY',
                          session: str = 'NORMAL', duration: str = 'DAY', stop_type: str = 'MARK'):
        if sec_type == "STK":
            return OrderBuilder(enforce_enums=False) \
                .set_order_type('STOP_LIMIT') \
                .set_session(session.upper()) \
                .set_duration(duration.upper()) \
                .set_order_strategy_type('SINGLE') \
                .set_stop_price(stop_price) \
                .set_price(limit_price) \
                .set_stop_type(stop_type.upper()) \
                .add_equity_leg(instr.upper(), symbol.upper(), quantity)

        elif sec_type == "OPT":
            pass

    def get_limit_order(self, symbol: str, quantity: int, sec_type, limit_price: float, instr: str = 'BUY',
                        session: str = 'NORMAL', duration: str = 'DAY'):
        if sec_type == "STK":
            return OrderBuilder(enforce_enums=False)\
                .set_order_type('LIMIT') \
                .set_session(session.upper()) \
                .set_duration(duration.upper()) \
                .set_order_strategy_type('SINGLE') \
                .set_price(limit_price) \
                .add_equity_leg(instr.upper(), symbol.upper(), quantity)

        elif sec_type == "OPT":
            pass

    def get_stop_order(self, symbol: str, quantity: int, sec_type, stop_price: float, instr: str = 'BUY',
                       stop_type: str = 'MARK', session: str = 'NORMAL', duration: str = 'DAY'):
        if sec_type == "STK":
            return OrderBuilder(enforce_enums=False) \
                .set_order_type('STOP') \
                .set_session(session.upper()) \
                .set_duration(duration.upper()) \
                .set_order_strategy_type('SINGLE') \
                .set_stop_price(stop_price) \
                .set_stop_type(stop_type.upper()) \
                .add_equity_leg(instr.upper(), symbol.upper(), quantity)

        elif sec_type == "OPT":
            pass

    def get_trailing_stop_order(self, symbol: str, quantity: int, sec_type, trailing_offset: float,
                             instr: str = 'BUY', stop_price_link_type: str = 'PERCENT', stop_price_link_basis: str = 'MARK',
                             stop_type: str = 'MARK', session: str = 'NORMAL', duration: str = 'DAY'):

        if stop_price_link_type == 'PERCENT' and (float(trailing_offset) < 1 or float(trailing_offset) > 99):
            raise ValueError('For percent trail, the offset must be between 1 to 99')

        if sec_type == "STK":
            return OrderBuilder(enforce_enums=False) \
                .set_order_type('TRAILING_STOP') \
                .set_quantity(quantity) \
                .set_duration(duration.upper()) \
                .set_session(session.upper()) \
                .set_order_strategy_type('SINGLE') \
                .set_stop_price_link_basis(stop_price_link_basis.upper()) \
                .set_stop_price_link_type(stop_price_link_type.upper()) \
                .set_stop_price_offset(trailing_offset) \
                .set_stop_type(stop_type.upper()) \
                .add_equity_leg(instr.upper(), symbol.upper(), quantity)

        elif sec_type == "OPT":
            pass

    def get_trailing_stop_limit_order(self, symbol: str, quantity: int, sec_type, trailing_offset: float,
                                   limit_price: float, instr: str = 'BUY', stop_price_link_type: str = 'PERCENT',
                                   stop_price_link_basis: str = 'MARK', stop_type: str = 'MARK', session: str = 'NORMAL',
                                   duration: str = 'DAY'):

        if stop_price_link_type == 'PERCENT' and (float(trailing_offset) < 1 or float(trailing_offset) > 99):
            raise ValueError('For percent trail, the offset must be between 1 to 99')

        if sec_type == "STK":
            return OrderBuilder(enforce_enums=False) \
                .set_order_type('TRAILING_STOP_LIMIT') \
                .set_quantity(quantity) \
                .set_duration(duration.upper()) \
                .set_session(session.upper()) \
                .set_order_strategy_type('SINGLE') \
                .set_stop_price_link_basis(stop_price_link_basis.upper()) \
                .set_stop_price_link_type(stop_price_link_type.upper()) \
                .set_stop_price_offset(trailing_offset) \
                .set_stop_type(stop_type.upper()) \
                .set_price(limit_price) \
                .add_equity_leg(instr.upper(), symbol.upper(), quantity)

        elif sec_type == "OPT":
            pass

    def get_oto_order(self, first_order, second_order):
        oto = first_triggers_second(first_order, second_order)
        return oto

    def get_oco_order(self, first_order, second_order):
        oco = one_cancels_other(first_order, second_order)
        return oco

    def send_order(self, account_no, order):
        try:
            res = self.c.place_order(account_no, order)
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
    def get_order_by_ticker(self, ticker, account_no):
        all_orders = self.get_all_orders(account_no)
        open_orders = []

        for i in all_orders['securitiesAccount']['orderStrategies']:
            open_status_list = ['AWAITING_PARENT_ORDER', 'AWAITING_CONDITION', 'AWAITING_MANUAL_REVIEW', 'ACCEPTED',
                   'AWAITING_UR_OUT', 'PENDING_ACTIVATION', 'QUEUED', 'WORKING']

            try:
                symbol = i['orderLegCollection'][0]['instrument']['symbol']
                underlying_symbol = symbol.split("_")
                status = i['status']

                if underlying_symbol[0] == ticker and status in open_status_list:
                    open_orders.append(i['orderLegCollection'][0])
            except:
                print("ERROR in get_order_by_ticker()")

        return open_orders

    def get_all_orders(self, account_no):
        fields = self.c.Account.Fields('orders')
        response = self.c.get_account(account_no, fields = fields)
        return response.json()

    def get_position_by_ticker(self, ticker, account_no):
        all_positions = self.get_all_positions(account_no)
        open_positions = []

        for i in all_positions['securitiesAccount']['positions']:
            try:
                symbol = i['instrument']['symbol']
                underlying_symbol = symbol.split("_")

                if underlying_symbol[0] == ticker:
                    open_positions.append(i['instrument'])

            except:
                print("ERROR in get_position_by_ticker()")

        return open_positions

    def get_all_positions(self, account_no):
        fields = self.c.Account.Fields('positions')
        response = self.c.get_account(account_no, fields = fields)
        return response.json()

    # Cancel Orders/Close Positions
    def cancel_order(self, order_id, account_no):
        self.c.cancel_order(order_id, account_no)

    def cancel_all_orders(self, account_no):
        open_orders = self.get_all_orders(account_no)
        orders = open_orders["securitiesAccount"]["orderStrategies"]

        for i in range(0, len(orders)):
            order_id = orders[i]["orderId"]
            self.cancel_order(order_id, account_no)

    def replace_order(self, account_no, order_id, order):
        self.c.replace_order(account_no, order_id, order)

    def close_position(self, account_no, symbol: str, quantity: int, sec_type, action: str = 'BUY', session: str = 'NORMAL', duration: str = 'DAY'):
        mkt_order = self.get_market_order(symbol, quantity, sec_type, action, session, duration)
        self.send_order(account_no, mkt_order)

    def close_all_positions(self, account_no):
        open_positions = self.get_all_positions(account_no)
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
                self.close_position(account_no, ticker, long_quantity, sec_type, "SELL", 'NORMAL', 'DAY')
            if short_quantity > 0:
                self.close_position(account_no, ticker, short_quantity, sec_type, "BUY", 'NORMAL', 'DAY')
