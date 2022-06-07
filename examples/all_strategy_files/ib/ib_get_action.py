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
        self.order_dict["primary_exchange"] = ""
        self.order_dict["open_action"] = self.order_dict["option_action"]
        self.order_dict["close_action"] = "SELL" if self.order_dict["open_action"] == "BUY" else "BUY"
