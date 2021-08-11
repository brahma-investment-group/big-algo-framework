from big_algo_framework.big.indicators import *

class resample:
    def __init__(self, ohlc_db, tickers, base_timeframe, resample_timeframe, rule):
        self.ohlc_db = ohlc_db
        self.tickers = tickers
        self.base_timeframe = base_timeframe
        self.resample_timeframe = resample_timeframe
        self.rule = rule

    def resample_price(self, historic_data_table):
        table = self.ohlc_db[historic_data_table]

        # Fetch the results for the specific ticker form the historic_data table
        # Create dataframe and set date_time as index and convert it to a python datetime object
        results = table.find(ticker=self.tickers[0], timeframe=self.base_timeframe, order_by=['date_time'])
        data = pd.DataFrame(results)
        data['date_time'] = pd.to_datetime(data['date_time'])

        # Resample lower time frame to to higher time frame OHLC candles
        # Drop the NA and reset index
        price_ohlc = data.resample(rule=self.rule, label='left', on='date_time', origin=data['date_time'][0]).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
        price_ohlc = price_ohlc.dropna()
        price_ohlc.reset_index(level=0, inplace=True)

        return price_ohlc
