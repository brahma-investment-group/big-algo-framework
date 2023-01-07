class PositionSizing():
    def __init__(self, available_capital, total_risk, total_risk_units, risk_unit, max_position_percent, entry):
        self.quantity = 0
        self.available_capital = float(available_capital)
        self.total_risk = total_risk
        self.total_risk_units = total_risk_units
        self.risk_unit = risk_unit
        self.max_position_percent = max_position_percent
        self.entry = entry

        self.max_cost = self.available_capital * self.max_position_percent * 0.01

    def stock_quantity(self):
        if self.total_risk_units == "amount":
            self.quantity = int(self.total_risk / self.risk_unit)

        if self.total_risk_units == "percent":
            self.quantity = int(self.total_risk * self.available_capital * 0.01 / self.risk_unit)
            cost = self.quantity * self.entry

            if cost > self.max_cost:
                self.quantity = int(self.max_cost / self.entry)

        return self.quantity

    def options_quantity(self, multiplier):
        if self.total_risk_units == "amount":
            self.quantity = int(self.total_risk / (self.risk_unit * multiplier))

        if self.total_risk_units == "percent":
            self.quantity = int(self.total_risk * self.available_capital * 0.01 / (self.risk_unit * multiplier))
            cost = self.quantity * self.entry * multiplier

            if cost > self.max_cost:
                self.quantity = int(self.max_cost / (self.entry * multiplier))

        return self.quantity