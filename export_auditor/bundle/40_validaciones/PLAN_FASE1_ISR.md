# Plan Fase 1 — Deep-dive ISR (extracción desde las bases)

Objetivo: reconstruir el **ISR día-por-día real de OpenFin** (tabla `isr_diario`), traer el **ISR al
pago de AurumCore**, correr el **oráculo C** sobre los saldos, y **clasificar** cada discrepancia
(sincronía / modelo / redondeo / DEFECTO). Cierra el "paso a paso" que quedó pendiente en el Excel
`ISR_paso_a_paso_A_B_C.xlsx` y alimenta P-010 y el ledger de hallazgos.

> Regla dura del proyecto: **solo lectura, acotado por cohorte + fechas, y doble validación humana
> antes de tocar la BD**. El runner corre en `--dry-run` por defecto; requiere `--confirm` explícito.
> Bases: `openfin_aurum` (t-1, esquema `public`) y AurumCore (esquema `aurumcore`). t-1 **no** es
> fuente de verdad para cifras finales (K-DAT-002).

---

## 0. Columnas reales confirmadas (diccionarios F-014/F-015 — nada inventado)

**OpenFin (`public`)**
- `isr_diario(fecha date, kasociado int, saldo numeric(14,2), isr numeric(14,2), auxiliares array, data array)` — **ISR diario a nivel cliente-día**. `saldo` = base que usó OpenFin ese día.
- `isr_diario_aux_log(fecha, kauxiliar bigint, fecha_real timestamp, data array, isr_diario numeric)` — ISR diario a nivel **cuenta** (42 GB; solo si se necesita el detalle por cuenta).
- `asociados(idsucursal, idrol, idasociado, kasociado int, ...)` — mapea `kasociado` ↔ cliente `100-10-X`.
- `acreedores(idsucaux, idproducto, idauxiliar, kauxiliar int, saldo, tasa, montocontrato, ...)` — cuenta ↔ `kauxiliar`.
- `calculo_intereses_acreedores(cb_retencion, top_isr, ...)` — retención al momento del cálculo (cruce).

**AurumCore (`aurumcore`)**
- `cat_tax(id, scheme_id, isr real, iva real, status, ...)` — **tasa ISR de catálogo** (P-010).
- `account_tax(id, name, tax_scheme_id, isr numeric, isr_concept, base_period_type, ...)` — esquema fiscal por cuenta.
- `account_yield(interest_rate, days_in_year, isr_exempt bool, ...)` — **bandera de exención** y base de días.
- `system_configuration(name, value, category, ...)` — parámetros (UMA, multiplicador) [por confirmar nombres].
- `account_balance_tracking(account_id, registration_date, final_balance, accumulated_balance_total, accumulated_balance_partial, ...)` — **saldo diario** por cuenta (base de saldo promedio para C).
- ISR al pago: **no hay columna `isr` en `transaction_detail`** → se asienta como **transacción** de tipo ISR (`debit_amount`). El `transaction_type` exacto se **descubre** (paso D1), no se inventa.

---

## 1. Actividades

| # | Actividad | Fuente | Produce |
|---|-----------|--------|---------|
| A1 | **Volumetría / perfilado** (medidas antes de extraer) | isr_diario, cat_tax, account_balance_tracking | conteos, rangos de fecha, nulos, estimación de filas |
| A2 | **Cerrar P-010** (parámetros de la regla) | cat_tax, account_tax, account_yield, system_configuration | tasa ISR, exención, días, bandera exención |
| A3 | **Descubrir asiento de ISR al pago en Aurum** | transaction_detail ⋈ transaction (cuentas semilla) | `transaction_type` del ISR |
| A4 | **Extraer ISR diario OpenFin** (A) | isr_diario ⋈ asociados | ledger día-por-día por cliente (saldo, isr) |
| A5 | **Extraer ISR al pago Aurum** (B) | transaction_detail (tipo ISR) | ISR retenido por cuenta/fecha de pago |
| A6 | **Extraer saldos base** (para C) | account_balance_tracking (Aurum) + isr_diario.saldo (OF) | saldo total cliente-día |
| A7 | **Correr C** (oráculo) sobre A6 | motor C + P-010 | ISR diario/acumulado independiente |
| A8 | **Comparar A/B/C** normalizado + dos momentos | todo lo anterior | tabla de discrepancias clasificadas |
| A9 | **Cargar hallazgos** (257 tipo-C, etc.) | A8 | fichas en `50_hallazgos/` |

---

## 2. Rangos (acotamiento) y medidas

