class PositionSizing():
    def __init__(self, order_dict):
        self.quantity = 0
        self.available_capital = order_dict["available_capital"]
        self.total_risk = order_dict["total_risk"]
        self.total_risk_units = order_dict["total_risk_units"]
        self.risk_unit = order_dict["risk_unit"]
        self.max_position_percent = order_dict["max_position_percent"]
        self.entry = order_dict["entry"]

        self.max_cost = self.available_capital * self.max_position_percent * 0.01

    def stock_quantity(self):
        if self.total_risk_units == "amount":
            self.quantity = int(self.total_risk / self.risk_unit)

        if self.total_risk_units == "percent":
            self.quantity = int(self.total_risk * self.available_capital * 0.01 / self.risk_unit)
            cost = self.quantity * self.entry

            if cost > self.max_cost:
                self.quantity = int(self.max_cost / self.entry)

        print("Available Funds = ", self.available_capital)
        print("Quantity = ", self.quantity)

        return self.quantity

    def options_quantity(self):
        if self.total_risk_units == "amount":
            self.quantity = int(self.total_risk / self.risk_unit)

        if self.total_risk_units == "percent":
            self.quantity = int(self.total_risk * self.available_capital * 0.01 / self.risk_unit)

        return self.quantity