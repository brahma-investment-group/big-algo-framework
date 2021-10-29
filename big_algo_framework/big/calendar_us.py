import datetime
from datetime import date
import pandas_market_calendars as mcal

def is_mkt_open(market):
    """Check if markets are currently open using pandas_market_calendars"""
    mkt_dict = {}

    trading_day = mcal.get_calendar(market).schedule(start_date=date.today(), end_date=date.today())
    open_time = trading_day.iloc[0][0]
    close_time = trading_day.iloc[0][1]

    try:
        if open_time < datetime.datetime.now(tz=datetime.timezone.utc) < close_time:
            is_mkt_open = True
        else:
            is_mkt_open = False

    except Exception:
        is_mkt_open = False

    mkt_dict = {"mkt_open": open_time,
                "mkt_close": close_time,
                "is_mkt_open": is_mkt_open}

    return mkt_dict
