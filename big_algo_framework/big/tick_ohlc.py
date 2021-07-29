import pandas as pd

class tickToOHLC:
    def __init__(self, db, ticker, rule_tf, timeframe, streaming_data_table, historic_data_table):
        self.db = db
        self.ticker = ticker
        self.rule_tf = rule_tf
        self.timeframe = timeframe
        self.streaming_data_table = streaming_data_table
        self.historic_data_table = historic_data_table

    def convert_tick_ohlc(self):
        table1 = self.db[self.streaming_data_table]
        table2 = self.db[self.historic_data_table]

        # Fetch the results for the specific ticker form the streaming_data table
        # Create dataframe and set datetime as index and convert it to a python datetime object
        # Resample them to 1 min OHLC candles and drop the NA
        streaming_data = table1.find(ticker=self.ticker[0])
        data = pd.DataFrame(streaming_data)
        data = data.set_index(['datetime'])
        data.index = pd.to_datetime(data.index)
        data_ask = data.resample(self.rule_tf).agg({'price': 'ohlc', 'volume': 'sum'})
        data_ask = data_ask.dropna()

        # Flattening the multi-index dataframe to a single level dataframe
        data_ask.columns = data_ask.columns.to_series().str.join('')

        # Reanming the columns for the dataframe
        data_ask = data_ask.rename(columns={"priceopen": "open",
                                            "pricehigh": "high",
                                            "pricelow": "low",
                                            "priceclose": "close",
                                            "volumevolume": "volume"})

        # Reset the index and append ticker/timeframe columns to the dataframe.
        # Convert the dataframe to dictionary.
        data_ask.reset_index(level=0, inplace=True)
        data_ask["ticker"] = self.ticker[0]
        data_ask["timeframe"] = self.timeframe
        rows = data_ask.to_dict('records')

        # Append each row to the database table
        for row in rows:
            print(row)
            table2.upsert(row, ['datetime', 'ticker', 'timeframe'])