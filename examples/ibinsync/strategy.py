from big_algo_framework.strategies.abstract_strategy import *
from big_algo_framework.brokers.ib import IB
from examples.all_strategy_files.ib.ib_position_sizing import IbPositionSizing
from examples.all_strategy_files.ib.ib_get_action import IbGetAction
# from examples.all_strategy_files.ib.ib_filter_options import IbFilterOptions
from datetime import datetime, timedelta
from big_algo_framework.big.options import filter_option_contract
from big_algo_framework.data.td import TDData

broker = None

class IBORB(Strategy):
    def __init__(self, order_dict):
        super().__init__()
        self.is_position = True
        self.is_order = True
        self.orders_list = []
        self.pos_list = []
        self.order_dict = order_dict.copy()

    async def connect_broker(self):
        global broker
        if(broker == None) or (not broker.isConnected()):
            broker = IB()
            await broker.connectAsync(self.order_dict["ip_address"], self.order_dict["port"], self.order_dict["ib_client"])

        self.broker = broker
        self.order_dict["broker"] = broker

        x = await self.broker.accountSummaryAsync()
        for acc in x:
            if acc.tag == "AvailableFunds":
                self.order_dict["funds"] = acc.value

    async def check_open_orders(self):
        for trades in self.broker.trades():
            if trades.orderStatus.status == "PreSubmitted":
                self.orders_list.append(trades.contract.symbol)

        if self.order_dict["ticker"] not in self.orders_list:
            self.is_order = False

    async def check_positions(self):
        for pos in await self.broker.reqPositionsAsync():
            if pos.position != 0:
                self.pos_list.append(pos.contract.symbol)

        if self.order_dict["ticker"] not in self.pos_list:
            self.is_position = False

    async def before_send_orders(self):
        self.order_dict["gtd"] = datetime.fromtimestamp(self.order_dict["mkt_close_time"] / 1000)

        # FILTER OPTIONS
        # filter = IbFilterOptions(self.order_dict)
        # options_df = filter.filter_options()

        data = TDData()
        contract_type = ""

        if (self.order_dict["direction"] == "Bullish" and self.order_dict["option_action"] == "BUY") or \
                (self.order_dict["direction"] == "Bearish" and self.order_dict["option_action"] == "SELL"):
            contract_type = "CALL"

        elif (self.order_dict["direction"] == "Bullish" and self.order_dict["option_action"] == "SELL") or \
                (self.order_dict["direction"] == "Bearish" and self.order_dict["option_action"] == "BUY"):
            contract_type = "PUT"

        options_df = data.get_options_data(symbol=self.order_dict["ticker"],
                                           contract_type=contract_type,
                                           range=self.order_dict["option_range"],
                                           days_forward=10,
                                           api_key=self.order_dict["tda_api"])

        option_contract = filter_option_contract(direction=self.order_dict["direction"],
                                                   open_action=self.order_dict["option_action"],
                                                   option_range=self.order_dict["option_range"],
                                                   option_strikes=self.order_dict["option_strikes"],
                                                   stock_price=self.order_dict["entry"],
                                                   option_expiry_days=self.order_dict["option_expiry_days"],
                                                   options_df=options_df)

        self.order_dict["lastTradeDateOrContractMonth"] = option_contract["lastTradeDateOrContractMonth"]
        self.order_dict["strike"] = option_contract["strike"]
        self.order_dict["right"] = option_contract["right"]
        self.order_dict["ask"] = option_contract["ask"]
        self.order_dict["bid"] = option_contract["bid"]
        self.order_dict["symbol"] = option_contract["symbol"]
        self.order_dict["multiplier"] = option_contract["multiplier"]

        action = IbGetAction(self.order_dict)
        action.get_options_action()

        self.order_dict["stock_entry"] = self.order_dict["entry"]
        self.order_dict["stock_sl"] = self.order_dict["sl"]

        self.order_dict["entry"] = self.order_dict["ask"]
        self.order_dict["sl"] = 0

        # IB Position Sizing Class
        ib_pos_size = IbPositionSizing(self.order_dict)
        quantity = ib_pos_size.get_options_quantity()
        self.order_dict["quantity"] = quantity

        # Contract
        self.stock_contract = await self.broker.get_stock_contract(self.order_dict["broker"], self.order_dict["ticker"],
                                                                   self.order_dict["exchange"], self.order_dict["currency"],
                                                                   self.order_dict["primary_exchange"])
        self.option_contract = await self.broker.get_options_contract(self.order_dict["broker"],
                                                                      self.order_dict["ticker"],
                                                                      self.order_dict["lastTradeDateOrContractMonth"],
                                                                      self.order_dict["strike"],
                                                                      self.order_dict["right"],
                                                                      self.order_dict["exchange"],
                                                                      self.order_dict["multiplier"],
                                                                      self.order_dict["currency"],
                                                                      )

        # Prepare Orders
        self.x = True if self.order_dict["direction"] == "Bullish" else False
        self.y = False if self.order_dict["direction"] == "Bullish" else True

    async def send_orders(self):
        entry_order = await self.broker.get_market_order(self.order_dict["open_action"], self.order_dict["quantity"], "", "GTD", (self.order_dict["gtd"] + timedelta(minutes=-30)).strftime('%Y%m%d %H:%M:%S'), False)
        p_cond = self.broker.get_price_condition(cond_type=1, conjunction='o', is_more=self.y, price=self.order_dict["stock_entry"], contract_id=self.stock_contract[0].conId, exchange="SMART", trigger_method=0)
        entry_order.conditions = [p_cond]
        entry_trade = await self.broker.send_order(self.option_contract[0], entry_order)

        sl_order = await self.broker.get_market_order(self.order_dict["close_action"], self.order_dict["quantity"], entry_trade.order.orderId, "", "", False)
        p_cond = self.broker.get_price_condition(cond_type=1, conjunction='o', is_more=self.y, price=self.order_dict["stock_sl"], contract_id=self.stock_contract[0].conId, exchange="SMART", trigger_method=0)
        sl_order.conditions = [p_cond]
        await self.broker.send_order(self.option_contract[0], sl_order)

        tp_order = await self.broker.get_market_order(self.order_dict["close_action"], self.order_dict["quantity"], entry_trade.order.orderId, "", "",  transmit=True)
        p_cond = self.broker.get_price_condition(cond_type=1, conjunction='o', is_more=self.x, price=self.order_dict["tp1"], contract_id=self.stock_contract[0].conId, exchange="SMART", trigger_method=0)
        t_cond = self.broker.get_time_condition(cond_type=3, conjunction='o', is_more=True, time=(self.order_dict["gtd"] + timedelta(minutes=-5)).strftime('%Y%m%d %H:%M:%S'))
        tp_order.conditions = [p_cond, t_cond]
        await self.broker.send_order(self.option_contract[0], tp_order)

    async def start(self):
        await self.connect_broker()

    async def execute(self):
        await self.start()

        if self.order_dict["is_close"] == 0:
            await self.check_positions()
            if not self.is_position:
                await self.check_open_orders()
                if not self.is_order:
                    await self.before_send_orders()

                    if self.order_dict["quantity"] > 0:
                        await self.send_orders()
                        self.after_send_orders()


    # TRADE CLASS OUTPUT!!!!
    # Trade(
    # contract=Stock(conId=270639, symbol='INTC', exchange='SMART', primaryExchange='NASDAQ', currency='USD', localSymbol='INTC', tradingClass='NMS'),
    # order=LimitOrder(orderId=104, clientId=1, permId=1405222075, action='SELL', totalQuantity=1.0, lmtPrice=1.11, auxPrice=0.0),
    # orderStatus=OrderStatus(orderId=104, status='PreSubmitted', filled=0.0, remaining=1.0, avgFillPrice=0.0, permId=1405222075, parentId=0, lastFillPrice=0.0, clientId=1, whyHeld='', mktCapPrice=0.0),
    # fills=[],
    # log=[TradeLogEntry(time=datetime.datetime(2022, 6, 18, 23, 7, 29, 87606, tzinfo=datetime.timezone.utc), status='PendingSubmit', message='', errorCode=0),
    # TradeLogEntry(time=datetime.datetime(2022, 6, 18, 23, 7, 29, 120600, tzinfo=datetime.timezone.utc), status='PreSubmitted', message='', errorCode=0)]),


    # POSITIONS OUTPUT
    # [Position(account='U3584554',
    #           contract=Stock(conId=344439802, symbol='TME', exchange='NYSE', currency='USD', localSymbol='TME', tradingClass='TME'),
    #           position=1.0, avgCost=5.2227)]