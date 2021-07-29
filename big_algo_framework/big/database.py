from mysql.connector import connect, Error
import dataset
import pymysql
import time
import numpy as np
import configparser

#CREATE DATABASE
def createDB(db_name, config_path):
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['DATABASE']

        conn = pymysql.connect(host=database["host"],
                               user=database["user"],
                               password=database["password"])
        conn.cursor().execute('CREATE DATABASE IF NOT EXISTS {}' .format(db_name))

        db = dataset.connect("mysql+pymysql://root:ibalgo2021@127.0.0.1:3306/{}" . format(db_name))
        return db

    except Error as e:
        print(e)

def insertOHLCData(resp, db, ticker, timeframe, historic_data_table):
    """
        Insert historic data into database
    """
    try:
        table = db[historic_data_table]

        for candle in resp["candles"]:
            data = dict(datetime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(candle["datetime"]/1000)),
                        ticker=ticker,
                        timeframe=timeframe,
                        open=candle["open"],
                        high=candle["high"],
                        low=candle["low"],
                        close=candle["close"],
                        volume=candle["volume"])

            table.upsert(data, ['datetime', 'ticker', 'timeframe'])

    except Error as e:
        #TODO: Maybe we should do something else other than printing the error??
        print(e)

def insertOptionsData(opt_df, db):
    """
        Insert tdOptions data into database
    """
    try:
        table = db["options_data"]

        opt_df = opt_df.replace(np.nan, 0)
        opt_df = opt_df.replace([np.inf, -np.inf], 999999)
        rows = opt_df.to_dict('records')

        for row in rows:
            table.upsert(row, ['ticker', 'strike', 'date'])

    except Error as e:
        #TODO: Maybe we should do something else other than printing the error??
        print(e)
