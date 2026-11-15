
## Desarrollo

Proyecto ETL del Tema 10: Turismo — ViajaYa.

### Entorno

- Python 3.12
- DuckDB
- pandas
- Marimo para exploración
- Apache Airflow para orquestación

Instalación de dependencias:

```bash
uv pip install -r requirements.txt
```

Ejecución inicial:

```bash
python pipeline.py
```

### Etapas del pipeline

1. `extract()`: carga original en `raw_reservas`.
2. `validate()`: separación en válidos y rechazados.
3. `clean()`: recuperación de registros rechazados.
4. `merge()`: construcción de `tabla_final`.

Las funciones 2, 3 y 4 están pendientes de implementación.

### Organización del equipo

- Infraestructura, extracción, consultas de negocio y Airflow.
- Validaciones, limpieza y unión de registros.

Cada integrante desarrolla en su propia rama y propone los cambios mediante pull requests.
