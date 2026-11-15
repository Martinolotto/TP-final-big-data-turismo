-- Limpieza: recupera y normaliza los registros corregibles de rechazados
-- en la tabla rechazados_limpios, eliminando duplicados y aplicando tipos finales.

CREATE OR REPLACE TABLE rechazados_limpios AS
WITH deduplicados AS (
    -- Conserva una única fila por id_reserva cuando existen copias duplicadas.
    SELECT *
    FROM rechazados
    QUALIFY ROW_NUMBER() OVER (PARTITION BY id_reserva) = 1
),
parseados AS (
    -- Normaliza textos, formatos de fecha, huéspedes negativos y decimales con coma.
    SELECT
        id_reserva,
        COALESCE(
            TRY_STRPTIME(fecha_reserva, '%Y-%m-%d'),
            TRY_STRPTIME(fecha_reserva, '%d/%m/%Y')
        )::DATE AS dt_reserva,
        COALESCE(
            TRY_STRPTIME(fecha_checkin, '%Y-%m-%d'),
            TRY_STRPTIME(fecha_checkin, '%d/%m/%Y')
        )::DATE AS dt_checkin_raw,
        COALESCE(
            TRY_STRPTIME(fecha_checkout, '%Y-%m-%d'),
            TRY_STRPTIME(fecha_checkout, '%d/%m/%Y')
        )::DATE AS dt_checkout_raw,
        CASE LOWER(TRIM(hotel))
            WHEN 'posada del sol' THEN 'Posada del Sol'
            WHEN 'hotel andino' THEN 'Hotel Andino'
            WHEN 'gran plaza' THEN 'Gran Plaza'
            WHEN 'mirador resort' THEN 'Mirador Resort'
            WHEN 'costa azul' THEN 'Costa Azul'
            ELSE TRIM(hotel)
        END AS hotel,
        TRIM(ciudad) AS ciudad,
        CASE
            WHEN pais <> '' THEN TRIM(pais)
            ELSE CASE TRIM(ciudad)
                WHEN 'Bariloche' THEN 'Argentina'
                WHEN 'Mendoza' THEN 'Argentina'
                WHEN 'Salta' THEN 'Argentina'
                WHEN 'Cusco' THEN 'Peru'
                WHEN 'Punta del Este' THEN 'Uruguay'
                WHEN 'Cartagena' THEN 'Colombia'
                WHEN 'Florianopolis' THEN 'Brasil'
                ELSE ''
            END
        END AS pais,
        TRIM(tipo_habitacion) AS tipo_habitacion,
        ABS(CAST(huespedes AS INTEGER)) AS huespedes,
        TRY_CAST(noches AS INTEGER) AS noches_orig,
        CAST(REPLACE(precio_noche, ',', '.') AS DOUBLE) AS precio_noche,
        TRY_CAST(total AS DOUBLE) AS total_orig,
        TRIM(canal) AS canal
    FROM deduplicados
),
fechas_corregidas AS (
    -- Intercambia check-in y check-out si estaban invertidos respecto a noches.
    SELECT
        id_reserva,
        dt_reserva AS fecha_reserva,
        CASE
            WHEN dt_checkout_raw < dt_checkin_raw
                 AND noches_orig IS NOT NULL
                 AND date_diff('day', dt_checkout_raw, dt_checkin_raw) = noches_orig
            THEN dt_checkout_raw
            ELSE dt_checkin_raw
        END AS fecha_checkin,
        CASE
            WHEN dt_checkout_raw < dt_checkin_raw
                 AND noches_orig IS NOT NULL
                 AND date_diff('day', dt_checkout_raw, dt_checkin_raw) = noches_orig
            THEN dt_checkin_raw
            ELSE dt_checkout_raw
        END AS fecha_checkout,
        hotel,
        ciudad,
        pais,
        tipo_habitacion,
        huespedes,
        noches_orig,
        precio_noche,
        total_orig,
        canal
    FROM parseados
),
calculados AS (
    -- Deduce noches faltantes a partir de la diferencia entre fechas.
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
        COALESCE(
            noches_orig,
            CAST(date_diff('day', fecha_checkin, fecha_checkout) AS INTEGER)
        ) AS noches,
        precio_noche,
        total_orig,
        canal
    FROM fechas_corregidas
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
    COALESCE(total_orig, ROUND(noches * precio_noche, 2)) AS total,
    canal
FROM calculados
WHERE fecha_checkout > fecha_checkin
  AND pais <> ''
  AND noches > 0
  AND total IS NOT NULL;