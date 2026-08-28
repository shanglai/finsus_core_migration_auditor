# Inventario de Datasets en DuckDB — todo el detalle disponible

> Cada dataset materializado en `40_validaciones/_resultados/` (consultable con DuckDB in-memory): esquema,
> filas, rangos de fecha, conteos de id y **timestamp de ejecución** (mtime = cuándo se corrió/escribió el
> resultado). Generado 2026-08-26.

> **Nota:** la fecha en el *nombre* del archivo suele ser la **fecha de los datos**; el **mtime** es **cuándo lo
> corrimos**. Pueden diferir (p.ej. un feed con datos del 08-20 extraído el 08-23).

## Parquet

### _isr_join_full.parquet
- **Ejecutado (mtime corrida):** 2026-08-17 22:22:02
- **Filas:** 18,599  ·  **Columnas:** 14  ·  **Tamaño:** 438 KB
- **Esquema:** `id_inversion_aurumcore`:VARCHAR, `id_inversion_openfin`:VARCHAR, `isr_ac`:DOUBLE, `isr_of`:DOUBLE, `id_cliente`:VARCHAR, `fecha_apertura`:VARCHAR, `fecha_cierre`:VARCHAR, `monto`:DOUBLE, `tasa`:DOUBLE, `rend`:DOUBLE, `f_ape`:DATE, `f_cie`:DATE, `dias`:BIGINT, `diff`:DOUBLE
- **Rangos de fecha (datos):** `fecha_apertura`: 01/02/2025 .. 27/07/2026 · `fecha_cierre`: 03/08/2026 .. 03/08/2026 · `f_ape`: 2024-08-01 .. 2026-07-27 · `f_cie`: 2026-08-03 .. 2026-08-03
- **Distintos (id):** `id_inversion_aurumcore`: 18,599 · `id_inversion_openfin`: 18,599 · `id_cliente`: 14,913

### f1_00_volumetria_ac_SEMILLA_s1.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 09:54:56
- **Filas:** 1  ·  **Columnas:** 5  ·  **Tamaño:** 2 KB
- **Esquema:** `filas`:BIGINT, `cuentas`:BIGINT, `titulares`:BIGINT, `fecha_min`:DATE, `fecha_max`:DATE
- **Rangos de fecha (datos):** `fecha_min`: 2025-10-16 .. 2025-10-16 · `fecha_max`: 2026-08-03 .. 2026-08-03
- **Distintos (id):** `cuentas`: 1 · `titulares`: 1

### f1_00_volumetria_ac_SEMILLA_s2.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 09:54:56
- **Filas:** 1  ·  **Columnas:** 3  ·  **Tamaño:** 1 KB
- **Esquema:** `esquemas_isr`:BIGINT, `isr_min`:DECIMAL(38,2), `isr_max`:DECIMAL(38,2)

### f1_00_volumetria_of_SEMILLA_s1.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 10:51:10
- **Filas:** 1  ·  **Columnas:** 2  ·  **Tamaño:** 1 KB
- **Esquema:** `tabla`:VARCHAR, `filas_estimadas`:BIGINT

### f1_00_volumetria_of_SEMILLA_s2.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 10:52:41
- **Filas:** 1  ·  **Columnas:** 2  ·  **Tamaño:** 1 KB
- **Esquema:** `fecha_min`:DATE, `fecha_max`:DATE
- **Rangos de fecha (datos):** `fecha_min`: 2025-09-03 .. 2025-09-03 · `fecha_max`: 2026-08-17 .. 2026-08-17

### f1_00_volumetria_of_SEMILLA_s3.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 10:52:41
- **Filas:** 1  ·  **Columnas:** 7  ·  **Tamaño:** 3 KB
- **Esquema:** `filas`:BIGINT, `clientes`:BIGINT, `fecha_min`:DATE, `fecha_max`:DATE, `isr_total`:DECIMAL(38,2), `dias_isr_cero`:BIGINT, `saldo_nulos`:BIGINT
- **Rangos de fecha (datos):** `fecha_min`: 2026-02-03 .. 2026-02-03 · `fecha_max`: 2026-08-03 .. 2026-08-03
- **Distintos (id):** `clientes`: 1

### f1_a_vs_c_diario_SEMILLA.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 10:56:32
- **Filas:** 728  ·  **Columnas:** 6  ·  **Tamaño:** 3 KB
- **Esquema:** `id_cliente`:VARCHAR, `fecha`:DATE, `saldo_base_of`:DECIMAL(38,2), `isr_dia_of`:DECIMAL(38,2), `C_dia`:DOUBLE, `dif_of_c`:DOUBLE
- **Rangos de fecha (datos):** `fecha`: 2026-02-03 .. 2026-08-03
- **Distintos (id):** `id_cliente`: 4

