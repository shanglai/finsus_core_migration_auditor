# Referencia — tablas / columnas / filtros / bases por caso de validación

> Para revisión. Por cada caso: **base**, **tablas**, **columnas clave**, **filtros/delimitadores**, **llaves**,
> **oráculo/identidad** y **script**. Bases (solo lectura): `aurum` (AurumCore, 10.10.160.53/aurumcore) ·
> `openfin` (réplica t-1, 10.10.164.25/openfin_aurum/public) · `identityshared` (WSO2, 10.10.160.27).
> **⚠️ Delimitador "Aurum vivo":** ver nota al final — `origin is null` NO es limpio; usar `created >= cutover`.

---

## ISR-01 · Retención de ISR al pago (motor B — AurumCore)
- **Base:** aurum
- **Tablas:** `transaction_detail`, `transaction`, `account` (payer y payee), `accountholder`; saldo base:
  `account_balance_tracking`; capital inversión: `account.iv_initial_amount`.
- **Firma del asiento (verificada):** `transaction_type='INTERNAL TRANSFER'` · `transaction_channel='Generic'` ·
  contrapartida = cuenta de ISR, producto `0000` (p.ej. `100-0000-438220`); `isr_retenido = credit_amount`.
- **Columnas:** `td.credit_amount` (ISR), `t.payer_account_id`/`payee_account_id`, `t.origin`, `td.created`.
- **Filtros:** ventana de fecha; contrapartida producto 0000; cohorte por `accountholder`. **Live:** `created >= cutover`.
- **Oráculo (C):** `oraculo_isr.py::isr_retenido(saldo_total, saldo_cuenta, dias)` · params UMA 42,794.64 · tasa 0.90% ·
  exención 5×UMA=213,973.20 · 365 días · proporción ÷ **saldo_total**.
- **Script:** `comparadores/fase1_isr_*` · (nuevo) `isr_live_nativo.py`.

## ISR-02 · Devengo diario de ISR (motor A — OpenFin)
- **Base:** openfin · **Tabla:** `isr_diario` (cliente-día, 171.8M), `isr_diario_aux_log`.
- **Llave:** `kasociado` = `idsucursal-idrol-idasociado`. **Filtros:** ventana 2025-09-03 → 2026-08-17.
- **Identidad:** el devengo diario sigue la regla 2026 (≈100% de días) → el descuadre OF↔AC es de **modelo**.
- **Script:** `entrega_finsus/V2_isr_devengo_openfin.sql`, `fase1_isr_desviacion.py`.

## ISR-03 · Parámetros del ISR vs norma
- **Base:** norma (INEGI/LIF 2026/LISR) · AurumCore: `cat_tax`, `system_configuration`.
- **Valores:** UMA 42,794.64 · tasa 0.90% (LIF Art.24) · 5×UMA (LISR 93 fr.XX) · 365.

## REND-PLAZO · Rendimiento de plazo fijo (motor B)
- **Base:** aurum · **Tablas:** `iv_payment_plan`, `account`.
- **Columnas:** `iv_payment_plan`: `origin`, `interest_amount`, `interest_paid` (bool), `start_date`, `due_date`,
  `payment_date`, `payment_number`; `account.iv_initial_amount` (capital).
- **Días periodo:** `due_date - start_date`. **Tasa:** NO en tabla limpia (`account_yield.interest_rate`=0 para
  inversión) → se **despeja del periodo 1**.
- **Filtros:** `interest_paid=true`, `interest_amount>0`. **Migrado:** `origin='FINSUS'`. **Live:** `origin is null`
  + `payment_date >= cutover`.
- **Oráculo:** `oraculo_rendimientos.py::rendimiento_plazo` (Ceil10/Ceil10/RoundHalfEven2, base 360).
- **Script:** `comparadores/validate_plazo_origin.py`, `V5`.

## REND-VISTA · Interés de cuentas vista/ahorro (PENDIENTE)
- **Base:** aurum · **Tablas:** `transaction_detail` (ref `Capitaliza Interes …`, src=tgt), `account`
  (`average_balance_amount`, `yield_scheme_id`), `account_yield` (tasa ahorro).
- **Filtros:** productos 2006/2011/2012/2013/2015/2017/2019; capitalización fin de mes. **Live:** 1er cierre 1-sep.
- **Bloqueos:** tasa/saldo promedio exacto (logs del CORE, P-006). Migrado (ene-jul) validable con avg guardado.

## SALDO-PROM · Saldo promedio (PENDIENTE)
- **Base:** aurum · **Tablas:** `account.average_balance_amount` (guardado), `account_balance_tracking`
  (`initial/final/accumulated_balance`, `days_number_partial_accumulation`).
