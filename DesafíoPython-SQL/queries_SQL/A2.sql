/* A2. Parte 1: top 5 de clientes */

WITH monto_por_cliente AS (
    SELECT
        cl.id AS cliente_id,
        cl.nombre,
        SUM(t.monto) AS monto_total
    FROM transacciones AS t
    INNER JOIN cuentas AS c
        ON t.cuenta_id = c.id
    INNER JOIN clientes AS cl
        ON c.cliente_id = cl.id
    WHERE t.estado = 'aprobada'
    GROUP BY
        cl.id,
        cl.nombre
),
ranking_clientes AS (
    SELECT
        cliente_id,
        nombre,
        monto_total,
        ROW_NUMBER() OVER (
            ORDER BY monto_total DESC, cliente_id
        ) AS posicion
    FROM monto_por_cliente
)
SELECT
    cliente_id,
    nombre,
    monto_total,
    posicion
FROM ranking_clientes
WHERE posicion <= 5
ORDER BY posicion;


/* A2. Parte 2: saldo acumulado por cada cuenta activa.
Se considera que solo las transacciones aprobadas modifican el saldo efectivo. */

WITH transacciones_activas AS (
    SELECT
        t.id AS transaccion_id,
        t.cuenta_id,
        t.fecha,
        t.tipo,
        t.monto,
        CASE
            WHEN t.tipo = 'credito' THEN t.monto
            WHEN t.tipo = 'debito' THEN -t.monto
            ELSE 0
        END AS monto_contable
    FROM transacciones AS t
    INNER JOIN cuentas AS c
        ON t.cuenta_id = c.id
    WHERE c.estado = 'activa'
      AND t.estado = 'aprobada'
)
SELECT
    transaccion_id,
    cuenta_id,
    fecha,
    tipo,
    monto,
    monto_contable,
    SUM(monto_contable) OVER (
        PARTITION BY cuenta_id
        ORDER BY fecha, transaccion_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS saldo_acumulado
FROM transacciones_activas
ORDER BY
    cuenta_id,
    fecha,
    transaccion_id;
