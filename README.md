Grupo: Martino Lotto, Jonathan Sánchez 

# Tema 10: Turismo - ViajaYa

Nuestro trabajo consiste en desarrollar un pipeline ETL sobre un conjunto de datos de reservas hoteleras, recuperar los registros que presentan errores y obtener una tabla final con datos para responder las preguntas de negocio.

## Estructura del proyecto

Decidimos separar las consultas SQL del código Python para tener una mejor organización. cada consulta tiene su propia responsabilidad dentro del pipeline

También utilizamos Marimo para explorar los datos originales, comprobar los resultados de cada etapa y responder las preguntas de negocio

```
bigdata-turismo-etl/
├── analisis/
│   ├── exploracion.py
│   ├── auditoria.py
│   └── negocio.py
├── consultas/
│   ├── extract.sql
│   ├── validar.sql
│   ├── limpiar.sql
│   ├── unir.sql
│   └── consultas.sql
├── dags/
│   └── dag_pipeline.py
├── datos/
│   └── reservas.csv
├── pipeline.py
├── requirements.txt
├── pipeline.duckdb
├── ENUNCIADO.md
└── README.md
```

El archivo pipeline.py se encarga de ejecutar las consultas correspondientes a cada etapa, mientras que el DAG se encarga de establecer el orden de ejecución de las tareas mediante Airflow.

## Ejecución con Apache Airflow

Para el desarrollo utilizamos Python 3.12, uv y Apache Airflow 3.0.0.

Desde la raíz del proyecto creamos el entorno virtual:

```bash
uv venv --python 3.12
source .venv/bin/activate
```

Instalamos las dependencias:

```bash
uv pip install -r requirements.txt
```

Configuramos la ubicación de nuestro DAG e iniciamos Airflow:

```bash
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/dags"
airflow standalone
```

Ingresamos a <http://localhost:8080>, activamos el DAG `turismo_etl` y lo ejecutamos manualmente desde la interfaz.

El DAG está configurado para ejecutarse automáticamente todos los días a las 2 AM. Las tareas se ejecutan en el orden de:

```
extraer → validar → limpiar → unir → consultas_negocio
```

Los resultados de cada etapa y las respuestas de negocio se pueden observar en los logs de las tareas de Airflow.
