# ============================================================
# Análisis del reclamo:
# "Desde hace unas semanas los clientes se quejan
# de operaciones que fallan en la app"
# ============================================================

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "desafio.db"
GRAFICO_PATH = BASE_DIR / "tasa_rechazo_semanal_por_canal.png"

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 180)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

# ============================================================
# VALIDACIÓN DEL ARCHIVO
# ============================================================

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"No se encontró la base de datos en: {DB_PATH}"
    )

# ============================================================
# 1. CARGA Y COMPRENSIÓN DE LOS DATOS
# ============================================================

print("\n" + "=" * 80)
print("1. CARGA Y COMPRENSIÓN DE LOS DATOS")
print("=" * 80)

with sqlite3.connect(DB_PATH) as conexion:
    transacciones = pd.read_sql_query(
        "SELECT * FROM transacciones",
        conexion
    )

    cuentas = pd.read_sql_query(
        "SELECT * FROM cuentas",
        conexion
    )

    clientes = pd.read_sql_query(
        "SELECT * FROM clientes",
        conexion
    )

print(f"Transacciones cargadas: {len(transacciones):,}")
print(f"Cuentas cargadas: {len(cuentas):,}")
print(f"Clientes cargados: {len(clientes):,}")

print(
    f"Columnas de transacciones: "
    f"{transacciones.columns.tolist()}"
)

print(
    f"Columnas de cuentas: "
    f"{cuentas.columns.tolist()}"
)

print(
    f"Columnas de clientes: "
    f"{clientes.columns.tolist()}"
)

# ============================================================
# 2. EXPLORACIÓN INICIAL
# ============================================================

print("\n" + "=" * 80)
print("2. EXPLORACIÓN INICIAL")
print("=" * 80)

print("\nInformación de transacciones:")
transacciones.info()

print("\nValores nulos en transacciones:")
print(transacciones.isna().sum())

print("\nRegistros duplicados completos en transacciones:")
print(transacciones.duplicated().sum())

print("\nDistribución por estado:")
print(transacciones["estado"].value_counts())

print("\nDistribución por canal:")
print(transacciones["canal"].value_counts())

print("\nDistribución por tipo de operación:")
print(transacciones["tipo"].value_counts())

print("\nDistribución de clientes por segmento:")
print(clientes["segmento"].value_counts())

# ============================================================
# 3. PREPARACIÓN Y ENRIQUECIMIENTO DE LOS DATOS
# ============================================================

print("\n" + "=" * 80)
print("3. PREPARACIÓN Y ENRIQUECIMIENTO DE LOS DATOS")
print("=" * 80)

transacciones["fecha"] = pd.to_datetime(
    transacciones["fecha"],
    errors="coerce"
)

fechas_invalidas = transacciones["fecha"].isna().sum()

print(f"Fechas inválidas: {fechas_invalidas}")

if fechas_invalidas > 0:
    transacciones = transacciones.dropna(
        subset=["fecha"]
    ).copy()

fecha_minima = transacciones["fecha"].min()
fecha_maxima = transacciones["fecha"].max()

print(
    f"Rango de fechas: "
    f"{fecha_minima} a {fecha_maxima}"
)

# Se incorpora el cliente y su segmento a cada transacción.
transacciones = (
    transacciones
    .merge(
        cuentas[["id", "cliente_id"]],
        how="left",
        left_on="cuenta_id",
        right_on="id",
        validate="many_to_one",
        suffixes=("", "_cuenta")
    )
    .drop(columns=["id_cuenta"])
    .merge(
        clientes[["id", "segmento"]],
        how="left",
        left_on="cliente_id",
        right_on="id",
        validate="many_to_one",
        suffixes=("", "_cliente")
    )
    .drop(columns=["id_cliente"])
)

segmentos_faltantes = transacciones["segmento"].isna().sum()

print(
    f"Transacciones sin segmento asociado: "
    f"{segmentos_faltantes}"
)

# Creación del período semanal.
transacciones["periodo_semana"] = (
    transacciones["fecha"]
    .dt.to_period("W")
)

