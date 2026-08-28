# Paquete de Datos para Auditoría — Validación de Migración de Core Finsus

> Solicitado por la auditoría de Finsus: **lista de cada validación, rango de fechas de la base, número de
> cuentas y todo el detalle disponible.** Este paquete se arma **desde los datos materializados en DuckDB**
> (`40_validaciones/_resultados/`: parquet + feeds CSV + reportes de corrida). Linko · tercero independiente.
> Corte **2026-08-26**. Motor A = openfin · Motor B = AurumCore · Motor C = oráculo independiente.

## Cómo está organizado
| Archivo | Contenido |
|---|---|
| **00_INDICE.md** | este índice + cobertura de fechas de las bases + notas de método |
| **01_TABLA_MAESTRA_VALIDACIONES.md** | una fila por validación: motor, universo (#cuentas/contratos/clientes), rango de fechas, resultado, fuente |
| **02_FICHAS_POR_VALIDACION.md** | ficha a detalle por validación: qué se validó, contra qué, universo, fechas, resultado, no-conformes |
| **03_INVENTARIO_DUCKDB.md** | inventario de cada dataset en DuckDB: esquema, filas, rangos de fecha, conteos de id |

## Principio (CLAUDE.md §3 · veracidad)
Cada cifra cita su **fuente exacta** (parquet/CSV/reporte). Lo no computado va **[PENDIENTE]**, nunca inventado.
Marcas: **[CONFIRMADO]** consta en BD/dato · **[PENDIENTE]** falta · **◐** parcial/reconstruido · **🔒** bloqueado.
Cada validación reporta **las filas que violan la regla** (0 filas = pasa); el foco está en los **no-conformes**.

---

## Cobertura de fechas de las bases (rango de datos disponible)

> De la volumetría materializada en DuckDB (`f1_00_volumetria_*`), corte de extracción de Fase 1.

| Base | Rango de fechas | Fuente (DuckDB) | Nota |
|---|---|---|---|
| **openfin (A, t-1)** | **2025-09-03 → 2026-08-17** | `f1_00_volumetria_of_SEMILLA_s2.parquet` | Core histórico (referencia, no la verdad). |
| **AurumCore (B)** | **2025-10-16 → 2026-08-03** | `f1_00_volumetria_ac_SEMILLA_s1.parquet` | Sistema bajo prueba. |
| **Inversiones (apertura)** | **2024-08-01 → 2026-07-27** | `_isr_join_full.parquet` (`f_ape`) | Fecha de apertura de las inversiones vivas. |
| **Inversiones (cierre/corte)** | **2026-08-03** | `_isr_join_full.parquet` (`f_cie`) | Fecha de corte del universo de inversiones. |

**Hito de cutover:** las **retenciones de ISR en AurumCore existen desde el 2026-08-02** (antes, el ISR lo llevaba
openfin). La comparación de ISR es, en el fondo, de migración/cutover.
→ fuente: `REPORTE_FASE1_ISR.md` §1.5.

**Ventanas de corrida por dominio** (fecha de los datos con que se validó cada motor; detalle en las fichas):
- Plazo / inversiones (origin): **2026-08-20** · ISR inversiones (join): corte **2026-08-03**, diario **2026-02-03 → 2026-08-03**.
- Crédito (provisión diaria del feed): **2026-08-20** · Rendimiento vista (feed yield): **2026-08-18**.
- Saldo promedio (barrido logs): **2026-08-06 → 2026-08-23** · Motor B diario: **2026-08-10 → 2026-08-18** (6 días).
- Contable B/C: **2026-08-10 → 2026-08-16** (7 días).

---

## Nota de método (para leer los números)
- **Universo (n):** número de eventos/cuentas/contratos/clientes efectivamente comparados por cada validación.
  Donde el dato es una **muestra semilla** (SEMILLA) se indica explícitamente; donde es el **universo completo**
  también.
- **% de cuadre a 8 dec (1e-8) / al centavo ($0.01):** ver `MATRIZ_TOLERANCIAS.md` para la explicación de las
  granularidades y la prueba de sesgo. En este paquete se reportan los % ya computados con su universo.
- **DuckDB:** las bases fuente (openfin/AurumCore, PostgreSQL) se consultan en solo lectura; los resultados se
  materializan a `_resultados/` (parquet/CSV) y se consultan con DuckDB in-memory. Este paquete se arma de esos
  materializados (snapshot estable), no de la BD viva.
- **Timestamp de ejecución (cuándo se corrió):** cada resultado lleva su hora de corrida (mtime del artefacto). La
  **cronología por validación** está en `01_TABLA_MAESTRA_VALIDACIONES.md` y el **mtime exacto por dataset** en
  `03_INVENTARIO_DUCKDB.md`. Ventana global de ejecución: **2026-08-17 22:22 → 2026-08-23 18:26**. Ojo: la fecha en
  el *nombre* del archivo es la **fecha de los datos**; el mtime es **cuándo lo corrimos** (pueden diferir).
