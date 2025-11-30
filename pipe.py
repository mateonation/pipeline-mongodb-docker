from cassandra.cluster import Cluster
import mysql.connector
import pandas as pd

DEBUG = True

def main():
    df = pd.read_csv('spotify-clean.csv')

    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="changeme",
        database="pipe"
    )
    cursor = cnx.cursor()
    
    if DEBUG: cursor.execute("DROP TABLE IF EXISTS track")

    cursor.execute("CREATE TABLE IF NOT EXISTS track (" \
        "track_id varchar(250), " \
        "artists varchar(1000)," \
        "album_name varchar(5120)," \
        "track_name varchar(250), " \
        "popularity int," \
        "duration_ms bigint," \
        "PRIMARY KEY (track_id)" \
        ");")

    sql = "INSERT INTO track VALUES (%s, %s, %s, %s, %s, %s)"
    tuples=[x for x in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, tuples)
    cnx.commit()

main()