transacciones["semana"] = (
    transacciones["periodo_semana"]
    .astype(str)
)

transacciones["inicio_semana"] = (
    transacciones["periodo_semana"]
    .apply(lambda periodo: periodo.start_time)
)

transacciones["fin_semana"] = (
    transacciones["periodo_semana"]
    .apply(
        lambda periodo:
        periodo.end_time.normalize()
    )
)

# Se consideran completas las semanas totalmente contenidas
# dentro del rango de fechas disponible.
transacciones["semana_completa"] = (
    (
        transacciones["inicio_semana"]
        >= fecha_minima.normalize()
    )
    &
    (
        transacciones["fin_semana"]
        <= fecha_maxima.normalize()
    )
)

# Agrupación para comparar la app contra el resto de los canales.
transacciones["grupo_canal"] = (
    transacciones["canal"]
    .apply(
        lambda canal:
        "app" if canal == "app" else "otros_canales"
    )
)

# ============================================================
# 4. DEFINICIÓN DE LA MÉTRICA DE ANÁLISIS
# ============================================================

print("\n" + "=" * 80)
print("4. DEFINICIÓN DE LA MÉTRICA DE ANÁLISIS")
print("=" * 80)

# La tasa de rechazo se calcula únicamente sobre operaciones
# que tienen una resolución definitiva.
#
# Tasa de rechazo =
# operaciones rechazadas / (aprobadas + rechazadas)
#
# Las operaciones pendientes no se incluyen en esta métrica.

resueltas = transacciones[
    transacciones["estado"].isin(
        ["aprobada", "rechazada"]
    )
].copy()

cantidad_resueltas = len(resueltas)

cantidad_rechazadas = (
    resueltas["estado"]
    .eq("rechazada")
    .sum()
)

tasa_rechazo_general = (
    cantidad_rechazadas
    / cantidad_resueltas
    * 100
    if cantidad_resueltas > 0
    else 0
)

print(
    "Tasa de rechazo = "
    "Operaciones rechazadas / Operaciones resueltas × 100"
)

print(f"Operaciones resueltas: {cantidad_resueltas:,}")
print(f"Operaciones rechazadas: {cantidad_rechazadas:,}")

print(
    f"Tasa de rechazo general: "
    f"{tasa_rechazo_general:.2f}%"
)

# ============================================================
# 5. EVOLUCIÓN SEMANAL DE LA TASA DE RECHAZO POR CANAL
# ============================================================

print("\n" + "=" * 80)
print("5. EVOLUCIÓN SEMANAL DE LA TASA DE RECHAZO POR CANAL")
print("=" * 80)

resumen_semanal_canal = (
    resueltas
    .groupby(
        [
            "grupo_canal",
            "semana",
            "inicio_semana",
            "semana_completa",
            "estado"
        ],
        dropna=False
    )
    .size()
    .unstack(fill_value=0)
    .reindex(
        columns=["aprobada", "rechazada"],
        fill_value=0
    )
    .reset_index()
)

resumen_semanal_canal["total_resueltas"] = (
    resumen_semanal_canal["aprobada"]
    + resumen_semanal_canal["rechazada"]
)

resumen_semanal_canal["tasa_rechazo"] = (
    resumen_semanal_canal["rechazada"]
    .div(resumen_semanal_canal["total_resueltas"])
    .mul(100)
    .round(2)
)

resumen_semanal_canal = resumen_semanal_canal.sort_values(
    [
        "inicio_semana",
        "grupo_canal"
    ]
)

# Se muestran únicamente semanas completas para evitar
# tasas distorsionadas por períodos con pocos registros.
semanas_completas_canal = resumen_semanal_canal[
    resumen_semanal_canal["semana_completa"]
].copy()

print(
    semanas_completas_canal[
        [
            "semana",
            "grupo_canal",
            "aprobada",
            "rechazada",
            "total_resueltas",
            "tasa_rechazo"
        ]
    ].to_string(index=False)
)

grafico_semanal = semanas_completas_canal.pivot(
    index="inicio_semana",
    columns="grupo_canal",
    values="tasa_rechazo"
).sort_index()

