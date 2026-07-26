# Parte C – Propuesta de tablero de monitoreo de canales

## Objetivo

Contar con un tablero que permita monitorear la salud de los canales digitales, detectar desvíos de forma temprana y actuar antes de que los problemas generen reclamos de clientes o un impacto significativo en el negocio.

---

# C1. KPIs propuestos

## 1. Tasa de rechazo (KPI principal)

**Definición**

- Numerador: cantidad de operaciones rechazadas.
- Denominador: cantidad de operaciones resueltas (aprobadas + rechazadas).
- Ventana temporal: diaria, semanal y últimos 30 días.

**Motivo**

Es el principal indicador de salud operativa del canal. Permite detectar rápidamente deterioros en la experiencia del cliente independientemente del volumen de operaciones.

---

## 2. Clientes afectados

**Definición**

- Numerador: cantidad de clientes únicos con al menos una operación rechazada.
- Denominador: no aplica.
- Ventana temporal: semanal y mensual.

**Motivo**

Permite dimensionar el impacto sobre la base de clientes y priorizar acciones cuando aumenta la cantidad de personas afectadas.

---

## 3. Monto rechazado

**Definición**

- Numerador: suma del monto de las operaciones rechazadas.
- Denominador: no aplica.
- Ventana temporal: diaria, semanal y mensual.

**Motivo**

No todos los rechazos tienen el mismo impacto económico. Este indicador permite cuantificar el costo potencial del problema.

---

## 4. Porcentaje del monto rechazado

**Definición**

- Numerador: monto rechazado.
- Denominador: monto total de operaciones resueltas.
- Ventana temporal: diaria, semanal y mensual.

**Motivo**

Complementa al indicador anterior mostrando qué proporción del dinero operado está siendo afectada.

---

## 5. Cantidad de operaciones resueltas

**Definición**

- Numerador: operaciones aprobadas + rechazadas.
- Denominador: no aplica.
- Ventana temporal: diaria y semanal.

**Motivo**

Brinda contexto sobre el volumen operado y permite interpretar correctamente el resto de los indicadores.

---

## 6. Tiempo medio de resolución de operaciones pendientes *(si la información estuviera disponible)*

**Definición**

- Numerador: suma del tiempo transcurrido entre la creación y la resolución de cada operación.
- Denominador: cantidad de operaciones resueltas.
- Ventana temporal: diaria y semanal.

**Motivo**

Permitiría detectar demoras operativas antes de que se conviertan en rechazos o reclamos de clientes.

---

# C2. Organización del tablero

## Página 1 – Monitoreo Ejecutivo

**Objetivo:** responder rápidamente si existe un problema operativo.

```
---------------------------------------------------------------------
| Tasa rechazo | Clientes afectados | Monto rechazado |
---------------------------------------------------------------------
| % Monto rechazado | Operaciones | Tiempo resolución |
---------------------------------------------------------------------

          Evolución semanal de la tasa de rechazo por canal

---------------------------------------------------------------------

     Rechazos por canal     Rechazos por segmento     Rechazos por tipo

---------------------------------------------------------------------
```

### Filtros

- Período.
- Canal.
- Segmento.
- Tipo de operación.

---

## Página 2 – Análisis de detalle

**Objetivo:** identificar dónde se origina el problema.

Tabla de detalle con:

- Fecha.
- Canal.
- Segmento.
- Tipo de operación.
- Estado.
- Monto.

Visualizaciones adicionales:

- Evolución de la tasa de rechazo por segmento.
- Evolución por tipo de operación.
- Ranking de clientes con mayor cantidad de rechazos.
- Ranking de cuentas con mayor cantidad de rechazos.

---

## Alertas automáticas

Configurar alertas cuando:

- La tasa de rechazo de cualquier canal supere el promedio histórico en más de un umbral definido (por ejemplo, 5 puntos porcentuales).
- La tasa de rechazo aumente durante tres días consecutivos.
- La tasa de rechazo de un canal sea significativamente superior a la del resto de los canales durante dos días consecutivos.
- El monto rechazado supere un valor determinado.
- La cantidad de clientes afectados aumente significativamente respecto de la semana anterior.

Estas alertas permitirían detectar desvíos antes de que los clientes comiencen a reportar inconvenientes.

---

# C3. ¿El KPI principal debería ser la cantidad de transacciones?

No utilizaría la **cantidad de transacciones** como KPI principal porque mide el volumen de actividad y el crecimiento del canal, pero no refleja la calidad del servicio.

Un incremento en las transacciones puede convivir con un deterioro importante en la experiencia del cliente, como ocurrió en el análisis realizado, donde el principal problema fue el aumento de la tasa de rechazo en la App.

Sin embargo, tampoco descartaría ese indicador. Propondría mantener ambos KPIs con objetivos diferentes:

- **Cantidad de transacciones** como indicador de adopción y crecimiento del canal.
- **Tasa de rechazo** como indicador de salud operativa y experiencia del cliente.

De esta manera, Producto puede seguir monitoreando el crecimiento del canal, mientras que Canales Digitales y Operaciones pueden detectar rápidamente problemas que impactan en la experiencia de los clientes.

En lugar de discutir cuál KPI es "el correcto", buscaría alinear los indicadores con las distintas preguntas de negocio que cada área necesita responder.