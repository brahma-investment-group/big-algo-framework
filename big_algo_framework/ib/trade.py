from big_algo_framework.ib.orders import *
from big_algo_framework.big.general import getEarningTickers
from big_algo_framework.ib.contracts import *
import time

myorder = BIGOrders()

def takeTrade(app, con, order_dict, dashboard_dict):
    # change this from "<" to ">" later
    if (order_dict["action"] == "BUY" and order_dict["tp2"] < order_dict["tp1"]) or \
            (order_dict["action"] == "SELL" and order_dict["tp2"] < order_dict["tp1"]):
        print("2>1")
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
    orders = db["orders"]
    earnings_tickers = getEarningTickers()

    # Lets check if we have an open order to enter the mkt. If we do, we close the order and cancel its child orders
    pending_positions = orders.find(orderType="STP LMT", status=("PreSubmitted", "Submitted"))

    for order_row in pending_positions:
        order_id = order_row['orderId']
        ticker = order_row['ticker']
        remaining = order_row['remaining']

        for i in range(len(earnings_tickers)):
            if earnings_tickers[i] == ticker:
                print("Ticker modifier is: ", ticker, " --- ", order_row)

                if remaining != 0:
                    app.cancelOrder(order_id)

    # Lets check if we are already in a position and if so, we change the takeprofit to MKT order to close the position at current price
    open_positions = orders.find(orderType="LMT", status=("PreSubmitted", "Submitted"))

    for order_row in open_positions:
        ticker = order_row['ticker']
        remaining = order_row['remaining']

        for i in range(len(earnings_tickers)):
            if earnings_tickers[i] == ticker:
                print("Ticker modifier is: ", ticker, " --- ", order_row)
                # Modify the order
                if remaining != 0:
                    cont = StockContract()
                    con = cont.getStockContract(ticker)

                    order_dict = {"orderId": order_row['orderId'],
                                  "action": order_row["action"],
                                  "quantity": order_row["remaining"],
                                  }

                    myorder.ModifyMarketOrder(app, con, order_dict)
