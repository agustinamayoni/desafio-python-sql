/* A1. Cantidad de transacciones y monto total por canal, mes y estado
Solo se consideran cuentas activas y transacciones aprobadas o rechazadas. */

SELECT
    strftime('%Y-%m', t.fecha) AS mes,
    t.canal,
    t.estado,
    COUNT(*) AS cantidad_transacciones,
    SUM(t.monto) AS monto_total
FROM transacciones AS t
INNER JOIN cuentas AS c
    ON t.cuenta_id = c.id
WHERE c.estado = 'activa'
  AND t.estado IN ('aprobada', 'rechazada')
GROUP BY
    strftime('%Y-%m', t.fecha),
    t.canal,
    t.estado
ORDER BY
    mes,
    t.canal,
    t.estado;
