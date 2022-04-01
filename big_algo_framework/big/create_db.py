import psycopg2
import configparser
from sqlalchemy import create_engine

#CREATE DATABASE
def create_db(db_name, config_path):
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        database = config['DATABASE']

        host = database["host"]
        user = database["user"]
        password = database["password"]
        port = database["port"]

        conn = psycopg2.connect(host=host, user=user, password=password)
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        list_database = cur.fetchall()

        if (db_name,) in list_database:
            pass
        else:
            conn.cursor().execute('CREATE DATABASE {};'.format(db_name))

        psql_info = "postgresql://postgres:{}@{}:{}/{}" . format(password, host, port, db_name)
        db = create_engine(psql_info)

        return db

    except Exception as e:
        print("Database Connection Error:", e)
