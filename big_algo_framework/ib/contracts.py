from ibapi.contract import Contract

class StockContract():
    def __init__(self):
        self.contract = Contract()

    def getStockContract(self, symbol, sec_type="STK", currency="USD", exchange="SMART"):
        self.contract.symbol = symbol
        self.contract.secType = sec_type
        self.contract.currency = currency
        self.contract.exchange = exchange
        self.contract.PrimaryExch = exchange
        return self.contract

    def getQuantity(self, order_dict):
        totalRisk = order_dict["totalRisk"]
        riskPerShare = order_dict["riskPerShare"]

        quantity = totalRisk/riskPerShare
        return quantity


class ForexContract():
    def __init__(self):
        self.contract = Contract()

    def forexContract(self, symbol, sec_type="CASH", currency="USD", exchange="IDEALPRO"):
        self.contract.symbol = symbol
        self.contract.secType = sec_type
        self.contract.currency = currency
        self.contract.exchange = exchange
        return self.contract