- **Fórmula (Finsus):** `(saldo_ant + Σ saldos_día) / n_días`. **Bloqueo:** valor exacto en **logs del CORE**;
  `account_balance_tracking` arranca ~ago-2025 (historia incompleta).

## DIARIO-B · Transaccional diaria (Motor B, A↔B)
- **Bases:** openfin + aurum.
- **OpenFin:** `vista_movimientos_cargos` / `vista_movimientos_abonos` (`tipo_transaccion`, `monto`, `referencia`,
  `secuencia`); catálogo `cat_tx_cuadre` (`tipo_transaccion`→`cuenta_contable_cargo/abono`).
- **AurumCore:** `transaction_detail` (`transaction_type`) JOIN `transaction` (`origin`).
- **Filtros:** `created::date = día`; **sucursal 201 fuera**; exclusión de crédito (dispersión/pago); delimitador
  live (**revisar:** se usó `origin is null`; lo correcto es `created >= cutover`).
- **Clasificación:** `cat_tx_cuadre` ↔ `cat_finsus_transaction` (misma numeración); PEER 2:1 (2 piernas→1) vs UNI 1:1;
  categorización **por pierna** (SPEI-in = depósito en Aurum).
- **Script:** `comparadores/motor_b_diario.py`.

## CONTABLE-B1 · Doble partida diaria
- **Base:** aurum · **Tablas:** `transaction_detail` (`debit_amount` neg, `credit_amount` pos,
  `source_accounting_account`, `target_accounting_account`), `cat_accounting_account` (`account_nature`).
- **Filtro:** `created::date` por día (origin-agnóstico). **Identidad:** `Σ(debit)+Σ(credit)=0` (tol **0.00**).
- **Script:** `comparadores/contable_bc.py` (B1/B2 directo; B3/B4 vía DuckDB).

## BALANZA-D · Balanza por producto (cross A/B)
- **AurumCore:** `account.balance_amount` por producto (`split_part(account_number,'-',2)`); excl `201-%`.
- **OpenFin:** `acreedores.saldo` por `idproducto`; `estatus in (1,3,4,5)`; excl sucursal 201.
- **Nota:** `daily_account_balances` está **STALE** (solo oct-nov 2025) — NO usar.
- **Script:** (pendiente) `contable_d_balanza.py`.

## CUENTAHAB-01 · Identidad WSO2 ↔ AurumCore
- **WSO2 (identityshared):** `um_hybrid_user_role` (`um_user_name`=teléfono 10díg, `um_role_id`), `um_hybrid_role`.
  Clientes = roles CTP (id 40-48; created=42).
- **AurumCore:** `accountholder` (`username`, `contact_mobile_phone`, `email`, `accountholder_number`).
- **Llave:** teléfono 10 díg (WSO2.phone ↔ AU.username/contact_mobile_phone). **Excl:** sucursal 201.
- **Script:** `comparadores/cuentahabientes_wso2.py` · extracción `extraccion/wso2_cuentahabientes.sql`.

## GAPB-IDNC · Suspensión de devengo / IDNC
- **Base:** aurum · **Tablas:** `lc_finantial_data_stage` (`io`, `io_venc`, `iodnc`, `capital_venc`,
  `information_date`, `*_accounting_id`), `lc_loan_contract`.
- **Identidad:** `io + io_venc = 0` (suspensión total del devengo en vencida). **Script:** `V3_gapB_idnc.sql`.

## GAPC-PROSOFIPO · Cuota Prosofipo
- **Base:** aurum · **Búsqueda:** `system_configuration` (`name`/`value`/`category`) = **0** para
  cobertura/UDIS/prosofipo/fondo. **Hallazgo:** motor faltante (cuota por fuera). **Script:** `V4_gapC_prosofipo.sql`.

---

## ⚠️ Nota crítica — delimitador "Aurum vivo/nativo"
`transaction.origin` tiene semántica **mixta**: unos valores = **fuente de migración** (`FINSUS_INVESTMENT`,
`FINSUS_2`, `841`, `FINSUS_YIELD…`), otros = **canal/producto vivo** (`DIMO`, y `FINSUS_CREDIT`/`FINSUS_2` con
fecha post-cutover). Además `origin IS NULL` aparece **desde abril-2026** (periodo shadow, pre-cutover).
→ **`origin is null` NO es delimitador limpio.** El robusto es **`created >= cutover (2026-08-02/03)`**
(los migrados están fechados en su fecha original). Taxonomía completa de `origin`: **pedir a Finsus** ([[P-013]]).
