from big_algo_framework.ib.orders import *
from big_algo_framework.big.general import getEarningTickers
from big_algo_framework.ib.contracts import *
import time
import pandas as pd

myorder = BIGOrders()

def takeTrade(app, con, order_dict, dashboard_dict):
    if (order_dict["action"] == "BUY" and order_dict["tp2"] > order_dict["tp1"]) or \
            (order_dict["action"] == "SELL" and order_dict["tp2"] < order_dict["tp1"]):
        app.reqIds(1)
        time.sleep(1)
        parentOrderId = app.orderId

        order_dict["quantity"] = order_dict["quantity"] / 2
        order_dict["profitPrice"] = order_dict["tp1"]

        dashboard_dict["parentOrderId1"] = parentOrderId
        dashboard_dict["profitOrderId1"] = parentOrderId + 1
        dashboard_dict["stopLossOrderId1"] = parentOrderId + 2
        myorder.sendBracketOrder(app, con, order_dict, dashboard_dict["parentOrderId1"], dashboard_dict["profitOrderId1"], dashboard_dict["stopLossOrderId1"])

        app.reqIds(1)
        time.sleep(1)
        parentOrderId = app.orderId

        order_dict["quantity"] = order_dict["quantity"]  #We dont have to divide by 2 here, since in the 1st order the result is divided by 2 and saved in the dict
        order_dict["profitPrice"] = order_dict["tp2"]

        dashboard_dict["parentOrderId2"] = parentOrderId
        dashboard_dict["profitOrderId2"] = parentOrderId + 1
        dashboard_dict["stopLossOrderId2"] = parentOrderId + 2
        myorder.sendBracketOrder(app, con, order_dict, dashboard_dict["parentOrderId2"], dashboard_dict["profitOrderId2"], dashboard_dict["stopLossOrderId2"])

        return dashboard_dict

    else:
        app.reqIds(1)
        time.sleep(1)
        parentOrderId = app.orderId

        order_dict["quantity"] = order_dict["quantity"]
        order_dict["profitPrice"] = order_dict["tp2"]

        dashboard_dict["parentOrderId1"] = parentOrderId
        dashboard_dict["profitOrderId1"] = parentOrderId + 1
        dashboard_dict["stopLossOrderId1"] = parentOrderId + 2

        dashboard_dict["parentOrderId2"] = -1
        dashboard_dict["profitOrderId2"] = -1
        dashboard_dict["stopLossOrderId2"] = -1
        myorder.sendBracketOrder(app, con, order_dict, dashboard_dict["parentOrderId1"], dashboard_dict["profitOrderId1"], dashboard_dict["stopLossOrderId1"])
        return dashboard_dict

def closeOnEarnings(db, app):
    earnings_tickers = getEarningTickers()

    # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders
    open_orders = pd.read_sql_query("select * from orders where order_type='STP LMT' and order_status IN ('PreSubmitted', 'Submitted'));", con=db)

    for ind in open_orders.index:
        ticker = open_orders['ticker'][ind]

        if ticker in earnings_tickers:
            order_id = open_orders['order_id'][ind]
            remaining = open_orders['remaining'][ind]

            if remaining != 0:
                app.cancelOrder(order_id)

    # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
    open_positions = pd.read_sql_query("select * from orders where order_type='LMT' and order_status IN ('PreSubmitted', 'Submitted'));", con=db)

    for ind in open_positions.index:
        ticker = open_positions['ticker'][ind]

        if ticker in earnings_tickers:
            order_id = open_positions['order_id'][ind]
            remaining = open_positions['remaining'][ind]
            action = open_positions['action'][ind]

            if remaining != 0:
                cont = StockContract()
                con = cont.getStockContract(ticker)

                order_dict = {"orderId": order_id,
                              "action": action,
                              "quantity": remaining,
                              }

                myorder.ModifyMarketOrder(app, con, order_dict)
