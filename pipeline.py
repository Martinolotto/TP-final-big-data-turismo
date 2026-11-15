
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


def main():
    """Punto de entrada del pipeline."""
    extract()


if __name__ == "__main__":
    main()
