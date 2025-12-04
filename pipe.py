from cassandra.cluster import Cluster
from pymongo import MongoClient
import mysql.connector
import pandas as pd
import time
import redis

CSV='spotify-tracks.csv'

class Crono:
    def __init__(self) -> None:
        self.start_time = time.time()

    def crono(self):
        t = time.time() - self.start_time
        self.start_time = time.time()
        return t

def clean_dataset(df: pd.DataFrame):
    new_df = df.iloc[:50000, :7]
    new_df.drop(columns="Unnamed: 0", inplace=True)
    new_df.dropna(inplace=True)
    new_df.drop_duplicates(subset="track_id",inplace=True)
    return new_df

def main():
    crono = Crono()

    df = clean_dataset(pd.read_csv(CSV))

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
    tuples=[x for x in df.itertuples(index=False, name=None)]
    cursor.executemany(sql, tuples)
    cnx.commit()
    cursor.execute("SELECT * FROM track")

    print(f"Información insertada en MySQL en {crono.crono():.2f} segundos.")
    print(f"{len(cursor.fetchall())} inserciones.")

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

    result=session.execute("SELECT * FROM track")
    errors = [r for r in futueres if not r[0]]
    print(f"Información insertada en Cassandra en {crono.crono():.2f} segundos.")
    print(f"{len(result.all())} inserciones y {len(errors)} errores.")

    uri = "mongodb://root:changeme@localhost:27017/admin"
    client = MongoClient(uri)
    db = client.pipe

    db.drop_collection("tracks-MongoDB")
    coleccion = db["tracks-MongoDB"]

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
    session.shutdown()
    client.close()


########## PARTE EDU REDIS ##########
CASSANDRA_NODES = ['localhost']
CASSANDRA_KEYSPACE = 'pipe'
CASSANDRA_TABLE = 'track'

KEY_COLUMN = 'artists'
VALUE_COLUMN = 'album_name'

REDIS_HOST = 'localhost' 
REDIS_PORT = 6379
REDIS_PASSWORD = "changeme"

try:
    cluster = Cluster(CASSANDRA_NODES)
    session = cluster.connect(CASSANDRA_KEYSPACE)
    print(f"Conexión establecida con el Keyspace: {CASSANDRA_KEYSPACE}")

    query = f"""
    SELECT {KEY_COLUMN}, {VALUE_COLUMN} FROM {CASSANDRA_TABLE};
    """
    rows = session.execute(query)

    data_to_load = []
    for row in rows:
        key = str(getattr(row, KEY_COLUMN))
        value = str(getattr(row, VALUE_COLUMN))
        data_to_load.append((key, value))

    print(f"Datos recuperados de Cassandra: {len(data_to_load)} pares Clave-Valor.")

except Exception as e:
    print(f"Error al conectar o consultar Cassandra: {e}")
    data_to_load = [] 

if not data_to_load:
    print("No hay datos.")
else:
    try:
        r = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            password=REDIS_PASSWORD,
            decode_responses=True)
        r.ping() 
  
        pipe = r.pipeline()
        for key, value in data_to_load:
            redis_key = key
            pipe.set(redis_key, value)
        
        results = pipe.execute()
        print(f"{len(results)}/{len(data_to_load)} pares Clave-Valor insertados en Redis.")
        
    except Exception as e:
        print(f"Error en el proceso: {type(e).__name__}: {e}")    

for key, _ in data_to_load[:10]:
        redis_key = key
        stored_value = r.get(redis_key)
        print(f"{redis_key} -> {stored_value}")

########## FIN PARTE EDU REDIS ##########     

if __name__ == "__main__": main()
