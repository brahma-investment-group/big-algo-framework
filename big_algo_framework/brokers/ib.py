from big_algo_framework.brokers.abstract_broker import Broker
import ib_insync

class IB(Broker, ib_insync.IB):
    def __init__(self):
        ib_insync.IB.__init__(self)

    def connect_broker(self):
        pass

    # Asset
    async def get_stock_contract(self, broker, symbol: str = '', exchange: str = '', currency: str = '', primaryExchange: str = ''):
        stock_contract = ib_insync.Stock(symbol=symbol, exchange=exchange, currency=currency, primaryExchange=primaryExchange)
        return await broker.qualifyContractsAsync(stock_contract)

    async def get_options_contract(self, broker, symbol: str = '', lastTradeDateOrContractMonth: str = '', strike: float = 0.0,
                                   right: str = '', exchange: str = '', multiplier: str = '', currency: str = ''):
        option_contract = ib_insync.Option(symbol=symbol, lastTradeDateOrContractMonth=lastTradeDateOrContractMonth,
                                           strike=strike, right=right, exchange=exchange, multiplier=multiplier,
                                           currency=currency)
        return await broker.qualifyContractsAsync(option_contract)

    # Prepare/Send Orders
    async def get_market_order(self, action, quantity, parent_id='', tif='', gtd='', transmit=True, **kwargs):
        return ib_insync.MarketOrder(
            action=action,
            totalQuantity=quantity,
            parentId=parent_id,
            tif=tif,
            goodTillDate=gtd,
            transmit=transmit,
            **kwargs)

    def get_stop_limit_order(self, digits=2):
        pass

    def get_limit_order(self, digits=2):
        pass

    def get_stop_order(self, digits=2):
        pass

    def get_trailing_stop_order(self, orders, trail_type, trail_amount, trail_stop, digits=2):
       pass

    def get_oto_order(self, orders):
        pass

    def get_oco_order(self, orders, oca_group_name, oca_group_type):
        pass

    def get_price_condition(self, cond_type: int = 1, conjunction: str = 'a', is_more: bool = True, price: float = 0.0,
                            contract_id: int = 0, exchange: str = '', trigger_method: int = 0):
        price_cond = ib_insync.order.PriceCondition()
        price_cond.condType = cond_type
        price_cond.conjunction = conjunction
        price_cond.isMore = is_more
        price_cond.price = price
        price_cond.conId = contract_id
        price_cond.exch = exchange
        price_cond.triggerMethod = trigger_method

        return price_cond

    def get_time_condition(self, cond_type: int = 3, conjunction: str = 'a', is_more: bool = True, time: str = ''):
        time_cond = ib_insync.order.TimeCondition()
        time_cond.condType = cond_type
        time_cond.conjunction = conjunction
        time_cond.isMore = is_more
        time_cond.time = time

        return time_cond

    async def send_order(self, contract, order):
        return self.placeOrder(contract, order)

    # Get Orders/Positions
    def get_order_by_ticker(self):
        pass

    def get_all_orders(self):
        pass

    def get_position_by_ticker(self):
        pass

    def get_all_positions(self):
        pass

    # Cancel Orders/Close Positions
    def cancel_order(self, order_id):
        pass

    def cancel_all_orders(self):
        pass

    def close_position(self, underlying=False):
        pass

    def close_all_positions(self, underlying=False):
        pass