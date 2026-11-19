import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path
    import duckdb
    import marimo as mo

    duckdb_conn = duckdb.connect(
        str(Path(__file__).resolve().parents[1] / "pipeline.duckdb"),
        read_only=True
    )
    return duckdb_conn, mo


@app.cell
def _(duckdb_conn, mo):
    recaudacion_ciudad = mo.sql(
        f"""
        -- pregunta 1: cuanto se recaudo por ciudad?
        -- sumamos los totales de las reservas de cada ciudad
        -- ordenamos de mayor a menor recaudacion
        SELECT
            ciudad,
            ROUND(SUM(total), 2) AS recaudacion_total
        FROM tabla_final
        GROUP BY ciudad
        ORDER BY recaudacion_total DESC;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo):
    noches_mes = mo.sql(
        f"""
        -- pregunta 2: cuantas noches reservadas hubo por mes de check-in (primeros 6 meses)?
        -- sumamos las noches de cada mes segun la fecha de ingreso
        -- tomamos los primeros seis meses registrados

        SELECT
            DATE_TRUNC('month', fecha_checkin) AS mes_checkin,
            SUM(noches) AS noches_reservadas
        FROM tabla_final
        GROUP BY mes_checkin
        ORDER BY mes_checkin
        LIMIT 6;

        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo):
    promedio_habitacion = mo.sql(
        f"""
        -- pregunta 3: cual es el total promedio por tipo de habitacion?
        -- calculamos el importe promedio de las reservas de cada tipo
        SELECT
            tipo_habitacion,
            ROUND(AVG(total), 2) AS total_promedio
        FROM tabla_final
        GROUP BY tipo_habitacion
        ORDER BY total_promedio DESC;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo):
    canal_mayor = mo.sql(
        f"""
        -- pregunta 4: que canal concentra mas reservas?
        -- contamos las reservas por canal y mostramos el que tiene mas
        SELECT
            canal,
            COUNT(*) AS cantidad_reservas
        FROM tabla_final
        GROUP BY canal
        ORDER BY cantidad_reservas DESC
        LIMIT 1;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo):
    promedio_pais = mo.sql(
        f"""
        -- pregunta 5: cual es la estadia promedio en noches por pais?
        -- calculamos el promedio de noches para cada pais
        SELECT
            pais,
            ROUND(AVG(noches), 2) AS estadia_promedio
        FROM tabla_final
        GROUP BY pais
        ORDER BY estadia_promedio DESC;
        """,
        engine=duckdb_conn
    )
    return


if __name__ == "__main__":
    app.run()
