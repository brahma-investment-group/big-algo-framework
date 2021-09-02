from mysql.connector import connect, Error
import psycopg2
import time
import numpy as np
import configparser
from datetime import datetime
from pytz import timezone
import pandas as pd
from sqlalchemy import create_engine, text

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

        psql_info = "postgresql://postgres:{}@{}:5432/{}" . format(password, host, db_name)
        db = create_engine(psql_info)

        return db

    except Error as e:
        print(e)

def insertOHLCData(resp, db, ticker, timeframe, historic_data_table, time_zone):
    """
        Insert historic data into database
    """
    try:
        table_name = historic_data_table + "_" + timeframe.replace(" ", "_")

        if resp.get('candles'):
            df = pd.DataFrame.from_dict(resp['candles'])
            df['ticker'] = ticker

            if not df.empty:
                df = df.rename(columns={'datetime': 'date_time'})

                df.to_sql(table_name, db, if_exists='append', index=False, method='multi')

                query = text("CREATE INDEX IF NOT EXISTS {} ON {} (ticker, date_time);" .format(table_name +"_ticker_dt", table_name))
                with db.connect() as conn:
                    conn.execute(query)

    except Error as e:
        print(e)

def insertOptionsData(opt_df, db, options_data_table):
    """
        Insert tdOptions data into database
    """
    #TODO: Later rewrite below code using sqlalchemy
    try:
        table = db[options_data_table]

        opt_df = opt_df.replace(np.nan, 0)
        opt_df = opt_df.replace([np.inf, -np.inf], 999999)
        rows = opt_df.to_dict('records')

        for row in rows:
            table.upsert(row, ['ticker', 'strike', 'date'])

    except Error as e:
        print(e)
