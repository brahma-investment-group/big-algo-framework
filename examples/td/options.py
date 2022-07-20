from big_algo_framework.data.td import TDData
from big_algo_framework.brokers.td import TDA
from big_algo_framework.big.options import filter_option_contract
import pandas as pd
import asyncio

api_key = ""
ticker = "SPY"
broker = TDA(token_path='', api_key=api_key, redirect_uri='', chromedriver_path='')
account_no = 0

async def get_option_data():
    # FETCH STOCK DATA
    data = TDData(api_key=api_key)
    stock_data = await data.get_historic_stock_data(symbol=ticker, period_type="month", period=1, frequency_type="daily", frequency=1)
    stk_df = pd.DataFrame.from_dict(stock_data['candles'])
    print(stk_df)
    print(stk_df.iloc[-1]['close'])

    options_df = data.get_historic_option_data(symbol=ticker,
                                               contract_type="CALL",
                                               range="ITM",
                                               days_forward=10,
                                               )
    print(options_df)

    option_contract = filter_option_contract(direction="BULLISH",
                                             open_action="BUY",
                                             option_range="ITM",
                                             option_strikes=1,
                                             stock_price=4,
                                             option_expiry_days=2,
                                             options_df=options_df)
    print(option_contract)

async def mkt_order():
    # MKT ORDER
    order = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="OPT", action='BUY', session='NORMAL', duration='DAY')
    await broker.send_order(account_no=account_no, order=order)

async def stp_lmt_order():
    # STOP LIMIT ORDER
    order = await broker.get_stop_limit_order(symbol=ticker, quantity=1, sec_type="OPT", stop_price=6.25, limit_price=6.25, action='BUY', session='NORMAL', duration='DAY', stop_type='MARK')
    await broker.send_order(account_no=account_no, order=order)

async def lmt_order():
    # LIMIT ORDER
    order = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="OPT", limit_price=3.25, action='BUY', session='NORMAL', duration='DAY')
    await broker.send_order(account_no=account_no, order=order)

async def stp_order():
    # STOP ORDER
    order = await broker.get_stop_order(symbol=ticker, quantity=1, sec_type="OPT", stop_price=6.25, action='BUY', session='NORMAL', duration='DAY', stop_type='MARK')
    await broker.send_order(account_no=account_no, order=order)

async def trailing_stp_percentage_order():
    # TRAILING STOP ORDER (PERCENTAGE)
    order = await broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="OPT", trailing_offset=5, action='BUY',
                                                 stop_price_link_type='PERCENT', stop_price_link_basis='MARK', stop_type='MARK',
                                                 session='NORMAL', duration='DAY')
    await broker.send_order(account_no=account_no, order=order)

async def trailing_stp_amount_order():
    # TRAILING STOP ORDER (AMOUNT)
    order = await broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="OPT", trailing_offset=5, action='BUY',
                                                 stop_price_link_type='VALUE', stop_price_link_basis='MARK', stop_type='MARK',
                                                 session='NORMAL', duration='DAY')
    await broker.send_order(account_no=account_no, order=order)

async def trailing_stp_lmt_percentage_order():
    # TRAILING STOP LIMIT ORDER (PERCENTAGE)
    order = await broker.get_trailing_stop_limit_order(symbol=ticker, quantity=1, sec_type="OPT", trailing_offset=5, limit_price=6, action='BUY',
                                                       stop_price_link_type='PERCENT', stop_price_link_basis='MARK', stop_type='MARK',
                                                       session='NORMAL', duration='DAY')
    await broker.send_order(account_no=account_no, order=order)

async def trailing_stp_lmt_amount_order():
    # TRAILING STOP LIMIT ORDER (AMOUNT)
    order = await broker.get_trailing_stop_limit_order(symbol=ticker, quantity=1, sec_type="OPT", trailing_offset=5, limit_price=6, action='BUY',
                                                       stop_price_link_type='VALUE', stop_price_link_basis='MARK', stop_type='MARK',
                                                       session='NORMAL', duration='DAY')
    await broker.send_order(account_no=account_no, order=order)

async def oto_order():
    # OTO ORDER
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="OPT", action='BUY')
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="OPT", limit_price=6.25, action='SELL')
    order = await broker.get_oto_order(order1, order2)
    await broker.send_order(account_no=account_no, order=order)

async def oco_order():
    # OCO ORDER
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="OPT", action='BUY')
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="OPT", limit_price=6.25, action='BUY')
    order = await broker.get_oco_order(order1, order2)
    await broker.send_order(account_no=account_no, order=order)

if __name__ == "__main__":
    asyncio.run(get_option_data())
    asyncio.run(mkt_order())
    asyncio.run(stp_lmt_order())
    asyncio.run(lmt_order())
    asyncio.run(stp_order())
    asyncio.run(trailing_stp_percentage_order())
    asyncio.run(trailing_stp_amount_order())
    asyncio.run(trailing_stp_lmt_percentage_order())
    asyncio.run(trailing_stp_lmt_amount_order())
    asyncio.run(oto_order())
    asyncio.run(oco_order())
