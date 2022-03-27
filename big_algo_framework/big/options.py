import pandas as pd
import numpy as np

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
