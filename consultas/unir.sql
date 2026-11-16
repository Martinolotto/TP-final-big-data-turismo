-- Unión: consolida validos y rechazados_limpios en tabla_final
-- asegurando tipos de datos finales (DATE, INTEGER, DOUBLE) y unicidad de id_reserva.

CREATE OR REPLACE TABLE tabla_final AS
WITH unificados AS (
    -- Castea las columnas de validos (VARCHAR) para igualar el esquema tipado.
    SELECT
        id_reserva,
        CAST(fecha_reserva AS DATE) AS fecha_reserva,
        CAST(fecha_checkin AS DATE) AS fecha_checkin,
        CAST(fecha_checkout AS DATE) AS fecha_checkout,
        hotel,
        ciudad,
        pais,
        tipo_habitacion,
        CAST(huespedes AS INTEGER) AS huespedes,
        CAST(noches AS INTEGER) AS noches,
        CAST(precio_noche AS DOUBLE) AS precio_noche,
        CAST(total AS DOUBLE) AS total,
        canal
    FROM validos

    UNION ALL

    SELECT
        id_reserva,
        fecha_reserva,
        fecha_checkin,
        fecha_checkout,
        hotel,
        ciudad,
        pais,
        tipo_habitacion,
        huespedes,
        noches,
        precio_noche,
        total,
        canal
    FROM rechazados_limpios
)
SELECT *
FROM unificados
QUALIFY ROW_NUMBER() OVER (PARTITION BY id_reserva) = 1
ORDER BY id_reserva;