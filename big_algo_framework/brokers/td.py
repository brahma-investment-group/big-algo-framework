from big_algo_framework.brokers.abstract_broker import Broker
from big_algo_framework.big.helper import truncate
from datetime import datetime, date
from tda.orders.generic import OrderBuilder
from tda.auth import client_from_token_file, client_from_login_flow
from polygon import build_option_symbol

class TDA(Broker):
    def __init__(self, token_path, api_key, redirect_uri, chromedriver_path):
        try:
            self.c = client_from_token_file(token_path, api_key)

        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(chromedriver_path) as driver:
                self.c = client_from_login_flow(driver, api_key, redirect_uri, token_path)

    # Asset
    async def get_stock_contract(self, symbol: str = '', exchange: str = 'SMART', currency: str = '', primaryExchange: str = ''):
        """
            Returns a stock contract.

            :param symbol: The symbol.
            :param exchange: Not used.
            :param currency: Not used.
            :param primaryExchange: Not used.
        """

        stock_contract = symbol

        return stock_contract

    async def get_options_contract(self, symbol: str = '', expiry_date: int = '', expiry_month: int = '' ,
                                   expiry_year: int = '', strike: float = 0.0, right: str = '', exchange: str = 'SMART',
                                   multiplier: str = '100', currency: str = ''):
        """
            Returns an option contract.

            :param symbol: The symbol.
            :param expiry_date: The expiration date for the contract.
            :param expiry_month: The expiration month for the contract.
            :param expiry_year: The expiration year for the contract.
            :param strike: The strike price.
            :param right: The right of the option. Possible options are "C", "P"
            :param exchange: Not used.
            :param multiplier: Not used.
            :param currency: Not used.
        """

        option_contract = build_option_symbol(symbol, date(expiry_year, expiry_month, expiry_date), right, strike, _format='tda')

        return option_contract

    # Prepare/Send Orders
    async def get_market_order(self, symbol: str, quantity: int, sec_type: str, action: str = 'BUY', instruction: str = 'OPEN',
                               session: str = 'NORMAL', duration: str = 'DAY', good_till_cancel_start_time='',
                               good_till_cancel_end_time='', good_till_date='', good_after_time='', parent_id: int = '',
                               account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a market order. This doesn't actually submit an order. To submit order, use ``send_order`` function.
    
            :param symbol: The ticker symbol.
            :param quantity: The quantity/amount.
            :param sec_type: The security type Possible values are "STK", "OPT".
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param good_till_cancel_start_time: Not used.
            :param good_till_cancel_end_time: Not used.
            :param good_till_date: Not used.
            :param good_after_time: Not used.
            :param parent_id: Not used.
            :param account_no: Not used.
            :param transmit: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        order = OrderBuilder(enforce_enums=False) \
            .set_order_type('MARKET') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_strategy_type('SINGLE')

        if sec_type == "STK":
            return order.add_equity_leg(action.upper(), symbol.upper(), quantity)
        elif sec_type == "OPT":
            action = action.upper() + "_TO_" + instruction.upper()
            return order.add_option_leg(action.upper(), symbol.upper(), quantity)

    async def get_stop_limit_order(self, symbol: str, quantity: int, sec_type: str, stop_price: float,
                                   limit_price: float, digits: int = 2, trigger_method: str = 'LAST',
                                   action: str = 'BUY', instruction: str = 'OPEN', session: str = 'NORMAL', duration: str = 'DAY', good_till_cancel_start_time='',
                                   good_till_cancel_end_time='', good_till_date='', good_after_time='',
                                   parent_id: int = '', account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a stop limit order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The ticker symbol.
            :param quantity: The quantity/amount.
            :param sec_type: The security type Possible values are "STK", "OPT".
            :param stop_price: The stop price for the order.
            :param limit_price: The limit price for the order.
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param good_till_cancel_start_time: Not used.
            :param good_till_cancel_end_time: Not used.
            :param good_till_date: Not used.
            :param good_after_time: Not used.
            :param parent_id: Not used.
            :param account_no: Not used.
            :param transmit: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        order = OrderBuilder(enforce_enums=False) \
            .set_order_type('STOP_LIMIT') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_strategy_type('SINGLE') \
            .set_stop_price(truncate(stop_price, digits)) \
            .set_price(truncate(limit_price, digits)) \
            .set_stop_type(trigger_method.upper())

        if sec_type == "STK":
            return order.add_equity_leg(action.upper(), symbol.upper(), quantity)
        elif sec_type == "OPT":
            action = action.upper() + "_TO_" + instruction.upper()
            return order.add_option_leg(action.upper(), symbol.upper(), quantity)

    async def get_limit_order(self, symbol: str, quantity: int, sec_type: str, limit_price: float, digits: int = 2,
                              action: str = 'BUY', instruction: str = 'OPEN', session: str = 'NORMAL', duration: str = 'DAY',
                              good_till_cancel_start_time='', good_till_cancel_end_time='', good_till_date='',
                              good_after_time='', parent_id: int = '', account_no: str = '',
                              transmit: bool = True, **kwargs):
        """
            Returns a limit order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The ticker symbol.
            :param quantity: The quantity/amount.
            :param sec_type: The security type Possible values are "STK", "OPT".
            :param limit_price: The limit price for the order.
            :param digits: The number of digits to which the price should be truncated.
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param good_till_cancel_start_time: Not used.
            :param good_till_cancel_end_time: Not used.
            :param good_till_date: Not used.
            :param good_after_time: Not used.
            :param parent_id: Not used.
            :param account_no: Not used.
            :param transmit: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        order = OrderBuilder(enforce_enums=False) \
            .set_order_type('LIMIT') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_strategy_type('SINGLE') \
            .set_price(truncate(limit_price, digits)) \

        if sec_type == "STK":
            return order.add_equity_leg(action.upper(), symbol.upper(), quantity)
        elif sec_type == "OPT":
            action = action.upper() + "_TO_" + instruction.upper()
            return order.add_option_leg(action.upper(), symbol.upper(), quantity)

    async def get_stop_order(self, symbol: str, quantity: int, sec_type: str, stop_price: float,
                             digits: int = 2, trigger_method: str = 'LAST', action: str = 'BUY', instruction: str = 'OPEN',
                             session: str = 'NORMAL', duration: str = 'DAY', good_till_cancel_start_time='',
                             good_till_cancel_end_time='', good_till_date='', good_after_time='',
                             parent_id: int = '', account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a stop order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The ticker symbol.
            :param quantity: The quantity/amount.
            :param sec_type: The security type Possible values are "STK", "OPT".
            :param stop_price: The stop price for the order.
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param good_till_cancel_start_time: Not used.
            :param good_till_cancel_end_time: Not used.
            :param good_till_date: Not used.
            :param good_after_time: Not used.
            :param parent_id: Not used.
            :param account_no: Not used.
            :param transmit: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        order = OrderBuilder(enforce_enums=False) \
            .set_order_type('STOP') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_strategy_type('SINGLE') \
            .set_stop_price(truncate(stop_price, digits)) \
            .set_stop_type(trigger_method.upper())

        if sec_type == "STK":
            return order.add_equity_leg(action.upper(), symbol.upper(), quantity)
        elif sec_type == "OPT":
            action = action.upper() + "_TO_" + instruction.upper()
            return order.add_option_leg(action.upper(), symbol.upper(), quantity)

    async def get_trailing_stop_order(self, symbol: str, quantity: int, sec_type: str, trail_type: str,
                                      trail_amount: float, trail_stop: float = '', digits: int = 2,
                                      trigger_method: str = 'LAST', stop_price_link_basis: str = 'LAST',
                                      action: str = 'BUY', instruction: str = 'OPEN', session: str = 'NORMAL', duration: str = 'DAY',
                                      good_till_cancel_start_time='', good_till_cancel_end_time='',
                                      good_till_date='', good_after_time='', parent_id: int = '',
                                      account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a trailing stop order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The ticker symbol.
            :param quantity: The quantity/amount.
            :param sec_type: The security type Possible values are "STK", "OPT".
            :param trail_type: The type of trailing stop. Possible values are "PERCENTAGE", "AMOUNT".
            :param trail_amount: The amount to trail the stop by.
            :param trail_stop: Not used.
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param stop_price_link_basis: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param good_till_cancel_start_time: Not used.
            :param good_till_cancel_end_time: Not used.
            :param good_till_date: Not used.
            :param good_after_time: Not used.
            :param parent_id: Not used.
            :param account_no: Not used.
            :param transmit: Not used.
        """


        if str.upper(trail_type) == "AMOUNT":
            trail_type = "VALUE"
            if float(trail_amount) < 0:
                raise ValueError('The trail amount must be greater than 0')

        elif str.upper(trail_type) == "PERCENTAGE":
            trail_type = "PERCENT"
            if float(trail_amount) < 1 or float(trail_amount) > 99:
                raise ValueError('The trail amount must be between 1 to 99')

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        order = OrderBuilder(enforce_enums=False) \
            .set_order_type('TRAILING_STOP') \
            .set_quantity(quantity) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_session(session.upper()) \
            .set_order_strategy_type('SINGLE') \
            .set_stop_price_link_basis(stop_price_link_basis.upper()) \
            .set_stop_price_link_type(trail_type.upper()) \
            .set_stop_price_offset(truncate(trail_amount, digits)) \
            .set_stop_type(trigger_method.upper())

        if sec_type == "STK":
            return order.add_equity_leg(action.upper(), symbol.upper(), quantity)
        elif sec_type == "OPT":
            action = action.upper() + "_TO_" + instruction.upper()
            return order.add_option_leg(action.upper(), symbol.upper(), quantity)

    async def get_trailing_stop_limit_order(self, symbol: str, quantity: int, sec_type: str, trail_type: str,
                                            trail_amount: float, trail_stop: float = '', trail_limit: float = '',
                                            limit_price_offset: float = '', digits: int = 2,
                                            trigger_method: str = 'LAST', stop_price_link_basis: str = 'LAST',
                                            action: str = 'BUY', instruction: str = 'OPEN', session: str = 'NORMAL', duration: str = 'DAY',
                                            good_till_cancel_start_time='', good_till_cancel_end_time='',
                                            good_till_date='', good_after_time='', parent_id: int = '',
                                            account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a trailing stop limit order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The ticker symbol.
            :param quantity: The quantity/amount.
            :param sec_type: The security type Possible values are "STK", "OPT".
            :param trail_type: The type of trailing stop. Possible values are "PERCENTAGE", "AMOUNT".
            :param trail_amount: The amount to trail the stop by.
            :param trail_stop: Not used.
            :param trail_limit:
            :param limit_price_offset: Not used.
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param stop_price_link_basis: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param good_till_cancel_start_time: Not used.
            :param good_till_cancel_end_time: Not used.
            :param good_till_date: Not used.
            :param good_after_time: Not used.
            :param parent_id: Not used.
            :param account_no: Not used.
            :param transmit: Not used.
        """

        if str.upper(trail_type) == "AMOUNT":
            trail_type = "VALUE"
            if float(trail_amount) < 0:
                raise ValueError('The trail amount must be greater than 0')

        elif str.upper(trail_type) == "PERCENTAGE":
            trail_type = "PERCENT"
            if float(trail_amount) < 1 or float(trail_amount) > 99:
                raise ValueError('The trail amount must be between 1 to 99')

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        order = OrderBuilder(enforce_enums=False) \
            .set_order_type('TRAILING_STOP_LIMIT') \
            .set_quantity(quantity) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_session(session.upper()) \
            .set_order_strategy_type('SINGLE') \
            .set_stop_price_link_basis(stop_price_link_basis.upper()) \
            .set_stop_price_link_type(trail_type.upper()) \
            .set_stop_price_offset(truncate(trail_amount, digits)) \
            .set_stop_type(trigger_method.upper()) \
            .set_price(truncate(trail_limit, digits))

        if sec_type == "STK":
            return order.add_equity_leg(action.upper(), symbol.upper(), quantity)
        elif sec_type == "OPT":
            action = action.upper() + "_TO_" + instruction.upper()
            return order.add_option_leg(action.upper(), symbol.upper(), quantity)

    async def get_oto_order(self, parent_order, child_orders):
        """
            Returns a one-triggers-other order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param parent_order: The first order to be executed before triggering the remaining orders.
            :param child_orders: A list of orders to be triggered after the parent_order is executed.
        """

        parent_order.set_order_strategy_type('TRIGGER')

        for o in child_orders:
            parent_order.add_child_order_strategy(o)

        return parent_order

    async def get_oco_order(self, orders, oca_group_name: str, oca_group_type: str):
        """
            Returns a one-cancels-other order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param orders: A list of orders to be placed in the oco group.
            :param oca_group_name: Not Used.
            :param oca_group_type: Not Used.
        """

        return (OrderBuilder(enforce_enums=False)
                .set_order_strategy_type("OCO")
                .add_child_order_strategy(orders[0])
                .add_child_order_strategy(orders[1]))

    async def send_order(self, contract, account_no: str, order):
        """
            Submit the order

            :param contract: Not used.
            :param account_no: The account number to which the order should be sent.
            :param order: The order to be sent
        """

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
    async def get_order_by_symbol(self, symbol: str, account_no: str):
        """
            Returns a list of open orders for the given symbol

            :param symbol: The symbol for which to get the open orders.
            :param account_no: The account number from which to get the orders.
        """

        all_orders = await self.get_all_orders(account_no)
        open_orders = []

        for i in all_orders:
            try:
                ticker = i['orderLegCollection'][0]['instrument']['symbol']
                underlying_ticker = ticker.split("_")

                if underlying_ticker[0] == symbol:
                    open_orders.append(i)
            except:
                print("ERROR in get_order_by_ticker()")

        return open_orders

    async def get_all_orders(self, account_no: str):
        """
            Returns a list of all open orders.

            :param account_no: The account number from which to get the orders.
        """

        fields = self.c.Account.Fields('orders')
        all_orders = self.c.get_account(account_no, fields=fields)
        all_open_orders = all_orders.json()
        open_orders = []

        for i in all_open_orders['securitiesAccount']['orderStrategies']:
            open_status_list = ['AWAITING_PARENT_ORDER', 'AWAITING_CONDITION', 'AWAITING_MANUAL_REVIEW', 'ACCEPTED',
                                'AWAITING_UR_OUT', 'PENDING_ACTIVATION', 'QUEUED', 'WORKING']

            try:
                status = i['status']
                if status in open_status_list:
                    open_orders.append(i)

            except:
                print("ERROR in get_all_orders()")

        return open_orders

    async def get_position_by_symbol(self, symbol: str, account_no: str):
        """
            Returns a list of open positions for the given symbol

            :param symbol: The symbol for which to get the open positions.
            :param account_no: The account number from which to get the orders.
        """

        all_positions = await self.get_all_positions(account_no)
        open_positions = []

        for i in all_positions['securitiesAccount']['positions']:
            try:
                ticker = i['instrument']['symbol']
                underlying_ticker = ticker.split("_")

                if underlying_ticker[0] == symbol:
                    open_positions.append(i)

            except:
                print("ERROR in get_position_by_ticker()")

        return open_positions

    async def get_all_positions(self, account_no: str):
        """
            Returns a list of all open positions.

            :param account_no: The account number from which to get the orders.
        """

        fields = self.c.Account.Fields('positions')
        response = self.c.get_account(account_no, fields=fields)
        return response.json()

    # Cancel Orders/Close Positions
    async def cancel_order(self, order_id: int, account_no: str):
        """
            Cancels the order for an given order id.

            :param order_id: The order id for the order to be cancelled.
            :param account_no: The account number from which to get the orders.
        """

        self.c.cancel_order(order_id, account_no)

    async def cancel_all_orders(self, account_no: str):
        """
            Cancels all orders in the given account.

            :param account_no: The account number from which to get the orders.
        """

        open_orders = await self.get_all_orders(account_no)

        for i in range(0, len(open_orders)):
            order_id = open_orders[i]["orderId"]
            await self.cancel_order(order_id, account_no)

    async def close_position(self, account_no, symbol: str):
        """
            Closes all positions for the requested symbol.

            :param account_no: The account number from which to get the orders.
            :param symbol: The symbol for which the positions should be closed.
        """

        open_positions = await self.get_all_positions(account_no)
        positions = open_positions["securitiesAccount"]["positions"]

        for i in range(0, len(positions)):
            ticker = positions[i]["instrument"]["symbol"]

            if ticker == symbol:
                sec_type = positions[i]["instrument"]["assetType"]
                long_quantity = positions[i]["longQuantity"]
                short_quantity = positions[i]["shortQuantity"]
                quantity = 0
                action = ''

                if sec_type == "EQUITY":
                    sec_type = "STK"
                elif sec_type == "OPTION":
                    sec_type = "OPT"

                if long_quantity > 0:
                    quantity = long_quantity
                    action = "SELL"

                if short_quantity > 0:
                    quantity = short_quantity
                    action = "BUY"

                order = await self.get_market_order(symbol=ticker, quantity=quantity, sec_type=sec_type, action=action, instruction="CLOSE", account_no=account_no)
                await self.send_order('', account_no, order)

    async def close_all_positions(self, account_no):
        """
            Closes all positions.

            :param account_no: The account number from which to get the orders.
        """

        open_positions = await self.get_all_positions(account_no)
        positions = open_positions["securitiesAccount"]["positions"]

        for i in range(0, len(positions)):
            ticker = positions[i]["instrument"]["symbol"]
            sec_type = positions[i]["instrument"]["assetType"]
            long_quantity = positions[i]["longQuantity"]
            short_quantity = positions[i]["shortQuantity"]
            quantity = 0
            action = ''

            if sec_type == "EQUITY":
                sec_type = "STK"
            elif sec_type == "OPTION":
                sec_type = "OPT"

            if long_quantity > 0:
                quantity = long_quantity
                action = "SELL"

            if short_quantity > 0:
                quantity = short_quantity
                action = "BUY"

            order = await self.get_market_order(symbol=ticker, quantity=quantity, sec_type=sec_type, action=action, instruction="CLOSE", account_no=account_no)
            await self.send_order('', account_no, order)

    # Complex Option Contracts
    async def get_long_call_vertical_spread_contract(self, symbol: str, quantity: int, expiry_date: int, expiry_month: int,
                                                     expiry_year: int, low_strike: float, high_strike: float,
                                                     order_type: str = 'NET_DEBIT', order_price: float = '',
                                                     instruction: str = 'OPEN', session: str = 'NORMAL',
                                                     duration: str = 'DAY', exchange: str = '', multiplier: str = '100',
                                                     currency: str = ''):
        """
            Returns a long call vertical spread order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The symbol.
            :param quantity: The quantity/amount.
            :param expiry_date: The expiration date for the contract.
            :param expiry_month: The expiration month for the contract.
            :param expiry_year: The expiration year for the contract.
            :param low_strike: The lower strike price.
            :param high_strike: The higher strike price.
            :param order_type: The order type for the spread. Possible values are: "NET_DEBIT", "NET_CREDIT", "NET_ZERO", "MARKET"
            :param order_price: The price for the spread. 0 for "NET_ZERO", '' for "MARKET"
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param exchange: Not used.
            :param multiplier: Not used.
            :param currency: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        low_strike_call = await self.get_options_contract(symbol=symbol,
                                                          expiry_date=expiry_date,
                                                          expiry_month=expiry_month,
                                                          expiry_year=expiry_year,
                                                          strike=low_strike,
                                                          right='C')

        high_strike_call = await self.get_options_contract(symbol=symbol,
                                                           expiry_date=expiry_date,
                                                           expiry_month=expiry_month,
                                                           expiry_year=expiry_year,
                                                           strike=high_strike,
                                                           right='C')

        order = OrderBuilder(enforce_enums=False) \
            .set_complex_order_strategy_type('VERTICAL') \
            .set_order_strategy_type('SINGLE') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_type(order_type) \
            .set_price(order_price)

        if instruction.upper() == "OPEN":
            order = order\
                .add_option_leg('BUY_TO_OPEN', low_strike_call, quantity) \
                .add_option_leg('SELL_TO_OPEN', high_strike_call, quantity)

        elif instruction.upper() == "CLOSE":
            order = order\
                .add_option_leg('SELL_TO_CLOSE', low_strike_call, quantity) \
                .add_option_leg('BUY_TO_CLOSE', high_strike_call, quantity)

        return order

    async def get_short_call_vertical_spread_contract(self, symbol: str, quantity: int, expiry_date: int, expiry_month: int,
                                                      expiry_year: int, low_strike: float, high_strike: float,
                                                      order_type: str = 'NET_CREDIT', order_price: float = '',
                                                      instruction: str = 'OPEN', session: str = 'NORMAL',
                                                      duration: str = 'DAY', exchange: str = '', multiplier: str = '100',
                                                      currency: str = ''):
        """
            Returns a short call vertical spread order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The symbol.
            :param quantity: The quantity/amount.
            :param expiry_date: The expiration date for the contract.
            :param expiry_month: The expiration month for the contract.
            :param expiry_year: The expiration year for the contract.
            :param low_strike: The lower strike price.
            :param high_strike: The higher strike price.
            :param order_type: The order type for the spread. Possible values are: "NET_DEBIT", "NET_CREDIT", "NET_ZERO", "MARKET"
            :param order_price: The price for the spread. 0 for "NET_ZERO", '' for "MARKET"
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param exchange: Not used.
            :param multiplier: Not used.
            :param currency: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        low_strike_call = await self.get_options_contract(symbol=symbol,
                                                          expiry_date=expiry_date,
                                                          expiry_month=expiry_month,
                                                          expiry_year=expiry_year,
                                                          strike=low_strike,
                                                          right='C')

        high_strike_call = await self.get_options_contract(symbol=symbol,
                                                           expiry_date=expiry_date,
                                                           expiry_month=expiry_month,
                                                           expiry_year=expiry_year,
                                                           strike=high_strike,
                                                           right='C')

        order = OrderBuilder(enforce_enums=False) \
            .set_complex_order_strategy_type('VERTICAL') \
            .set_order_strategy_type('SINGLE') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_type(order_type) \
            .set_price(order_price)

        if instruction.upper() == "OPEN":
            order = order \
                .add_option_leg('BUY_TO_OPEN', high_strike_call, quantity) \
                .add_option_leg('SELL_TO_OPEN', low_strike_call, quantity)

        elif instruction.upper() == "CLOSE":
            order = order \
                .add_option_leg('SELL_TO_CLOSE', high_strike_call, quantity) \
                .add_option_leg('BUY_TO_CLOSE', low_strike_call, quantity)

        return order

    async def get_long_put_vertical_spread_contract(self, symbol: str, quantity: int, expiry_date: int, expiry_month: int,
                                                     expiry_year: int, low_strike: float, high_strike: float,
                                                     order_type: str = 'NET_DEBIT', order_price: float = '',
                                                     instruction: str = 'OPEN', session: str = 'NORMAL',
                                                     duration: str = 'DAY', exchange: str = '', multiplier: str = '100',
                                                     currency: str = ''):
        """
            Returns a long put vertical spread order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The symbol.
            :param quantity: The quantity/amount.
            :param expiry_date: The expiration date for the contract.
            :param expiry_month: The expiration month for the contract.
            :param expiry_year: The expiration year for the contract.
            :param low_strike: The lower strike price.
            :param high_strike: The higher strike price.
            :param order_type: The order type for the spread. Possible values are: "NET_DEBIT", "NET_CREDIT", "NET_ZERO", "MARKET"
            :param order_price: The price for the spread. 0 for "NET_ZERO", '' for "MARKET"
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param exchange: Not used.
            :param multiplier: Not used.
            :param currency: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        low_strike_put = await self.get_options_contract(symbol=symbol,
                                                          expiry_date=expiry_date,
                                                          expiry_month=expiry_month,
                                                          expiry_year=expiry_year,
                                                          strike=low_strike,
                                                          right='P')

        high_strike_put = await self.get_options_contract(symbol=symbol,
                                                           expiry_date=expiry_date,
                                                           expiry_month=expiry_month,
                                                           expiry_year=expiry_year,
                                                           strike=high_strike,
                                                           right='P')

        order = OrderBuilder(enforce_enums=False) \
            .set_complex_order_strategy_type('VERTICAL') \
            .set_order_strategy_type('SINGLE') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_type(order_type) \
            .set_price(order_price)

        if instruction.upper() == "OPEN":
            order = order\
                .add_option_leg('BUY_TO_OPEN', high_strike_put, quantity) \
                .add_option_leg('SELL_TO_OPEN', low_strike_put, quantity)

        elif instruction.upper() == "CLOSE":
            order = order\
                .add_option_leg('SELL_TO_CLOSE', high_strike_put, quantity) \
                .add_option_leg('BUY_TO_CLOSE', low_strike_put, quantity)

        return order

    async def get_short_put_vertical_spread_contract(self, symbol: str, quantity: int, expiry_date: int, expiry_month: int,
                                                     expiry_year: int, low_strike: float, high_strike: float,
                                                     order_type: str = 'NET_CREDIT', order_price: float = '',
                                                     instruction: str = 'OPEN', session: str = 'NORMAL',
                                                     duration: str = 'DAY', exchange: str = '', multiplier: str = '100',
                                                     currency: str = ''):
        """
            Returns a short put vertical spread order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The symbol.
            :param quantity: The quantity/amount.
            :param expiry_date: The expiration date for the contract.
            :param expiry_month: The expiration month for the contract.
            :param expiry_year: The expiration year for the contract.
            :param low_strike: The lower strike price.
            :param high_strike: The higher strike price.
            :param order_type: The order type for the spread. Possible values are: "NET_DEBIT", "NET_CREDIT", "NET_ZERO", "MARKET"
            :param order_price: The price for the spread. 0 for "NET_ZERO", '' for "MARKET"
            :param instruction: Whether to open or close a trade. Used for options. Possible values are "OPEN", "CLOSE".
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK".
            :param exchange: Not used.
            :param multiplier: Not used.
            :param currency: Not used.
        """

        duration_dict = {
            "DAY": "DAY",
            "GTC": "GOOD_TILL_CANCEL",
            "FOK": "FILL_OR_KILL"
        }

        low_strike_put = await self.get_options_contract(symbol=symbol,
                                                          expiry_date=expiry_date,
                                                          expiry_month=expiry_month,
                                                          expiry_year=expiry_year,
                                                          strike=low_strike,
                                                          right='P')

        high_strike_put = await self.get_options_contract(symbol=symbol,
                                                           expiry_date=expiry_date,
                                                           expiry_month=expiry_month,
                                                           expiry_year=expiry_year,
                                                           strike=high_strike,
                                                           right='P')

        order = OrderBuilder(enforce_enums=False) \
            .set_complex_order_strategy_type('VERTICAL') \
            .set_order_strategy_type('SINGLE') \
            .set_session(session.upper()) \
            .set_duration(duration_dict[duration.upper()]) \
            .set_order_type(order_type) \
            .set_price(order_price)

        if instruction.upper() == "OPEN":
            order = order\
                .add_option_leg('BUY_TO_OPEN', low_strike_put, quantity) \
                .add_option_leg('SELL_TO_OPEN', high_strike_put, quantity)

        elif instruction.upper() == "CLOSE":
            order = order\
                .add_option_leg('SELL_TO_CLOSE', low_strike_put, quantity) \
                .add_option_leg('BUY_TO_CLOSE', high_strike_put, quantity)

        return order

    # Account Information
    async def get_account(self, account_no: str = ''):
        """
            Returns a dictionary with account summary details.

            :param account_no: The account number from which to get the account details.
        """

        all_orders = self.c.get_account(account_no, fields=None)

        return all_orders.json()
