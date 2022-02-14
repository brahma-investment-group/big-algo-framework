class PositionSizing():
    def __init__(self):
        pass

    def stock_quantity(self, order_dict):
        quantity = 0

        available_capital = order_dict["available_capital"]
        total_risk = order_dict["total_risk"]
        total_risk_units = order_dict["total_risk_units"]
        risk_share = order_dict["risk_share"]

        if total_risk_units == "amount":
            quantity = int(total_risk / risk_share)

        if total_risk_units == "percent":
            quantity = int(total_risk * available_capital * 0.01 / risk_share)

        return quantity

    def options_quantity(self, order_dict):
        quantity = 0

        available_capital = order_dict["available_capital"]
        total_risk = order_dict["total_risk"]
        total_risk_units = order_dict["total_risk_units"]
        risk_contract = order_dict["risk_contract"] * 100
        price = order_dict["ask_price"] * 100

        if total_risk_units == "amount":
            quantity = int(total_risk / risk_contract)

        if total_risk_units == "percent":
            quantity = int(total_risk * available_capital * 0.01 / risk_contract )

        print("Available Funds = ", available_capital)
        print("Contract Full Price = ", price)
        print("Quantity = ", quantity)

        return quantity