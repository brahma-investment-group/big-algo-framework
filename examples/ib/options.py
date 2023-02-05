from big_algo_framework.brokers.ib import IB
import asyncio
import config

account_no = config.ib_account["account_no"]
broker = None

stock_ticker = 'TME'
expiry_date = 30
expiry_month = 9
expiry_year = 2022
strike = 5
right = 'C'

class IBExamples():
    def __init__(self):
        super().__init__()

    async def connect_broker(self):
        global broker
        if (broker == None) or (not broker.isConnected()):
            broker = IB()
            await broker.connectAsync(host=config.ib_account["ip_address"],
                                      port=config.ib_account["port"],
                                      clientId=config.ib_account["ib_client"],
                                      account=account_no)

        self.broker = broker

    async def mkt_order(self):
        # MKT ORDER
        await self.connect_broker()

        contract = await self.broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date,
                                                   expiry_month=expiry_month, expiry_year=expiry_year, strike=strike,
                                                   right=right)
        order = await self.broker.get_market_order(symbol=contract, quantity=1, sec_type="OPT", action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def stp_lmt_order(self):
        # STOP LIMIT ORDER
        await self.connect_broker()

        contract = await self.broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date,
                                                          expiry_month=expiry_month, expiry_year=expiry_year,
                                                          strike=strike, right=right)
        order = await self.broker.get_stop_limit_order(symbol=contract, quantity=1, sec_type="OPT", stop_price=6.25, limit_price=6.25, action='BUY', session='NORMAL', instruction='OPEN', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def lmt_order(self):
        # LIMIT ORDER
        await self.connect_broker()

        contract = await self.broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date,
                                                          expiry_month=expiry_month, expiry_year=expiry_year,
                                                          strike=strike, right=right)
        order = await self.broker.get_limit_order(symbol=contract, quantity=1, sec_type="OPT", limit_price=3.25, action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def stp_order(self):
        # STOP ORDER
        await self.connect_broker()

        contract = await self.broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date,
                                                          expiry_month=expiry_month, expiry_year=expiry_year,
                                                          strike=strike, right=right)
        order = await self.broker.get_stop_order(symbol=contract, quantity=1, sec_type="OPT", stop_price=6.25, action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def trailing_stp_percentage_order(self):
        # TRAILING STOP ORDER (PERCENTAGE)
        await self.connect_broker()

        contract = await self.broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date,
                                                          expiry_month=expiry_month, expiry_year=expiry_year,
                                                          strike=strike, right=right)
        order = await self.broker.get_trailing_stop_order(symbol=contract, quantity=1, sec_type="OPT", trail_type='PERCENTAGE',
                                                     trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                     session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def trailing_stp_amount_order(self):
        # TRAILING STOP ORDER (AMOUNT)
        await self.connect_broker()

        contract = await self.broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date,
                                                          expiry_month=expiry_month, expiry_year=expiry_year,
                                                          strike=strike, right=right)
        order = await self.broker.get_trailing_stop_order(symbol=contract, quantity=1, sec_type="OPT", trail_type='AMOUNT',
                                                     trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                     session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract[0], account_no=account_no, order=order)

    async def get_vertical_order(self):
        await self.connect_broker()

        contract = await self.broker.get_short_call_vertical_spread_contract(symbol=stock_ticker,
                                                                             expiry_date=expiry_date,
                                                                             expiry_month=expiry_month,
                                                                             expiry_year=expiry_year,
                                                                             low_strike=4.0,
                                                                             high_strike=5.0,
                                                                             instruction="OPEN",
                                                                             order_type="NET_CREDIT",
                                                                             order_price=0.90,
                                                                             quantity=5,
                                                                             currency='USD',
                                                                             exchange='SMART')
        order = await self.broker.get_market_order(symbol=contract, quantity=1, sec_type="OPT", action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
        await self.broker.send_order(contract=contract, account_no=account_no, order=order)

if __name__ == "__main__":
    ib = IBExamples()

    asyncio.run(ib.mkt_order())
    asyncio.run(ib.stp_lmt_order())
    asyncio.run(ib.lmt_order())
    asyncio.run(ib.stp_order())
    asyncio.run(ib.trailing_stp_percentage_order())
    asyncio.run(ib.trailing_stp_amount_order())
    asyncio.run(ib.get_vertical_order())

