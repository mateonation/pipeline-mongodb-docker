# Pipeline datos multibase: MongoDB, Cassandra, MySQL y Redis

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

## Grupo
*   **Fran** 
*   **Paula** 
*   **Mateo** 
*   **Edu** 
