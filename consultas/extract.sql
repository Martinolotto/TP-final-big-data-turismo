-- Extracción: carga el CSV original en la tabla raw_reservas.
-- No valida, corrige ni elimina registros.

CREATE OR REPLACE TABLE raw_reservas AS
SELECT *
FROM read_csv(
    ?,
    header = true,
    delim = ',',
    all_varchar = true,
    nullstr = '__VALOR_NULO_NO_PRESENTE__'
);
