import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _(df, pd):

    # Comparamos las noches declaradas con la diferencia entre fechas.
    # permite detectar noches vacias o que no coinciden antes de la validacion.
    fechas = df.copy()

    # el csv contiene fechas con guiones y tambien con barras.
    fechas["fecha_checkin"] = pd.to_datetime(
        fechas["fecha_checkin"],
        format="%Y-%m-%d",
        errors="coerce"
    ).fillna(
        pd.to_datetime(
            fechas["fecha_checkin"],
            format="%d/%m/%Y",
            errors="coerce"
        )
    )

    fechas["fecha_checkout"] = pd.to_datetime(
        fechas["fecha_checkout"],
        format="%Y-%m-%d",
        errors="coerce"
    ).fillna(
        pd.to_datetime(
            fechas["fecha_checkout"],
            format="%d/%m/%Y",
            errors="coerce"
        )
    )

    fechas["noches_calculadas"] = (
        fechas["fecha_checkout"] - fechas["fecha_checkin"]
    ).dt.days

    fechas["noches_declaradas"] = pd.to_numeric(
        fechas["noches"],
        errors="coerce"
    )

    fechas[
        fechas["noches_calculadas"] != fechas["noches_declaradas"]
    ][[
        "id_reserva",
        "fecha_checkin",
        "fecha_checkout",
        "noches_declaradas",
        "noches_calculadas"
    ]]

    return


@app.cell
def _():
    # leemos el csv como texto para conservar los vacios y los formatos originales.
    import pandas as pd

    df = pd.read_csv(
        "datos/reservas.csv",
        dtype=str,
        keep_default_na=False
    )

    # miramos las primeras filas para conocer la estructura de los datos.
    df.head()
    return df, pd


@app.cell
def _(df):
    # contamos registros e ids para saber si hay reservas repetidas.
    {
        "filas": len(df),
        "columnas": len(df.columns),
        "ids_unicos": df["id_reserva"].nunique(),
        "duplicados_por_id": df.duplicated("id_reserva").sum(),
    }
    return


@app.cell
def _(df):
    # Cantidad de valores vacíos por columna
    # indica en que campos faltan datos y puede hacer falta limpiar.
    (df == "").sum()
    return


@app.cell
def _(df):
    # Exploramos los valores únicos de las columnas categóricas.
    # revisamos los valores que aparecen para encontrar categorias inconsistentes.
    columnas_categoricas = [
        "hotel",
        "ciudad",
        "pais",
        "tipo_habitacion",
        "canal"
    ]

    resumen_categoricas = {
        columna: df[columna].value_counts(dropna=False)
        for columna in columnas_categoricas
    }

    resumen_categoricas
    return



if __name__ == "__main__":
    app.run()
