from big_algo_framework.big.position_sizing import PositionSizing

class IbPositionSizing():
    def __init__(self, order_dict):
        self.order_dict = order_dict
        # self.order_dict["available_capital"] = float(self.order_dict["broker"].acc_dict[self.order_dict["funds"]])
        self.order_dict["available_capital"] = float(self.order_dict["funds"])

    def get_stocks_quantity(self):
        self.order_dict["risk_unit"] = abs(self.order_dict["entry"] - self.order_dict["sl"])
        position = PositionSizing(self.order_dict)
        quantity = position.stock_quantity()

        return quantity

    def get_options_quantity(self):
        self.order_dict["risk_unit"] = abs(self.order_dict["entry"] - self.order_dict["sl"])
        position = PositionSizing(self.order_dict)
        quantity = position.options_quantity()

        return quantity