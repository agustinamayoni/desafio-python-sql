# Desafío Técnico – Python y SQL (IT Patagonia)

Este repositorio contiene la resolución de un desafío técnico desarrollado como parte del proceso de selección de **IT Patagonia**.

> **Nota:** Este proyecto fue realizado exclusivamente con fines de evaluación técnica.

---

## Objetivo

El objetivo del desafío es analizar información de liquidaciones utilizando **Python** y **SQL**, realizando tareas de procesamiento, validación, conciliación y generación de reportes.

Como resultado del análisis, se genera un gráfico con la evolución semanal de la tasa de rechazo por canal.

---

## Tecnologías utilizadas

- Python 3
- SQLite
- SQL
- Pandas
- Matplotlib

---

## Estructura del proyecto

```text
.
├── analisis.py                     # Script principal
├── seed_data.py                    # Generación de datos de prueba
├── desafio.db                      # Base de datos SQLite
├── queries_SQL/                    # Consultas SQL
├── discrepancias_conciliacion.csv  # Resultados de conciliación
├── liquidaciones_procesador.csv    # Datos de entrada
├── INFORME.md                      # Informe técnico
├── TABLERO.md                      # Documentación del tablero
└── tasa_rechazo_semanal_por_canal.png
```

---

## Cómo ejecutar el proyecto

1. Clonar el repositorio.

2. Instalar las dependencias necesarias:

```bash
pip install pandas matplotlib
```

3. Ejecutar el script principal:

```bash
python analisis.py
```

La base de datos SQLite (`desafio.db`) ya se encuentra incluida en el proyecto.

---

## Autor

**Agustina Mayoni**