### f1_aurum_isr_al_pago_SEMILLA_s1.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 09:59:49
- **Filas:** 2  ·  **Columnas:** 7  ·  **Tamaño:** 4 KB
- **Esquema:** `accountholder_id`:VARCHAR, `account_cliente`:VARCHAR, `fecha_pago`:TIMESTAMP, `isr_retenido_ac`:DECIMAL(38,2), `cuenta_isr`:VARCHAR, `alfanumeric_reference`:VARCHAR, `transaction_id`:VARCHAR
- **Rangos de fecha (datos):** `fecha_pago`: 2026-08-03 00:43:13.183000 .. 2026-08-03 01:18:01.737000
- **Distintos (id):** `accountholder_id`: 2 · `account_cliente`: 2 · `cuenta_isr`: 1 · `transaction_id`: 2

### f1_aurum_isr_al_pago_discovery_SEMILLA_s1.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 09:56:32
- **Filas:** 17  ·  **Columnas:** 8  ·  **Tamaño:** 4 KB
- **Esquema:** `transaction_type`:VARCHAR, `transaction_channel`:VARCHAR, `txn_type`:VARCHAR, `origin`:VARCHAR, `n`:BIGINT, `debito_min`:DECIMAL(38,2), `debito_max`:DECIMAL(38,2), `debito_sum`:DECIMAL(38,2)
- **Distintos (id):** `transaction_type`: 6 · `transaction_channel`: 3

### f1_aurum_isr_al_pago_discovery_SEMILLA_s2.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 09:56:32
- **Filas:** 0  ·  **Columnas:** 7  ·  **Tamaño:** 1 KB
- **Esquema:** `account_number`:INTEGER, `created`:INTEGER, `transaction_type`:INTEGER, `transaction_channel`:INTEGER, `debit_amount`:INTEGER, `credit_amount`:INTEGER, `txn_type`:INTEGER
- **Distintos (id):** `account_number`: 0 · `transaction_type`: 0 · `transaction_channel`: 0

### f1_aurum_saldo_base_isr_SEMILLA_s1.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 09:59:50
- **Filas:** 65  ·  **Columnas:** 9  ·  **Tamaño:** 5 KB
- **Esquema:** `accountholder_id`:VARCHAR, `account_number`:VARCHAR, `producto`:VARCHAR, `fecha`:DATE, `initial_balance`:DECIMAL(38,2), `final_balance`:DECIMAL(38,2), `accumulated_balance_total`:DECIMAL(38,2), `accumulated_balance_partial`:DECIMAL(38,2), `days_number_partial_accumulation`:BIGINT
- **Rangos de fecha (datos):** `fecha`: 2025-10-16 .. 2026-08-03
- **Distintos (id):** `accountholder_id`: 4 · `account_number`: 16

### f1_desviacion_clasificada.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 17:37:15
- **Filas:** 3,236  ·  **Columnas:** 7  ·  **Tamaño:** 54 KB
- **Esquema:** `id_cliente`:VARCHAR, `isr_of_arbol`:DOUBLE, `isr_ac_arbol`:DOUBLE, `A_prov_bd`:DOUBLE, `OF_frac_regla`:DOUBLE, `B_pago_bd`:DOUBLE, `clase`:VARCHAR
- **Distintos (id):** `id_cliente`: 2,774

### f1_openfin_isr_diario_SEMILLA_s1.parquet
- **Ejecutado (mtime corrida):** 2026-08-18 10:53:37
- **Filas:** 728  ·  **Columnas:** 8  ·  **Tamaño:** 4 KB
- **Esquema:** `id_sucursal`:BIGINT, `id_role`:BIGINT, `id_asociado`:BIGINT, `id_cliente`:VARCHAR, `kasociado`:BIGINT, `fecha`:DATE, `saldo_base_of`:DECIMAL(38,2), `isr_dia_of`:DECIMAL(38,2)
- **Rangos de fecha (datos):** `fecha`: 2026-02-03 .. 2026-08-03
- **Distintos (id):** `id_sucursal`: 2 · `id_asociado`: 4 · `id_cliente`: 4 · `kasociado`: 4

## Feeds CSV

### _td_2026-08-14.csv
- **Ejecutado (mtime corrida):** 2026-08-20 16:20:52
- **Filas:** 96,235  ·  **Columnas:** 10  ·  **Tamaño:** 17465 KB
- **Esquema:** `transaction_detail_id`:VARCHAR, `created`:TIMESTAMP, `source_address`:VARCHAR, `target_address`:VARCHAR, `source_prior_balance`:DOUBLE, `source_after_balance`:DOUBLE, `target_prior_balance`:DOUBLE, `target_after_balance`:DOUBLE, `debit_amount`:DOUBLE, `credit_amount`:DOUBLE
- **Rangos de fecha (datos):** `created`: 2026-08-14 00:00:27.298000 .. 2026-08-14 23:59:58.940000
- **Distintos (id):** `transaction_detail_id`: 96,235

