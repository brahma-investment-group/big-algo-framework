from big_algo_framework.big.database import insertOHLCData
from big_algo_framework.big.tick_ohlc import tickToOHLC
from big_algo_framework.td.data_streaming import tdTimeSaleDataStreaming
from big_algo_framework.td.td_hist import tdHist
from datetime import timedelta
from datetime import datetime
import tda
import asyncio
import datetime
import time
from datetime import datetime

class getData():
    def __init__(self, db, tickers, historic_data_table, streaming_data_table):
        self.db = db
        self.tickers = tickers
        self.historic_data_table = historic_data_table
        self.streaming_data_table = streaming_data_table

    def get_historic_data(self):
        tf_props = [
            {
                #DAILY
                "period": None,
                "periodType": tda.client.Client.PriceHistory.PeriodType.YEAR,
                "freq": tda.client.Client.PriceHistory.Frequency.EVERY_MINUTE,
                "freqType": tda.client.Client.PriceHistory.FrequencyType.DAILY,
                "timeframe": "1 day",
            },

            {
                #30 MINS
                "period": None,
                "periodType": tda.client.Client.PriceHistory.PeriodType.DAY,
                "freq": tda.client.Client.PriceHistory.Frequency.EVERY_THIRTY_MINUTES,
                "freqType": tda.client.Client.PriceHistory.FrequencyType.MINUTE,
                "timeframe": "30 mins",
            },

            {
                #MINUTE
                "period": None,
                "periodType": tda.client.Client.PriceHistory.PeriodType.DAY,
                "freq": tda.client.Client.PriceHistory.Frequency.EVERY_MINUTE,
                "freqType": tda.client.Client.PriceHistory.FrequencyType.MINUTE,
                "timeframe": "1 min",
            }
        ]

        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=25)
        start_dt = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=9, minute=30, second=00)
        end_dt = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=16, minute=00, second=00)

        yearly_end_date = datetime.now()
        yearly_start_date = yearly_end_date - timedelta(weeks=520)
        yearly_start_dt = datetime(year=yearly_start_date.year, month=yearly_start_date.month, day=yearly_start_date.day, hour=9, minute=30, second=00)
        yearly_end_dt = datetime(year=yearly_end_date.year, month=yearly_end_date.month, day=yearly_end_date.day, hour=16, minute=00, second=00)

        for ticker in self.tickers:
            for i in range(len(tf_props)):
                act = tdHist(ticker=[ticker],
                             db = self.db,
                             period = tf_props[i]["period"],
                             periodType = tf_props[i]["periodType"],
                             freq = tf_props[i]["freq"],
                             freqType = tf_props[i]["freqType"],
                             timeframe = tf_props[i]["timeframe"],
                             start_dt=start_dt,
                             end_dt=end_dt)

                resp = act.get_hist()
                time.sleep(1)
                insertOHLCData(resp, self.db, ticker, tf_props[i]["timeframe"], self.historic_data_table)

            #Yearly TimeFrame
            act = tdHist(ticker=[ticker],
                         db = self.db,
                         period = None,
                         periodType = tda.client.Client.PriceHistory.PeriodType.YEAR,
                         freq = tda.client.Client.PriceHistory.Frequency.MONTHLY,
                         freqType = tda.client.Client.PriceHistory.FrequencyType.MONTHLY,
                         timeframe= "1 month",
                         start_dt=yearly_start_dt,
                         end_dt=yearly_end_dt)

            resp = act.get_hist()
            time.sleep(1)
            insertOHLCData(resp, self.db, ticker, "1 month", self.historic_data_table)

    def get_live_data(self):
        async def main():
            consumer = tdTimeSaleDataStreaming(self.db, self.tickers, self.streaming_data_table)
            consumer.initialize()
            await consumer.stream()
        asyncio.run(main())

    def convert_live_ohlc_candles(self):
        for ticker in self.tickers:
            one_min_tick_ohlc = tickToOHLC(db=self.db, ticker=[ticker], rule_tf="1min", timeframe="1 min", streaming_data_table=self.streaming_data_table, historic_data_table=self.historic_data_table)
            one_min_tick_ohlc.convert_tick_ohlc()

            thirty_min_tick_ohlc = tickToOHLC(db=self.db, ticker=[ticker], rule_tf="30min", timeframe="30 mins", streaming_data_table=self.streaming_data_table, historic_data_table=self.historic_data_table)
            thirty_min_tick_ohlc.convert_tick_ohlc()

            one_day_tick_ohlc = tickToOHLC(db=self.db, ticker=[ticker], rule_tf="24H", timeframe="1 day", streaming_data_table=self.streaming_data_table, historic_data_table=self.historic_data_table)
            one_day_tick_ohlc.convert_tick_ohlc()

            one_month_tick_ohlc = tickToOHLC(db=self.db, ticker=[ticker], rule_tf="MS", timeframe="1 month", streaming_data_table=self.streaming_data_table, historic_data_table=self.historic_data_table)
            one_month_tick_ohlc.convert_tick_ohlc()
