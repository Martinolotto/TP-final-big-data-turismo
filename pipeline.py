"""
Pipeline ETL de reservas hoteleras - ViajaYa Turismo.

Responsabilidad:
Coordinar las etapas de procesamiento utilizando
Python, DuckDB y consultas SQL independientes.
"""

from pathlib import Path

import duckdb


# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datos"
SQL_DIR = BASE_DIR / "consultas"
DB_PATH = BASE_DIR / "pipeline.duckdb"


def read_sql(filename: str) -> str:
    """Lee una consulta SQL desde la carpeta consultas."""
    path = SQL_DIR / filename
    return path.read_text(encoding="utf-8")


def extract():
    """Carga las reservas originales en DuckDB sin modificarlas."""

    # Abrimos la base y ejecutamos la consulta de extracción.
    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(
            read_sql("extract.sql"),
            [str(DATA_DIR / "reservas.csv")]
        )

        # Comprobamos cuántos registros fueron cargados.
        total = con.execute(
            "SELECT COUNT(*) FROM raw_reservas"
        ).fetchone()[0]

        # Verificamos que se conservaron los campos vacíos.
        vacios = con.execute("""
            SELECT
                COUNT(*) FILTER (WHERE pais = ''),
                COUNT(*) FILTER (WHERE noches = ''),
                COUNT(*) FILTER (WHERE total = '')
            FROM raw_reservas
        """).fetchone()

    print(f"Registros extraídos: {total}")
    print(f"Vacíos (país, noches, total): {vacios}")


def validate():
    """Evalúa las reglas de calidad y separa en validos y rechazados."""

    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(read_sql("validar.sql"))

        cant_validos = con.execute("SELECT COUNT(*) FROM validos").fetchone()[0]
        cant_rechazados = con.execute("SELECT COUNT(*) FROM rechazados").fetchone()[0]

    print(f"Registros válidos: {cant_validos}")
    print(f"Registros rechazados: {cant_rechazados}")


def clean():
    """Recupera y normaliza los registros corregibles en rechazados_limpios."""

    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(read_sql("limpiar.sql"))

        cant_recuperados = con.execute(
            "SELECT COUNT(*) FROM rechazados_limpios"
        ).fetchone()[0]

    print(f"Registros recuperados (rechazados_limpios): {cant_recuperados}")


def merge():
    """Une validos y rechazados_limpios en tabla_final con tipos finales."""

    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(read_sql("unir.sql"))

        total_final, ids_unicos = con.execute(
            "SELECT COUNT(*), COUNT(DISTINCT id_reserva) FROM tabla_final"
        ).fetchone()

    print(f"Registros en tabla_final: {total_final} (IDs únicos: {ids_unicos})")


def main():
    """Punto de entrada del pipeline."""
    extract()
    validate()
    clean()
    merge()


if __name__ == "__main__":
    main()