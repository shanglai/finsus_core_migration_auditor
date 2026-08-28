# Tabla Maestra de Validaciones — universo, fechas y resultado

> Una fila por validación. **n** = universo comparado (cuentas/contratos/clientes/eventos). Cada cifra cita su
> fuente en `40_validaciones/_resultados/` (DuckDB). Corte 2026-08-26. Detalle en `02_FICHAS_POR_VALIDACION.md`.

## Leyenda de estado
🟢 validado (sin desviación de motor) · ◐ parcial/reconstruido · 🔒 bloqueado (insumo en logs) · 🟡 residuo/observación

## A. Captación / Inversión

| # | Validación | Motor | Universo (n) | Rango fechas | Resultado | Estado | Fuente (DuckDB / reporte) |
|---|---|---|---|---|---|---|---|
| V-01 | Rendimiento **plazo fijo** — motor vivo (origin IS NULL) | C vs B | **157,999 cuentas · 530,195 periodos** | corte 2026-08-20 | **100.00%** (0 no cuadran) | 🟢 | `PLAZO_LIVE_ESCALA_2026-08-20.txt` |
| V-02 | Rendimiento **plazo fijo** — migrado (origin=FINSUS) | C vs B | 300 cuentas (muestra) · 3,748 periodos | corte 2026-08-20 | 97.79% (83 no cuadran) | 🟡 | `PLAZO_origin_migrado_vs_live_2026-08-20.txt` |
| V-03 | Rendimiento **vista** — integridad de posteo (feed↔DB) | feed vs B | **30,769 pagos** capturados · 20,162 tx | 2026-08-18 | **100.00%** feed⊆DB | 🟢 | `yield_feed_2026-08-18.csv` · `RESULTADO_rendimiento_feed_2026-08-23.md` |
| V-04 | Rendimiento **vista** — oráculo independiente | C vs B | ◐ ~82% reconstruido | motor vivo 31-ago | ◐ pendiente corrida viva | ◐ | `average_balance_sweep_core-rendimientos.csv` |
| V-05 | **Saldo promedio (SPM)** — barrido de logs | insumo | 27 cuentas · 90 filas | 2026-08-06 → 2026-08-23 | insumo (no cierra sin log completo) | 🔒 | `average_balance_sweep_core-rendimientos.csv` |
| V-06 | **GAT** inversión (nominal/real) | C vs B | 126,465 inv. (term7) + volúmenes por plazo | corte 2026-08-20 | reproduce **exacto** (no-circular) | 🟢 | `COMPARACION_C_vs_DOC.md` A4 |

## B. Fiscal — ISR

| # | Validación | Motor | Universo (n) | Rango fechas | Resultado | Estado | Fuente |
|---|---|---|---|---|---|---|---|
| V-07 | **ISR inversiones** — join A/B/C completo | A/B/C | **18,599 inversiones · 14,913 clientes** | apertura 2024-08-01→2026-07-27; corte 2026-08-03 | descuadre bruto 0.006%; **$0.00 defecto real** | 🟢 | `_isr_join_full.parquet` |
| V-08 | **ISR** — desviación clasificada | A/B/C | **3,236 filas · 2,774 clientes** | corte 2026-08-03 | 100% de casos = diferencia de **modelo** | 🟢 | `f1_desviacion_clasificada.parquet` |
| V-09 | **ISR** — retención al pago (caso reconciliado) | C vs B | cliente 1-10-370 (+ semilla) | 2026-08-03 | **C = B** (765.75 / C 765.76) | 🟢 | `f1_aurum_isr_al_pago_SEMILLA_s1.parquet` |
| V-10 | **ISR** — devengo diario A vs C | A vs C | 728 filas · 4 clientes | 2026-02-03 → 2026-08-03 | Σ\|dif\|=5.87 (redondeo); mismo motor | 🟢 | `f1_a_vs_c_diario_SEMILLA.parquet` · `f1_openfin_isr_diario_SEMILLA_s1.parquet` |
| V-11 | **ISR** — saldo base (insumo) | insumo | 65 filas · 4 titulares · 16 cuentas | 2025-10-16 → 2026-08-03 | insumo de la comparación | 🟢 | `f1_aurum_saldo_base_isr_SEMILLA_s1.parquet` |
| V-12 | **ISR-vivo** nativo (post-cutover) | C vs B | ~13% match | motor vivo 31-ago | 🔒 gap de insumo (saldo base en logs) | 🔒 | `ISR_LIVE_NATIVO_2026-08-20.txt` |

