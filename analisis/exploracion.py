import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell
def _():
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
    return (df,)


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


if __name__ == "__main__":
    app.run()
