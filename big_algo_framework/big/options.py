import pandas as pd
import numpy as np

def filter_option_contract(order_dict, options_df):
    if order_dict["direction"] == "Bullish" and order_dict["option_action"] == "BUY":
        if order_dict["option_range"] == "OTM":
            df = options_df.loc[(options_df['strikePrice'] >= order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        elif order_dict["option_range"] == "ITM":
            df = options_df.loc[(options_df['strikePrice'] < order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=True if order_dict["option_range"] == "OTM" else False)

        order_dict["lastTradeDateOrContractMonth"] = dff.iloc[order_dict["option_strikes"] - 1]["expirationDate"].strftime("%Y%m%d")
        order_dict["strike"] = dff.iloc[order_dict["option_strikes"] - 1]["strikePrice"]
        order_dict["right"] = 'C'
        order_dict["ask"] = dff.iloc[order_dict["option_strikes"] - 1]["call_ask"]
        order_dict["bid"] = dff.iloc[order_dict["option_strikes"] - 1]["call_bid"]
        order_dict["multiplier"] = dff.iloc[-order_dict["option_strikes"]]["call_multiplier"]

    elif order_dict["direction"] == "Bullish" and order_dict["option_action"] == "SELL":
        if order_dict["option_range"] == "OTM":
            df = options_df.loc[(options_df['strikePrice'] <= order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        elif order_dict["option_range"] == "ITM":
            df = options_df.loc[(options_df['strikePrice'] > order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=False if order_dict["option_range"] == "OTM" else True)

        order_dict["lastTradeDateOrContractMonth"] = dff.iloc[order_dict["option_strikes"] - 1]["expirationDate"].strftime("%Y%m%d")
        order_dict["strike"] = dff.iloc[order_dict["option_strikes"] - 1]["strikePrice"]
        order_dict["right"] = 'P'
        order_dict["ask"] = dff.iloc[order_dict["option_strikes"] - 1]["put_ask"]
        order_dict["bid"] = dff.iloc[order_dict["option_strikes"] - 1]["put_bid"]
        order_dict["multiplier"] = dff.iloc[-order_dict["option_strikes"]]["put_multiplier"]

    elif order_dict["direction"] == "Bearish" and order_dict["option_action"] == "BUY":
        if order_dict["option_range"] == "OTM":
            df = options_df.loc[(options_df['strikePrice'] <= order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        elif order_dict["option_range"] == "ITM":
            df = options_df.loc[(options_df['strikePrice'] > order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=True if order_dict["option_range"] == "OTM" else False)

        order_dict["lastTradeDateOrContractMonth"] = dff.iloc[-order_dict["option_strikes"]]["expirationDate"].strftime("%Y%m%d")
        order_dict["strike"] = dff.iloc[-order_dict["option_strikes"]]["strikePrice"]
        order_dict["right"] = 'P'
        order_dict["ask"] = dff.iloc[-order_dict["option_strikes"]]["put_ask"]
        order_dict["bid"] = dff.iloc[-order_dict["option_strikes"]]["put_bid"]
        order_dict["multiplier"] = dff.iloc[-order_dict["option_strikes"]]["put_multiplier"]

    elif order_dict["direction"] == "Bearish" and order_dict["option_action"] == "SELL":
        if order_dict["option_range"] == "OTM":
            df = options_df.loc[(options_df['strikePrice'] >= order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        elif order_dict["option_range"] == "ITM":
            df = options_df.loc[(options_df['strikePrice'] < order_dict["entry"]) & (options_df['daysToExpiration'] >= order_dict["option_expiry_days"])]
        dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
        dff = dff.sort_values(by='strikePrice', ascending=False if order_dict["option_range"] == "OTM" else True)

        order_dict["lastTradeDateOrContractMonth"] = dff.iloc[-order_dict["option_strikes"]]["expirationDate"].strftime("%Y%m%d")
        order_dict["strike"] = dff.iloc[-order_dict["option_strikes"]]["strikePrice"]
        order_dict["right"] = 'C'
        order_dict["ask"] = dff.iloc[-order_dict["option_strikes"]]["call_ask"]
        order_dict["bid"] = dff.iloc[-order_dict["option_strikes"]]["call_bid"]
        order_dict["multiplier"] = dff.iloc[-order_dict["option_strikes"]]["call_multiplier"]

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
