import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _(df, pd):
    # Comparamos las noches declaradas con la diferencia entre fechas.
    fechas = df.copy()


    fechas["fecha_checkin"] = pd.to_datetime(
        fechas["fecha_checkin"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    fechas["fecha_checkout"] = pd.to_datetime(
        fechas["fecha_checkout"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
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
    import pandas as pd

    df = pd.read_csv(
        "datos/reservas.csv",
        dtype=str,
        keep_default_na=False
    )

    df.head()
    return df, pd


@app.cell
def _(df):
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
    (df == "").sum()
    return


@app.cell
def _(df):
    # Exploramos los valores únicos de las columnas categóricas.
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
