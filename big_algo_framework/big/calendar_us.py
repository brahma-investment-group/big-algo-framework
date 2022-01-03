import datetime
import pytz
import pandas_market_calendars as mcal

def is_mkt_open(market, start_date=datetime.date.today(), end_date=datetime.date.today(), timestamp=datetime.datetime.now(tz=datetime.timezone.utc).timestamp()):
    """Check if markets are currently open using pandas_market_calendars"""

    #timestamp in seconds
    trading_day = mcal.get_calendar(market).schedule(start_date=start_date, end_date=end_date)

    if trading_day.size:
        try:
            desired_dt = datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)

            open_time = trading_day.iloc[0][0]
            close_time = trading_day.iloc[0][1]

            if open_time < desired_dt < close_time:
                is_mkt_open = True
            else:
                is_mkt_open = False

        except Exception:
            is_mkt_open = False

        mkt_dict = {"mkt_open": open_time,
                    "mkt_close": close_time,
                    "is_mkt_open": is_mkt_open}

    else:
        mkt_dict = {"mkt_open": datetime.datetime.now(tz=datetime.timezone.utc),
                    "mkt_close": datetime.datetime.now(tz=datetime.timezone.utc),
                    "is_mkt_open": False}  # Not checking is_open since we are on TV now!!!

    return mkt_dict


