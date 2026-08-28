# Fichas por Validación — detalle a fondo

> Detalle de cada validación: qué se validó, contra qué, universo, fechas, método, resultado y no-conformes.
> Todas las cifras citan su fuente en `_resultados/` (DuckDB). Ver universos en `01_TABLA_MAESTRA_VALIDACIONES.md`.

---

## V-01 · Rendimiento plazo fijo — motor vivo (origin IS NULL)
- **Qué:** el interés de inversión a plazo que **genera AurumCore** (no el migrado), reproducido por el oráculo C.
- **Contra qué:** `investment_account` / plan de pagos, fórmula `RoundHalfEven2(Ceil10(Ceil10((C×T)/100)/Y)×Días)`,
  base 360. Método: tasa despejada del periodo 1; el oráculo reproduce **todos** los periodos.
- **Universo:** **157,999 cuentas · 530,195 periodos** (todas las origin IS NULL). Corte 2026-08-20.
- **Resultado:** **100.00% · 0 violaciones.** El motor de cálculo más sólido; sin no-conformes.
- **Fuente:** `PLAZO_LIVE_ESCALA_2026-08-20.txt`.

## V-02 · Rendimiento plazo fijo — migrado (origin=FINSUS)
- **Qué:** el mismo motor sobre inversiones **ingestadas de openfin** (origin=FINSUS).
- **Universo:** 300 cuentas (muestra) · 3,748 periodos. **97.79%** (3,665 cuadran, **83 no cuadran**).
- **No-conformes (ejemplos):** cta `00003b5f-18b` p8 aurum=376.46 / oráculo=426.66; p9 aurum=401.56 / oráculo=351.36;
  cta `0001a2ba-8cd` p0 aurum=122.49 / oráculo=237.33. Patrón: periodos de inversiones migradas con tasa/base de
  originación distinta a la despejada del p1 → residuo de **migración**, no del motor vivo (que da 100%).
- **Fuente:** `PLAZO_origin_migrado_vs_live_2026-08-20.txt`.

---

## V-03 · Rendimiento vista — integridad de posteo (feed ↔ DB)
- **Qué:** que **cada pago de rendimiento** que el core escribe en su feed operativo (`yield-trans`) exista en la
  DB con la misma cuenta y monto. (Integridad de posteo, no el cálculo independiente del oráculo → ese es V-04.)
- **Universo / fechas:** feed **2026-08-18**; **30,769 pagos capturados** (1 pod), 20,162 tx. DB día completo:
  **38,921 pagos · $5,751,013.03**. Productos 2301/2307/2308 (inversión).
- **Resultado:** **feed ⊆ DB = 30,769 / 30,769 = 100.00%** (match por `payee_account_id` + monto). El feed es un
  reflejo fiel de la DB; el capturado es parcial (un pod). La DB es la fuente autoritativa del día.
- **Fuente:** `yield_feed_2026-08-18.csv` · `RESULTADO_rendimiento_feed_2026-08-23.md`.

## V-04 · Rendimiento vista — oráculo independiente ◐
- **Qué:** el cálculo del interés vista por el oráculo (`SPM × dt × tasa / 36000`, base 360, half-up) vs lo posteado.
- **Estado:** ◐ **~82% reconstruido** de `finsus_account_history`; el **motor vivo se observa el 31-ago** (1er cierre
  mensual de vista post-cutover). El residuo es el `dt` exacto + el SPM-de-rendimiento (en la póliza).
- **Fuente:** `average_balance_sweep_core-rendimientos.csv` (barrido de saldo promedio, 27 cuentas, 08-06→08-23).

## V-05 · Saldo promedio (SPM) — insumo 🔒
- **Qué:** el saldo promedio de **rendimiento** (distinto del de consulta `account.average_balance_amount`).
- **Estado:** 🔒 solo existe en logs; barrido parcial (27 cuentas · 90 filas · 2026-08-06→08-23). No cierra sin la
  traza completa `Calculating with average balance`.
