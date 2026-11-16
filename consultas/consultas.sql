
-- Pregunta 1: cuanto se recaudo por ciudad?
-- sumamos los totales de las reservas de cada ciudad
-- ordenamos de mayor a menor recaudacion

SELECT
    ciudad,
    SUM(total) AS recaudacion_total
FROM tabla_final
GROUP BY ciudad
ORDER BY recaudacion_total DESC;


-- Pregunta 2: cuantas noches reservadas hubo por mes de check-in (primeros 6 meses)?
-- usamos la fecha de ingreso para obtener el mes de cada resrva
-- sumamos las noches por mes, manteniendo separados los distintos años
-- filtramos de enero a junio

SELECT
    DATE_TRUNC('month', fecha_checkin) AS mes_checkin,
    SUM(noches) AS noches_reservadas
FROM tabla_final
WHERE EXTRACT(MONTH FROM fecha_checkin) BETWEEN 1 AND 6
GROUP BY mes_checkin
ORDER BY mes_checkin;


-- Pregunta 3: cual es el total promedio por reserva segun tipo de habitacion?
-- calculamos el promedio de los importes de cada reserva
-- agrupando por tipo de habitacion para comparar los resultados

SELECT
    tipo_habitacion,
    AVG(total) AS total_promedio
FROM tabla_final
GROUP BY tipo_habitacion
ORDER BY total_promedio DESC;


-- Pregunta 4: que canal concentra mas reservas?
-- contamos cuantas reservas tiene cada canal
-- ordenamos por cantidad y tomamos solamente el primero

SELECT
    canal,
    COUNT(*) AS cantidad_reservas
FROM tabla_final
GROUP BY canal
ORDER BY cantidad_reservas DESC
LIMIT 1;


-- Pregunta 5: cual es la estadia promedio (noches) por pais?
-- calculamos el promedio de noches por reserva para cada pais
-- ordenamos los paises desde la estadia promedio mas larga

SELECT
    pais,
    AVG(noches) AS estadia_promedio
FROM tabla_final
GROUP BY pais
ORDER BY estadia_promedio DESC;
