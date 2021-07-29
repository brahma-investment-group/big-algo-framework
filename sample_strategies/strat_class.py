from big_algo_framework.big.general import *
from big_algo_framework.big.indicators import *
from big_algo_framework.big.resample_price_indicators import resample
from big_algo_framework.ib.trade import *
import time

class Strat():
    def __init__(self, app, ticker, db):
        self.app = app
        self.ticker = ticker
        self.db = db
        self.indi = BIGIndicators()
        self.cont = StockContract()
        self.con = self.cont.getStockContract(ticker)

        self.tf_props = {
            "1 day": {'base_timeframe': '1 day', 'rule': '24H'},
        }

    def checkTradeConditions(self, direction, dashboard_dict):
        print("COMMENCING TICKER...: ", self.ticker)
        orders = self.db["orders"]
        order_results = orders.find(orderType="STP", status=("PreSubmitted", "Submitted"))

        ticker_pos = []
        for row in order_results:
            ticker_pos.append(row['ticker'])
        print(ticker_pos)

        if self.ticker not in ticker_pos:
            #DAILY TIME FRAME RULES
            daily_resample = resample(self.db, [self.ticker], self.tf_props["1 day"]["base_timeframe"], "1 day", self.tf_props["1 day"]["rule"])
            daily_df = daily_resample.resample_price()
            daily_df.reset_index(level=0, inplace=True)

            #Get daily ATR
            daily_df["ATR"] = self.indi.atr(daily_df, atr_length=14, atr_ma_type="ema", adjust=False)["ATR"]
            if daily_df["ATR"].iloc[-1] > 2:
                self.app.reqContractDetails(12, self.con)
                time.sleep(1)

                order_dict = {}

                order_dict = {"ticker": self.ticker,
                              "strategy": "my_strategy",
                              "entryTIF": "GTD",
                              "entryGoodTillDate": "20211029 10:30:00",
                              "OrderRef": "my_orderRed",
                              "entryPrice": 100,
                              "stopLossPrice": 50,
                              "totalRisk": 100,
                              "tp1": 150,
                              "tp2": 200
                }

                getAction(direction, order_dict)
                order_dict["quantity"] = self.cont.getQuantity(order_dict)

                dashboard_dict["ticker"] = self.ticker
                dashboard_dict["atr"] = daily_df["ATR"].iloc[-1]

                print("Sending orders...")
                takeTrade(self.app, self.con, order_dict, dashboard_dict)
                self.writeDashboard(order_dict, dashboard_dict)

    def writeDashboard(self, order_dict, dashboard_dict):
        table = self.db["strategy"]

        data = dict(parentOrderId1=dashboard_dict["parentOrderId1"],
                    profitOrderId1=dashboard_dict["profitOrderId1"],
                    stopLossOrderId1=dashboard_dict["stopLossOrderId1"],
                    parentOrderId2=dashboard_dict["parentOrderId2"],
                    profitOrderId2=dashboard_dict["profitOrderId2"],
                    stopLossOrderId2=dashboard_dict["stopLossOrderId2"],
                    entryPrice=order_dict["entryPrice"],
                    riskPerShare = order_dict["riskPerShare"],
                    ticker=dashboard_dict["ticker"])

        table.upsert(data, ['orderId'])
