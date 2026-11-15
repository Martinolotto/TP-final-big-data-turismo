-- Validación: evalúa 9 reglas de calidad sobre raw_reservas y separa
-- los registros en las tablas validos y rechazados (con motivo_rechazo).

CREATE OR REPLACE TEMP VIEW reservas_evaluadas AS
WITH base AS (
    SELECT
        *,
        COUNT(*) OVER (PARTITION BY id_reserva) AS cant_id,
        COALESCE(
            TRY_STRPTIME(fecha_checkin, '%Y-%m-%d'),
            TRY_STRPTIME(fecha_checkin, '%d/%m/%Y')
        ) AS dt_checkin,
        COALESCE(
            TRY_STRPTIME(fecha_checkout, '%Y-%m-%d'),
            TRY_STRPTIME(fecha_checkout, '%d/%m/%Y')
        ) AS dt_checkout
    FROM raw_reservas
)
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
    canal,
    concat_ws(
        '; ',
        CASE WHEN cant_id > 1 THEN 'id_duplicado' END,
        CASE WHEN pais = '' THEN 'pais_vacio' END,
        CASE WHEN noches = '' THEN 'noches_vacio' END,
        CASE WHEN total = '' THEN 'total_vacio' END,
        CASE WHEN precio_noche LIKE '%,%' THEN 'precio_coma_decimal' END,
        CASE WHEN TRY_CAST(huespedes AS INTEGER) IS NULL OR TRY_CAST(huespedes AS INTEGER) <= 0 THEN 'huespedes_no_positivo' END,
        CASE WHEN NOT (
            regexp_matches(fecha_reserva, '^\d{4}-\d{2}-\d{2}$') AND TRY_STRPTIME(fecha_reserva, '%Y-%m-%d') IS NOT NULL
            AND regexp_matches(fecha_checkin, '^\d{4}-\d{2}-\d{2}$') AND TRY_STRPTIME(fecha_checkin, '%Y-%m-%d') IS NOT NULL
            AND regexp_matches(fecha_checkout, '^\d{4}-\d{2}-\d{2}$') AND TRY_STRPTIME(fecha_checkout, '%Y-%m-%d') IS NOT NULL
        ) THEN 'fecha_formato_invalido' END,
        CASE WHEN dt_checkin IS NOT NULL AND dt_checkout IS NOT NULL AND dt_checkout <= dt_checkin THEN 'checkout_menor_igual_checkin' END,
        CASE WHEN hotel NOT IN ('Posada del Sol', 'Hotel Andino', 'Gran Plaza', 'Mirador Resort', 'Costa Azul') THEN 'hotel_sin_normalizar' END
    ) AS motivo_rechazo
FROM base;

CREATE OR REPLACE TABLE validos AS
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
FROM reservas_evaluadas
WHERE motivo_rechazo = '';

CREATE OR REPLACE TABLE rechazados AS
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
    canal,
    motivo_rechazo
FROM reservas_evaluadas
WHERE motivo_rechazo <> '';