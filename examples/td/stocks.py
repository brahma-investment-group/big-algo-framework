from big_algo_framework.data.td import TDData
from big_algo_framework.brokers.td import TDA
import pandas as pd
import asyncio
import config

api_key = config.td_account["api_key"]
account_no = config.td_account["account_no"]
broker = TDA(token_path=config.td_account["token_path"],
             api_key=api_key,
             redirect_uri=config.td_account["redirect_uri"],
             chromedriver_path=config.td_account["chromedriver_path"])

ticker = 'TME'

async def get_stock_data():
    # FETCH STOCK DATA
    data = TDData(api_key=api_key)
    stock_data = await data.get_historic_stock_data(symbol=ticker, period_type="month", period=1, frequency_type="daily", frequency=1)
    stk_df = pd.DataFrame.from_dict(stock_data['candles'])
    print(stk_df)
    print(stk_df.iloc[-1]['close'])

async def mkt_order():
    # MKT ORDER
    order = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="STK", action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def stp_lmt_order():
    # STOP LIMIT ORDER
    order = await broker.get_stop_limit_order(symbol=ticker, quantity=1, sec_type="STK", stop_price=6.25, limit_price=6.25, action='BUY', session='NORMAL', instruction='OPEN', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def lmt_order():
    # LIMIT ORDER
    order = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="STK", limit_price=3.25, action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def stp_order():
    # STOP ORDER
    order = await broker.get_stop_order(symbol=ticker, quantity=1, sec_type="STK", stop_price=6.25, action='BUY', instruction='OPEN', session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def trailing_stp_percentage_order():
    # TRAILING STOP ORDER (PERCENTAGE)
    order = await broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="STK", trail_type='PERCENTAGE',
                                                 trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                 session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def trailing_stp_amount_order():
    # TRAILING STOP ORDER (AMOUNT)
    order = await broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type="STK", trail_type='AMOUNT',
                                                 trail_amount=5, digits=2, action='BUY', instruction='OPEN',
                                                 session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def oto_order():
    # OTO ORDER
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="STK", action='BUY')
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="STK", limit_price=6.25, action='SELL')
    order = await broker.get_oto_order(order1, [order2])
    await broker.send_order(contract='', account_no=account_no, order=order)

async def oco_order():
    # OCO ORDER
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type="STK", action='BUY')
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type="STK", limit_price=3.25, action='BUY')
    order = await broker.get_oco_order([order1, order2], oca_group_name='', oca_group_type='')
    await broker.send_order(contract='', account_no=account_no, order=order)

if __name__ == "__main__":
    asyncio.run(get_stock_data())
    asyncio.run(mkt_order())
    asyncio.run(stp_lmt_order())
    asyncio.run(lmt_order())
    asyncio.run(stp_order())
    asyncio.run(trailing_stp_percentage_order())
    asyncio.run(trailing_stp_amount_order())
    asyncio.run(oto_order())
    asyncio.run(oco_order())