**Cohortes (las define el runner desde `_isr_join_full.parquet`, sin tocar la BD):**
- `SEMILLA` (≈4–5 clientes, **vida completa**): casos ya validados offline — 1 "oro" (OF<AC), 2 "expuesto" (OF≫AC, AC>0) y 2 "exento" (OF≫AC, AC=0). **Los ids reales NO van en el repo**: el runner los deriva del parquet gitignored o de `_resultados/cohorte_semilla.txt` (también gitignored). Valida el pipeline sobre casos conocidos antes de escalar.
- `TIPO_C` (muestra 25 de 257) y `TIPO_B` (muestra 25) — **último ciclo**.
- `COHORTE_250` (estratificada) — Fase 1 amplia, **último ciclo**.

**Ventanas de fecha:**
- Semilla (vida completa): `[:fecha_ini='2025-08-01', :fecha_fin='2026-08-04')`.
- Cohorte / muestras (último ciclo): `[:fecha_ini='2026-07-01', :fecha_fin='2026-08-04')`.

**Medidas (siempre antes del extracto masivo):**
- Estimación barata de filas totales de `isr_diario` vía `pg_class.reltuples` (no full-scan).
- `MIN/MAX(fecha)` y, **acotado a cohorte+ventana**, `COUNT(*)`, `COUNT(DISTINCT kasociado)`, `SUM(isr)`, `SUM(saldo)`.
- `EXPLAIN` obligatorio antes de cualquier extracto amplio; `LIMIT` en las pruebas.
- `statement_timeout` y `default_transaction_read_only = on` en cada sesión.

---

## 3. Pasos (cada uno gated por doble validación)

1. **P0 — Preparación local (sin BD):** el runner construye las cohortes desde el parquet y genera las listas de llaves (Aurum `accountholder_number`; OpenFin `idsucursal,idrol,idasociado`). `--dry-run` imprime las cuentas y las ventanas. **Revisar y aprobar.**
2. **P1 — Volumetría (A1):** correr `00_volumetria_isr.sql`. Confirmar rangos de fecha y que los conteos acotados son razonables (no millones). **Medida, no extracto.**
3. **P2 — Config / P-010 (A2):** `aurum_cat_tax.sql`, `aurum_isr_config.sql`, `aurum_account_yield.sql`. Fijar tasa/exención/días reales. Actualizar `S-FIS-001` y cerrar/menguar P-010.
4. **P3 — Descubrir ISR Aurum (A3):** `aurum_isr_al_pago_discovery.sql` sobre las 5 cuentas semilla; identificar el `transaction_type` cuyo `debit_amount` = 46.37/… Fijar `:isr_txn_type`.
5. **P4 — Semilla vida-completa (A4/A5/A6):** extraer isr_diario + ISR al pago + saldos de las 5 semillas. **Reproducir el Excel con datos reales** (validación del pipeline).
6. **P5 — Correr C y comparar (A7/A8):** comparador A/B/C + dos momentos sobre la semilla. Cuadre esperado: C≈B; A explica su curva.
7. **P6 — Escalar a muestras y cohorte (A4–A8):** TIPO_C, TIPO_B, luego COHORTE_250, en **último ciclo**.
8. **P7 — Hallazgos (A9):** cargar los 257 tipo-C y demás como fichas `H-###`.

---

## 4. Código generado

En `40_validaciones/extraccion/` (SQL, solo lectura, columnas nombradas, parametrizado):
- `00_volumetria_isr.sql` — medidas (A1).
- `aurum_cat_tax.sql`, `aurum_account_yield.sql` — config ISR (A2).
- `aurum_isr_al_pago_discovery.sql` — descubrir tipo de asiento (A3).
- `openfin_isr_diario.sql` — ISR diario OpenFin (A4).
- `aurum_isr_al_pago.sql` — ISR al pago Aurum (A5).
- `aurum_saldo_base_isr.sql` — saldo diario para C (A6).

En `40_validaciones/comparadores/`:
- `fase1_isr_runner.py` — extractor **read-only, gated** (`--dry-run` por defecto), escribe Parquet a `_resultados/`.
- `fase1_isr_comparador.py` — corre C (Decimal) y arma A/B/C + clasificación.

---

## 5. Bullets de aviso a Finsus (antes de ejecutar)

- Bases: **openfin_aurum (réplica t-1)** y **AurumCore** — no producción para cifras finales.
- Acceso **solo lectura** (`default_transaction_read_only=on`); **sin DDL, sin writes**.
- Acotado a **≤ 5 cuentas semilla** en la primera corrida; ventana de fechas explícita; **sin `SELECT *`**.
- `EXPLAIN` + `LIMIT` antes de cualquier extracto amplio; `statement_timeout` fijado.
- Tablas grandes que se tocan (acotadas): `isr_diario` (~170M, por índice fecha+kasociado), `transaction_detail`, `account_balance_tracking`.
- Objetivo: reconstruir el acumulado diario de ISR de 5 casos y compararlo contra el oráculo.
