# Pipeline datos multibase: MongoDB, Cassandra, MySQL y Redis

## Miembros del grupo

*   **Paula** 
*   **Mateo**
*   **Fran** 
*   **Edu** 

## Descripción

Este proyecto implementa un **pipeline de procesamiento de datos** que integra cuatro tipos de bases de datos utilizando Python, pandas y Docker Compose.  

El flujo de datos sigue estos pasos:  

1. **Preprocesado del dataset CSV**: se seleccionan las columnas relevantes, se eliminan duplicados y valores nulos, y se limita a 50.000 filas.  
2. **Inserción en MySQL**: creación de tabla y carga del dataset limpio.  
3. **Inserción en Cassandra**: creación de keyspace y tabla, y carga desde MySQL.  
4. **Inserción en Redis**: extracción de pares clave-valor seleccionados desde Cassandra.  
5. **Inserción en MongoDB**: creación de colección y carga desde MySQL.  

Todo el proceso se ha implementado en **Python** y está documentado en **notebooks de Jupyter**, que contienen explicaciones paso a paso en celdas Markdown.  


## Estructura del Repositorio

```text
├── machine-init.sh                 # Script de inicialización de la máquina de OpenStack
├── docker-compose.yaml             # Definición de servicios para desarrollo
├── docker-compose.production.yaml  # Definición de servicios para producción
├── pipe.py                         # Pipeline completo
├── notebooks/
│   ├── notebook1-procesarcsv.ipynb     # Limpieza y preprocesado de datos (Pandas)
│   ├── mysql.ipynb                     # Conexión y operaciones CRUD en MySQL
│   ├── notebook3-cassandra.ipynb       # Ingesta y modelado de datos en Cassandra
│   └── notebook4-consultaMongo.ipynb   # Consultas y agregaciones en MongoDB
├── data/
│   └── spotify-tracks.csv              # Dataset original
└── README.md
```



## Dataset

Archivo: spotify-tracks.csv

Contenido: Información sobre tracks de Spotify, incluyendo artistas, álbum, nombre del track, popularidad y duración.

## Requisitos

- Docker y Docker Compose
- Python 3.x con las librerías:
  - `pandas`
  - `mysql-connector-python`
  - `cassandra-driver`
  - `pymongo`
  - `redis`
  - `matplotlib` (opcional para visualizaciones)
- Jupyter Notebook

## Ejecución

### 1. Inicializar máquina y dependencias

```bash
sh machine-init.sh
```
Este script:

- Instala Docker y Docker Compose
- Instala Python y librerías necesarias
- Clona el repositorio
- Levanta los servicios Docker (MySQL, Cassandra, Redis, MongoDB)
- Ejecuta el pipeline completo (`pipe.py`)

### 2. Levantar servicios Docker manualmente

```bash
docker-compose up -d
```

### 3. Ejecutar notebooks individualmente

Ejecutar los notebooks en orden:

1. `notebook0-parseCSV.ipynb` → limpieza y preparación del CSV
2. `notebook1-mysql.ipynb` → carga en MySQL
3. `notebook2-cassandra.ipynb` → carga en Cassandra
4. `notebook3-redis.ipynb` → carga de pares clave-valor en Redis
5. `notebook4-mongo.ipynb` → carga en MongoDB

> Cada notebook incluye celdas Markdown explicativas de cada paso.
