from strategies.all_strategy_files.database.database import createDB
from strategies.all_strategy_files.database.database import insertOHLCData
from big_algo_framework.data.td import TD
from tickers import tickers
import configparser
from datetime import timedelta
from datetime import datetime
import tda
import time

historic_data_table = "us_equity_historic_data"
streaming_data_table = "us_equity_streaming_data"
db = createDB("market_data", "config.ini")

config = configparser.ConfigParser()
config.read("config.ini")
tda_api = config['TDA_API']
api_key = tda_api["api_key"]
account_id = tda_api["account_id"]
redirect_uri = tda_api["redirect_uri"]

td_tf = [{
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

for ticker in tickers:
    act = TD(ticker=[ticker],
             api_key=api_key,
             account_id=account_id,
             redirect_uri=redirect_uri)

    #Lower TimeFrames
    for i in range(len(td_tf)):
        resp = act.get_hist_equity_data(period_type = td_tf[i]["periodType"],
                                 period = td_tf[i]["period"],
                                 frequency_type = td_tf[i]["freqType"],
                                 frequency = td_tf[i]["freq"],
                                 start_dt=start_dt,
                                 end_dt=end_dt)
        time.sleep(1)
        insertOHLCData(resp, db, ticker, td_tf[i]["timeframe"], historic_data_table, "US/Eastern")

    #Monthly TimeFrame
    resp = act.get_hist_equity_data(period_type=tda.client.Client.PriceHistory.PeriodType.YEAR,
                                    period=None,
                                    frequency_type=tda.client.Client.PriceHistory.FrequencyType.MONTHLY,
                                    frequency=tda.client.Client.PriceHistory.Frequency.MONTHLY,
                                    start_dt=yearly_start_dt,
                                    end_dt=yearly_end_dt)
    time.sleep(1)
    insertOHLCData(resp, db, ticker, "1 month", historic_data_table, "US/Eastern")
