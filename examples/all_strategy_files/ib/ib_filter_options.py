from big_algo_framework.data.td import TDData
from big_algo_framework.big.options import filter_option_contract

class IbFilterOptions():
    def __init__(self, order_dict):
        self.order_dict = order_dict

    def filter_options(self):
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

        data = TDData()
        api_key = self.order_dict["tda_api"]

        # Based on the direction, derive the option price and build the order_dict
        if self.order_dict["direction"] == "Bullish" and self.order_dict["option_action"] == "BUY":
            options_dict["contract_type"] = "CALL"
            options_df = data.get_options_data(options_dict, api_key)
            filter_option_contract(self.order_dict, options_df)

        elif self.order_dict["direction"] == "Bullish" and self.order_dict["option_action"] == "SELL":
            options_dict["contract_type"] = "PUT"
            options_df = data.get_options_data(options_dict, api_key)
            filter_option_contract(self.order_dict, options_df)

        elif self.order_dict["direction"] == "Bearish" and self.order_dict["option_action"] == "BUY":
            options_dict["contract_type"] = "PUT"
            options_df = data.get_options_data(options_dict, api_key)
            filter_option_contract(self.order_dict, options_df)

        elif self.order_dict["direction"] == "Bearish" and self.order_dict["option_action"] == "SELL":
            options_dict["contract_type"] = "CALL"
            options_df = data.get_options_data(options_dict, api_key)
            filter_option_contract(self.order_dict, options_df)