### average_balance_sweep_core-rendimientos.csv
- **Ejecutado (mtime corrida):** 2026-08-23 17:26:46
- **Filas:** 90  ·  **Columnas:** 5  ·  **Tamaño:** 8 KB
- **Esquema:** `fecha`:DATE, `timestamp`:TIME, `account_uuid`:VARCHAR, `avg_balance`:DOUBLE, `source_file`:VARCHAR
- **Rangos de fecha (datos):** `fecha`: 2026-08-06 .. 2026-08-23
- **Distintos (id):** `account_uuid`: 27

### credito_dias_log_2026-08-23.csv
- **Ejecutado (mtime corrida):** 2026-08-23 13:57:19
- **Filas:** 3  ·  **Columnas:** 3  ·  **Tamaño:** 0 KB
- **Esquema:** `contract_id`:VARCHAR, `dias_ord`:BIGINT, `dias_mora`:VARCHAR
- **Distintos (id):** `contract_id`: 3

### credito_provision_feed_2026-08-20.csv
- **Ejecutado (mtime corrida):** 2026-08-23 14:06:24
- **Filas:** 5,365  ·  **Columnas:** 7  ·  **Tamaño:** 648 KB
- **Esquema:** `fecha`:TIMESTAMP, `col4`:BIGINT, `monto_precision`:DOUBLE, `contract_id`:VARCHAR, `col7`:DOUBLE, `tipo`:VARCHAR, `tx_id`:BIGINT
- **Rangos de fecha (datos):** `fecha`: 2026-08-20 00:59:59 .. 2026-08-20 01:35:12
- **Distintos (id):** `contract_id`: 4,945 · `tx_id`: 4,945

### cuentahab_altas_incompletas.csv
- **Ejecutado (mtime corrida):** 2026-08-20 13:58:25
- **Filas:** 295  ·  **Columnas:** 4  ·  **Tamaño:** 8 KB
- **Esquema:** `phone`:VARCHAR, `r_confirmed`:BOOLEAN, `r_accounts`:BOOLEAN, `r_investments`:BOOLEAN
- **Distintos (id):** `phone`: 295 · `r_accounts`: 2

### cuentahab_aurum_no_en_wso2.csv
- **Ejecutado (mtime corrida):** 2026-08-20 13:58:25
- **Filas:** 20  ·  **Columnas:** 3  ·  **Tamaño:** 1 KB
- **Esquema:** `accountholder_id`:VARCHAR, `accountholder_number`:VARCHAR, `tel`:VARCHAR
- **Distintos (id):** `accountholder_id`: 20 · `accountholder_number`: 20 · `tel`: 20

### cuentahab_tel_duplicado_aurum.csv
- **Ejecutado (mtime corrida):** 2026-08-20 13:58:26
- **Filas:** 1  ·  **Columnas:** 2  ·  **Tamaño:** 0 KB
- **Esquema:** `tel`:BIGINT, `n`:BIGINT
- **Distintos (id):** `tel`: 1

### cuentahab_wso2_no_en_aurum.csv
- **Ejecutado (mtime corrida):** 2026-08-20 13:58:24
- **Filas:** 181,850  ·  **Columnas:** 1  ·  **Tamaño:** 1953 KB
- **Esquema:** `phone`:VARCHAR
- **Distintos (id):** `phone`: 181,850

### saldo_promedio_feed_2026-08-18.csv
- **Ejecutado (mtime corrida):** 2026-08-23 14:09:10
- **Filas:** 2  ·  **Columnas:** 2  ·  **Tamaño:** 0 KB
- **Esquema:** `account_uuid`:VARCHAR, `avg_balance`:DOUBLE
- **Distintos (id):** `account_uuid`: 2

### saldo_promedio_log_core-rendimientos_2026-08-23.csv
- **Ejecutado (mtime corrida):** 2026-08-23 14:01:54
- **Filas:** 0  ·  **Columnas:** 2  ·  **Tamaño:** 0 KB
- **Esquema:** `account_uuid`:VARCHAR, `avg_balance`:VARCHAR
- **Distintos (id):** `account_uuid`: 0

### yield_feed_2026-08-18.csv
- **Ejecutado (mtime corrida):** 2026-08-23 14:04:58
- **Filas:** 30,769  ·  **Columnas:** 7  ·  **Tamaño:** 3995 KB
- **Esquema:** `fecha`:TIMESTAMP, `tx_id`:BIGINT, `uuid_origen`:VARCHAR, `uuid_destino`:VARCHAR, `monto`:DOUBLE, `producto`:BIGINT, `cliente`:BIGINT
- **Rangos de fecha (datos):** `fecha`: 2026-08-18 00:20:50 .. 2026-08-18 00:57:36
- **Distintos (id):** `tx_id`: 20,162 · `uuid_origen`: 30,769 · `uuid_destino`: 20,162 · `cliente`: 30,769
