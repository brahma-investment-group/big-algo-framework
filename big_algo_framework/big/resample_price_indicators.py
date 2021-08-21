from big_algo_framework.big.indicators import *

class resample:
    def __init__(self, db, tickers, base_timeframe, resample_timeframe, rule, historic_data_table, streaming_data_table, tick_rule):
        self.db = db
        self.tickers = tickers
        self.base_timeframe = base_timeframe
        self.resample_timeframe = resample_timeframe
        self.rule = rule
        self.historic_data_table = historic_data_table
        self.streaming_data_table = streaming_data_table
        self.tick_rule = tick_rule

    def resample_price(self):
        # Fetch the results for the specific ticker form the historic_data table
        hist_data = pd.read_sql_query("select * from {} where ticker = '{}'".format(self.historic_data_table + "_" + self.base_timeframe.replace(" ", "_"), self.tickers[0]),
                                           con=self.db).sort_values("date_time", ascending=True)

        # Call the function responsible for fetching tick data and converting it to the base timeframe.
        # Then concat the historic df and streaming df
        tick_data = self.convert_tick_ohlc()
        data = pd.concat([hist_data, tick_data])
        data.reset_index(level=0, inplace=True)

        price_ohlc = pd.DataFrame()

        if not data.empty:
            data['date_time'] = pd.to_datetime(data['date_time'], utc=True)

            # Resample lower time frame to to higher time frame OHLC candles
            # Drop the NA and reset index
            price_ohlc = data.resample(rule=self.rule, label='left', on='date_time', origin=data['date_time'][0]).agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'})
            price_ohlc = price_ohlc.dropna()
            price_ohlc.reset_index(level=0, inplace=True)

        return price_ohlc

    def convert_tick_ohlc(self):
        # Fetch the results for the specific ticker form the streaming_data table
        # Create dataframe and set date_time as index and convert it to a python datetime object
        # Resample them to "base timeframe" OHLC candles and drop the NA
        data = pd.read_sql_query(
            "select * from {} where ticker = '{}'".format(self.streaming_data_table, self.tickers[0]),
            con=self.db).sort_values("date_time", ascending=True)

        data_ask = pd.DataFrame()
        if not data.empty:
            data = data.set_index(['date_time'])
            data.index = pd.to_datetime(data.index)
            data_ask = data.resample(self.tick_rule).agg({'price': 'ohlc', 'volume': 'sum'})
            data_ask = data_ask.dropna()

            # Flattening the multi-index dataframe to a single level dataframe
            data_ask.columns = data_ask.columns.to_series().str.join('')

            # Renaming the columns for the dataframe
            data_ask = data_ask.rename(columns={"priceopen": "open",
                                                "pricehigh": "high",
                                                "pricelow": "low",
                                                "priceclose": "close",
                                                "volumevolume": "volume"})

            # Reset the index and append ticker/timeframe columns to the dataframe.
            # Convert the dataframe to dictionary.
            data_ask.reset_index(level=0, inplace=True)
            data_ask["ticker"] = self.tickers[0]

        return data_ask