/* A3. Validación de calidad de datos
   Detección de posibles transacciones duplicadas:
   - Misma cuenta
   - Mismo monto
   - Menos de 60 segundos de diferencia
   */


SELECT
    t1.id AS transaccion_id_1,
    t2.id AS transaccion_id_2,
    t1.cuenta_id,
    t1.tipo,
    t1.canal,
    t1.estado,
    t1.monto,
    t1.fecha AS fecha_1,
    t2.fecha AS fecha_2,
    ROUND(
        ABS(
            (julianday(t2.fecha) - julianday(t1.fecha)) * 86400
        ),
        2
    ) AS diferencia_segundos
FROM transacciones t1
INNER JOIN transacciones t2
    ON t1.cuenta_id = t2.cuenta_id
    AND t1.monto = t2.monto
    AND t1.id < t2.id
WHERE ABS(
    (julianday(t2.fecha) - julianday(t1.fecha)) * 86400
) < 60
ORDER BY
    t1.cuenta_id,
    t1.fecha;


/* Observaciones:

1. Se detectaron 8 pares de transacciones duplicadas según el criterio solicitado
   (misma cuenta, mismo monto y menos de 60 segundos de diferencia).
   
2. Verificar referencias externas duplicadas cuando correspondan a operaciones externas.
   Riesgo: pueden dificultar la conciliación con el procesador externo e indicar
   reprocesamientos o inconsistencias de integración.

3. Verificar si existen transacciones con estados fuera del catálogo esperado
   (por ejemplo: aprobada, rechazada, pendiente).
   Riesgo: generan métricas incorrectas y pueden afectar filtros y dashboards.

4. Revisar la antigüedad de las transacciones pendientes.
   Riesgo: operaciones pendientes durante largos períodos pueden indicar
   problemas operativos y distorsionar indicadores de gestión.

5. Validar que todas las transacciones estén asociadas a cuentas válidas y
   que la condición de "activa" sea consistente con las reglas del negocio.
   Riesgo: incluir cuentas que no deberían operar puede alterar análisis
   comerciales y operativos.

6. Verificar la existencia de transacciones exactamente iguales
   (misma cuenta, fecha, tipo, canal, monto y referencia externa).
   Riesgo: podrían indicar reprocesamientos o duplicaciones completas de eventos,
   impactando métricas de volumen y conciliación.

7. Validar que la secuencia temporal de las transacciones sea consistente.
   Riesgo: si existen registros con fechas fuera del período esperado o desordenadas, 
   el cálculo de saldos acumulados y análisis temporales puede resultar incorrecto.
*/
