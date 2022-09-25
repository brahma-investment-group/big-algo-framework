from big_algo_framework.data.td import TDData
from big_algo_framework.brokers.td import TDA
from big_algo_framework.big.options import filter_option_contract
import asyncio
import config

api_key = config.td_account["api_key"]
account_no = config.td_account["account_no"]
broker = TDA(token_path=config.td_account["token_path"],
             api_key=api_key,
             redirect_uri=config.td_account["redirect_uri"],
             chromedriver_path=config.td_account["chromedriver_path"])

stock_ticker = 'TME'
expiry_date = 30
expiry_month = 9
expiry_year = 2022
strike = 5
right = 'C'

async def get_option_data():
    # FETCH OPTIONS DATA
    data = TDData(api_key=api_key)
    options_df = await data.get_historic_option_data(symbol=stock_ticker,
                                                     contract_type="CALL",
                                                     range="ITM",
                                                     days_forward=100)
    print(options_df)

    option_contract = filter_option_contract(direction="BULLISH",
                                             open_action="BUY",
                                             option_range="ITM",
                                             option_strikes=1,
                                             stock_price=5,
                                             option_expiry_days=1,
                                             options_df=options_df)
    print(option_contract)

async def mkt_order():
    # MKT ORDER
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="OPT", action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def stp_lmt_order():
    # STOP LIMIT ORDER
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order = await broker.get_stop_limit_order(symbol=ticker, quantity=1, sec_type="OPT", stop_price=6.25, limit_price=6.25, action='BUY', session='NORMAL', instruction='OPEN', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def lmt_order():
    # LIMIT ORDER
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="OPT", limit_price=3.25, action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def stp_order():
    # STOP ORDER
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order = await broker.get_stop_order(symbol=ticker, quantity=1, sec_type="OPT", stop_price=6.25, action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def trailing_stp_percentage_order():
    # TRAILING STOP ORDER (PERCENTAGE)
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order = await broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="OPT", trail_type='PERCENTAGE',
                                                 trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                 session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def trailing_stp_amount_order():
    # TRAILING STOP ORDER (AMOUNT)
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order = await broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="OPT", trail_type='AMOUNT',
                                                 trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                 session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def oto_order():
    # OTO ORDER
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="OPT", action='BUY')
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="OPT", limit_price=6.25, action='SELL')
    order = await broker.get_oto_order(order1, [order2])
    await broker.send_order(contract='', account_no=account_no, order=order)

async def oco_order():
    # OCO ORDER
    ticker = await broker.get_options_contract(symbol=stock_ticker, expiry_date=expiry_date, expiry_month=expiry_month, expiry_year=expiry_year, strike=strike, right=right)
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="OPT", action='BUY')
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="OPT", limit_price=3.25, action='BUY')
    order = await broker.get_oco_order([order1, order2], oca_group_name='', oca_group_type='')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def get_vertical_order():
    order = await broker.get_short_call_vertical_spread_contract(symbol=stock_ticker,
                                                                 expiry_date=expiry_date,
                                                                 expiry_month=expiry_month,
                                                                 expiry_year=expiry_year,
                                                                 low_strike=4,
                                                                 high_strike=5,
                                                                 instruction="OPEN",
                                                                 order_type="NET_CREDIT",
                                                                 order_price=0.90,
                                                                 quantity=5)
    await broker.send_order(account_no=account_no, order=order, contract='')

if __name__ == "__main__":
    asyncio.run(get_option_data())
    asyncio.run(mkt_order())
    asyncio.run(stp_lmt_order())
    asyncio.run(lmt_order())
    asyncio.run(stp_order())
    asyncio.run(trailing_stp_percentage_order())
    asyncio.run(trailing_stp_amount_order())
    asyncio.run(oto_order())
    asyncio.run(oco_order())
    asyncio.run(get_vertical_order())

