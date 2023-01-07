from big_algo_framework.data.td import TDData
from big_algo_framework.brokers.td import TDA
import pandas as pd
import asyncio
import config

api_key = config.td_account["api_key"]
account_no = config.td_account["account_no"]

ticker = 'TME'

class TDExamples():
    def __init__(self):
        super().__init__()

    async def get_stock_data(self):
        # FETCH STOCK DATA
        data = TDData(api_key=api_key)
        stock_data = await data.get_historic_stock_data(symbol=ticker, period_type="month", period=1, frequency_type="daily", frequency=1)
        stk_df = pd.DataFrame.from_dict(stock_data['candles'])
        print(stk_df)
        print(stk_df.iloc[-1]['close'])

    async def connect_broker(self):
        self.broker = TDA(token_path=config.td_account["token_path"],
                          api_key=api_key,
                          redirect_uri=config.td_account["redirect_uri"],
                          chromedriver_path=config.td_account["chromedriver_path"])

    async def mkt_order(self):
        # MKT ORDER
        await self.connect_broker()

        contract = await self.broker.get_stock_contract(symbol=ticker, exchange='SMART', currency='USD', primaryExchange='NYSE')
        order = await self.broker.get_market_order(symbol=ticker, quantity=1, sec_type="STK", action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def stp_lmt_order(self):
        # STOP LIMIT ORDER
        await self.connect_broker()

        contract = await self.broker.get_stock_contract(symbol=ticker, exchange='SMART', currency='USD',
                                                        primaryExchange='NYSE')
        order = await self.broker.get_stop_limit_order(symbol=ticker, quantity=1, sec_type="STK", stop_price=6.25,
                                                       limit_price=6.25, action='BUY', session='NORMAL',
                                                       instruction='OPEN', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def lmt_order(self):
        # LIMIT ORDER
        await self.connect_broker()

        contract = await self.broker.get_stock_contract(symbol=ticker, exchange='SMART', currency='USD',
                                                        primaryExchange='NYSE')
        order = await self.broker.get_limit_order(symbol=ticker, quantity=1, sec_type="STK", limit_price=3.25,
                                                  action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def stp_order(self):
        # STOP ORDER
        await self.connect_broker()

        contract = await self.broker.get_stock_contract(symbol=ticker, exchange='SMART', currency='USD',
                                                        primaryExchange='NYSE')
        order = await self.broker.get_stop_order(symbol=ticker, quantity=1, sec_type="STK", stop_price=6.25,
                                                 action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def trailing_stp_percentage_order(self):
        # TRAILING STOP ORDER (PERCENTAGE)
        await self.connect_broker()

        contract = await self.broker.get_stock_contract(symbol=ticker, exchange='SMART', currency='USD',
                                                        primaryExchange='NYSE')
        order = await self.broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="STK",
                                                          trail_type='PERCENTAGE',
                                                          trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                          session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def trailing_stp_amount_order(self):
        # TRAILING STOP ORDER (AMOUNT)
        await self.connect_broker()

        contract = await self.broker.get_stock_contract(symbol=ticker, exchange='SMART', currency='USD',
                                                        primaryExchange='NYSE')
        order = await self.broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="STK",
                                                          trail_type='AMOUNT',
                                                          trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                          session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def oto_order(self):
        # OTO ORDER
        await self.connect_broker()

        order1 = await self.broker.get_market_order(symbol=ticker, quantity=1, sec_type="STK", action='BUY', instruction='OPEN')
        order2 = await self.broker.get_limit_order(symbol=ticker, quantity=1, sec_type="STK", limit_price=6.25, action='SELL', instruction='CLOSE')
        order = await self.broker.get_oto_order(order1, [order2])
        await self.broker.send_order(contract='', account_no=account_no, order=order)

    async def oco_order(self):
        # OCO ORDER
        await self.connect_broker()

        order1 = await self.broker.get_market_order(symbol=ticker, quantity=1, sec_type="STK", action='BUY')
        order2 = await self.broker.get_limit_order(symbol=ticker, quantity=1, sec_type="STK", limit_price=3.25, action='BUY')
        order = await self.broker.get_oco_order([order1, order2], oca_group_name='', oca_group_type='')
        await self.broker.send_order(contract='', account_no=account_no, order=order)

if __name__ == "__main__":
    td = TDExamples()

    asyncio.run(td.get_stock_data())
    asyncio.run(td.mkt_order())
    asyncio.run(td.stp_lmt_order())
    asyncio.run(td.lmt_order())
    asyncio.run(td.stp_order())
    asyncio.run(td.trailing_stp_percentage_order())
    asyncio.run(td.trailing_stp_amount_order())
    asyncio.run(td.oto_order())
    asyncio.run(td.oco_order())
