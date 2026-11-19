
# DAG del ETL de reservas hoteleras

# Responsabilidad:
# Orquestar las etapas de extracción, validación,
# limpieza y unión mediante Apache Airflow.
import sys
from pathlib import Path

import pendulum
from airflow.sdk import dag, task


# Ubico la raíz del proyecto para importar pipeline.py
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

#dag convierte la funcion en la defincion de un flujo de trabajo
#aca se configura el dag
@dag(
    dag_id="turismo_etl", # el nombre con el q3ue aparece en airlfow
    start_date=pendulum.datetime(
        2026, 11, 15, 
        tz="America/Argentina/Cordoba", 
    ),
    schedule="0 2 * * *", # todos los dias a las 2am
    catchup=False, #evita programar ejecuciones historicas pendientes
    max_active_runs=1, #para evitar q dos ejecuciones del mismo
)#sag se aplica automaticamente a la funcion de abajo dag trabajen al mimso tiempo sobre nuestra bd

def turismo_etl():
    """Define las tareas del ETL y sus dependencias"""
#task declara una funcion como tarea de ariflow
    @task
    def extraer():
        """Carga el CSV original en raw_reservas"""
        from pipeline import extract
        extract()

    @task
    def validar():
        """Separa los registros válidos y rechazados"""
        from pipeline import validate
        validate()

    @task
    def limpiar():
        """Recupera los registros rechazados corregibles"""
        from pipeline import clean
        clean()

    @task
    def unir():
        """Construye la tabla_final sin duplicados"""
        from pipeline import merge
        merge()

    @task
    def consultas_negocio():
        """Ejecuta las consultas sobre tabla_final"""
        from pipeline import business_queries
        business_queries()

    # Cada etapa depende de que finalice la anterior.
    extraccion = extraer()
    validacion = validar()
    limpieza = limpiar()
    union = unir()
    negocio = consultas_negocio()

    #orden obligatorio entre tareas, establece dependencias entre las funciones
    extraccion >> validacion >> limpieza >> union >> negocio


# Registra el DAG para que Airflow pueda descubrirlo
turismo_etl()
