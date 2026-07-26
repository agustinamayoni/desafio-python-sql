"""
Generador de datos para el desafío técnico Python + SQL.
Crea `desafio.db` (SQLite) y `liquidaciones_procesador.csv`.

Uso:
    python seed_data.py

Requiere solo la librería estándar de Python 3.10+.
"""
import csv
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

DB_PATH = Path("desafio.db")
CSV_PATH = Path("liquidaciones_procesador.csv")

SEGMENTOS = ["retail", "pyme", "corporativo"]
CANALES = ["app", "web", "cajero", "sucursal", "api"]
MONEDAS = ["ARS", "USD"]
NOMBRES = [
    "Acme SA", "Lumen SRL", "Patagonia Foods", "Norte Textil", "Delta Agro",
    "Kappa Logística", "Vega Seguros", "Orion Salud", "Rueda Motors",
    "Sur Energía", "Cumbre Construcciones", "Río Software",
]


def crear_esquema(cx: sqlite3.Connection) -> None:
    cx.executescript(
        """
        DROP TABLE IF EXISTS transacciones;
        DROP TABLE IF EXISTS cuentas;
        DROP TABLE IF EXISTS clientes;

        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            segmento TEXT NOT NULL
        );

        CREATE TABLE cuentas (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id),
            moneda TEXT NOT NULL,
            estado TEXT NOT NULL  -- 'activa' | 'cerrada'
        );

        CREATE TABLE transacciones (
            id INTEGER PRIMARY KEY,
            cuenta_id INTEGER NOT NULL REFERENCES cuentas(id),
            fecha TEXT NOT NULL,              -- ISO 8601
            tipo TEXT NOT NULL,               -- 'debito' | 'credito'
            monto REAL NOT NULL,              -- siempre positivo; el signo lo da 'tipo'
            canal TEXT NOT NULL,
            estado TEXT NOT NULL,             -- 'aprobada' | 'rechazada' | 'pendiente'
            referencia_externa TEXT           -- puede ser NULL (operaciones internas)
        );
        """
    )


def poblar(cx: sqlite3.Connection) -> list[dict]:
    for i, nombre in enumerate(NOMBRES, start=1):
        cx.execute(
            "INSERT INTO clientes VALUES (?, ?, ?)",
            (i, nombre, random.choice(SEGMENTOS)),
        )

    cuentas = []
    cid = 1
    for cliente_id in range(1, len(NOMBRES) + 1):
        for _ in range(random.randint(1, 3)):
            estado = "activa" if random.random() > 0.15 else "cerrada"
            cx.execute(
                "INSERT INTO cuentas VALUES (?, ?, ?, ?)",
                (cid, cliente_id, random.choice(MONEDAS), estado),
            )
            cuentas.append(cid)
            cid += 1

    inicio = datetime(2026, 4, 1)
    transacciones = []
    ref_counter = 10000
    for tx_id in range(1, 1501):
        cuenta = random.choice(cuentas)
        fecha = inicio + timedelta(
            days=random.randint(0, 89),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        tipo = random.choice(["debito", "credito"])
        monto = round(random.uniform(500, 250_000), 2)
        # Señal 2 (secundaria): el canal sucursal pierde peso mes a mes
        # (migración a digital). Abril ~equilibrado, junio con sucursal al 40%.
        mes = fecha.month
        peso_sucursal = {4: 20, 5: 13, 6: 8}[mes]
        pesos_canal = [24, 24, 20, peso_sucursal, 12]  # app, web, cajero, sucursal, api
        canal = random.choices(CANALES, weights=pesos_canal)[0]
        # Señal 1 (principal): desde el 1/6 la tasa de rechazo del canal app
        # salta de ~10% a ~35% (simula un deploy fallido en la integración).
        if canal == "app" and fecha >= datetime(2026, 6, 1):
            pesos_estado = [58, 35, 7]
        else:
            pesos_estado = [85, 10, 5]
        estado = random.choices(
            ["aprobada", "rechazada", "pendiente"], weights=pesos_estado
        )[0]
        # ~75% de las transacciones vienen de un procesador externo
        if random.random() < 0.75:
            referencia = f"PX-{ref_counter}"
            ref_counter += 1
        else:
            referencia = None
        row = dict(
            id=tx_id, cuenta_id=cuenta, fecha=fecha, tipo=tipo, monto=monto,
            canal=canal, estado=estado, referencia_externa=referencia,
        )
        transacciones.append(row)
        cx.execute(
            "INSERT INTO transacciones VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (tx_id, cuenta, fecha.isoformat(sep=" "), tipo, monto, canal,
             estado, referencia),
        )

    # --- Anomalías plantadas: duplicados sospechosos (misma cuenta, mismo
    # monto, pocos segundos de diferencia) ---
    base = [t for t in transacciones if t["estado"] == "aprobada"][:8]
    next_id = 1501
    for t in base:
        fecha_dup = t["fecha"] + timedelta(seconds=random.randint(5, 45))
        cx.execute(
            "INSERT INTO transacciones VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (next_id, t["cuenta_id"], fecha_dup.isoformat(sep=" "), t["tipo"],
             t["monto"], t["canal"], "aprobada", None),
        )
        next_id += 1

    return transacciones


def generar_csv(transacciones: list[dict]) -> None:
    """CSV del procesador: cubre la mayoría de las refs, con anomalías."""
    con_ref = [t for t in transacciones if t["referencia_externa"]]
    random.shuffle(con_ref)

    filas = []
    # 90% de las refs aparecen en el CSV
    presentes = con_ref[: int(len(con_ref) * 0.9)]
    for t in presentes:
        monto = t["monto"]
        estado = "OK" if t["estado"] == "aprobada" else "FALLIDA"
        # ~4%: diferencia de monto (redondeos / fees mal aplicados)
        if random.random() < 0.04:
            monto = round(monto + random.choice([-0.01, 0.01, 12.5, -100.0]), 2)
        # Formato de monto inconsistente a propósito: a veces coma decimal
        monto_str = (
            f"{monto:.2f}".replace(".", ",") if random.random() < 0.2
            else f"{monto:.2f}"
        )
        filas.append(
            [t["referencia_externa"], t["fecha"].date().isoformat(),
             monto_str, estado]
        )

    # Refs que están en el CSV pero NO en la base (15 filas)
    for i in range(15):
        filas.append(
            [f"PX-{99000 + i}",
             (datetime(2026, 5, 1) + timedelta(days=i)).date().isoformat(),
             f"{random.uniform(1000, 90000):.2f}", "OK"]
        )

    # 5 filas corruptas (monto vacío o basura) para testear robustez
    filas.append(["PX-10001", "2026-05-10", "", "OK"])
    filas.append(["PX-10002", "no-es-fecha", "1500.00", "OK"])
    filas.append(["", "2026-05-11", "2000.00", "OK"])
    filas.append(["PX-10003", "2026-05-12", "N/A", "OK"])
    filas.append(["PX-10004", "2026-05-13", "3.000,50", "PENDIENTE"])

    random.shuffle(filas)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["referencia", "fecha_liquidacion", "monto", "estado"])
        w.writerows(filas)


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    cx = sqlite3.connect(DB_PATH)
    crear_esquema(cx)
    transacciones = poblar(cx)
    cx.commit()
    cx.close()
    generar_csv(transacciones)
    print(f"OK -> {DB_PATH} y {CSV_PATH} generados.")


if __name__ == "__main__":
    main()