# ============================================================
# GRÁFICO DE EVOLUCIÓN SEMANAL
# ============================================================

fig, ax = plt.subplots(figsize=(11, 6))

if "app" in grafico_semanal.columns:
    ax.plot(
        grafico_semanal.index,
        grafico_semanal["app"],
        marker="o",
        linewidth=2.5,
        label="App"
    )

    for fecha, tasa in grafico_semanal["app"].dropna().items():
        ax.annotate(
            f"{tasa:.1f}%",
            xy=(fecha, tasa),
            xytext=(0, 9),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8
        )

if "otros_canales" in grafico_semanal.columns:
    ax.plot(
        grafico_semanal.index,
        grafico_semanal["otros_canales"],
        marker="o",
        linewidth=2.5,
        label="Otros canales"
    )

    for fecha, tasa in (
        grafico_semanal["otros_canales"]
        .dropna()
        .items()
    ):
        ax.annotate(
            f"{tasa:.1f}%",
            xy=(fecha, tasa),
            xytext=(0, -14),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=8
        )

ax.set_title(
    "Evolución semanal de la tasa de rechazo por canal",
    fontsize=14,
    fontweight="bold",
    pad=16
)

ax.set_xlabel("Inicio de semana")
ax.set_ylabel("Tasa de rechazo (%)")

ax.yaxis.set_major_formatter(
    plt.FuncFormatter(
        lambda valor, posicion: f"{valor:.0f}%"
    )
)

ax.set_xticks(grafico_semanal.index)

ax.set_xticklabels(
    [
        fecha.strftime("%d/%m")
        for fecha in grafico_semanal.index
    ],
    rotation=45,
    ha="right"
)

ax.set_ylim(bottom=0)
ax.grid(axis="y", alpha=0.3)
ax.legend()

fig.tight_layout()

fig.savefig(
    GRAFICO_PATH,
    dpi=150,
    bbox_inches="tight"
)

plt.close(fig)

print(f"\nGráfico guardado en: {GRAFICO_PATH}")

# ============================================================
# 6. COMPARACIÓN ENTRE EL PERÍODO RECIENTE Y EL ANTERIOR
# ============================================================

print("\n" + "=" * 80)
print("6. COMPARACIÓN ENTRE EL PERÍODO RECIENTE Y EL ANTERIOR")
print("=" * 80)

semanas_completas = (
    resueltas.loc[
        resueltas["semana_completa"],
        ["semana", "inicio_semana"]
    ]
    .drop_duplicates()
    .sort_values("inicio_semana")
)

cantidad_semanas_completas = len(semanas_completas)

# Se consideran recientes las últimas cuatro semanas completas.
cantidad_semanas_recientes = min(
    4,
    cantidad_semanas_completas
)

semanas_recientes = (
    semanas_completas
    .tail(cantidad_semanas_recientes)["semana"]
    .tolist()
)

print(
    f"Semanas completas disponibles: "
    f"{cantidad_semanas_completas}"
)

print(
    f"Semanas consideradas recientes: "
    f"{semanas_recientes}"
)

resueltas_completas = resueltas[
    resueltas["semana_completa"]
].copy()

resueltas_completas["periodo_analisis"] = (
    resueltas_completas["semana"]
    .isin(semanas_recientes)
    .map(
        {
            True: "ultimas_4_semanas",
            False: "periodo_anterior"
        }
    )
)

comparacion_periodos = (
    resueltas_completas
    .groupby(
        [
            "periodo_analisis",
            "grupo_canal",
            "estado"
        ],
        dropna=False
    )
    .size()
    .unstack(fill_value=0)
    .reindex(
        columns=["aprobada", "rechazada"],
        fill_value=0
    )
    .reset_index()
)

comparacion_periodos["total_resueltas"] = (
    comparacion_periodos["aprobada"]
    + comparacion_periodos["rechazada"]
)

comparacion_periodos["tasa_rechazo"] = (
    comparacion_periodos["rechazada"]
    .div(comparacion_periodos["total_resueltas"])
    .mul(100)
    .round(2)
)

