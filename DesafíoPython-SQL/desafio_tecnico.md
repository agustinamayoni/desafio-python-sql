# Desafío Técnico — Data Business Translator Senior (Analytics & BI)

**Duración estimada:** 1,5 a 2 horas
**Modalidad:** Remoto + defensa oral posterior (30–40 min)
**Entrega:** repositorio Git o ZIP con queries, código/notebook, informe y propuesta de tablero

---

## Contexto

Sos parte del equipo de Analytics & BI de una entidad financiera. La base
`desafio.db` (SQLite) registra las transacciones de las cuentas de los
clientes durante el segundo trimestre de 2026, a través de cinco canales:
app, web, cajero, sucursal y api.

**El disparador:** el gerente de Canales Digitales escaló al comité que
"desde hace unas semanas los clientes se quejan de operaciones que fallan en
la app, y nadie le da una respuesta con datos". Te piden que investigues,
cuantifiques y le presentes conclusiones. No hay un Data Engineer disponible
para asistirte: tenés que meterte en la base vos.

## Setup

Requisitos: Python 3.10+ (el generador usa solo librería estándar).

```bash
python seed_data.py
```

Genera `desafio.db` y `liquidaciones_procesador.csv` (archivo de
liquidaciones del procesador externo; es opcional, ver Bonus).

**Esquema:**

- `clientes(id, nombre, segmento)` — segmento: retail / pyme / corporativo
- `cuentas(id, cliente_id, moneda, estado)` — estado: `activa` / `cerrada`
- `transacciones(id, cuenta_id, fecha, tipo, monto, canal, estado, referencia_externa)`
  - `tipo`: `debito` / `credito` (monto siempre positivo)
  - `estado`: `aprobada` / `rechazada` / `pendiente`
  - `referencia_externa`: id del procesador externo; `NULL` en operaciones internas

---

## Parte A — SQL: exploración y validación (~40 min)

Entregá las queries en `queries.sql`, comentadas. Cualquier cliente SQLite
o el módulo `sqlite3` de Python sirve.

**A1.** Cantidad de transacciones y monto total por canal y por mes,
distinguiendo aprobadas de rechazadas, **solo cuentas activas**. Esta va a
ser tu foto base del trimestre.

**A2.** Para entender a los clientes más relevantes: top 5 de clientes por
monto operado (aprobadas) con su posición en el ranking, y para cada cuenta
activa el **saldo acumulado** (running balance) transacción a transacción
por fecha, donde créditos suman y débitos restan.

**A3.** Validación de calidad de datos: el área de fraude sospecha que hay
**transacciones duplicadas** (misma cuenta, mismo monto, menos de 60
segundos de diferencia). Detectalas mostrando ambos IDs. Además, listá
brevemente (en comentarios) cualquier otro problema de calidad o rareza que
hayas visto en los datos mientras explorabas, y cómo podría distorsionar un
análisis si nadie lo detecta.

## Parte B — Python: análisis e informe ejecutivo (~50 min)

Investigá el reclamo del gerente con Python (script o notebook, como
prefieras; pandas y librerías de visualización bienvenidas, no
obligatorias).

Entregables:

1. **Tu análisis** (`analisis.py` o `analisis.ipynb`): el camino que
   seguiste para encontrar qué está pasando, reproducible de punta a punta.
2. **Un informe ejecutivo de una carilla** (`INFORME.md` o PDF) dirigido al
   gerente de Canales Digitales — una persona de negocio, no técnica — que
   responda: **qué pasó, desde cuándo, a quiénes afecta y de cuánto es el
   impacto**, con al menos una visualización o tabla que lo muestre de un
   vistazo, y una recomendación concreta de próximos pasos.

No evaluamos ingeniería de software (no hacen falta tests ni empaquetado):
evaluamos criterio analítico, rigor en la cuantificación y claridad para
comunicar. Un hallazgo correcto mal contado vale la mitad.

## Parte C — Del análisis al tablero (~15 min, respuesta escrita)

El comité quiere dejar de enterarse de estos problemas por quejas de
clientes. Te piden proponer un **tablero de monitoreo de canales** en
Power BI. En `TABLERO.md` describí (no hace falta construirlo):

**C1.** Los 4–6 KPIs que pondrías, con su definición exacta (numerador,
denominador, ventana temporal) y por qué esos y no otros.

**C2.** Cómo organizarías la o las páginas (un wireframe a mano alzada o en
texto alcanza), qué filtros/segmentaciones tendría, y qué alertas
automáticas configurarías.

**C3.** Producto insiste en que el KPI principal sea "cantidad de
transacciones totales" porque "es el número que más crece". ¿Estás de
acuerdo? ¿Cómo manejarías la conversación?

## Bonus (opcional, solo si te sobra tiempo)

El procesador externo envía `liquidaciones_procesador.csv`, que debería
coincidir con las transacciones que tienen `referencia_externa`. Explorá
qué tan consistentes son las dos fuentes y cuantificá las discrepancias.
Ojo: el archivo viene sucio, como en la vida real.

---

## Sobre el uso de asistentes de IA

Podés usar las herramientas de tu trabajo diario, incluyendo asistentes de
IA. Lo que evaluamos es tu criterio: en la defensa oral vas a explicar y
justificar cada decisión, y vamos a conversar sobre tus hallazgos como lo
haría un stakeholder de negocio. Entregá solo lo que puedas defender.

## Qué valoramos

- Hallazgos correctos y **cuantificados**, no listas de gráficos sin lectura
- Que cuestiones los datos antes de confiar en ellos
- Comunicación: que el gerente entienda el informe sin ayuda
- Supuestos explícitos y honestidad sobre lo que no llegaste a mirar

¡Éxitos!