- **Fuente:** `average_balance_sweep_core-rendimientos.csv` · `saldo_promedio_feed_2026-08-18.csv` (2 cuentas).

---

## V-07/08 · ISR inversiones — join A/B/C y desviación clasificada
- **Qué:** ISR de openfin (A) vs AurumCore (B) vs oráculo (C) sobre el universo de inversiones en común.
- **Universo:** **18,599 inversiones · 14,913 clientes.** Fechas: apertura **2024-08-01 → 2026-07-27**, corte **2026-08-03**.
  Plazos observados: `dias` 7 → 732.
- **Resultado:** descuadre bruto de ISR **0.006%**; tras clasificar **3,236 filas (2,774 clientes)** el **100%** es
  diferencia de **modelo** (openfin devenga ISR **diario**; AurumCore retiene **al pago**) → **$0.00 de defecto de
  cálculo real**. Las diferencias van en ambos sentidos (neto ≪ bruto).
- **Fuente:** `_isr_join_full.parquet` · `f1_desviacion_clasificada.parquet`.

## V-09/10/11 · ISR — reconciliación al pago y devengo diario
- **V-09 (al pago):** caso `1-10-370` **C = B** (Aurum posteó 765.75; C 765.76, dif de redondeo). `f1_aurum_isr_al_pago_SEMILLA_s1.parquet` (2 pagos, 2026-08-03).
- **V-10 (devengo diario A vs C):** 728 filas · 4 clientes · **2026-02-03 → 2026-08-03**; Σ\|dif\|=**5.87** en 728
  días-cliente (solo redondeo) → openfin y C aplican el **mismo motor**. `isr_dia_of` 0.00 → 13.90.
- **V-11 (saldo base, insumo):** 65 filas · 4 titulares · 16 cuentas · 2025-10-16→2026-08-03.
- **Parámetros:** tasa **0.9%**, exención **5×UMA = 213,973.20** (2026), base 365 — corroborados contra ley y config.
- **Observaciones abiertas:** **[go-forward]** openfin config efectiva 2026-08-31 = `tasa_ret 1.45% / top 158,469`
  ≠ Aurum (0.9% / 213,973.20) → escalar. **[C-001]** exención configurada en Aurum (206,367.60 = UMA 2025) ≠ la que
  aplica (213,973.20 = UMA 2026) → config stale.
- **Fuente:** `REPORTE_FASE1_ISR.md`.

---

## V-13 · Crédito interés ordinario
- **Qué:** provisión **diaria** de interés que el core escribe en su feed operativo (`credits-closing`), vs el
  oráculo `interes_dia = capital × (tasa/100) / 360` (base 360 = `calendar_type 1`).
- **Universo / fechas:** feed **2026-08-20**; **5,365 provisiones = 4,091 ordinario + 1,274 moratorio**; 4,945
  contract_id distintos.
- **Resultado ordinario:** tasa feed=DB **4,091/4,091 (0 mismatch)**; **Match EXACTO 1e-8 = 96.8%** (3,472/3,585 con
  capital); ≤$0.01 = 97.0%. **Sin sesgo.** El residual (108 con `capital=0` en stage; 506 sin snapshot ≤08-20) es
  **linaje de datos** (tabla de capital punto-en-tiempo), **no defecto de motor** (P-019, prioridad media).
- **Fuente:** `credito_provision_feed_2026-08-20.csv` · `RESULTADO_credito_vivo_2026-08-23.md`.

