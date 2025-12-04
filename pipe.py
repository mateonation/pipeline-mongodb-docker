from cassandra.cluster import Cluster
from pymongo import MongoClient
import mysql.connector
import pandas as pd
import time
import redis
import sys

THE_TABLE = "track"
REDIS_KEY_COLUMN = "artists"
REDIS_VALUE_COLUMN = "album_name"
URI_MONGO= "mongodb://root:changeme@localhost:27017/admin"

class Crono:
    def __init__(self) -> None:
        self.start_time = time.time()

    def crono(self):
        t = time.time() - self.start_time
        self.start_time = time.time()
        return t

def main():
    crono = Crono()
    df = pd.read_csv('spotify-clean.csv')

    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="changeme",
        database="pipe"
    )
    cursor = cnx.cursor()
    
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
    tuples=list(df.itertuples(index=False, name=None))
    cursor.executemany(sql, tuples)
    cnx.commit()
    cursor.execute("SELECT * FROM track")

    print(f"Información insertada en MySQL en {crono.crono():.2f} segundos.")
    print(f"{len(cursor.fetchall())} inserciones.")

    cursor.execute("SELECT * FROM track")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    session_cassandra=Cluster(['localhost'], port=9042).connect() 
    session_cassandra.execute("CREATE KEYSPACE IF NOT EXISTS pipe WITH replication = {'class': 'SimpleStrategy', 'replication_factor':1};")
    session_cassandra.execute("USE pipe")
    
    session_cassandra.execute("DROP TABLE IF EXISTS track")
    session_cassandra.execute("CREATE TABLE IF NOT EXISTS track ("\
        "track_id VARCHAR PRIMARY KEY,"\
        "artists VARCHAR,"\
        "album_name VARCHAR,"\
        "track_name VARCHAR,"\
        "popularity INT,"\
        "duration_ms BIGINT)")

    ps = session_cassandra.prepare("INSERT INTO track ("\
        "track_id, artists, album_name, track_name, popularity, duration_ms)"\
        "VALUES (?, ?, ?, ?, ?, ?)")

    rows=list(df.itertuples(index=False, name=None))
    futueres = session_cassandra.execute_concurrent_with_args(ps, tuples)

    result=session_cassandra.execute("SELECT * FROM track")
    errors = [r for r in futueres if not r[0]]
    print(f"Información insertada en Cassandra en {crono.crono():.2f} segundos.")
    print(f"{len(result.all())} inserciones y {len(errors)} errores.")


    query = f"SELECT {REDIS_KEY_COLUMN}, {REDIS_VALUE_COLUMN} FROM {THE_TABLE};"
    rows = session_cassandra.execute(query)

    data_to_load = []
    for row in rows:
        key = str(getattr(row, "artists"))
        value = str(getattr(row, REDIS_VALUE_COLUMN))
        data_to_load.append((key, value))

    print(f"Datos recuperados de Cassandra: {len(data_to_load)} pares Clave-Valor.")

    session_redis = redis.Redis(host='localhost', port=6379, password="changeme", decode_responses=True)
    session_redis.flushall()

    counter=0
    while not session_redis.ping(): 
        counter += 1
        if (counter==10): 
            print("No se consiguió conectar con Redis.", file=sys.stderr)
            exit(-1)

    pipe = session_redis.pipeline()
    for key, value in data_to_load:
        redis_key = key
        pipe.set(redis_key, value)

    results = pipe.execute()
    print(f"{len(results)}/{len(data_to_load)} pares Clave-Valor insertados en Redis.")

    client = MongoClient(URI_MONGO)
    db = client.pipe

    db.drop_collection("tracks")
    coleccion = db["tracks"]

    cursor.execute("SELECT * FROM track")
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

    print(f"Información insertada en Mongo en {crono.crono():.2f} segundos.")
    print(f"{coleccion.count_documents({})} inserciones.")

    cnx.close()
    session_cassandra.shutdown()
    session_redis.close() 
    client.close()

if __name__ == "__main__": main()
