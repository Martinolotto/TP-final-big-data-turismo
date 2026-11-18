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
def _(
    duckdb_conn,
    mo,
    raw_reservas,
    rechazados,
    rechazados_limpios,
    tabla_final,
    validos,
):
    conteos_etl = mo.sql(
        f"""
        -- control de registros entre etapas
        SELECT
            (SELECT COUNT(*) FROM raw_reservas) AS originales,
            (SELECT COUNT(*) FROM validos) AS validos,
            (SELECT COUNT(*) FROM rechazados) AS rechazados,
            (SELECT COUNT(*) FROM rechazados_limpios) AS recuperados,
            (SELECT COUNT(*) FROM tabla_final) AS finales,
            (SELECT COUNT(DISTINCT id_reserva) FROM tabla_final) AS ids_unicos;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, raw_reservas):
    duplicados_origen = mo.sql(
        f"""
        -- cantidad de filas repetidas en el csv original
        -- hay 2575 filas y 2500 ids distintos, hay 75 copias adicionales
        SELECT
            COUNT(*) AS filas_originales,
            COUNT(*) - COUNT(DISTINCT id_reserva) AS filas_duplicadas,
            COUNT(DISTINCT id_reserva) AS reservas_unicas
        FROM raw_reservas;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, raw_reservas):
    duplicados_por_id = mo.sql(
        f"""
        --ids que aparecen mas de una vez
        -- para ver de donde salen los registros duplicados
        SELECT
            id_reserva,
            COUNT(*) AS apariciones
        FROM raw_reservas
        GROUP BY id_reserva
        HAVING COUNT(*) > 1
        ORDER BY apariciones DESC, id_reserva;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, tabla_final):
    calidad_final = mo.sql(
        f"""
        -- revisar fechas, noches importes y huespedes
        -- 0 en las cuatro columnas
        SELECT
            COUNT(*) FILTER (
                WHERE fecha_checkout <= fecha_checkin
                   OR fecha_checkin IS NULL
                   OR fecha_checkout IS NULL
            ) AS fechas_invalidas,
            COUNT(*) FILTER (
                WHERE noches IS NULL
                   OR noches <> date_diff('day', fecha_checkin, fecha_checkout)
            ) AS noches_incorrectas,
            COUNT(*) FILTER (
                WHERE total IS NULL
                   OR precio_noche IS NULL
                   OR ABS(total - noches * precio_noche) > 0.01
            ) AS totales_incorrectos,
            COUNT(*) FILTER (
                WHERE huespedes IS NULL OR huespedes <= 0
            ) AS huespedes_invalidos
        FROM tabla_final;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, tabla_final):
    tipos_final = mo.sql(
        f"""
        --tipos que quedaron en tabla_final
        -- las fechas deben ser DATE, las cantidades INTEGER y los importes DOUBLE
        DESCRIBE tabla_final;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, tabla_final):
    categorias_final = mo.sql(
        f"""
        -- revisar categorias y paises vacios en la tabla final
        -- las tres columnas deberian devolver 0
        SELECT
            COUNT(*) FILTER (
                WHERE tipo_habitacion NOT IN ('simple', 'doble', 'suite')
                   OR tipo_habitacion IS NULL
            ) AS habitaciones_invalidas,
            COUNT(*) FILTER (
                WHERE canal NOT IN ('web_propia', 'booking', 'agencia', 'telefono')
                   OR canal IS NULL
            ) AS canales_invalidos,
            COUNT(*) FILTER (
                WHERE pais IS NULL OR TRIM(pais) = ''
            ) AS paises_vacios
        FROM tabla_final;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, rechazados, rechazados_limpios):
    ejemplos_limpieza = mo.sql(
        f"""
        -- ejemplos de datos antes y despues de la limpieza
        -- cada fila permite revisar que se corrigio y que se mantuvo
        -- es una muestra, el JOIN puede repetir ids que estaban duplicados
        SELECT
            r.id_reserva,
            r.motivo_rechazo,
            r.pais AS pais_original,
            l.pais AS pais_corregido,
            r.noches AS noches_originales,
            l.noches AS noches_corregidas,
            r.total AS total_original,
            l.total AS total_corregido
        FROM rechazados r
        JOIN rechazados_limpios l
            ON r.id_reserva = l.id_reserva
        ORDER BY r.id_reserva
        LIMIT 15;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, rechazados):
    _df = mo.sql(
        f"""
        -- cantidad de registros rechazados por cada regla
        -- un registro puede incumplir mas de una regla

        SELECT
            TRIM(regla) AS regla,
            COUNT(*) AS cantidad
        FROM rechazados,
        UNNEST(string_split(motivo_rechazo, ';')) AS t(regla)
        WHERE TRIM(regla) <> ''
        GROUP BY TRIM(regla)
        ORDER BY cantidad DESC;
        """,
        engine=duckdb_conn
    )
    return


@app.cell
def _(duckdb_conn, mo, validos):
    _df = mo.sql(
        f"""
        -- comprobar que los registros validos respeten el diccionario de datos
        -- para buscar inconsitencias que no contemplen las 9 reglas
        SELECT
            COUNT(*) FILTER (
                WHERE tipo_habitacion IS NULL
                   OR tipo_habitacion NOT IN ('simple', 'doble', 'suite')
            ) AS habitaciones_invalidas,

            COUNT(*) FILTER (
                WHERE canal IS NULL
                   OR canal NOT IN ('web_propia', 'booking', 'agencia', 'telefono')
            ) AS canales_invalidos,

            COUNT(*) FILTER (
                WHERE TRY_CAST(noches AS INTEGER) IS NULL
                   OR TRY_CAST(noches AS INTEGER) <> date_diff(
                       'day',
                       CAST(fecha_checkin AS DATE),
                       CAST(fecha_checkout AS DATE)
                   )
            ) AS noches_incorrectas,

            COUNT(*) FILTER (
                WHERE TRY_CAST(total AS DOUBLE) IS NULL
                   OR TRY_CAST(precio_noche AS DOUBLE) IS NULL
                   OR ABS(
                       TRY_CAST(total AS DOUBLE) -
                       TRY_CAST(noches AS INTEGER) * TRY_CAST(precio_noche AS DOUBLE)
                   ) > 0.01
            ) AS totales_incorrectos

        FROM validos;
        """,
        engine=duckdb_conn
    )
    return

@app.cell
def _(duckdb_conn, mo):
    ids_faltantes = mo.sql(
        f"""
        -- comprobamos si algun id del origen quedo fuera de la tabla final
        -- ids presentes en raw que no aparecen en tabla_final

        SELECT id_reserva
        FROM raw_reservas

        EXCEPT

        SELECT id_reserva
        FROM tabla_final;
        """,
        engine=duckdb_conn
    )
    return


if __name__ == "__main__":
    app.run()
