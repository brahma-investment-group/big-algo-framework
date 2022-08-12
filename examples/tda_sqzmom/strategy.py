from datetime import datetime
import pandas as pd
from dateutil import tz

import os, sys
sys.path.append(os.path.abspath('C:/Users/Owner/Desktop/Projects/big/big-algo-framework'))

from examples.tda_sqzmom import config
from big_algo_framework.strategies.abstract_strategy import *
from big_algo_framework.brokers import td
from big_algo_framework.data.td import TDData
from big_algo_framework.big.options import filter_option_contract
from big_algo_framework.big.helper import truncate
import asyncio

ticker = "SPY_081222C412" #SPY_081222C412
sec_type = "OPT"
action = "BUY"
stp_price = 6.25
lmt_prce = 4.00

token_path = config.td_account["token_path"]
api_key = config.td_account["api_key"]
redirect_uri = config.td_account["redirect_uri"]
chromedriver_path = config.td_account["chromedriver_path"]
account_no = config.td_account["account_no"]

broker = td.TDA(token_path, api_key, redirect_uri, chromedriver_path)

async def mkt_order():
    # MKT ORDER
    order = await broker.get_market_order(symbol=ticker, quantity=1, sec_type=sec_type, action=action, session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def stp_lmt_order():
    # STOP LIMIT ORDER
    order = await broker.get_stop_limit_order(symbol=ticker, quantity=1, sec_type=sec_type, stop_price=stp_price, limit_price=stp_price, action=action, session='NORMAL', duration='DAY', stop_type='MARK')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def lmt_order():
    # LIMIT ORDER
    order = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type=sec_type, limit_price=lmt_prce, action=action, session='NORMAL', duration='DAY')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def stp_order():
    # STOP ORDER
    order = await broker.get_stop_order(symbol=ticker, quantity=1, sec_type=sec_type, stop_price=stp_price, action=action, session='NORMAL', duration='DAY', stop_type='MARK')
    await broker.send_order(contract='', account_no=account_no, order=order)

async def trailing_stp_order():
    # TRAILING STOP ORDER
    order = await broker.get_trailing_stop_order(symbol=ticker, quantity=1, sec_type=sec_type, trail_type="AMOUNT", trail_amount=1)
    await broker.send_order(contract='', account_no=account_no, order=order)

async def trailing_stp_lmt_order():
    # TRAILING STOP LIMIT ORDER
    order = await broker.get_trailing_stop_limit_order(symbol=ticker, quantity=1, sec_type=sec_type, trail_type="AMOUNT",
                                                       trail_amount=1, trail_limit=6)
    await broker.send_order(contract='', account_no=account_no, order=order)

async def oto_order():
    # OTO ORDER
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type=sec_type, action=action)
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type=sec_type, limit_price=lmt_prce, action='SELL')
    order = await broker.get_oto_order(order1, [order2])
    await broker.send_order(contract='', account_no=account_no, order=order)

async def oco_order():
    # OCO ORDER
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type=sec_type, action=action)
    order2 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type=sec_type, limit_price=lmt_prce, action=action)
    order = await broker.get_oco_order([order1, order2], "", "")
    await broker.send_order(contract='', account_no=account_no, order=order)

async def bracket_order():
    order1 = await broker.get_market_order(symbol=ticker, quantity=1, sec_type=sec_type, action="BUY")
    order2 = await broker.get_stop_order(symbol=ticker, quantity=1, sec_type=sec_type, action="SELL", stop_price=2)
    order3 = await broker.get_limit_order(symbol=ticker, quantity=1, sec_type=sec_type, action="SELL", limit_price=10)
    order4 = await broker.get_oco_order([order2, order3], "", "")
    order5 = await broker.get_oto_order(order1, [order4])
    await broker.send_order(contract='', account_no=account_no, order=order5)

async def cancel_all_orders():
    await broker.cancel_all_orders(account_no)

async def cancel_one_order():
    broker.cancel_order(9126231956, account_no)

async def get_all_orders():
    print(await broker.get_all_orders(account_no))

async def get_order_by_ticker():
    print(await broker.get_order_by_ticker(ticker, account_no))

if __name__ == "__main__":
    # asyncio.run(get_stock_data())
    # asyncio.run(mkt_order())
    # asyncio.run(stp_lmt_order())
    # asyncio.run(lmt_order())
    # asyncio.run(stp_order())
    # asyncio.run(trailing_stp_order())
    # asyncio.run(trailing_stp_lmt_order())   # NOT WORKING
    # asyncio.run(oto_order())
    # asyncio.run(oco_order())
    # asyncio.run(bracket_order())
    asyncio.run(cancel_all_orders())
    # asyncio.run(cancel_one_order())
    # asyncio.run(get_all_orders())
    # asyncio.run(get_order_by_ticker())