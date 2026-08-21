---
id: K-DAT-006
titulo: Modelo de datos y queries de AurumCore (esquema aurumcore)
dominio: DAT
estado: CONFIRMADO
confianza: alta
version: 6
creado: 2026-08-16
actualizado: 2026-08-16
fuentes:
  - ref: 20_fuentes/datos/Inventario_Queries_AurumCore.xlsx
    ubicacion: "Hoja 1, queries CLIENTES/CUENTAS/INVERSIONES/CRÉDITOS/TRANSACCIONES"
  - ref: acceso directo a la base aurumcore (screenshot \\d)
    ubicacion: "2026-08-16 · esquema public · owner aurumcoreuser · 26 relaciones"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md, 00_entendimiento/MODELO_DATOS_OPENFIN.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El modelo de datos de AurumCore (esquema `aurumcore`) queda revelado por los queries
oficiales de extracción. **Cierra buena parte de P-011** (la contraparte de OpenFin).
  → fuente: F-012

## Tablas y campos (de los queries)
- **`accountholder`** (clientes): `accountholder_id`, `accountholder_number`, `created`, `state`,
  `name`, `last_name`, `person_type`.
- **`account`** (cuentas vista e inversión): `account_id`, `account_number`, `accountholder_id`,
  `balance_amount`, `average_balance_amount`, `account_scheme_id`, `account_type`
  (`INVESTMENT_ACCOUNT` para inversiones), `activation_date`, `iv_closing_date`,
  `iv_initial_amount`, `bonus_amount`. **El producto se obtiene con `split_part(account_number,'-',2)`.**
- **`stored_value`** (`acc_id`, `amount`) → saldo disponible adicional (`available = balance + sv`).
- **`account_scheme`** (`account_scheme_id`, `yield_scheme_id`) ⋈ **`account_yield`**
  (`yield_scheme_id`, `interest_rate`, `enable`, `status`, `branch_id`) → la **tasa**.
- **`iv_account_commission`** (`account_id`, `percentage_amount`) e **`iv_payment_plan`**
  (`account_id`, `interest_amount`, `interest_paid`) → rendimiento pagado de inversiones.
- **`lc_loan_contract`** (`id`, `contract_number`, `accountholder_id`, `ordinary_interest_rate`,
  `moratorium_interest_rate`, `loan_amount`, `activation_date`, `term`, `lc_product_id`) ⋈
  **`lc_products`** (`product_number` = '5004') ⋈ **`lc_loan_charge`** (`lc_contract_id`, `amount`).
- **`"transaction"`** (`created`, …) — el query trae `select *` filtrado por día.

## Inventario real de tablas (acceso directo `\d`, 2026-08-16)
[CONFIRMADO] Ya hay **acceso de lectura a la base `aurumcore`**. El `\d` lista 26 relaciones
(esquema `public`, owner `aurumcoreuser`). Tablas relevantes: `account`, `account_balance_tracking`,
`account_holder`, `accountholder`, `investment`, `iv_payment_plan`, `payment_plan`,
`transaction_detail`, `fns_commission_task`, `fns_history_tiiemxn`, `diary_serie_report_history`,
`view_investment_balance_history`, `tmp_linaje_*`, `tmp_migracion_linaje`, `test/z_test/ztest`.

### Señales / discrepancias a verificar (banderas)
- **Tablas duplicadas aparentes:** `accountholder` **y** `account_holder`; `account` **y**
  `investment`; `payment_plan` **y** `iv_payment_plan`. Riesgo de doble modelo / artefacto de
  migración → confirmar cuál es la vigente para no comparar contra la tabla equivocada.
- **La query de transacciones (F-012) usa `aurumcore."transaction"`, que NO aparece en el `\d`**
  (sólo `transaction_detail`). La query está desactualizada o `transaction` es una vista no listada.
  **Verificar el nombre real** antes de correr el comparador de transacciones.
- **`fns_history_tiiemxn`** = probable histórico de **TIIE** (tasa de referencia MXN) → insumo de
  tasas/devengo. `fns_commission_task` → comisiones. `account_balance_tracking` /
  `view_investment_balance_history` → historia de saldos (útil para reconstrucción).
- **`tmp_linaje_*` y `tmp_migracion_linaje`** = tablas temporales de **linaje de migración** →
  directamente el tema calculado-vs-ingestado (K-MIG-002). Revisar qué marcan.