## C. Crédito

| # | Validación | Motor | Universo (n) | Rango fechas | Resultado | Estado | Fuente |
|---|---|---|---|---|---|---|---|
| V-13 | Crédito **interés ordinario** | C vs B | **4,091 provisiones** (3,585 c/ capital) · dentro de 4,945 contratos del feed | feed 2026-08-20 | **96.8% exacto 1e-8**; ≤$0.01 97.0%; **0 mismatch de tasa** | 🟢 | `credito_provision_feed_2026-08-20.csv` · `RESULTADO_credito_vivo_2026-08-23.md` |
| V-14 | Crédito **interés moratorio** | C vs B | **1,274 provisiones** (692 c/ capital_venc) | feed 2026-08-20 | **81.1% exacto 1e-8**; ≤$0.01 95.7%; **0 mismatch de tasa** | 🟢 | `RESULTADO_credito_vivo_2026-08-23.md` |
| V-15 | Crédito **conteo de días** | mecánica | 3 contratos (traza log) | 2026-08-23 | días = período de amortización (confirmado) | 🟢 | `credito_dias_log_2026-08-23.csv` |
| V-16 | Crédito **IVA** sobre interés | C vs B | **54,716 filas** con IVA | corte crédito | **99.0% exacto** (tasa impl. 16.0% en 95%) | 🟢 | `COMPARACION_C_vs_DOC.md` C3b |
| V-17 | Crédito **amortización** (francesa) | C vs B | 794 contratos | corte crédito | identidad de fila **99.9%**; interés Actual/360 exacto | 🟢 | `COMPARACION_C_vs_DOC.md` C5 |
| V-18 | Crédito **CAT** | C vs doc/B | 3 ejemplos doc + caso real | corte crédito | **3/3 vs doc**; caso real 35.1% = CAT stored | 🟢 | `COMPARACION_C_vs_DOC.md` C6 |
| V-19 | **IFRS 9** — etapas + % de reserva | C vs config B | **37/37 celdas** + stages | corte crédito | **37/37 exacto** = config real de Aurum | 🟢 | `COMPARACION_C_vs_DOC.md` E4 |

## D. Transaccional / Contable

| # | Validación | Motor | Universo (n) | Rango fechas | Resultado | Estado | Fuente |
|---|---|---|---|---|---|---|---|
| V-20 | **Motor B diario** — completitud A vs B | A vs B | 6 días · 21K–29K ops/día | 2026-08-10 → 2026-08-18 | OF ≥ AU siempre (+0.1% a +2.1%); 0 faltantes | 🟡 | `MOTOR_B_multidia_2026-08.txt` |
| V-21 | **Contable** — doble partida diaria | B | 7 días · 17K–220K asientos/día | 2026-08-10 → 2026-08-16 | descuadre **$0.00** en 7/7 días | 🟢 | `CONTABLE_BC_2026-08-20.txt` |
| V-22 | **Contable** — detalle transaccional (día completo) | B | **96,235 movimientos** (08-14) | 2026-08-14 | insumo de amarre (doble partida) | 🟢 | `_td_2026-08-14.csv` |
| V-23 | **Cuentahabientes** WSO2 ↔ padrón Aurum | cobertura | Aurum→WSO2: **20 huérfanos**; WSO2→Aurum: **181,850**; altas incompletas 295 | corte 2026-08-20 | asimetría de retención (P-017) | 🟡 | `cuentahab_*.csv` |

---

## Cronología de ejecución (cuándo se corrió cada validación)

> **Timestamp de ejecución** = mtime del resultado materializado (cuándo lo corrimos). Distinto de la **fecha de los
> datos** (con qué corte se validó). Ventana global de ejecución: **2026-08-17 22:22 → 2026-08-23 18:26**.