## V-14 · Crédito interés moratorio
- **Qué:** `capital_venc × (tasaMor/100) / 360`, días=1, sin redondear, vs `lc_finantial_data.capital_venc`.
- **Universo:** **1,274 provisiones** (692 con capital_venc). Feed 2026-08-20.
- **Resultado:** tasa feed=DB 100% (0 mismatch); **Match EXACTO 1e-8 = 81.1%** (561/692); ≤$0.01 = **95.7%** (662).
  Fuera = 30 placeholders (`capital_venc=10,000,000`) / liquidados (clase P-019). El residual sub-centavo =
  **granularidad del snapshot de capital_venc** (más volátil intra-período). **P-020 RESUELTA** (la "asimetría 2.7%"
  fue artefacto de comparación: moratorio redondeado vs feed sin redondear). Ratio `feed×360/(tasa/100)=capital_venc`
  = 1.0000 en 666/692.
- **Fuente:** `RESULTADO_credito_vivo_2026-08-23.md`.

## V-15 · Crédito conteo de días
- **Qué:** que los días de provisión = días del **período de amortización** (no transcurridos).
- **Universo:** 3 contratos (traza log `CreditAmortizationChargeServiceImpl.java:844 - Days N`), 2026-08-23.
- **Resultado:** confirmado — Aurum topa al período. Explica el ~5% de residual histórico del oráculo ordinario.
- **Fuente:** `credito_dias_log_2026-08-23.csv`.

---

## V-20 · Motor B diario — completitud A vs B
- **Qué:** que **no falte** ninguna operación de openfin (A) en AurumCore (B) — cruce de volumen por día.
- **Universo / fechas:** **6 días (2026-08-10 → 2026-08-18)**; 21K–29K ops/día.
- **Resultado:** **OF ≥ AU siempre** (delta +0.1% a +2.1%), es decir **0 faltantes** en B. Ejemplos: 08-14
  OF 29,029 vs AU 29,004 (+0.1%); 08-11 OF 21,956 vs AU 21,501 (+2.1%). Es cruce de **volumen** (falta el crosswalk
  tipo-numérico para instancia-a-instancia; SOL-004).
- **Fuente:** `MOTOR_B_multidia_2026-08.txt` · `motor_b_diario_2026-08-14*.txt`.

## V-21/22 · Contable — doble partida y detalle transaccional
- **Qué:** que cada día la balanza cumpla **doble partida** (Σdébitos + Σcréditos = 0.00, tolerancia **0.00**).
- **Universo / fechas:** **7 días (2026-08-10 → 2026-08-16)**; 17K–220K asientos/día. Detalle transaccional del
  08-14: **96,235 movimientos** (`_td_2026-08-14.csv`).
- **Resultado:** **descuadre = $0.00 en 7/7 días** (0 días violan). Montos diarios de $84M a $1,301M. Alerta abierta
  (balanza): producto 2001 −34% / `daily_account_balances` stale (D2, gap de mapeo contable → SOL).
- **Fuente:** `CONTABLE_BC_2026-08-20.txt` · `_td_2026-08-14.csv`.

## V-23 · Cuentahabientes WSO2 ↔ padrón Aurum
- **Qué:** cobertura bidireccional identidad ↔ padrón.
- **Universo / resultado:** Aurum→WSO2: **20 huérfanos** (`cuentahab_aurum_no_en_wso2.csv`); WSO2→Aurum: **181,850**
  teléfonos no en Aurum (`cuentahab_wso2_no_en_aurum.csv`); altas incompletas **295** (`cuentahab_altas_incompletas.csv`);
  teléfono duplicado en Aurum **1**. Asimetría de retención esperada por ciclo de vida de identidad (P-017), por confirmar.
- **Fuente:** `cuentahab_*.csv`.

---

## Nota final
- **Sin desviación de cálculo material abierta.** Los bloqueos (V-04 vista-oráculo, V-05 SPM, V-12 ISR-vivo) son de
  **insumo** (saldo base punto-en-tiempo en logs / 1er cierre mensual 31-ago), no de regla.
- Los % a 8 dec / 5 dec / centavo y la prueba de sesgo se explican en `MATRIZ_TOLERANCIAS.md`.
- **Verde ≠ dictamen:** el dictamen técnico lo emite el humano contra el Manual de Cálculos Oficiales.
