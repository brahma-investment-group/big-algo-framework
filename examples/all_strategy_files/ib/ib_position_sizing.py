from big_algo_framework.big.position_sizing import PositionSizing

class IbPositionSizing():
    def __init__(self, order_dict):
        self.order_dict = order_dict
        self.order_dict["available_capital"] = float(self.order_dict["funds"])

    def get_stocks_quantity(self):
        self.order_dict["risk_unit"] = abs(self.order_dict["entry"] - self.order_dict["sl"])
        position = PositionSizing(self.order_dict["available_capital"],
                                  self.order_dict["total_risk"],
                                  self.order_dict["total_risk_units"],
                                  self.order_dict["risk_unit"],
                                  self.order_dict["max_position_percent"],
                                  self.order_dict["entry"])
        quantity = position.stock_quantity()

        return quantity

    def get_options_quantity(self):
        self.order_dict["risk_unit"] = abs(self.order_dict["entry"] - self.order_dict["sl"])
        position = PositionSizing(self.order_dict["available_capital"],
                                  self.order_dict["total_risk"],
                                  self.order_dict["total_risk_units"],
                                  self.order_dict["risk_unit"],
                                  self.order_dict["max_position_percent"],
                                  self.order_dict["entry"])
        quantity = position.options_quantity(self.order_dict["multiplier"])

        return quantity