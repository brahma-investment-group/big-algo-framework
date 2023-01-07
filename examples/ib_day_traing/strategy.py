import time

from big_algo_framework.strategies.abstract_strategy import *
from big_algo_framework.brokers.ib import IB
from big_algo_framework.data.td import TDData
from big_algo_framework.big.options import filter_option_contract
from big_algo_framework.big.position_sizing import PositionSizing
from datetime import datetime, timedelta

broker = None

class IBORB(Strategy):
    def __init__(self, order_dict):
        super().__init__()
        self.is_position = True
        self.is_order = True
        self.orders_list = []
        self.pos_list = []

        self.ip_address = order_dict["ip_address"]
        self.port = order_dict["port"]
        self.ib_client = order_dict["ib_client"]
        # self.order_id = order_dict["order_id"]
        self.ticker = order_dict["ticker"]
        self.primary_exchange = order_dict["primary_exchange"]
        self.time_frame = order_dict["time_frame"]
        self.entry_time = order_dict["entry_time"]
        self.entry = order_dict["entry"]
        self.sl = order_dict["sl"]
        self.tp1 = order_dict["tp1"]
        self.tp2 = order_dict["tp2"]
        self.risk = order_dict["risk"]
        self.direction = order_dict["direction"]
        self.is_close = order_dict["is_close"]
        self.mkt_close_time = order_dict["mkt_close_time"]
        self.sec_type = order_dict["sec_type"]
        self.option_action = order_dict["option_action"]
        self.option_range = order_dict["option_range"]
        self.option_strikes = order_dict["option_strikes"]
        self.option_expiry_days = order_dict["option_expiry_days"]
        self.currency = order_dict["currency"]
        self.exchange = order_dict["exchange"]
        self.lastTradeDateOrContractMonth = order_dict["lastTradeDateOrContractMonth"]
        self.strike = order_dict["strike"]
        self.right = order_dict["right"]
        self.multiplier = order_dict["multiplier"]
        self.ask_price = order_dict["ask_price"]
        self.account_no = order_dict["account_no"]
        self.funds = order_dict["funds"]
        self.total_risk = order_dict["total_risk"]
        self.total_risk_units = order_dict["total_risk_units"]
        self.max_position_percent = order_dict["max_position_percent"]
        self.tda_api = order_dict["tda_api"]

    async def connect_broker(self):
        global broker
        if(broker == None) or (not broker.isConnected()):
            broker = IB()
            await broker.connectAsync(self.ip_address, self.port, self.ib_client)
        self.broker = broker
        self.account_dict = await self.broker.get_account()

    async def check_open_orders(self):
        self.orders_list = await self.broker.get_order_by_symbol(symbol=self.ticker, account_no=self.account_no)

        if len(self.orders_list) == 0:
            self.is_order = False

    async def check_positions(self):
        self.pos_list = await self.broker.get_position_by_symbol(symbol=self.ticker, account_no=self.account_no)

        if len(self.pos_list) == 0:
            self.is_position = False

    async def before_send_orders(self):
        self.gtd = datetime.fromtimestamp(self.mkt_close_time / 1000)

        # FILTER OPTIONS
        data = TDData(api_key=self.tda_api)
        contract_type = "CALL" if self.direction == "Bullish" else "PUT"

        options_df = await data.get_historic_option_data(symbol=self.ticker,
                                                         contract_type=contract_type,
                                                         range=self.option_range,
                                                         days_forward=10)

        option_contract = filter_option_contract(direction=self.direction,
                                                   open_action=self.option_action,
                                                   option_range=self.option_range,
                                                   option_strikes=self.option_strikes,
                                                   stock_price=self.entry,
                                                   option_expiry_days=self.option_expiry_days,
                                                   options_df=options_df)

        self.lastTradeDateOrContractMonth = datetime.strptime(option_contract["lastTradeDateOrContractMonth"], '%Y%m%d')
        self.strike = option_contract["strike"]
        self.right = option_contract["right"]
        self.ask = option_contract["ask"]
        self.bid = option_contract["bid"]
        self.symbol = option_contract["symbol"]
        self.multiplier = option_contract["multiplier"]

        # ACTION
        self.open_action = self.option_action
        self.close_action = "SELL" if self.open_action == "BUY" else "BUY"

        self.stock_entry = self.entry
        self.stock_sl = self.sl

        self.entry = self.ask
        self.sl = 0

        # Position Sizing
        self.risk_unit = abs(self.entry - self.sl)
        position = PositionSizing(self.account_dict["AvailableFunds"],
                                  self.total_risk,
                                  self.total_risk_units,
                                  self.risk_unit,
                                  self.max_position_percent,
                                  self.entry)
        self.quantity = position.options_quantity(self.multiplier)

        # Contract
        self.option_contract = await self.broker.get_options_contract(symbol=self.ticker,
                                                                      expiry_date=self.lastTradeDateOrContractMonth.day,
                                                                      expiry_month=self.lastTradeDateOrContractMonth.month,
                                                                      expiry_year=self.lastTradeDateOrContractMonth.year,
                                                                      strike=self.strike,
                                                                      right=self.right,
                                                                      exchange=self.exchange,
                                                                      multiplier=self.multiplier,
                                                                      currency=self.currency)

    async def send_orders(self):
        no_of_trades = 3
        final_quantity = [round(self.quantity/no_of_trades) for i in range(1,no_of_trades+1)]

        for i in range(0, len(final_quantity)):
            quantity = final_quantity[i]
            entry_order = await self.broker.get_market_order(action=self.open_action,
                                                             quantity=quantity,
                                                             duration="GTD",
                                                             good_till_date=(self.gtd + timedelta(minutes=-30)).strftime('%Y%m%d %H:%M:%S'),
                                                             account_no=self.account_no,
                                                             transmit=True,
                                                             sec_type="",
                                                             symbol="")
            await self.broker.send_order(contract=self.option_contract[0], account_no=self.account_no, order=entry_order)

        time.sleep(60)

        for i in range(0, len(final_quantity)):
            quantity = final_quantity[i]
            tp_order = await self.broker.get_limit_order(action=self.close_action,
                                                         quantity=quantity,
                                                         parent_id=0,
                                                         limit_price=(1.1 + (0.1*i)) * self.ask,
                                                         account_no=self.account_no,
                                                         transmit=True,
                                                         sec_type="",
                                                         symbol="")
            await self.broker.send_order(contract=self.option_contract[0], account_no=self.account_no, order=tp_order)

    async def start(self):
        await self.connect_broker()

    async def execute(self):
        await self.start()

        if self.is_close == 0:
            await self.check_positions()
            if not self.is_position:
                await self.check_open_orders()
                if not self.is_order:
                    await self.before_send_orders()

                    if self.quantity > 0:
                        await self.send_orders()
                        self.after_send_orders()
