# Informe Detallado — Captación / Inversión y Fiscal

> Ficha por punto: Alcance · Periodo · Universo y representatividad · Metodología + rationale
> Conciliación. Motor A=openfin · B=AurumCore · C=oráculo. Todo solo lectura, `decimal.Decimal`. Corte 2026-08-26.

---

## V-01 · Rendimiento plazo fijo — motor vivo (`origin IS NULL`)

- **Alcance — sí:** interés de inversión a plazo **generado por AurumCore** (no migrado), todos los periodos.
  **No:** inversiones migradas (eso es V-02); productos sin plan de pagos.
- **Periodo:** corte de datos 2026-08-20. Ejecutado 2026-08-21 17:04.
- **Universo y representatividad:** **530,195 periodos / 157,999 cuentas** validados, de **1,339,023** periodos
  **live-pagados** (`origin IS NULL ∧ interest_paid ∧ interest_amount>0`) → **~39.6%** (de 36,905,411 periodos totales
  en `iv_payment_plan`, la mayoría migrados/futuros). Es **censo del cohorte aplicable**, no muestra.
- **Metodología + rationale:** el método V5 (**despejar la tasa del periodo 1 y reproducir los demás**) exige que la
  cuenta tenga **≥2 pagos** (`having count(*)>=2`) + `iv_initial_amount>0` + días válidos. Ese cohorte = 157,999 ctas /
  530,195 per. Las cuentas de **un solo pago** (el grueso del resto) **no son validables por este método** (no hay
  periodo desde donde despejar sin circularidad) → quedan fuera **por metodología, no por muestreo**. Dentro del
  cohorte se corre el **100%** (censo).
- **Santo y seña:** CTE cohorte sobre `aurumcore.iv_payment_plan` (`origin IS NULL`, `interest_paid=true`,
  `interest_amount>0`, `having count(*)>=2`) ⋈ `aurumcore.account` (`iv_initial_amount>0`); campos `payment_number`,
  `due_date−start_date` (días), `interest_amount`, `iv_initial_amount`. Motor `comparadores/validate_plazo_origin.py`
  (`--limite 0`). Fórmula `RoundHalfEven2(Ceil10(Ceil10((C×T)/100)/Y)×Días)`.
- **Conciliación (C vs B):** **100.00%**, 0 violaciones. `PLAZO_LIVE_ESCALA_2026-08-20.txt`.

## V-02 · Rendimiento plazo fijo — migrado (`origin='FINSUS'`)

- **Alcance — sí:** inversiones **ingestadas de openfin**. **No:** las live (V-01).
- **Universo y representatividad:** **300 cuentas / 3,748 periodos = muestra de contraste**, de **32,986,518** periodos
  migrados (`origin='FINSUS'` en `iv_payment_plan`).
- **Metodología + rationale:** muestra para **contrastar** el comportamiento migrado vs live; no busca cerrar el motor
  (ya cerrado en V-01), sino caracterizar el residuo de migración.
- **Santo y seña:** igual que V-01 con filtro `origin='FINSUS'`. Motor `validate_plazo_origin.py`.
- **Conciliación:** 97.79% (83 no cuadran) — residuo de **migración** (tasa/base de originación ≠ despejada del p1),
  no del motor vivo. `PLAZO_origin_migrado_vs_live_2026-08-20.txt`.

## V-03 · Rendimiento vista — integridad de posteo (feed ↔ DB)

- **Alcance — sí:** que **cada pago** del feed `yield-trans` exista en la DB con misma cuenta y monto. **No:** el
  cálculo independiente del oráculo (eso es V-04).
- **Periodo:** datos 2026-08-18. Ejecutado 2026-08-23 17:15.
- **Universo y representatividad:** **30,769 pagos capturados (1 pod) = subconjunto**; el día completo en DB son
  **38,921 pagos** ($5,751,013.03). Repr. = 79% del día (limitado por captura de 1 pod, no por muestreo).
- **Santo y seña:** feed `yield-trans-*.gz` ↔ `aurumcore.transaction_detail`/`transaction`; llave `payee_account_id`
  + monto. `RESULTADO_rendimiento_feed_2026-08-23.md`.
- **Conciliación:** feed ⊆ DB = **30,769/30,769 = 100.00%**.

## V-04 · Rendimiento vista — oráculo independiente (ciclo julio)

- **Alcance — sí:** el interés mensual de **cuenta a la vista** que Aurum posteó, recalculado por el oráculo.
  **No:** cuentas sin pago en julio; el ciclo vivo de agosto (cierra 31-ago → se re-corre entonces).
- **Periodo:** SPM al **cierre 2026-07-31**; B posteada **pago 2026-08-01**. Ejecutado 2026-08-28.
- **Universo y representatividad:** **83,094 cuentas = censo** de los pagadores vista de julio (≈83,174 con `yield_amount>0`
  ∧ historia). ~100% de los pagadores del ciclo. (Cuentas vista totales el 31-jul: 915,016, la mayoría con interés 0.)
- **Metodología + rationale:** censo del ciclo cerrado; se probaron las convenciones (base 360/365 · dt 30/31) y se
  reporta la que ajusta (no-circular).
