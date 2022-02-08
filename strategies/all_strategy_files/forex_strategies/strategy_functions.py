import MetaTrader5 as mt5

class StrategyFunctions():
    def __init__(self, ticker):
        self.ticker = ticker

    def set_strategy_status(self):
        pass


    def is_exist_positions(self):
        positions = mt5.positions_get(symbol=self.ticker)

        if len(positions) > 0:
            print("Total positions =", len(positions))
            for position in positions:
                print(position)
            return True

        else:
            return False

    def is_exist_orders(self):
        orders = mt5.orders_get(symbol=self.ticker)

        if len(orders) > 0:
            print("Total orders =", len(orders))
            for order in orders:
                print(order)
            return True

        else:
            return False




def closeAllPositions(self):
        pass
        # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders


        # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
