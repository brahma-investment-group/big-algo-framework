from get_options_data import *
from datetime import datetime

print("start time: ",  datetime.now())
ticker = "SPY"
entry = 431.24

options_dict = {
    "days_forward": 10,
    "ticker": "SPY",
    "strike_count": '',
    "include_quotes": "FALSE",
    "strategy": "SINGLE",
    "interval": '',
    "strike": '',
    "range": "OTM",
    "volatility": '',
    "underlying_price": '',
    "interest_rate": '',
    "days_to_expiration": '',
    "exp_month": "ALL",
    "option_type": "ALL"
}

options_dict["contract_type"] = "CALL"

options_df = getOptions1(options_dict)
print(options_df)

df = options_df.loc[(options_df['strikePrice'] >= entry) & (options_df['daysToExpiration'] >=2)]
dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]

exp_date = dff.iloc[0]["expirationDate"].strftime("%Y%m%d")
strike = dff.iloc[0]["strikePrice"]
price = dff.iloc[0]["call_ask"]


print("Ticker: ", ticker)
print("Entry: ", entry)
print("Exp Date: ", exp_date)
print("Strike: ", strike)
print("Call Ask: ", price)

print("end time: ",  datetime.now())