print(comparacion_periodos.to_string(index=False))

# ============================================================
# VARIACIÓN DE LA TASA DE RECHAZO EN LA APP
# ============================================================

app_por_periodo = (
    comparacion_periodos[
        comparacion_periodos["grupo_canal"] == "app"
    ]
    .set_index("periodo_analisis")
)

periodos_necesarios = {
    "periodo_anterior",
    "ultimas_4_semanas"
}

hay_comparacion_app = periodos_necesarios.issubset(
    app_por_periodo.index
)

if hay_comparacion_app:
    tasa_app_anterior = app_por_periodo.loc[
        "periodo_anterior",
        "tasa_rechazo"
    ]

    tasa_app_reciente = app_por_periodo.loc[
        "ultimas_4_semanas",
        "tasa_rechazo"
    ]

    variacion_puntos = (
        tasa_app_reciente
        - tasa_app_anterior
    )

    print(
        f"\nTasa de rechazo anterior en app: "
        f"{tasa_app_anterior:.2f}%"
    )

    print(
        f"Tasa de rechazo en las últimas cuatro semanas: "
        f"{tasa_app_reciente:.2f}%"
    )

    print(
        f"Variación: "
        f"{variacion_puntos:+.2f} puntos porcentuales"
    )

else:
    print(
        "\nNo hay suficientes períodos para realizar "
        "la comparación de la app."
    )

# ============================================================
# 7. ANÁLISIS POR SEGMENTO DE CLIENTE
# ============================================================

print("\n" + "=" * 80)
print("7. ANÁLISIS POR SEGMENTO DE CLIENTE")
print("=" * 80)

app_resueltas_completas = resueltas_completas[
    resueltas_completas["canal"] == "app"
].copy()

resumen_app_segmento = (
    app_resueltas_completas
    .groupby(
        [
            "periodo_analisis",
            "segmento",
            "estado"
        ],
        dropna=False
    )
    .size()
    .unstack(fill_value=0)
    .reindex(
        columns=["aprobada", "rechazada"],
        fill_value=0
    )
    .reset_index()
)

resumen_app_segmento["total_resueltas"] = (
    resumen_app_segmento["aprobada"]
    + resumen_app_segmento["rechazada"]
)

resumen_app_segmento["tasa_rechazo"] = (
    resumen_app_segmento["rechazada"]
    .div(resumen_app_segmento["total_resueltas"])
    .mul(100)
    .round(2)
)

print(
    resumen_app_segmento
    .sort_values(
        ["periodo_analisis", "segmento"]
    )
    .to_string(index=False)
)

# Variación por segmento entre el período anterior
# y las últimas cuatro semanas.
segmentos_comparacion = resumen_app_segmento.pivot(
    index="segmento",
    columns="periodo_analisis",
    values="tasa_rechazo"
)

if periodos_necesarios.issubset(
    segmentos_comparacion.columns
):
    segmentos_comparacion["variacion_puntos"] = (
        segmentos_comparacion["ultimas_4_semanas"]
        - segmentos_comparacion["periodo_anterior"]
    )

    print("\nVariación de la tasa de rechazo por segmento:")
    print(
        segmentos_comparacion[
            [
                "periodo_anterior",
                "ultimas_4_semanas",
                "variacion_puntos"
            ]
        ]
        .round(2)
        .to_string()
    )

# ============================================================
# 8. VERIFICACIÓN POR TIPO DE OPERACIÓN
# ============================================================

print("\n" + "=" * 80)
print("8. VERIFICACIÓN POR TIPO DE OPERACIÓN")
print("=" * 80)

resumen_app_tipo = (
    app_resueltas_completas
    .groupby(
        [
            "periodo_analisis",
            "tipo",
            "estado"
        ],
        dropna=False
    )
    .size()
    .unstack(fill_value=0)
    .reindex(
        columns=["aprobada", "rechazada"],
        fill_value=0
    )
    .reset_index()
)

