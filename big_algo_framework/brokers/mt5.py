import MetaTrader5 as mt5
from big_algo_framework.brokers.abstract_broker import Broker

class MT(Broker):
    def __init__(self):
        pass

    def init_client(self, login, server, password):
        res = mt5.initialize(login=login, server=server, password=password)

        if res:
            print("Sucessfully Connected To MT5")
        else:
            print("Connection to MT5 Failed, Error Code =", mt5.last_error())
            quit()

    def get_market_order(self, order_dict):
        pass
        # market_order = {
        #     "action": mt5.TRADE_ACTION_DEAL,
        #     "symbol": order_dict["ticker"],
        #     "volume": order_dict["mkt_quantity"],
        #     "type": order_dict["mkt_action"],
        #     "tp": order_dict["mkt_tp"],
        #     "sl": order_dict["mkt_sl"],
        #     "deviation": order_dict["deviation"],
        #     "magic": order_dict["magic"],
        #     "comment": order_dict["comment"],
        #     "type_time": order_dict["mkt_time_in_force"],
        #     "type_filling": mt5.ORDER_FILLING_IOC
        # }

        # return market_order

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

    def get_stop_limit_order(self, order_dict):
        pass

    def get_stop_order(self, order_dict):
        pass

    def send_bracket_order(self, order_dict):
        pass

    def send_order(self, order_dict):
        res = mt5.order_send(order_dict)
        if res.retcode != mt5.TRADE_RETCODE_DONE:
            print("Order Sending Failed, retcode={}".format(res.retcode))
            print(res)