- **Tablas de prueba en producción** (`test`, `z_test`, `ztest`, owner `postgres`) → higiene del ambiente.

### DDL de tablas del esquema `public` (`\d+`, 2026-08-16) — OJO: NO es el esquema que usa F-012
- **`transaction_detail`** (PK `transaction_detail_id` varchar): `credit_amount`, `debit_amount`,
  `fee_amount`, `bonus_amount` (numeric(38,2)); **`source_prior_balance`, `source_after_balance`,
  `target_prior_balance`, `target_after_balance`**; `source_address`, `target_address`;
  `transaction_type`. **NO tiene columna de fecha/`created` ni `account_id`.**
- **`account`** (PK `account_id` varchar): **sólo 4 columnas** — `balance_amount`, `branch_id`,
  `object_type`. **No** tiene `account_number`, `accountholder_id`, `average_balance_amount`,
  `account_type` ni fechas.
- **`iv_payment_plan`** (PK `plan_id`): `account_id`, `account_number`, `account_type`, `due_date`,
  `interest_amount`, `interest_paid` (bool), `is_full`/`parcial` (bool), `payment_number`,
  `payment_date`, `id` (bigint), **`investment_id` → FK a `investment(id)`**.
- **`accountholder` = 1,072,056 filas** (la tabla de cliente viva; `aurumcore.account_holder` NO
  existe → el duplicado del `\d` es artefacto de esquema `public`).
- Todos los montos son **`numeric(38,2)`** → Aurum **almacena a 2 decimales**; la precisión 20/5 de
  K-DEV-001 es de cálculo intermedio, no de storage.

- **`public.account_balance_tracking`** (PK `account_id`+`registration_date`): `transactions_number`,
  `transactions_amount`, `initial_balance`, `final_balance`, **`accumulated_balance_total`**,
  `days_number_partial_accumulation`, `accumulated_balance_partial` (numeric(19,2)). → **base del saldo
  promedio / devengo** (Aurum sí acumula saldo por cuenta-día; OpenFin lo reconstruye).
- **`public.investment`** usa **`double precision` (float)** en `interest_amount` e `iv_initial_amount`
  → **bandera de precisión** (float en dinero); verificar en la tabla vigente (`aurumcore.*`).
- **`public.fns_history_tiiemxn`**: `value` (varchar), `creation_date` → histórico **TIIE** (tasa referencia).

### CORRECCIÓN de la v3 (retracto la "bandera crítica")
**Antes (v3, incorrecto):** dije que los queries de F-012 no coinciden con el esquema y "fueron
escritos contra otro ambiente". **Después (v4):** `\dn` muestra **dos esquemas** — `aurumcore` (el core
real, 100+ tablas transaccionales) y `public` (subconjunto reducido/derivado). El `\d`/`\d+` sin
calificar resuelve a `public` por el search_path, por eso vi tablas mínimas. **F-012 lee `aurumcore.*`,
que SÍ es el esquema rico → los queries NO están mal.** El error fue mío por leer `public`.
> Lo real que queda: hay **tablas con el mismo nombre en ambos esquemas y estructura distinta**
> (`public.account` 4 cols vs `aurumcore.account` rica; `public.transaction_detail` sin fecha vs
> `aurumcore.transaction_detail` con `created`). **Siempre calificar `aurumcore.`** y confirmar con
> Finsus qué es el esquema `public` (reporte/derivado/leftovers) — es un hallazgo a validar (ver mensaje).

### Modelo transaccional real (esquema `aurumcore`, inferido de índices + F-012)
`aurumcore.transaction` = **cabecera** (índices sobre `created`, `payer/payee_account_id`,
`accountholder_payer/payee_id`, `channel`, `state`, `external_id`, `parent_transaction_id`,
`idempotency_key`) → 1:N `aurumcore.transaction_detail` (con `created`, `transaction_type`,
`commission_type`, montos y saldos prior/after). Variantes: `transaction_investment`,
`transaction_credit`(+detail), `stp_transactions` (SPEI, `tracking_key`), `pld_transaction_detail` (PLD).
- **`external_id`** = llave cross-sistema (= `id_external` de OpenFin, K-DAT-003).
- **`parent_transaction_id`** = enlaza reversos / transacciones hijas.
- Catálogos: **`tbl_transactiontype`** (tipos); **`cat_accounting_transaction` / `cat_finsus_transaction`**
  (mapeo a cuenta contable → **la matriz CTB** que faltaba). Vistas regulatorias:
  **`successful_transactions_cnbv_report`**, `transaction_gross_amounts_per_account`.
