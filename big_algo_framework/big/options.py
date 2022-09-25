import pandas as pd
import numpy as np

def filter_option_contract(direction, open_action, option_range, option_strikes, stock_price, option_expiry_days, options_df):
    if direction == "BULLISH" and open_action == "BUY":
        if option_range == "OTM":
            df = options_df.loc[(options_df['strikePrice'] >= stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        elif option_range == "ITM":
            df = options_df.loc[(options_df['strikePrice'] < stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=True if option_range == "OTM" else False)

        filtered_options = {
            "lastTradeDateOrContractMonth": dff.iloc[option_strikes - 1]["expirationDate"].strftime("%Y%m%d"),
            "strike": dff.iloc[option_strikes - 1]["strikePrice"],
            "right": 'C',
            "ask": dff.iloc[option_strikes - 1]["call_ask"],
            "bid": dff.iloc[option_strikes - 1]["call_bid"],
            "symbol": dff.iloc[option_strikes - 1]["call_symbol"],
            "multiplier": dff.iloc[-option_strikes]["call_multiplier"]
        }

        return filtered_options

    elif direction == "BULLISH" and open_action == "SELL":
        if option_range == "OTM":
            df = options_df.loc[(options_df['strikePrice'] <= stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        elif option_range == "ITM":
            df = options_df.loc[(options_df['strikePrice'] > stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=False if option_range == "OTM" else True)

        filtered_options = {
            "lastTradeDateOrContractMonth": dff.iloc[option_strikes - 1]["expirationDate"].strftime("%Y%m%d"),
            "strike": dff.iloc[option_strikes - 1]["strikePrice"],
            "right": 'P',
            "ask": dff.iloc[option_strikes - 1]["put_ask"],
            "bid": dff.iloc[option_strikes - 1]["put_bid"],
            "symbol": dff.iloc[option_strikes - 1]["put_symbol"],
            "multiplier": dff.iloc[-option_strikes]["put_multiplier"]
        }

        return filtered_options

    elif direction == "BEARISH" and open_action == "BUY":
        if option_range == "OTM":
            df = options_df.loc[(options_df['strikePrice'] <= stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        elif option_range == "ITM":
            df = options_df.loc[(options_df['strikePrice'] > stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=True if option_range == "OTM" else False)

        filtered_options = {
            "lastTradeDateOrContractMonth": dff.iloc[-option_strikes]["expirationDate"].strftime("%Y%m%d"),
            "strike": dff.iloc[-option_strikes]["strikePrice"],
            "right": 'P',
            "ask": dff.iloc[-option_strikes]["put_ask"],
            "bid": dff.iloc[-option_strikes]["put_bid"],
            "symbol": dff.iloc[-option_strikes]["put_symbol"],
            "multiplier": dff.iloc[-option_strikes]["put_multiplier"]
        }

        return filtered_options

    elif direction == "BEARISH" and open_action == "SELL":
        if option_range == "OTM":
            df = options_df.loc[(options_df['strikePrice'] >= stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        elif option_range == "ITM":
            df = options_df.loc[(options_df['strikePrice'] < stock_price) & (options_df['daysToExpiration'] >= option_expiry_days)]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=False if option_range == "OTM" else True)

        filtered_options = {
            "lastTradeDateOrContractMonth": dff.iloc[-option_strikes]["expirationDate"].strftime("%Y%m%d"),
            "strike": dff.iloc[-option_strikes]["strikePrice"],
            "right": 'C',
            "ask": dff.iloc[-option_strikes]["call_ask"],
            "bid": dff.iloc[-option_strikes]["call_bid"],
            "symbol": dff.iloc[-option_strikes]["call_symbol"],
            "multiplier": dff.iloc[-option_strikes]["call_multiplier"]
        }

        return filtered_options

def get_option_ratios(call_options, put_options, ticker):
    options_chain = pd.merge(call_options, put_options, how='outer',
                             on=['strikePrice', 'expirationDate', 'daysToExpiration'],
                             suffixes=("_call", "_put"))
    options_chain['expirationDate'] = pd.to_datetime(options_chain['expirationDate'], unit="ms")

    options_chain["call_put_volume"] = options_chain["call_totalVolume"] / options_chain["put_totalVolume"]
    options_chain["call_put_oi"] = options_chain["call_openInterest"] / options_chain["put_openInterest"]
    options_chain["call_volume_oi"] = options_chain["call_totalVolume"] / options_chain["call_openInterest"]

    options_chain["put_call_volume"] = options_chain["put_totalVolume"] / options_chain["call_totalVolume"]
    options_chain["put_call_oi"] = options_chain["put_openInterest"] / options_chain["call_openInterest"]
    options_chain["put_volume_oi"] = options_chain["put_totalVolume"] / options_chain["put_openInterest"]

    options_chain["ticker"] = ticker

    options_chain = options_chain.replace(np.nan, 0)
    options_chain = options_chain.replace([np.inf, -np.inf], 999999)

    return options_chain
