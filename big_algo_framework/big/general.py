from datetime import timedelta
from datetime import datetime
# from big_algo_framework.finnhub.earnings import *
from big_algo_framework.big.calendar_us import *

def getAction(direction, order_dict):
    order_dict["action"] = ""
    order_dict["reverseAction"] = ""

    if direction == "Bullish":
        order_dict["action"] = "BUY"
        order_dict["reverseAction"] = "SELL"

    elif direction == "Bearish":
        order_dict["action"] = "SELL"
        order_dict["reverseAction"] = "BUY"

    return order_dict

def getEarningTickers():
    earnings_tickers = []

    # earnings_from_date = datetime.today().strftime('%Y-%m-%d')
    # earnings_to_date = datetime.today() + timedelta(days=1)
    #
    # time_now = datetime.now()
    # x = get_trading_close_holidays(time_now.year)
    # while earnings_to_date in x or earnings_to_date.weekday() in [5, 6]:
    #     earnings_to_date = earnings_to_date + timedelta(days=1)
    # earnings_to_date = earnings_to_date.strftime('%Y-%m-%d')
    #
    # earnings_data = FinnHubData()
    # earnings_data.get_earnings_data(earnings_from_date, earnings_to_date)
    #
    # if len(earnings_data.earning) != 0:
    #     df = earnings_data.earning.loc[
    #         ((earnings_data.earning['date'] == str(earnings_from_date)) & (earnings_data.earning['hour'] == "amc")) |
    #         ((earnings_data.earning['date'] == str(earnings_to_date)) & (earnings_data.earning['hour'] == "bmo"))]
    #
    #     earnings_tickers = df['symbol'].tolist()

    return earnings_tickers