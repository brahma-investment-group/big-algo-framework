from big_algo_framework.brokers.abstract_broker import Broker
from big_algo_framework.big.helper import truncate
import ib_insync

class IB(Broker, ib_insync.IB):
    def __init__(self):
        ib_insync.IB.__init__(self)

    # Asset
    async def get_stock_contract(self, symbol: str = '', exchange: str = '', currency: str = '', primaryExchange: str = ''):
        stock_contract = ib_insync.Stock(symbol=symbol, exchange=exchange, currency=currency, primaryExchange=primaryExchange)
        return await self.qualifyContractsAsync(stock_contract)

    async def get_options_contract(self, symbol: str = '', expiration_date: str = '', strike: float = 0.0,
                                   right: str = '', exchange: str = '', multiplier: str = '100', currency: str = ''):
        option_contract = ib_insync.Option(symbol=symbol, lastTradeDateOrContractMonth=expiration_date,
                                           strike=strike, right=right, exchange=exchange, multiplier=multiplier,
                                           currency=currency)
        return await self.qualifyContractsAsync(option_contract)

    # Prepare/Send Orders
    async def get_market_order(self, symbol: str, quantity: int, sec_type: str, action: str = 'BUY', instruction: str = 'OPEN',
                               session: str = 'NORMAL', duration: str = 'DAY', good_till_cancel_start_time='',
                               good_till_cancel_end_time='', good_till_date='', good_after_time='', parent_id: int = '',
                               account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a market order. This doesn't actually submit an order. To submit order, use ``send_order`` function.
    
            :param symbol: Not used.
            :param quantity: The quantity/amount.
            :param sec_type: Not used.
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Not used.
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK", "IOC", "GTD", "GAT", "OPG", "DTC".
            :param good_till_cancel_start_time: The start time of GTC orders.
            :param good_till_cancel_end_time: The stop time of GTC orders.
            :param good_till_date: The date/time until which the order will be active (If ``duration`` is set to ``GTD``).
            :param good_after_time: The date/time after which the order will become active (If ``duration`` is set to ``GAT``).
            :param parent_id: The id of the parent order.
            :param account_no: The account number to which the order is being submitted.
            :param transmit: Whether to transmit the order to the broker or not. Default value is ``True``.
        """

        session = True if session == "AM" or "PM" or "SEAMLESS" else False

        return ib_insync.MarketOrder(totalQuantity=quantity,
                                     action=action,
                                     outsideRth=session,
                                     tif=duration,
                                     activeStartTime=good_till_cancel_start_time,
                                     activeStopTime=good_till_cancel_end_time,
                                     goodTillDate=good_till_date,
                                     goodAfterTime=good_after_time,
                                     parentId=parent_id,
                                     account=account_no,
                                     transmit=transmit,
                                     **kwargs)

    async def get_stop_limit_order(self, symbol: str, quantity: int, sec_type: str, stop_price: float,
                                   limit_price: float, digits: int = 2, trigger_method: str = 'LAST', action: str = 'BUY', instruction: str = 'OPEN',
                                   session: str = 'NORMAL', duration: str = 'DAY', good_till_cancel_start_time='',
                                   good_till_cancel_end_time='', good_till_date='', good_after_time='',
                                   parent_id: int = '', account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a stop limit order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: Not used.
            :param quantity: The quantity/amount.
            :param sec_type: Not used.
            :param stop_price: The stop price for the order.
            :param limit_price: The limit price for the order.
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Not used.
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK", "IOC", "GTD", "GAT", "OPG", "DTC".
            :param good_till_cancel_start_time: The start time of GTC orders.
            :param good_till_cancel_end_time: The stop time of GTC orders.
            :param good_till_date: The date/time until which the order will be active (If ``duration`` is set to ``GTD``).
            :param good_after_time: The date/time after which the order will become active (If ``duration`` is set to ``GAT``).
            :param parent_id: The id of the parent order.
            :param account_no: The account number to which the order is being submitted.
            :param transmit: Whether to transmit the order to the broker or not. Default value is ``True``.
        """

        trigger_methods = ["DEFAULT", "DOUBLE_BID_ASK", "LAST", "DOUBLE_LAST", "BID_ASK", "", "", "LAST_BID_ASK", "MID"]
        session = True if session == "AM" or "PM" or "SEAMLESS" else False

        return ib_insync.StopLimitOrder(totalQuantity=quantity,
                                        lmtPrice=truncate(limit_price, digits),
                                        stopPrice=truncate(stop_price, digits),
                                        triggerMethod=trigger_methods.index(trigger_method),
                                        action=action,
                                        outsideRth=session,
                                        tif=duration,
                                        activeStartTime=good_till_cancel_start_time,
                                        activeStopTime=good_till_cancel_end_time,
                                        goodTillDate=good_till_date,
                                        goodAfterTime=good_after_time,
                                        parentId=parent_id,
                                        account=account_no,
                                        transmit=transmit,
                                        **kwargs)

    async def get_limit_order(self, symbol: str, quantity: int, sec_type: str, limit_price: float, digits: int = 2,
                              action: str = 'BUY', instruction: str = 'OPEN', session: str = 'NORMAL', duration: str = 'DAY',
                              good_till_cancel_start_time='', good_till_cancel_end_time='', good_till_date='',
                              good_after_time='', parent_id: int = '', account_no: str = '',
                              transmit: bool = True, **kwargs):
        """
            Returns a limit order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: Not used.
            :param quantity: The quantity/amount.
            :param sec_type: Not used.
            :param limit_price: The limit price for the order.
            :param digits: The number of digits to which the price should be truncated.
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Not used.
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK", "IOC", "GTD", "GAT", "OPG", "DTC".
            :param good_till_cancel_start_time: The start time of GTC orders.
            :param good_till_cancel_end_time: The stop time of GTC orders.
            :param good_till_date: The date/time until which the order will be active (If ``duration`` is set to ``GTD``).
            :param good_after_time: The date/time after which the order will become active (If ``duration`` is set to ``GAT``).
            :param parent_id: The id of the parent order.
            :param account_no: The account number to which the order is being submitted.
            :param transmit: Whether to transmit the order to the broker or not. Default value is ``True``.
        """

        session = True if session == "AM" or "PM" or "SEAMLESS" else False

        return ib_insync.LimitOrder(totalQuantity=quantity,
                                        lmtPrice=truncate(limit_price, digits),
                                        action=action,
                                        outsideRth=session,
                                        tif=duration,
                                        activeStartTime=good_till_cancel_start_time,
                                        activeStopTime=good_till_cancel_end_time,
                                        goodTillDate=good_till_date,
                                        goodAfterTime=good_after_time,
                                        parentId=parent_id,
                                        account=account_no,
                                        transmit=transmit,
                                        **kwargs)

    async def get_stop_order(self, symbol: str, quantity: int, sec_type: str, stop_price: float,
                             digits: int = 2, trigger_method: str = 'LAST', action: str = 'BUY', instruction: str = 'OPEN',
                             session: str = 'NORMAL', duration: str = 'DAY', good_till_cancel_start_time='',
                             good_till_cancel_end_time='', good_till_date='', good_after_time='',
                             parent_id: int = '', account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a stop order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: Not used.
            :param quantity: The quantity/amount.
            :param sec_type: Not used.
            :param stop_price: The stop price for the order.
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Not used.
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK", "IOC", "GTD", "GAT", "OPG", "DTC".
            :param good_till_cancel_start_time: The start time of GTC orders.
            :param good_till_cancel_end_time: The stop time of GTC orders.
            :param good_till_date: The date/time until which the order will be active (If ``duration`` is set to ``GTD``).
            :param good_after_time: The date/time after which the order will become active (If ``duration`` is set to ``GAT``).
            :param parent_id: The id of the parent order.
            :param account_no: The account number to which the order is being submitted.
            :param transmit: Whether to transmit the order to the broker or not. Default value is ``True``.
        """

        trigger_methods = ["DEFAULT", "DOUBLE_BID_ASK", "LAST", "DOUBLE_LAST", "BID_ASK", "", "", "LAST_BID_ASK", "MID"]
        session = True if session == "AM" or "PM" or "SEAMLESS" else False

        return ib_insync.StopOrder(totalQuantity=quantity,
                                   stopPrice=truncate(stop_price, digits),
                                   triggerMethod=trigger_methods.index(trigger_method),
                                   action=action,
                                   outsideRth=session,
                                   tif=duration,
                                   activeStartTime=good_till_cancel_start_time,
                                   activeStopTime=good_till_cancel_end_time,
                                   goodTillDate=good_till_date,
                                   goodAfterTime=good_after_time,
                                   parentId=parent_id,
                                   account=account_no,
                                   transmit=transmit,
                                   **kwargs)

    async def get_trailing_stop_order(self, symbol: str, quantity: int, sec_type: str, trail_type: str,
                                      trail_amount: float, trail_stop: float = '', digits: int = 2,
                                      trigger_method: str = 'LAST', stop_price_link_basis: str = 'LAST',
                                      action: str = 'BUY', instruction: str = 'OPEN', session: str = 'NORMAL', duration: str = 'DAY',
                                      good_till_cancel_start_time='', good_till_cancel_end_time='',
                                      good_till_date='', good_after_time='', parent_id: int = '',
                                      account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a trailing stop order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: Not used.
            :param quantity: The quantity/amount.
            :param sec_type: Not used.
            :param trail_type: The type of trailing stop. Possible values are "PERCENTAGE", "AMOUNT".
            :param trail_amount: The amount to trail the stop by.
            :param trail_stop:
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param stop_price_link_basis: Not used.
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Not used.
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK", "IOC", "GTD", "GAT", "OPG", "DTC".
            :param good_till_cancel_start_time: The start time of GTC orders.
            :param good_till_cancel_end_time: The stop time of GTC orders.
            :param good_till_date: The date/time until which the order will be active (If ``duration`` is set to ``GTD``).
            :param good_after_time: The date/time after which the order will become active (If ``duration`` is set to ``GAT``).
            :param parent_id: The id of the parent order.
            :param account_no: The account number to which the order is being submitted.
            :param transmit: Whether to transmit the order to the broker or not. Default value is ``True``.
        """

        trigger_methods = ["DEFAULT", "DOUBLE_BID_ASK", "LAST", "DOUBLE_LAST", "BID_ASK", "", "", "LAST_BID_ASK", "MID"]
        session = True if session == "AM" or "PM" or "SEAMLESS" else False

        if trail_stop != "":
            trail_stop = truncate(trail_stop, digits)

        if str.upper(trail_type) == "AMOUNT":
            if float(trail_amount) < 0:
                raise ValueError('The trail amount must be greater than 0')
            else:
                aux_price = truncate(trail_amount, digits)
                trailing_percent = ""
        elif str.upper(trail_type) == "PERCENTAGE":
            if float(trail_amount) < 1 or float(trail_amount) > 99:
                raise ValueError('The trail amount must be between 1 to 99')
            else:
                trailing_percent = trail_amount
                aux_price = ""

        return ib_insync.Order(
            orderType='TRAIL',
            totalQuantity=quantity,
            trailStopPrice=trail_stop,
            triggerMethod=trigger_methods.index(trigger_method),
            auxPrice=aux_price,
            trailingPercent=trailing_percent,
            action=action,
            outsideRth=session,
            tif=duration,
            activeStartTime=good_till_cancel_start_time,
            activeStopTime=good_till_cancel_end_time,
            goodTillDate=good_till_date,
            goodAfterTime=good_after_time,
            parentId=parent_id,
            account=account_no,
            transmit=transmit,
            **kwargs)

    async def get_trailing_stop_limit_order(self, symbol: str, quantity: int, sec_type: str, trail_type: str,
                                            trail_amount: float, trail_stop: float = '', trail_limit: float = '',
                                            limit_price_offset: float = '', digits: int = 2,
                                            trigger_method: str = 'LAST', stop_price_link_basis: str = 'LAST',
                                            action: str = 'BUY', instruction: str = 'OPEN', session: str = 'NORMAL', duration: str = 'DAY',
                                            good_till_cancel_start_time='', good_till_cancel_end_time='',
                                            good_till_date='', good_after_time='', parent_id: int = '',
                                            account_no: str = '', transmit: bool = True, **kwargs):
        """
            Returns a trailing stop order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: Not used.
            :param quantity: The quantity/amount.
            :param sec_type: Not used.
            :param trail_type: The type of trailing stop. Possible values are "PERCENTAGE", "AMOUNT".
            :param trail_amount: The amount to trail the stop by.
            :param trail_stop:
            :param trail_limit:
            :param limit_price_offset:
            :param digits: The number of digits to which the price should be truncated.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
                                   Possible values are "STANDARD", "BID", "ASK", "LAST", "MARK"
            :param stop_price_link_basis: Not used.
            :param action: The required action. Possible values are "BUY", "SELL".
            :param instruction: Not used.
            :param session: The session where the order should be executed. Possible values are "NORMAL", "AM", "PM", "SEAMLESS".
            :param duration: The length of time over which the order will be active. Possible values are "DAY", "GTC", "FOK", "IOC", "GTD", "GAT", "OPG", "DTC".
            :param good_till_cancel_start_time: The start time of GTC orders.
            :param good_till_cancel_end_time: The stop time of GTC orders.
            :param good_till_date: The date/time until which the order will be active (If ``duration`` is set to ``GTD``).
            :param good_after_time: The date/time after which the order will become active (If ``duration`` is set to ``GAT``).
            :param parent_id: The id of the parent order.
            :param account_no: The account number to which the order is being submitted.
            :param transmit: Whether to transmit the order to the broker or not. Default value is ``True``.
        """

        trigger_methods = ["DEFAULT", "DOUBLE_BID_ASK", "LAST", "DOUBLE_LAST", "BID_ASK", "", "", "LAST_BID_ASK", "MID"]
        session = True if session == "AM" or "PM" or "SEAMLESS" else False

        if trail_stop != "":
            trail_stop = truncate(trail_stop, digits)
        if trail_limit != "":
            trail_limit = truncate(trail_limit, digits)
            limit_price_offset = ""
        if limit_price_offset != "":
            trail_limit = ""
            limit_price_offset = truncate(limit_price_offset, digits)

        if str.upper(trail_type) == "AMOUNT":
            if float(trail_amount) < 0:
                raise ValueError('The trail amount must be greater than 0')
            else:
                aux_price = truncate(trail_amount, digits)
                trailing_percent = ""
        elif str.upper(trail_type) == "PERCENTAGE":
            if float(trail_amount) < 1 or float(trail_amount) > 99:
                raise ValueError('The trail amount must be between 1 to 99')
            else:
                trailing_percent = trail_amount
                aux_price = ""

        return ib_insync.Order(
            orderType='TRAIL LIMIT',
            totalQuantity=quantity,
            trailStopPrice=trail_stop,
            lmtPrice=trail_limit,
            lmtPriceOffset=limit_price_offset,
            triggerMethod=trigger_methods.index(trigger_method),
            auxPrice=aux_price,
            trailingPercent=trailing_percent,
            action=action,
            outsideRth=session,
            tif=duration,
            activeStartTime=good_till_cancel_start_time,
            activeStopTime=good_till_cancel_end_time,
            goodTillDate=good_till_date,
            goodAfterTime=good_after_time,
            parentId=parent_id,
            account=account_no,
            transmit=transmit,
            **kwargs)

    async def get_oto_order(self, parent_order, child_orders):
        """
            Returns a one-triggers-other order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param parent_order: The first order to be executed before triggering the remaining orders.
            :param child_orders: A list of orders to be triggered after the parent_order is executed.
        """

        for o in child_orders:
            o.parentId = parent_order.order.orderId

        return child_orders

    async def get_oco_order(self, orders, oca_group_name: str, oca_group_type: str):
        """
            Returns a one-cancels-other order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param orders: A list of orders to be placed in the oco group.
            :param oca_group_name: A name to be assigned to the oco group.
            :param oca_group_type: The oco group type. Possible values are: "CANCEL", "REDUCE_WITH_BLOCK", "REDUCE_WITH_NO_BLOCK"
        """

        oca_types= ["", "CANCEL", "REDUCE_WITH_BLOCK", "REDUCE_WITH_NO_BLOCK"]

        return self.oneCancelsAll(orders, oca_group_name, oca_types.index(oca_group_type))

    async def get_price_condition(self, price: float, exchange: str, conjunction: str = 'a', is_more: bool = True,
                            contract_id: int = 0, trigger_method: str = "DEFAULT"):
        """
            Returns an order condition based on price. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param price: The price at which the order should be sent.
            :param exchange: The exchange at which the contract is being traded.
            :param conjunction: To be used to join multiple conditions. Possible values are: 'a' (AND), 'o' (OR)
            :param is_more: Should the current price be more than the ``price`` variable. True if yes, else False.
            :param contract_id: The id of the contract being traded.
            :param trigger_method: Specifies how Simulated Stop, Stop-Limit and Trailing Stop orders are triggered.
        """

        trigger_methods = ["DEFAULT", "DOUBLE_BID_ASK", "LAST", "DOUBLE_LAST", "BID_ASK", "", "", "LAST_BID_ASK", "MID"]

        price_cond = ib_insync.order.PriceCondition()
        price_cond.condType = 1
        price_cond.conjunction = conjunction
        price_cond.isMore = is_more
        price_cond.price = price
        price_cond.conId = contract_id
        price_cond.exch = exchange
        price_cond.triggerMethod = trigger_methods.index(trigger_method)

        return price_cond

    async def get_time_condition(self, time: str, conjunction: str = 'a', is_more: bool = True):
        """
            Returns an order condition based on time. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param time: The time at which the order should be sent.
            :param conjunction: To be used to join multiple conditions. Possible values are: 'a' (AND), 'o' (OR)
            :param is_more: Should the current time be more than the ``time`` variable. True if yes, else False.
        """

        time_cond = ib_insync.order.TimeCondition()
        time_cond.condType = 3
        time_cond.conjunction = conjunction
        time_cond.isMore = is_more
        time_cond.time = time

        return time_cond

    async def send_order(self, contract, account_no: str, order):
        """
            Submit the order

            :param contract: The contract to be traded.
            :param account_no: Not used.
            :param order: The order to be sent
        """

        return self.placeOrder(contract, order)

    # Get Orders/Positions
    async def get_order_by_ticker(self, ticker: str, account_no: str):
        """
            Returns a list of open orders for the given ticker

            :param ticker: The ticker for which to get the open orders.
            :param account_no: Not used.
        """

        orders_list = []
        all_orders = await self.get_all_orders(account_no='')

        for trades in all_orders:
            if trades.contract.symbol == ticker:
                orders_list.append(trades)

        return orders_list

    async def get_all_orders(self, account_no: str):
        """
            Returns a list of all open orders.

            :param account_no: Not used.
        """

        orders_list = []
        open_status = ['ApiPending', 'PendingSubmit', 'PreSubmitted', 'Submitted']

        for trades in self.trades():
            if trades.orderStatus.status in open_status:
                orders_list.append(trades)

        return orders_list

    async def get_position_by_ticker(self, ticker: str, account_no: str):
        """
            Returns a list of open positions for the given ticker

            :param ticker: The ticker for which to get the open positions.
            :param account_no: Not used.
        """

        pos_list = []
        all_pos = await self.get_all_positions(account_no='')

        for pos in all_pos:
            if pos.contract.symbol == ticker:
                pos_list.append(pos)

        return pos_list

    async def get_all_positions(self, account_no: str):
        """
            Returns a list of all open positions.

            :param account_no: The account number from which to get the orders.
        """

        pos_list = []

        for pos in await self.reqPositionsAsync():
            if account_no:
                if pos.position != 0 and pos.account == account_no:
                    pos_list.append(pos)

            else:
                if pos.position != 0:
                    pos_list.append(pos)

        return pos_list

    # Cancel Orders/Close Positions
    async def cancel_order(self, order_id: int, account_no: str):
        """
            Cancels the order for an given order id.

            :param order_id: The order id for the order to be cancelled.
            :param account_no: Not used.
        """

        trades = await self.get_all_orders(account_no='')

        for trade in trades:
            if trade.order.orderId == order_id:
                self.cancelOrder(trade.order)

    async def cancel_all_orders(self, account_no: str):
        """
            Cancels all orders in the given account.

            :param account_no: Not used.
        """

        trades = await self.get_all_orders(account_no='')

        for trade in trades:
            self.cancelOrder(trade.order)

    async def close_position(self, account_no, symbol: str):
        """
            Closes all positions for the requested symbol.

            :param account_no: Not Used.
            :param symbol: The symbol for which the positions should be closed.
        """

        pos_list = await self.get_all_positions(account_no='')

        for pos in pos_list:
            if pos.contract.symbol == symbol:
                action = ""
                if pos.position > 0:
                    action = "SELL"
                elif pos.position < 0:
                    action = "BUY"

                order = await self.get_market_order(symbol=symbol, quantity=int(pos.position), sec_type='', action=action, account_no=pos.account, transmit=True)
                await self.send_order(contract=ib_insync.Contract(conId=pos.contract.conId, exchange="SMART"), account_no='', order=order)

    async def close_all_positions(self, account_no):
        """
            Closes all positions.

            :param account_no: Not Used.
        """

        pos_list = await self.get_all_positions(account_no='')

        for pos in pos_list:
            action = ""
            if pos.position > 0:
                action = "SELL"
            elif pos.position < 0:
                action = "BUY"

            order = await self.get_market_order(symbol=pos.contract.symbol, quantity=int(pos.position), sec_type='', action=action, account_no=pos.account, transmit=True)
            await self.send_order(ib_insync.Contract(conId=pos.contract.conId, exchange="SMART"), account_no, order)

    # Complex Option Contracts
    async def get_long_call_vertical_spread_contract(self, symbol: str = '', expiration_date: str = '',
                                                     itm_strike: float = 0.0, otm_strike: float = 0.0,
                                                     exchange: str = '', multiplier: str = '100', currency: str = ''):
        """
            Returns a long call vertical spread order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The symbol.
            :param expiration_date: The expiration date for the contract. Format: #YYYYMMDD.
            :param itm_strike: In-The-Money strike price. Usually lower than the current market price.
            :param otm_strike: Out-The-Money strike price. Usually greater than the current market price.
            :param exchange: The exchange on which the order should be submitted. Possible values are "SMART" or any other valid exchange.
            :param multiplier: The multiplier for the option price. Default value is 100.
            :param currency: IThe currency for the contract.
        """

        itm_call = await self.get_options_contract(symbol=symbol, expiration_date=expiration_date, strike=itm_strike,
                                                   right='C', exchange=exchange, multiplier=multiplier, currency=currency)
        otm_call = await self.get_options_contract(symbol=symbol, expiration_date=expiration_date, strike=otm_strike,
                                                   right='C', exchange=exchange, multiplier=multiplier, currency=currency)

        contract = ib_insync.Contract()
        contract.symbol = symbol
        contract.secType = "BAG"
        contract.currency = currency
        contract.exchange = exchange

        leg1 = ib_insync.ComboLeg()
        leg1.conId = itm_call[0].conId
        leg1.ratio = 1
        leg1.action = "BUY"
        leg1.exchange = itm_call[0].exchange

        leg2 = ib_insync.ComboLeg()
        leg2.conId = otm_call[0].conId
        leg2.ratio = 1
        leg2.action = "SELL"
        leg2.exchange = otm_call[0].exchange

        contract.comboLegs = []
        contract.comboLegs.append(leg1)
        contract.comboLegs.append(leg2)

        return contract

    async def get_long_put_vertical_spread_contract(self, symbol: str = '', expiration_date: str = '',
                                                    itm_strike: float = 0.0, otm_strike: float = 0.0,
                                                    exchange: str = '', multiplier: str = '100', currency: str = ''):
        """
            Returns a long put vertical spread order. This doesn't actually submit an order. To submit order, use ``send_order`` function.

            :param symbol: The symbol.
            :param expiration_date: The expiration date for the contract. Format: #YYYYMMDD.
            :param itm_strike: In-The-Money strike price. Usually greater than the current market price.
            :param otm_strike: Out-The-Money strike price. Usually lower than the current market price.
            :param exchange: The exchange on which the order should be submitted. Possible values are "SMART" or any other valid exchange.
            :param multiplier: The multiplier for the option price. Default value is 100.
            :param currency: IThe currency for the contract.
        """

        itm_put = await self.get_options_contract(symbol=symbol, expiration_date=expiration_date, strike=itm_strike,
                                                   right='P', exchange=exchange, multiplier=multiplier, currency=currency)
        otm_put = await self.get_options_contract(symbol=symbol, expiration_date=expiration_date, strike=otm_strike,
                                                   right='P', exchange=exchange, multiplier=multiplier, currency=currency)

        contract = ib_insync.Contract()
        contract.symbol = symbol
        contract.secType = "BAG"
        contract.currency = currency
        contract.exchange = exchange

        leg1 = ib_insync.ComboLeg()
        leg1.conId = itm_put[0].conId
        leg1.ratio = 1
        leg1.action = "BUY"
        leg1.exchange = itm_put[0].exchange

        leg2 = ib_insync.ComboLeg()
        leg2.conId = otm_put[0].conId
        leg2.ratio = 1
        leg2.action = "SELL"
        leg2.exchange = otm_put[0].exchange

        contract.comboLegs = []
        contract.comboLegs.append(leg1)
        contract.comboLegs.append(leg2)

        return contract

    # Account Information
    async def get_account(self):
        """
            Returns a dictionary with account summary details.
        """

        account = {}
        acc_summary = await self.accountSummaryAsync()

        for acc in acc_summary:
            account[acc.tag] = acc.value

        return account