resumen_app_tipo["total_resueltas"] = (
    resumen_app_tipo["aprobada"]
    + resumen_app_tipo["rechazada"]
)

resumen_app_tipo["tasa_rechazo"] = (
    resumen_app_tipo["rechazada"]
    .div(resumen_app_tipo["total_resueltas"])
    .mul(100)
    .round(2)
)

print(
    resumen_app_tipo
    .sort_values(
        ["periodo_analisis", "tipo"]
    )
    .to_string(index=False)
)

# ============================================================
# 9. CUANTIFICACIÓN DEL IMPACTO
# ============================================================

print("\n" + "=" * 80)
print("9. CUANTIFICACIÓN DEL IMPACTO")
print("=" * 80)

# Para cuantificar el impacto total se consideran todas las fechas,
# incluidas las semanas parciales del inicio y final del período.
app_resueltas_total = resueltas[
    resueltas["canal"] == "app"
].copy()

rechazos_app = app_resueltas_total[
    app_resueltas_total["estado"] == "rechazada"
].copy()

total_operaciones_app = len(app_resueltas_total)
cantidad_rechazos_app = len(rechazos_app)
monto_rechazado_app = rechazos_app["monto"].sum()

cuentas_afectadas_app = (
    rechazos_app["cuenta_id"]
    .nunique()
)

clientes_afectados_app = (
    rechazos_app["cliente_id"]
    .nunique()
)

tasa_rechazo_app_total = (
    cantidad_rechazos_app
    / total_operaciones_app
    * 100
    if total_operaciones_app > 0
    else 0
)

# Monto total de operaciones resueltas (aprobadas + rechazadas)
# en la app durante todo el período.
monto_total_operado_app = (
    app_resueltas_total["monto"]
    .sum()
)

porcentaje_monto_rechazado = (
    monto_rechazado_app
    / monto_total_operado_app
    * 100
    if monto_total_operado_app > 0
    else 0
)

print(
    f"Operaciones resueltas en app: "
    f"{total_operaciones_app:,}"
)

print(
    f"Operaciones rechazadas en app: "
    f"{cantidad_rechazos_app:,}"
)

print(
    f"Tasa de rechazo total en app: "
    f"{tasa_rechazo_app_total:.2f}%"
)

print(
    f"Monto total rechazado: "
    f"${monto_rechazado_app:,.2f}"
)

print(
    f"Monto total de operaciones resueltas en app: "
    f"${monto_total_operado_app:,.2f}"
)

print(
    f"El monto rechazado representa "
    f"{porcentaje_monto_rechazado:.2f}% "
    f"del monto total de operaciones resueltas en la app."
)

print(
    f"Cuentas afectadas: "
    f"{cuentas_afectadas_app:,}"
)

print(
    f"Clientes afectados: "
    f"{clientes_afectados_app:,}"
)

# ============================================================
# IMPACTO ACUMULADO POR SEGMENTO
# ============================================================

impacto_segmento = (
    rechazos_app
    .groupby("segmento", dropna=False)
    .agg(
        operaciones_rechazadas=("id", "size"),
        clientes_afectados=("cliente_id", "nunique"),
        cuentas_afectadas=("cuenta_id", "nunique"),
        monto_rechazado=("monto", "sum")
    )
    .reset_index()
)

if monto_rechazado_app > 0:
    impacto_segmento["porcentaje_monto_rechazado"] = (
        impacto_segmento["monto_rechazado"]
        .div(monto_rechazado_app)
        .mul(100)
        .round(2)
    )
else:
    impacto_segmento["porcentaje_monto_rechazado"] = 0

print("\nImpacto acumulado por segmento:")
print(
    impacto_segmento
    .sort_values(
        "monto_rechazado",
        ascending=False
    )
    .to_string(index=False)
)


# ============================================================
# FIN DEL ANÁLISIS
# ============================================================

print("\n========================================")
print("Proceso finalizado correctamente.")
print(f"Gráfico generado: {GRAFICO_PATH.name}")
print("Las tablas impresas en consola constituyen")
print("la base para el Informe Ejecutivo.")
print("========================================")