from cassandra.cluster import Cluster
from pymongo import MongoClient
import mysql.connector
import pandas as pd
import time

DEBUG = True

def main():
    start_time = time.time()
    df = pd.read_csv('spotify-clean.csv')

    if DEBUG: print(time.time() - start_time)

    cnx_mysql = mysql.connector.connect(
        host="localhost",
        user="root",
        password="changeme",
        database="pipe"
    )
    cursor = cnx_mysql.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS track")

    cursor.execute("CREATE TABLE IF NOT EXISTS track (" \
        "track_id varchar(250), " \
        "artists varchar(1000)," \
        "album_name varchar(5120)," \
        "track_name varchar(250), " \
        "popularity int," \
        "duration_ms bigint," \
        "PRIMARY KEY (track_id)" \
        ")")

    sql = "INSERT INTO track VALUES (%s, %s, %s, %s, %s, %s)"
    tuples=[x for x in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, tuples)
    cnx_mysql.commit()

    if DEBUG: print(time.time() - start_time)
    cursor.execute("SELECT * FROM track")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    session=Cluster(['localhost'], port=9042).connect() 
    session.execute("""CREATE KEYSPACE IF NOT EXISTS pipe WITH replication = {'class': 'SimpleStrategy', 'replication_factor':1};""")
    session.execute('USE pipe')

    session.execute("DROP TABLE IF EXISTS track")

    session.execute("CREATE TABLE IF NOT EXISTS track ("\
        "track_id VARCHAR PRIMARY KEY,"\
        "artists VARCHAR,"\
        "album_name VARCHAR,"\
        "track_name VARCHAR,"\
        "popularity INT,"\
        "duration_ms BIGINT)")

    ps = session.prepare("INSERT INTO track ("\
        "track_id, artists, album_name, track_name, popularity, duration_ms)"\
        "VALUES (?, ?, ?, ?, ?, ?)")

    rows=list(df.itertuples(index=False, name=None))
    futueres = session.execute_concurrent_with_args(ps, tuples)

    if DEBUG: print(time.time() - start_time)

    result=session.execute("SELECT * FROM track")
    errors = [r for r in futueres if not r[0]]
    print(f"Inserciones en cassandra: {len(result.all())}\nErrores totales: {len(errors)}")

    uri = "mongodb://root:changeme@localhost:27017/admin"
    client = MongoClient(uri)
    db = client.pipe

    db.drop_collection("tracks-MongoDB")
    coleccion = db["tracks-MongoDB"]

    cursor.execute("SELECT * FROM track;")
    rows = cursor.fetchall()
    documentos=list()
    for r in rows:
        documentos.append({
            "_id": r[0],
            "artists": r[1],
            "album_name ": r[2],
            "track_name": r[3],
            "popularity": r[4],
            "duration_ms": r[5]
        })
    coleccion.insert_many(documentos)

    print(f"Inserciones en mongo: {coleccion.count_documents({})}. {time.time() - start_time}")

if __name__ == "__main__": main()