| # | Validación | Ejecutado (corrida) | Fecha de datos | Artefacto |
|---|---|---|---|---|
| V-01 | Plazo live | 2026-08-21 17:04 | corte 08-20 | `PLAZO_LIVE_ESCALA_2026-08-20.txt` |
| V-02 | Plazo migrado | 2026-08-20 18:49 | corte 08-20 | `PLAZO_origin_migrado_vs_live_2026-08-20.txt` |
| V-03 | Vista feed↔DB | feed 2026-08-23 14:04 · reporte 2026-08-23 17:15 | datos 08-18 | `yield_feed_2026-08-18.csv` · `RESULTADO_rendimiento_feed_2026-08-23.md` |
| V-04/05 | Vista oráculo / SPM | 2026-08-23 17:26 | 08-06→08-23 | `average_balance_sweep_core-rendimientos.csv` |
| V-07 | ISR join A/B/C | 2026-08-17 22:22 | corte 08-03 | `_isr_join_full.parquet` |
| V-08 | ISR desviación clasif. | 2026-08-18 17:37 | corte 08-03 | `f1_desviacion_clasificada.parquet` |
| V-09 | ISR al pago | 2026-08-18 09:59 | 08-03 | `f1_aurum_isr_al_pago_SEMILLA_s1.parquet` |
| V-10 | ISR devengo diario | 2026-08-18 10:53–10:56 | 02-03→08-03 | `f1_a_vs_c_diario_SEMILLA.parquet` · `f1_openfin_isr_diario_SEMILLA_s1.parquet` |
| V-11 | ISR saldo base | 2026-08-18 09:59 | 10-16→08-03 | `f1_aurum_saldo_base_isr_SEMILLA_s1.parquet` |
| V-12 | ISR-vivo nativo | 2026-08-21 08:27 | corte 08-20 | `ISR_LIVE_NATIVO_2026-08-20.txt` |
| V-13/14 | Crédito ord/mora | feed 2026-08-23 14:06 · reporte 2026-08-23 18:26 | feed 08-20 | `credito_provision_feed_2026-08-20.csv` · `RESULTADO_credito_vivo_2026-08-23.md` |
| V-15 | Crédito días | 2026-08-23 13:57 | 08-23 | `credito_dias_log_2026-08-23.csv` |
| V-20 | Motor B diario | 2026-08-23 13:10 (multidía) · 08-14 corrido 2026-08-20 07:55 | 08-10→08-18 | `MOTOR_B_multidia_2026-08.txt` · `motor_b_diario_2026-08-14.txt` |
| V-21 | Contable doble partida | 2026-08-20 14:53 | 08-10→08-16 | `CONTABLE_BC_2026-08-20.txt` |
| V-22 | Contable detalle txn | 2026-08-20 16:20 | 08-14 | `_td_2026-08-14.csv` |
| V-23 | Cuentahabientes WSO2 | 2026-08-20 13:58 | corte 08-20 | `cuentahab_*.csv` |
| V-06,16,17,18,19 | GAT · IVA · Amortización · CAT · IFRS 9 | corrida ad-hoc (autopruebas `oraculo_*.py` + cruce BD), documentada en `COMPARACION_C_vs_DOC.md` (act. 2026-08-23) | corte crédito | `COMPARACION_C_vs_DOC.md` |

**Lectura:** el grueso del ISR se corrió el **17–18 de ago**; plazo, contable, cuentahabientes y motor-B el **20–21 de
ago**; crédito vivo, rendimiento vista y saldo promedio el **23 de ago** (tras unificarse la VPN de logs). El detalle
por-dataset (mtime exacto) está en `03_INVENTARIO_DUCKDB.md`.

---

## Resumen de universos (headline)
- **Inversiones:** 18,599 (14,913 clientes) · **Plazo fijo:** 530,195 periodos (157,999 cuentas) · **GAT:** 126,465 (term7).
- **Crédito:** 4,091 ordinario + 1,274 moratorio (feed 08-20; 4,945 contratos) · **IVA:** 54,716 · **Amortización:** 794 · **IFRS 9:** 37/37.
- **Vista (feed):** 30,769 pagos (día completo DB 38,921) · **Contable:** 96,235 movimientos (08-14), doble partida 7/7 días $0.00.
- **Motor B:** 6 días, 21K–29K ops/día · **Cuentahabientes:** 20 / 181,850 / 295.
- **Sin desviación de cálculo material abierta.** Bloqueos por insumo (logs/31-ago): vista-oráculo, SPM, ISR-vivo.
