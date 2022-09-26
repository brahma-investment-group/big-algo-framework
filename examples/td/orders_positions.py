import asyncio
import config
from big_algo_framework.brokers.td import TDA

api_key = config.td_account["api_key"]
account_no = config.td_account["account_no"]
broker = TDA(token_path=config.td_account["token_path"],
             api_key=api_key,
             redirect_uri=config.td_account["redirect_uri"],
             chromedriver_path=config.td_account["chromedriver_path"])

ticker = 'TME'

async def get_orders_by_symbol():
    # Get orders for specified ticker
    print(await broker.get_order_by_symbol(symbol=ticker, account_no=account_no))

async def get_all_orders():
    # Get all orders
    print(await broker.get_all_orders(account_no))

async def get_positions_by_symbol():
    # Get positions for specified ticker
    print(await broker.get_position_by_symbol(symbol=ticker, account_no=account_no))

async def get_all_positions():
    # Get all positions
    print(await broker.get_all_positions(account_no))

async def cancel_order_by_id():
    # Cancel a specific order identified by an order id
    await broker.cancel_order(order_id=9445694496, account_no=account_no)

async def cancel_all_orders():
    # Cancel all open orders
    await broker.cancel_all_orders(account_no)

async def close_position_by_ticker():
    # Close a position for specified ticker
    await broker.close_position(symbol=ticker, account_no=account_no)

async def close_all_positions():
    # Close all open positions
    await broker.close_all_positions(account_no)

async def get_account_details():
    # Get account details
    await broker.get_account(account_no)

if __name__ == "__main__":
    asyncio.run(get_orders_by_symbol())
    asyncio.run(get_all_orders())
    asyncio.run(get_positions_by_symbol())
    asyncio.run(get_all_positions())
    asyncio.run(cancel_order_by_id())
    asyncio.run(cancel_all_orders())
    asyncio.run(close_position_by_ticker())
    asyncio.run(close_all_positions())
    asyncio.run(get_account_details())
