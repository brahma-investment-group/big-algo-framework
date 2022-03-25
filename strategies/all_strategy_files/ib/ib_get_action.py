from strategies.all_strategy_files.data.get_options_data import getOptions1

class IbGetAction():
    def __init__(self, order_dict):
        self.order_dict = order_dict

    def get_stocks_action(self):
        if self.order_dict["direction"] == "Bullish":
            self.order_dict["open_action"] = "BUY"
            self.order_dict["close_action"] = "SELL"
        elif self.order_dict["direction"] == "Bearish":
            self.order_dict["open_action"] = "SELL"
            self.order_dict["close_action"] = "BUY"

    def get_options_action(self):
        options_dict = {
            "days_forward": 10,
            "ticker": self.order_dict["ticker"],
            "strike_count": '',
            "include_quotes": "FALSE",
            "strategy": "SINGLE",
            "interval": '',
            "strike": '',
            "range": self.order_dict["option_range"],
            "volatility": '',
            "underlying_price": '',
            "interest_rate": '',
            "days_to_expiration": '',
            "exp_month": "ALL",
            "option_type": "ALL"
        }

        # Based on the direction, derive the option price and build the order_dict
        if self.order_dict["direction"] == "Bullish" and self.order_dict["option_action"] == "BUY":
            options_dict["contract_type"] = "CALL"
            options_df = getOptions1(options_dict)

            if self.order_dict["option_range"] == "OTM":
                df = options_df.loc[(options_df['strikePrice'] >= self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            elif self.order_dict["option_range"] == "ITM":
                df = options_df.loc[(options_df['strikePrice'] < self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
            dff = dff.sort_values(by='strikePrice', ascending=True if self.order_dict["option_range"] == "OTM" else False)

            self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[self.order_dict["option_strikes"] - 1]["expirationDate"].strftime("%Y%m%d")
            self.order_dict["strike"] = dff.iloc[self.order_dict["option_strikes"] - 1]["strikePrice"]
            self.order_dict["right"] = 'C'
            self.order_dict["delta"] = dff.iloc[self.order_dict["option_strikes"] - 1]["call_delta"]
            self.order_dict["multiplier"] = dff.iloc[-self.order_dict["option_strikes"]]["call_multiplier"]

        elif self.order_dict["direction"] == "Bullish" and self.order_dict["option_action"] == "SELL":
            options_dict["contract_type"] = "PUT"
            options_df = getOptions1(options_dict)

            if self.order_dict["option_range"] == "OTM":
                df = options_df.loc[(options_df['strikePrice'] <= self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            elif self.order_dict["option_range"] == "ITM":
                df = options_df.loc[(options_df['strikePrice'] > self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
            dff = dff.sort_values(by='strikePrice', ascending=False if self.order_dict["option_range"] == "OTM" else True)

            self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[self.order_dict["option_strikes"] - 1]["expirationDate"].strftime("%Y%m%d")
            self.order_dict["strike"] = dff.iloc[self.order_dict["option_strikes"] - 1]["strikePrice"]
            self.order_dict["right"] = 'P'
            self.order_dict["delta"] = dff.iloc[self.order_dict["option_strikes"] - 1]["put_delta"]
            self.order_dict["multiplier"] = dff.iloc[-self.order_dict["option_strikes"]]["put_multiplier"]

        elif self.order_dict["direction"] == "Bearish" and self.order_dict["option_action"] == "BUY":
            options_dict["contract_type"] = "PUT"
            options_df = getOptions1(options_dict)

            if self.order_dict["option_range"] == "OTM":
                df = options_df.loc[(options_df['strikePrice'] <= self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            elif self.order_dict["option_range"] == "ITM":
                df = options_df.loc[(options_df['strikePrice'] > self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
            dff = dff.sort_values(by='strikePrice', ascending=True if self.order_dict["option_range"] == "OTM" else False)

            self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[-self.order_dict["option_strikes"]][
                "expirationDate"].strftime("%Y%m%d")
            self.order_dict["strike"] = dff.iloc[-self.order_dict["option_strikes"]]["strikePrice"]
            self.order_dict["right"] = 'P'
            self.order_dict["delta"] = dff.iloc[-self.order_dict["option_strikes"]]["put_delta"]
            self.order_dict["multiplier"] = dff.iloc[-self.order_dict["option_strikes"]]["put_multiplier"]

        elif self.order_dict["direction"] == "Bearish" and self.order_dict["option_action"] == "SELL":
            options_dict["contract_type"] = "CALL"
            options_df = getOptions1(options_dict)

            if self.order_dict["option_range"] == "OTM":
                df = options_df.loc[(options_df['strikePrice'] >= self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            elif self.order_dict["option_range"] == "ITM":
                df = options_df.loc[(options_df['strikePrice'] < self.order_dict["entry"]) & (options_df['daysToExpiration'] >= self.order_dict["option_expiry_days"])]
            dff = df[df["daysToExpiration"] == df["daysToExpiration"].min()]
            dff = dff.sort_values(by='strikePrice', ascending=False if self.order_dict["option_range"] == "OTM" else True)

            self.order_dict["lastTradeDateOrContractMonth"] = dff.iloc[-self.order_dict["option_strikes"]]["expirationDate"].strftime("%Y%m%d")
            self.order_dict["strike"] = dff.iloc[-self.order_dict["option_strikes"]]["strikePrice"]
            self.order_dict["right"] = 'C'
            self.order_dict["delta"] = dff.iloc[-self.order_dict["option_strikes"]]["call_delta"]
            self.order_dict["multiplier"] = dff.iloc[-self.order_dict["option_strikes"]]["call_multiplier"]

        # Build order_dict and get the contract
        self.order_dict["primary_exchange"] = ""
        self.order_dict["open_action"] = self.order_dict["option_action"]
        self.order_dict["close_action"] = "SELL" if self.order_dict["open_action"] == "BUY" else "BUY"


