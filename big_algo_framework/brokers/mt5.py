import MetaTrader5 as mt5
from big_algo_framework.brokers.abstract_broker import Broker

class MT(Broker):
    def __init__(self, login, server, password):
        res = mt5.initialize(login=login, server=server, password=password)

        if res:
            print("Sucessfully Connected To MT5")
        else:
            print("Connection to MT5 Failed, Error Code =", mt5.last_error())
            quit()

    def connect_broker(self):
        pass

    def get_market_order(self):
        pass

    def get_stop_limit_order(self):
        pass

    def get_limit_order(self, order_dict):
        limit_order = {
            "action": mt5.TRADE_ACTION_PENDING,
            "magic": order_dict["magic"],
            "order": order_dict["order_id"],
            "symbol": order_dict["ticker"],
            "volume": order_dict["lo_quantity"],
            "price": order_dict["lo_price"],
            "sl": order_dict["lo_sl"],
            "tp": order_dict["lo_tp"],
            "deviation": order_dict["deviation"],
            "type": order_dict["lo_type"],
            "type_filling": mt5.ORDER_FILLING_IOC,
            "type_time": order_dict["lo_time_in_force"],
            "expiration": order_dict["expiration"],
            "comment": order_dict["comment"],
            "position": order_dict["position_id"],
            "position_by": order_dict["position_by"]
        }

        return limit_order

    
    def get_stop_order(self):
        pass

    def send_oto_order(self):
        pass

    def send_oco_order(self):
        pass

    def send_order(self, order_dict):
        res = mt5.order_send(order_dict)
        if res.retcode != mt5.TRADE_RETCODE_DONE:
            print("Order Sending Failed, retcode={}".format(res.retcode))
            print(res)
    
    def get_order(self, order_dict):
        orders = mt5.orders_get(symbol=order_dict["ticker"])

    def get_all_orders(self):
        orders = mt5.orders_get()

        if len(orders) > 0:
            print("Total orders =", len(orders))
            for order in orders:
                print(order)
            return True

        else:
            return False
    
    def get_position(self):
        pass

    def get_all_positions(self, order_dict):
        positions = mt5.positions_get(symbol=order_dict["ticker"])

        if len(positions) > 0:
            print("Total positions =", len(positions))
            for position in positions:
                print(position)
            return True

        else:
            return False
    
    def cancel_order(self):
        pass

    def cancel_all_orders(self):
        pass

    def close_position(self):
        pass

    def close_all_positions(self):
        pass
