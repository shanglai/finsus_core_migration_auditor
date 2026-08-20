# Mapeo columna a columna — OpenFin ↔ AurumCore

Versión: 1 · 2026-08-17 · Base de la Fase 1 (comparador A↔B).
Fuentes: F-014 (diccionario Aurum), F-015 (diccionario OpenFin), K-DAT-002/003/006, K-CTB-001.
OpenFin = esquema `public` de `openfin_aurum` (t‑1). Aurum = esquema `aurumcore`.

> Marcas: [CONFIRMADO] = validado por el árbol (los joins produjeron los universos en común) o por
> DDL directo. [INFERIDO] = deducido del formato de id, por confirmar en el primer cuadre.

## Llaves de correlación (lo primero)
| concepto | OpenFin | AurumCore | nota |
|----------|---------|-----------|------|
| **cliente** | `asociados(idsucursal, idrol, idasociado)` | `accountholder.accountholder_number` | [CONFIRMADO] mismo string, formato `suc-rol-asoc` (p.ej. `100-10-233102`). El árbol cuadró 956,331 clientes por esta llave |
| **cuenta** | `acreedores/deudores(idsucaux, idproducto, idauxiliar)` | `account.account_number` | [CONFIRMADO] formato `sucaux-producto-auxiliar` (p.ej. `100-2002-232884`); producto = `split_part(account_number,'-',2)` |
| **producto** | `idproducto` | 2º segmento de `account_number` | 2000s vista · 2300s inversión · 5004 One Click |
| **movimiento↔transacción (cross-core)** | `detalle_auxiliar_masdatos.id_external` | `transaction.external_id` | [CONFIRMADO] única llave 1:1, **garantizada sólo en SPEI** (K-MOV-003) |

## Cuentas y saldos
| concepto | OpenFin `acreedores` | AurumCore `account` (+ `account_yield`) | nota |
|----------|----------------------|------------------------------------------|------|
| estatus | `estatus` (1-5) | `state` / `iv_account_state` (3/4/5) | dominios distintos; homologar |
| saldo | `saldo` | `balance_amount` | |
| saldo promedio | esquema `etl_saldo_prom_mensual` / reconstruir | `average_balance_amount` (+ `account_balance_tracking`) | base del ISR y del rendimiento vista (P-006) |
| tasa | `tasa` | `account_yield.interest_rate` | |
| base días | (config/misceláneo) | `account_yield.days_in_year` | 360/365 |
| exención ISR | `retxaplicar` (parcial) | `account_yield.isr_exempt` | |
| fecha apertura | `fechaape` | `activation_date` / `created` | |
| fecha cierre | `fechacancelacion` | `iv_closing_date` / `closed_date` | |

## Inversiones (plazo)
| concepto | OpenFin | AurumCore | nota |
|----------|---------|-----------|------|
| capital | `acreedores.montocontrato` | `account.iv_initial_amount` | validado en Fase 0 |
| rendimiento por periodo | `pago_intereses_log` / detalle | `iv_payment_plan.interest_amount` | multiperiodo: usar el plan |
| rendimiento pagado (total) | detalle_auxiliar (montoio) | Σ `iv_payment_plan` | |
| **ISR retenido** | **`isr_diario`** (diario) / `retxaplicar` | `transaction_detail` (ISR al pago) | ⚠ **modelo distinto** (A15-ISR-DIARIO): OF diario vs AC al pago → normalizar antes de comparar |

## Movimientos ↔ transacciones
| concepto | OpenFin `detalle_auxiliar`(+`_masdatos`) | AurumCore `transaction`(+`transaction_detail`) | nota |
|----------|------------------------------------------|-----------------------------------------------|------|
| id | `secuencia` (PK) | `transaction_detail_id` / `transaction_id` | no 1:1 |
| fecha/hora | `fecha`, `hora` | `transaction.created`, `transaction_detail.created` | |
| cargo / abono | `cargo` / `abono` | `debit_amount` / `credit_amount` | |
| saldo posterior | `saldo` (sólo final) | `source_after_balance` / `target_after_balance` | Aurum tiene prior+after; OF solo final → reconstruir (K-MOV-006) |
| comisión | `montocomision` (misma fila) | `fee_amount` (fila) + `parent_transaction_id` | OF empaqueta; AC enlaza al padre (K-MOV-001/005) |
| tipo | `masdatos.tipo_transaccion` (3/183/0) + `tipomov` (0-5) | `transaction.type` / `transaction_detail.transaction_type` | modelos distintos; mapear vía catálogo |
| cuenta contable | `idpoliza` → `polizas` | `accounting_account` + `cat_accounting_transaction` | K-CTB-001 |
| cross-sistema | `id_external` | `external_id` | SPEI |

## Crédito One Click (5004)
| concepto | OpenFin `deudores` (prod 5004) | AurumCore `lc_loan_contract` (+`lc_products`) | nota |
|----------|-------------------------------|-----------------------------------------------|------|
| monto entregado | `montoentregado` | `loan_amount` | cuadró 100% en el árbol (K-COL-001) |
| tasa ord/mor | `tasaio` / `tasaim` | `ordinary_interest_rate` / `moratorium_interest_rate` | |
| estatus cartera | `estatuscartera` | (lc_*) | |

## Diferencias de modelo a normalizar ANTES de comparar (no son defectos)
1. **ISR:** OF diario (`isr_diario`) vs AC al pago → sumar el diario del periodo. (A15-ISR-DIARIO)
2. **Atomicidad:** OF cargo+abono(+comisión/impuesto sueltos) vs AC atómico con `parent_transaction_id`. (K-MOV-001)
3. **Saldo anterior:** OF no lo guarda (reconstruir); AC sí (`*_prior_balance`). (K-MOV-006)
4. **Redondeo:** OF trunca; AC half_even. (K-DEV-001, hallazgo Fase 0)
5. **Sincronía:** procesos en distinto momento (ver `VALIDACION_DOS_MOMENTOS`).

## Pendiente
- Confirmar el formato exacto de `accountholder_number`/`account_number` vs las llaves de 3 campos en
  el primer cuadre (marcado [CONFIRMADO] por el árbol, pero fijar la transformación exacta).
- Mapear el catálogo de tipos (`tipomov`/`tipo_transaccion` OF ↔ `type`/`transaction_type` AC).