- **Santo y seña:** `aurumcore.yield_dto` (`iv_payment_plan_id IS NULL` = vista, `process_date='2026-08-01'`,
  `yield_amount`) ⋈ `aurumcore.finsus_account_history` (`record_date='2026-07-31'`: `average_balance_amount`=SPM,
  `interest_rate`=tasa); llave `account_id`. Motor `comparadores/oraculo_vista_finsus_history.py`; tolerancias
  `tolerancias.py`.
- **Conciliación (C vs B, base 360·dt 31) — CICLO VIVO DE AGOSTO [2026-09-01]:** **94.56% a 1e-8 · 94.82% al centavo**
  (censo 82,925; pago 01-sep vs SPM 31-ago). Consistente con julio (94.76/95.03) → **cifra de referencia única, AUD-004
  cerrado.** Residuo ~5% = `dt` intra-mes (ambos sentidos), no defecto. `RESULTADO_vista_vivo_2026-09-01.md`.

## V-05 · Saldo promedio (SPM) — insumo 🔒

- **Alcance:** el SPM **de rendimiento** (distinto del de consulta `account.average_balance_amount`).
- **Universo y representatividad:** **27 cuentas / 90 filas = subconjunto parcial** (barrido de logs).
- **Metodología + rationale:** el SPM de rendimiento **solo existe en logs** (rolling logs); barrido parcial. Bloqueado
  hasta el cierre con logs.
- **Santo y seña:** `average_balance_sweep_core-rendimientos.csv` (barrido `barrido_average_balance.py`, string
  `Calculating with average balance`). **Nota:** V-04 ya no depende de este SPM (usa `finsus_account_history`).

## V-06 · GAT inversión (nominal/real)

- **Alcance — sí:** el GAT publicado al cliente (`nominal_cgat`/`real_cgat`), prueba **no-circular**. **No:** GAT de
  cuenta vista (Aurum no lo guarda: `nominal_cgat=0` en ACCOUNT).
- **Universo y representatividad:** **126,465 inversiones term7 = estrato de prueba**, de **706,600** cuentas de
  inversión (`aurumcore.account` con `nominal_cgat>0`; el doc citaba 689,479, un corte previo). El estrato prueba que el
  `nominal_cgat` es función pura de (tasa, plazo) — no requiere censo para ser concluyente.
- **Santo y seña:** `aurumcore.account.nominal_cgat`/`real_cgat` (las inversiones son filas de `account`, no una tabla
  aparte); inflación `cat_financial_variables.INFLATIONMXN`
  punto-en-tiempo. Motor `oraculo_gat.py`. `GATnom = ((Inicial+Interés)/Inicial)^(360/días) − 1`.
- **Conciliación:** reproduce **exacto** el `nominal_cgat` desde la tasa contratada (term7→10.42 en 126,465 inv.).
  Cruce 1-a-1 masivo pendiente de la tabla de tramos de tasa (SOL-015, data-sourcing).

---

## V-07/08 · ISR inversiones — join A/B/C y desviación clasificada

- **Alcance — sí:** ISR de openfin (A) vs Aurum (B) vs oráculo (C) sobre el universo de inversiones en común. **No:**
  personas morales (residuo P/SOL-011); ISR-vivo post-cutover (V-12).
- **Periodo:** apertura 2024-08-01 → 2026-07-27; corte 2026-08-03. Ejecutado 2026-08-17/18.
- **Universo y representatividad:** **18,599 inversiones / 14,913 clientes = censo del universo común A∩B.** Desviación
  clasificada: **3,236 filas / 2,774 clientes** (censo de las que difieren).
- **Metodología + rationale:** este es el único cruce que **concilia A contra B** (no solo vs Aurum): se emparejan las
  inversiones comunes por id y se clasifica cada diferencia.
- **Santo y seña:** `_isr_join_full.parquet` (id_inversion_aurumcore/openfin, isr_ac/isr_of, id_cliente, monto, tasa);
  clasificación `f1_desviacion_clasificada.parquet`. Comparadores `fase1_isr_*`.
- **Conciliación:** descuadre bruto **0.006%**; el 100% de las 3,236 = diferencia de **modelo** (openfin devenga ISR
  diario; Aurum retiene al pago) → **$0.00 de defecto real**. Caso reconciliado 1-10-370: **C=B**. Parámetros = ley
  2026 (0.9%, 5×UMA=213,973.20). Observaciones abiertas: config go-forward openfin 1.45% (P) y C-001 exención stale.

## V-12 · ISR-vivo nativo (post-cutover) 🔒

- **Alcance:** el ISR que Aurum retiene en vivo tras el cutover.
- **Universo y representatividad:** ~13% match — **bloqueado** por insumo.
- **Metodología + rationale:** requiere el **saldo base punto-en-tiempo** al momento del pago; los saldos actuales solo
  aproximan y no sirven (F-031 @00:52). Mismo bloqueo que V-05.
- **Santo y seña:** `ISR_LIVE_NATIVO_2026-08-20.txt`. Desbloqueo: traza de saldo base al pago / cierre con logs.
