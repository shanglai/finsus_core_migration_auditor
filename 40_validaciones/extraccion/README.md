# Queries de extracción — Fase 1 (solo lectura)

Extractos **de solo lectura** de openfin (t‑1, base `openfin_aurum`) y AurumCore, a Parquet/DuckDB
local o BigQuery. **Columnas nombradas (nunca `select *`)** y **parametrizados por periodo y clientes.**

## Convención de parámetros
- **Periodo:** `:fecha_ini`, `:fecha_fin` (timestamps; ventana **`[fecha_ini, fecha_fin)`**).
- **Cohorte de clientes:** una **tabla temporal/staging `cohorte`** que el runner llena antes de
  extraer, con la lista de 250 clientes estratificados. Se une por la llave de cliente de cada core.
  - Aurum: `cohorte(accountholder_number text)`.
  - OpenFin: `cohorte_of(id_sucursal int, id_role int, id_asociado int)` (llave de 3 campos).
  - Alternativa sin temp table: sustituir el `join cohorte` por un `IN (:lista)` que inyecte el runner.

## Reglas
- **Anclar a un saldo de arranque conocido** (día cero) para el rollforward; extraer TODAS las
  transacciones del cohorte en la ventana, no un corte ciego.
- **Acotar SIEMPRE por fecha** (hay índices sobre `created`/`fecha`) — nunca full‑scan (la base es de
  cientos de GB).
- Ejecutar en horario no crítico; `EXPLAIN` + `LIMIT` antes de correr amplio.
- openfin t‑1 **no es fuente de verdad** para cifras finales (K-DAT-002): validar contra producción.

## Archivos
| archivo | core | qué extrae |
|---------|------|-----------|
| `aurum_inversiones.sql` | Aurum | inversiones (account+accountholder+tasa) del cohorte |
| `aurum_iv_payment_plan.sql` | Aurum | plan de rendimiento por periodo (multiperiodo) |
| `aurum_saldo_diario.sql` | Aurum | saldo diario/acumulado (base de saldo promedio) |
| `aurum_isr_config.sql` | Aurum | parámetros de ISR (`system_configuration`) — cierra P-010 |
| `openfin_inversiones.sql` | OpenFin | inversiones (acreedores, productos 2301/2302/2307/2308) |
| `openfin_movimientos.sql` | OpenFin | movimientos `detalle_auxiliar ⋈ _masdatos` del cohorte |

### Deep-dive ISR (Fase 1) — ver `../PLAN_FASE1_ISR.md`
| archivo | core | qué extrae |
|---------|------|-----------|
| `00_volumetria_isr.sql` | ambos | **medidas** (conteos, rangos, nulos) acotadas a cohorte+ventana, antes de extraer |
| `openfin_isr_diario.sql` | OpenFin | **ISR diario cliente-día** (`isr_diario`: saldo+isr) = motor A día por día |
| `aurum_cat_tax.sql` | Aurum | tasa ISR de catálogo (`cat_tax`, `account_tax`) — P-010 |
| `aurum_account_yield.sql` | Aurum | `interest_rate`, `days_in_year`, `isr_exempt` por cuenta del cohorte |
| `aurum_isr_al_pago_discovery.sql` | Aurum | **descubre** el `transaction_type` del ISR sobre cuentas semilla |
| `aurum_isr_al_pago.sql` | Aurum | ISR al pago (motor B) una vez fijado `:isr_txn_type` |
| `aurum_saldo_base_isr.sql` | Aurum | saldo diario (`account_balance_tracking`) = base del oráculo C |

**Runner y comparador** (`../comparadores/`): `fase1_isr_runner.py` (extractor **solo lectura, gated**;
`--dry-run` por defecto, `--confirm` para conectar) y `fase1_isr_comparador.py` (corre C con `Decimal`
y arma A/B/C + clasificación). El runner arma la cohorte como **CTE `VALUES`** (sin temp tables → seguro
en `read only`). Conexión por DSN en variables de entorno `OF_DSN`/`AC_DSN` (nunca hardcodear).
Requiere `psycopg2` solo al usar `--confirm`.

> Los nombres físicos de columnas de OpenFin se confirman con su diccionario
> (`openfin_columnas.csv`, ver `utils/README_extraccion_openfin.md`). Donde haya duda se marca `--[?]`.
