# from mysql.connector import connect, Error
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

    except Exception as e:
        print(e)