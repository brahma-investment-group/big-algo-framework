from examples.ib_orb import config
from ibapi.order_condition import PriceCondition
from random import randint
import time
from datetime import timedelta

class IbSendOrders():
    def __init__(self, order_dict, dashboard_dict):
        self.order_dict = order_dict
        self.dashboard_dict = {}
        self.dashboard_dict[1] = dashboard_dict

    def get_contract(self):
        # Request the contract for the asset that we are trading
        self.order_dict["con"] = self.order_dict["broker"].get_contract(self.order_dict)
        time.sleep(1)
        # Using the contract, request details like mintick
        self.order_dict["broker"].reqContractDetails(randint(0, 10000), self.order_dict["con"])
        time.sleep(1)

    def get_underlying_contract(self):
        # Form the dictionary for the underlying and get the contract
        stock_dict = {"ticker": self.order_dict["ticker"],
                      "sec_type": "STK",
                      "currency": self.order_dict["currency"],
                      "exchange": self.order_dict["exchange"],
                      "primary_exchange": self.order_dict["primary_exchange"],
                      "lastTradeDateOrContractMonth": "",
                      "strike": "",
                      "right": "",
                      "multiplier": ""}
        stock_contract = self.order_dict["broker"].get_contract(stock_dict)
        time.sleep(1)
        # Using the underlying contract, request details like mintick
        self.order_dict["broker"].reqContractDetails(randint(0, 10000), stock_contract)
        time.sleep(1)
        stocks_min_tick = self.order_dict["broker"].mintick

        # Adjust the entry/sl/tp to take into account the mintick
        # TODO: Replace "%" formula with truncate function from big folder
        self.order_dict["entry"] = self.order_dict["entry"] - (self.order_dict["entry"] % stocks_min_tick)
        self.order_dict["tp1"] = self.order_dict["tp1"] - (self.order_dict["tp1"] % stocks_min_tick)
        self.order_dict["tp2"] = self.order_dict["tp2"] - (self.order_dict["tp2"] % stocks_min_tick)
        self.order_dict["sl"] = self.order_dict["sl"] - (self.order_dict["sl"] % stocks_min_tick)

        # Price/Time conditions
        x = True if self.order_dict["direction"] == "Bullish" else False
        y = False if self.order_dict["direction"] == "Bullish" else True
        self.parent_order_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, self.order_dict["broker"].conid, stock_contract.exchange, y, self.order_dict["entry"])
        self.sl_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, self.order_dict["broker"].conid, stock_contract.exchange, y, self.order_dict["sl"])
        self.tp_price_condition = PriceCondition(PriceCondition.TriggerMethodEnum.Default, self.order_dict["broker"].conid, stock_contract.exchange, x, self.order_dict["tp1"])
        time.sleep(1)

    def send_underlying_mkt_order(self):
        self.get_contract()
        self.get_underlying_contract()

        # Parent Order for Order 1
        self.order_dict["order_id"] = self.order_dict["order_id"] + 1

        self.order_dict["mkt_order_id"] = self.order_dict["order_id"]
        parent_id = self.order_dict["mkt_order_id"]
        self.dashboard_dict[1]["parent_order_id"] = self.order_dict["order_id"]

        self.order_dict["mkt_action"] = self.order_dict["open_action"]
        self.order_dict["mkt_quantity"] = self.order_dict["quantity"]
        self.order_dict["mkt_parent_order_id"] = ""
        self.order_dict["mkt_time_in_force"] = "GTD"
        self.order_dict["mkt_good_till_date"] = self.order_dict["gtd"].strftime('%Y%m%d %H:%M:%S')
        self.order_dict["mkt_transmit"] = False

        order = self.order_dict["broker"].get_market_order(self.order_dict)
        order.conditions.append(self.parent_order_price_condition)
        self.order_dict["broker"].send_order(self.order_dict, self.order_dict["con"], order)

        # Stoploss Order for Order 1
        self.order_dict["order_id"] = self.order_dict["order_id"] + 1

        self.order_dict["mkt_order_id"] = self.order_dict["order_id"]
        self.order_dict["mkt_parent_order_id"] = parent_id
        self.dashboard_dict[1]["stoploss_order_id"] = self.order_dict["order_id"]

        self.order_dict["mkt_action"] = self.order_dict["close_action"]
        self.order_dict["mkt_quantity"] = self.order_dict["quantity"]
        self.order_dict["mkt_time_in_force"] = "GTC"
        self.order_dict["mkt_good_till_date"] = ""
        self.order_dict["mkt_transmit"] = False

        order = self.order_dict["broker"].get_market_order(self.order_dict)
        order.conditions.append(self.sl_price_condition)
        self.order_dict["broker"].send_order(self.order_dict, self.order_dict["con"], order)

        # Profit Order for Order 1
        self.order_dict["order_id"] = self.order_dict["order_id"] + 1

        self.order_dict["mkt_order_id"] = self.order_dict["order_id"]
        self.order_dict["mkt_parent_order_id"] = parent_id
        self.dashboard_dict[1]["profit_order_id"] = self.order_dict["order_id"]

        self.order_dict["mkt_action"] = self.order_dict["close_action"]
        self.order_dict["mkt_quantity"] = self.order_dict["quantity"]
        self.order_dict["mkt_time_in_force"] = "GTC"
        self.order_dict["mkt_good_till_date"] = ""
        self.order_dict["mkt_transmit"] = True

        order = self.order_dict["broker"].get_market_order(self.order_dict)
        order.conditions.append(self.tp_price_condition)
        self.order_dict["broker"].send_order(self.order_dict, self.order_dict["con"], order)

        return self.order_dict["order_id"]

    def send_lmt_stp_order(self):
        self.get_contract()
        cont_min_tick = self.order_dict["broker"].mintick

        s = str(cont_min_tick)
        digits = len(s) - s.index('.') - 1

        # Parent Order for Order 1
        self.order_dict["order_id"] = self.order_dict["order_id"] + 1
        self.order_dict["slo_order_id"] = self.order_dict["order_id"]
        self.dashboard_dict[1]["parent_order_id"] = self.order_dict["order_id"]

        self.order_dict["slo_action"] = self.order_dict["open_action"]
        self.order_dict["slo_quantity"] = self.order_dict["quantity"]
        self.order_dict["slo_stop_price"] = self.order_dict["entry"]
        self.order_dict["slo_limit_price"] = self.order_dict["entry"] * 1.00 # Setting limit price to 10% higher than stop price, so that in fast moving markets, we can still get an entry!
        self.order_dict["slo_time_in_force"] = "GTD"
        self.order_dict["slo_good_till_date"] = (self.order_dict["gtd"] + timedelta(minutes=-15)).strftime('%Y%m%d %H:%M:%S')
        self.order_dict["slo_good_after_date"] = ""
        self.order_dict["slo_transmit"] = False

        order1 = self.order_dict["broker"].get_stop_limit_order(self.order_dict, digits)

        # Profit Order for Order 1
        self.order_dict["order_id"] = self.order_dict["order_id"] + 1
        self.order_dict["mkt_order_id"] = self.order_dict["order_id"]
        self.dashboard_dict[1]["profit_order_id"] = self.order_dict["order_id"]

        self.order_dict["mkt_action"] = self.order_dict["close_action"]
        self.order_dict["mkt_quantity"] = self.order_dict["quantity"]
        self.order_dict["mkt_time_in_force"] = "GAT"
        self.order_dict["mkt_good_till_date"] = ""
        self.order_dict["mkt_good_after_date"] = (self.order_dict["gtd"] + timedelta(minutes=-5)).strftime('%Y%m%d %H:%M:%S')
        self.order_dict["mkt_transmit"] = False

        order2 = self.order_dict["broker"].get_market_order(self.order_dict)

        # Stoploss Order for Order 1
        self.order_dict["order_id"] = self.order_dict["order_id"] + 1
        self.order_dict["so_order_id"] = self.order_dict["order_id"]
        self.dashboard_dict[1]["stoploss_order_id"] = self.order_dict["order_id"]

        self.order_dict["so_action"] = self.order_dict["close_action"]
        self.order_dict["so_quantity"] = self.order_dict["quantity"]
        self.order_dict["so_stop_price"] = self.order_dict["sl"]
        self.order_dict["so_time_in_force"] = "GTC"
        self.order_dict["so_good_till_date"] = ""
        self.order_dict["so_good_after_date"] = ""
        self.order_dict["so_transmit"] = True

        order3 = self.order_dict["broker"].get_stop_order(self.order_dict, digits)
        order3 = self.order_dict["broker"].get_trailing_stop_order([order3], "amount", self.order_dict["risk"], "", digits)

        oto_order = [order1, order2, order3]
        self.order_dict["broker"].get_oto_order(oto_order)

        final_orders = [order1, order2, order3]
        for o in final_orders:
            self.order_dict["broker"].send_order(o.orderId, self.order_dict["con"], o)

        return self.order_dict["order_id"]
