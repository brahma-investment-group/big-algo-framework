class PositionSizing():
    def __init__(self, order_dict):
        self.quantity = 0
        self.available_capital = order_dict["available_capital"]
        self.total_risk = order_dict["total_risk"]
        self.total_risk_units = order_dict["total_risk_units"]
        self.risk_unit = order_dict["risk_unit"]

    def stock_quantity(self, order_dict):
        if self.total_risk_units == "amount":
            self.quantity = int(self.total_risk / self.risk_unit)

        if self.total_risk_units == "percent":
            self.quantity = int(self.total_risk * self.available_capital * 0.01 / self.risk_unit)

        return self.quantity

    def options_quantity(self, order_dict):
        if self.total_risk_units == "amount":
            self.quantity = int(self.total_risk / self.risk_unit)

        if self.total_risk_units == "percent":
            self.quantity = int(self.total_risk * self.available_capital * 0.01 / self.risk_unit)

        print("Available Funds = ", self.available_capital)
        print("Quantity = ", self.quantity)

        return self.quantity