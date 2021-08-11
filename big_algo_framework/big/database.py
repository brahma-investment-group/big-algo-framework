from mysql.connector import connect, Error
import dataset
import psycopg2
import time
import numpy as np
import configparser
from datetime import datetime
from pytz import timezone

#CREATE DATABASE
def createDB(db_name, config_path):
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['DATABASE']

        host = database["host"]
        user = database["user"]
        password = database["password"]

        conn = psycopg2.connect(host=host, user=user, password=password)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        list_database = cur.fetchall()

        if (db_name,) in list_database:
            pass
        else:
            conn.cursor().execute('CREATE DATABASE {};'.format(db_name))

        db = dataset.connect("postgresql://postgres:{}@{}:5432/{}" . format(password, host, db_name))
        return db

    except Error as e:
        print(e)

def deleteAllRows(db, table_name):
    """
        Deletes all rows from table_name
    """
    table = db[table_name]
    table.delete()

def insertOHLCData(resp, db, ticker, timeframe, historic_data_table, time_zone):
    """
        Insert historic data into database
    """
    try:
        statement = "CREATE TABLE IF NOT EXISTS {} (date_time timestamp with time zone NOT NULL);" .format(historic_data_table)
        db.query(statement)
        table = db[historic_data_table]

        for candle in resp["candles"]:
            dt = datetime.fromtimestamp(int(candle["datetime"] / 1000))

            #Brokers like TD return monthly historic data at 01 hour instead of 00 hour. So manually replacing them to be 00.
            if timeframe == "1 month":
                dt = dt.replace(hour=0)

            timezone1 = timezone(time_zone)
            dt = timezone1.localize(dt)

            data = dict(date_time=dt,
                        ticker=ticker,
                        timeframe=timeframe,
                        open=candle["open"],
                        high=candle["high"],
                        low=candle["low"],
                        close=candle["close"],
                        volume=candle["volume"])

            table.upsert(data, ['date_time', 'ticker', 'timeframe'])

    except Error as e:
        print(e)

def insertOptionsData(opt_df, db, options_data_table):
    """
        Insert tdOptions data into database
    """
    try:
        table = db[options_data_table]

        opt_df = opt_df.replace(np.nan, 0)
        opt_df = opt_df.replace([np.inf, -np.inf], 999999)
        rows = opt_df.to_dict('records')

        for row in rows:
            table.upsert(row, ['ticker', 'strike', 'date'])

    except Error as e:
        print(e)
