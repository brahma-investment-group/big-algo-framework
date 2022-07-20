from big_algo_framework.data.td import TDData
from big_algo_framework.brokers.td import TDA
import pandas as pd
import asyncio

api_key = ""
ticker = "TME"
broker = TDA(token_path='', api_key=api_key, redirect_uri='', chromedriver_path='')
account_no = 0

async def get_account_data():
    print(await broker.get_order_by_ticker(ticker=ticker, account_no=account_no))
    print("*****************************************************************************************************")
    print(await broker.get_all_orders(account_no))
    print("*****************************************************************************************************")
    print(await broker.get_position_by_ticker(ticker=ticker, account_no=account_no))
    print("*****************************************************************************************************")
    print(await broker.get_all_positions(account_no))
    print("*****************************************************************************************************")

    # broker.cancel_order(order_id=XXXXXXXXXXXXX, account_no=account_no)
    # print("*****************************************************************************************************")
    # broker.cancel_all_orders(account_no)
    # print("*****************************************************************************************************")

if __name__ == "__main__":
    asyncio.run(get_account_data())
