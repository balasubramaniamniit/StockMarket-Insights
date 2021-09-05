from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import logging
import pandas as pd
from data import *


def getDBSession():
    """Create and get a Cassandra session"""
    cloud_config = {
        'secure_connect_bundle': 'socialmediadata/secure-connect-socialmediadata.zip'
    }
    auth_provider = PlainTextAuthProvider('fTqwp',
                                          "KT_tXbPRQgi,Tpr8KeYM+RN5C") # USE UR KEYS
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    return session


def insert_dataframe_db(df, db_table_name, stock_tweets=False, stock_news=False, stock_semantic=False,
                        stock_named_entities=False, ticker_tweets=False, ticker_news=False):
    """The main routine."""

    column_names = list(df.columns.values)
    col_names = ','.join(map(str, column_names))
    session = getDBSession()
    val_insert = "?," * (len(column_names) - 1)
    # print(column_names)
    # print(db_table_name)

    query = f"INSERT INTO {db_table_name} ({col_names}) VALUES ({val_insert + '?'})"
    # print(query)
    # query = "INSERT INTO cassandra_pythondemo.twitterdata3(id ,datehour,user,text,url) VALUES (?,?,?,?,?)"
    prepared = session.prepare(str(query))

    for indx, item in df.iterrows():
        if indx / (len(df) / 5) == 0:
            print(f"Inserted {indx} records out of {len(df)}")
        # print(item)
        try:
            # print(item.ID, item.date_hour, item.USER, item.text, item.URL)
            if stock_tweets:
                session.execute(prepared, (
                item.ID, item.date_hour, item.USER, item.text, item.URL, item.sentiment_score, item.sentiment))
            if stock_news:
                session.execute(prepared, (
                item.Date, item.Title, item.Source, item.Link, item.text, item.id, item.sentiment_score, item.sentiment,
                item.summary))
            if stock_named_entities:
                session.execute(prepared, (str(item.id), item.count, item.Label, item.source, item.Text))
            if stock_semantic:
                session.execute(prepared,
                                (str(item.id), item.date, item.text, item.sentiment_score, item.link, item.Source))
            if ticker_tweets:
                session.execute(prepared, (
                item.ID, item.date_hour, item.USER, item.text, item.URL, item.sentiment_score, item.sentiment,
                item.ticker))
            if ticker_news:
                session.execute(prepared, (
                item.Date, item.Title, item.Link, item.text, item.id, item.sentiment_score, item.sentiment,
                item.summary, item.ticker))

        except Exception as e:
            print(e)
            break

    print("Inserted Data to DB")

def get_data_from_db(db_table_name):
    session = getDBSession()
    select_query = session.prepare(f"SELECT * FROM  {db_table_name}")
    data = session.execute(select_query)
    list = data.all()
    df = (pd.DataFrame(list))
    return  df