**CONFIRMADO (`\d+ aurumcore.*`, con descripción de columnas del propio core):**
- **`aurumcore.transaction`** (PK `transaction_id` varchar(36)): `created`, `last_updated`,
  `external_id`(40), `type` (PAYMENT/REFUND/CHARGEBACK), `state` (AUTHORIZATION_PENDING…CONFIRMED/
  CANCELLED), `channel`, `gross_amount` numeric(19,2), `payer_id`/`payee_id` (accountholder),
  `payer_account_id`/`payee_account_id`, `message_id`, **`parent_transaction_id`** (doc: "used when
  the transaction is tax or commission" → **enlaza la comisión/impuesto con su transacción padre**),
  **`origin` (FINSUS | AURUMCORE)**, `processed`, `loan_adjustment_reason` ("CNBV Report 452").
- **`aurumcore.transaction_detail`** (~70 cols; FK `transaction_id`): `transaction_type`,
  `transaction_channel`, `source/target_address`, `credit/debit/fee/bonus_amount` numeric(19,2),
  `source/target_prior/after_balance`, `created`, **`total_in/out_daily/monthly_account_balance`**
  (base de saldo promedio), **`accounting_account`, `source_accounting_account`,
  `target_accounting_account`** (cuenta contable), `transaction_number` (id por par de cuentas
  contables), `commission_type`, `oct_transaction` (One Click), geoloc/card/POS, `deposit_payer_*`.
  Nota: columnas `commission`/`tax` existen pero doc dice "not used on Aurumcore" (usan filas
  separadas + `parent_transaction_id`).
- **`tbl_transactiontype`**: `transactiontype` (1 carácter) → `dcs` (descripción). Catálogo de tipos.
- **`cat_accounting_transaction`** = **matriz de amarre CTB** → ver [[K-CTB-001]].
- **Precisión:** el core usa **`numeric(19,2)`** (no float; el float de `public.investment` era del
  esquema derivado). Resuelve la bandera de precisión.
- `search_path = "$user", public` → lo no calificado cae en `public`. Navegar: `set search_path to aurumcore, public;`.
- **`aurumcore.investment` NO existe**: el modelo de inversión vive en `transaction_investment`(+detail)
  e `iv_payment_plan` (pendiente su `\d+`). `public.investment` es copia derivada.

**Dos hallazgos de alto valor:**
1. **`transaction.origin` (FINSUS/AURUMCORE)** podría ser el marcador **ingestado-vs-calculado**
   (el riesgo metodológico de K-MIG-002). Si distingue de forma confiable el dato migrado del
   generado por Aurum, es la columna más útil del modelo. → **verificar semántica con Finsus (P-013)**.
2. **`parent_transaction_id`** le da a Aurum la relación comisión/impuesto ↔ transacción que **OpenFin
   no tiene** (K-MOV-005). El comparador debe normalizar los movimientos sueltos de OpenFin contra
   la jerarquía padre-hijo de Aurum.

### Hallazgos estructurales (vs OpenFin)
- Aurum **guarda saldo anterior y posterior** por lado (source/target) → **no requiere reconstrucción**
  del saldo anterior, a diferencia de OpenFin (K-MOV-006).
- Aurum **empaqueta `fee_amount`/`bonus_amount` en la misma fila** de la transacción; OpenFin los
  parte en movimientos separados (refuerza K-MOV-001).
- **Fecha/vínculo de transacción — RESUELTO:** vive en `aurumcore.transaction` (header, con `created`,
  `payer/payee_account_id`, `accountholder_payer/payee_id`), no en `public.transaction_detail`. La
  correlación cross-core es por `external_id`.

### Cómo cerrar el resto de P-011 (calificando el esquema)
`\d+ aurumcore.transaction`, `\d+ aurumcore.transaction_detail`, `\d+ aurumcore.account`,
`\d+ aurumcore.investment`, `\d+ aurumcore.tbl_transactiontype`, `\d+ aurumcore.cat_accounting_transaction`;
`show search_path`. Y confirmar con Finsus el rol del esquema `public` (ver mensaje).

## Mapeo con OpenFin (llaves de correlación)
| concepto | OpenFin (K-DAT-003) | AurumCore |
|----------|---------------------|-----------|
| cliente | id_sucursal·id_role·id_asociado | `accountholder_number` |
| cuenta | id_suc_aux·id_producto·id_auxiliar | `account_number` (producto = split_part `-2`) |
| producto | id_producto (2000s/2300s/5004) | 2º segmento de `account_number` / `product_number` |
| tasa | tasa en acreedores | `account_yield.interest_rate` |
| capital inversión | — | `iv_initial_amount` (ya en K-DEV-003) |
| crédito | deudores 5004 | `lc_loan_contract` + `lc_products.product_number='5004'` |
| cross-tx | id_external (SPEI) | `transaction` / `id_openfin` en créditos |

## Diccionario completo y volumetría (F-014)
[CONFIRMADO] El diccionario de datos completo de `aurumcore` está extraído: **240 tablas / 3,529
columnas** (`aurum_columnas.csv`). `aurumcore.account` es la tabla rica (**106 columnas**), no la de
`public` (4). **P-011 queda cerrada a nivel modelo.**
- **Volumetría real (grande):** `transaction` 38 GB/31 M filas, `transaction_detail` 31 GB, `account`
  13 GB/8.2 M, `finsus_account_history` 28 GB/77.7 M, `authorization` 29 GB, `iv_payment_plan` 16 GB,
  `daily_account_balances` 2.7 GB/15.5 M, `account_balance_tracking` 2.9 GB, `accountholder` 1.07 M.
  La base es de **cientos de GB** → **la extracción debe ir por ventanas de fecha** (hay índices sobre
  `created`), nunca full-scan. Actualiza la estimación de volumetría del correo de accesos.
- **Tablas `finsus_*_history`** (`finsus_account_history` 77.7 M, `finsus_accountholder_history` 25 M,
  `finsus_sequences`) → probable **historia ingestada de OpenFin/Finsus** (ligado a `origin=FINSUS`,
  P-013, K-MIG-002). Revisar si son el marcador de lo migrado.
- Modelos por dominio (del diccionario): inversión en `investment`/`transaction_investment`(+detail)/
  `iv_*`; crédito en `lc_*`; contable en `cat_accounting_*`/`*_accounting_accounts`; PLD en `pld_*`;
  SPEI en `stp_transactions`; tiempos en `holidays_days`; tasas en `cat_reference_rate`/`fns_history_tiiemxn`;
  parámetros en `system_configuration` (donde viven los params de ISR de F-009 → verificar P-010).

## Puntos abiertos
- **Modelo: CERRADO** (diccionario F-014). Resta **confirmación de Finsus**: rol del esquema `public`
  (P-012) y **semántica de `origin`** (P-013).
- Redactar **nuestras** queries independientes por dominio contra el esquema real (Fase 1).

## Implicaciones para la validación
- Habilita construir el **comparador A↔B** por dominio con llaves reales.
- El oráculo (C) puede leer ambos lados desde la norma y arbitrar.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-16 | Creada desde F-012. | F-012 |
| 2 | 2026-08-16 | Acceso directo a la base: inventario real de tablas (`\d`) + banderas (duplicados, transaction_detail, TIIE, linaje). | acceso aurumcore |
| 3 | 2026-08-16 | DDL (`\d+`): transaction_detail (saldos prior/after), account minimal, iv_payment_plan→investment; accountholder 1.07M. **[Contenía un error: ver v4]** | acceso aurumcore |
| 4 | 2026-08-16 | **Corrección:** el `\d+` era del esquema `public`, no de `aurumcore`. F-012 SÍ es correcto (lee `aurumcore.*`). Documentado el modelo real (transaction header+detail, external_id, catálogos CTB, CNBV, TIIE, balance_tracking) y la bandera de dos esquemas a confirmar con Finsus. | acceso aurumcore |
| 5 | 2026-08-16 | DDL confirmado de `aurumcore.transaction` y `transaction_detail` (con descripción de columnas). Hallazgos: `origin` (FINSUS/AURUMCORE, posible marcador ingesta) y `parent_transaction_id` (comisión↔padre). CTB via cat_accounting_transaction → K-CTB-001. Precisión numeric(19,2). | acceso aurumcore |
| 6 | 2026-08-16 | Diccionario completo (F-014): 240 tablas/3,529 columnas; `aurumcore.account` 106 cols. Volumetría real (cientos de GB → extracción por ventanas). Tablas `finsus_*_history` (ingesta). P-011 cerrada a nivel modelo. | F-014 |
