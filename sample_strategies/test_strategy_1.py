from big_algo_framework.strategies.abstract_strategy import *
from big_algo_framework.brokers.ib import *
import threading

class TestStrategy1(Strategy):
    def __init__(self):
        super().__init__()

        self.check_long = True
        self.check_short = True

        self.trade_long = True
        self.trade_short = True

        self.send_trade = True

        self.broker = IB()

    def initialize(self):
        self.broker.connect('127.0.0.1', 7497, 2)
        time.sleep(3)

        self.broker.reqPositions()
        time.sleep(3)

        self.broker.reqOpenOrders()
        time.sleep(3)

        def websocket_con():
            self.broker.run()

        con_thread = threading.Thread(target=websocket_con, daemon=True)
        con_thread.start()
        time.sleep(3)

    def start(self, order_dict):
        self.broker.initialize(self.broker, order_dict)

    def send_orders(self, client):
        self.broker.reqIds(1)
        time.sleep(1)
        my_order = self.broker.get_market_order(self.broker.orderId)
        self.broker.send_order(my_order)


x = TestStrategy1()
x.initialize()


order_dict = {"ticker": "MSFT",
              "sec_type": "STK",
              "currency": "USD",
              "exchange": "SMART",
              "primary_exchange": "SMART",
              "action": "BUY",
              "quantity": 10,
              "parent_order_id": "",
              "transmit": True,
              "orderId": x.broker.orderId}

x.start(order_dict)
x.send_orders(x.broker)



# x.execute("MSFT", "STK", "USD", "SMART", "SMART")
