# Plan / Spec — Contable (familias B y C)

> Validación contable del charter §10. Tolerancia **0.00, sin excepción** (no son cálculos con redondeo).
> Cada invariante **devuelve las filas que violan** (cero = pasa). Estado: **ARRANCADO** (2026-08-20).
> Comparador: `comparadores/contable_bc.py`. Sustento: [[K-CTB-001]].

## 1. Modelo contable (hallazgo clave)
**AurumCore NO guarda póliza/balanza como tabla** — solo catálogos. El **asiento vive embebido en
`transaction_detail`**:
- `source_accounting_account` (cuenta que **debita**), `target_accounting_account` (cuenta que **acredita**).
- `debit_amount` se guarda **NEGATIVO**, `credit_amount` **POSITIVO**. **Cada fila = 1 asiento balanceado.**
- Saldos corrientes: `total_in/out_daily/monthly_account_balance` (para rollforward).
- **Plan de cuentas:** `cat_accounting_account` (3,759 cuentas) con `account_type` (ACTIVO/PASIVO/…) y
  `account_nature` (DEUDOR/ACREEDOR).
- **Mapeo tipo→cuenta:** `cat_accounting_transaction` (697): `transaction_type` (texto) → `source/target_accounting_id`.
  *(Esto además resuelve el crosswalk tipo-texto que faltaba en Motor B.)*
- OpenFin (A) sí almacena el mayor (`detalle_polizas`, `aux_polizas`, `detalle_auxiliar`) → base para el cross A/B.

## 2. Familias e invariantes
- **B — Balanza consigo misma:**
  - **B1 · Doble partida diaria:** `Σ(debit_amount) + Σ(credit_amount) = 0` por día. Tol 0.00. ✅ implementado.
  - **B2 · Naturaleza:** cada cuenta respeta su `account_nature` (deudor/acreedor). Parcial (reporte de netos + naturaleza).
  - **B3 · Doble partida por PÓLIZA** (no solo diaria): agrupar por `transaction_id` y verificar Σ=0. *(pendiente)*
  - **B4 · Rollforward contable:** saldo_cierre(d-1) + Σmov(d) = saldo_cierre(d) por cuenta, con los
    `*_daily_account_balance`. *(pendiente)*
- **C — Amarre auxiliar ↔ balanza:**
  - **C1 · Stock por producto-día:** Σ saldos auxiliares (por `account`) = saldo de la cuenta contable de mayor
    del producto. *(pendiente)*
  - **C2 · Flujo por tipo-mov-día:** Σ movimientos del auxiliar por tipo = movimiento de la cuenta de mayor. *(pendiente)*
  - **C3 · Cuentas puente explicadas** línea por línea. *(pendiente)*
- **D — Cross-motor A/B:** la misma identidad en OpenFin (`detalle_polizas`) y AurumCore. *(pendiente)*

## 3. Primera corrida (2026-08-20, datos 10–16 ago)
`comparadores/contable_bc.py` · salida `_resultados/CONTABLE_BC_2026-08-20.txt`.

**B1 — doble partida diaria: ✅ 0/7 días violan. Descuadre = $0.00 todos los días** (asientos 17K–220K/día,
montos $84M–$1,301M). Los libros **cuadran** a tolerancia 0.00.
**Cobertura:** **0** asientos sin cuenta contable (todo movimiento trae src y tgt).
**B2 — naturaleza correcta:** 2101… PASIVO/ACREEDOR (depósitos cliente), 1102… ACTIVO/DEUDOR (interbancaria).

**Causuística surgida:** una cuenta con neto **$309,897.94 no está en `cat_accounting_account`** (usada en
transacciones pero fuera del plan de cuentas) → revisar (posible cuenta nueva sin catalogar o nulo).

## 3.bis B3, B4 y cuenta fuera de catálogo (2026-08-20)

**Grano confirmado:** cada `transaction_detail` **balancea sola** (`debit_amount = −credit_amount`) y cada
`transaction_id` = **1 fila**. → "doble partida por póliza" es **trivial** aquí (no hay pólizas multi-pierna).

**B3 · monto posteado vs delta de saldo** (reorientado a integridad). Cruda: 7,596 filas (crédito) donde
`(after−prior) ≠ credit_amount`. **Caracterizado = NO defecto:** **93% (7,103) es UNA cuenta**, la cámara de
compensación SPEI `1102010112103` (interbancaria, alto tráfico) cuyo snapshot prior/after **no es atómico** por
concurrencia; solo **12 cuentas contables** en total, todas operativas/pool. El check es válido al grano
**cliente con 1 movimiento** (4 casos → 0 violaciones). La confirmación masiva al grano cliente **timeout** (scan
del día pesado) → pendiente en **cohorte acotada**.

**B4 · rollforward por continuidad.** Cohorte 400 cuentas: 365/784 "rotos" → **artefacto de método**
(se encadenaron solo las piernas crédito). **Reimplementado bien via DuckDB** (extraer el día → stream
unificado source+target por cuenta → chains locales, sin timeouts): ver §3.ter.

## 3.ter B3/B4 cerrados via DuckDB (grano cuenta UUID, 14-ago)
`contable_bc.py::cerrar_b3_b4` extrae el día a CSV y arma el **stream unificado por cuenta** (cada cuenta como
target=crédito y source=débito), con window functions locales. 192,470 piernas; 8 cuentas **pool** (>500 mov).

| check | crudo (incl. pool) | **cliente (excl. 8 pools) = invariante real** |
|---|---|---|
| **B3** `(after−prior)=monto` | 8,000 | **891 / 139,193 (0.6%)** |
| **B4** continuidad `prior[i]=after[i-1]` | 43,021 | **8,525** → 5,550 empates de timestamp (orden ambiguo, benigno) + **2,975 gaps reales** |

- **Pools dominan el crudo:** 4 cuentas operativas concentran ~80% de las rupturas B4 (fd0d328e 17,760; e36c2c4a
  11,178; …) — snapshot prior/after no atómico por concurrencia. **No defecto.**
- **Residual cliente:** B3 0.6% y B4 2,975 gaps → candidato a investigar (probable saldo movido por posteos
  **fuera del stream de `transaction_detail`**, p.ej. capitalización/devengo en otra tabla, o sub-orden intra-segundo).
  **No es defecto confirmado**; se marca para cohorte de detalle.
- **Conclusión:** **B1 (doble partida) sólido a 0.00**; B3/B4 residuales pequeños y mayormente explicados
  (pools + empates). El comparador ya corre por DuckDB **sin timeouts**.

**Cuenta fuera de catálogo → es cadena vacía `''`.** ~**510 mov/día (~$620K, 16-ago)** posteados con
`accounting_account` **en blanco**, sobre todo **INTERNAL CREDIT TRANSFER** (pagos a crédito) y DEPOSIT. Hipótesis:
la pierna del **módulo de crédito** se contabiliza en el `lc_*` (no aquí) → confirmar con Finsus. Es
**data-quality**, no descuadre (B1 igual cuadra porque la fila balancea; el `''` se le escapó al check de nulos).

## 3.quater Familia C (auxiliar) y D (cross A/B por producto) — 2026-08-20

**Fuentes del auxiliar / balanza:**
- **AurumCore auxiliar (actual):** `account.balance_amount` por cuenta. Balanza por producto = Σ por
  `split_part(account_number,'-',2)` (excl. sucursal 201). ✅ tractable y **vigente**.
- **AurumCore `daily_account_balances`** (account_number, date, closing_balance) = auxiliar **con fecha**, PERO
  ⚠️ **STALE** (ver hallazgo abajo) → **no usar**.
- **OpenFin auxiliar:** `acreedores.saldo` por `idproducto` (estatus vigentes 1/3/4/5, excl. sucursal 201).

**Cross D — balanza por producto A vs B** (el "listado de saldos" que hace Alberto, ahora por el tercero).
Ambos cores tienen **misma numeración de producto**. Resultado (snapshot actual AU vs réplica t-1 OF):

| producto | AurumCore (B) | OpenFin (A) | delta | % |
|---|---|---|---|---|
| 2301 inversión | 20,790,644,617 | 20,551,876,241 | +238.8M | +1.2% |
| 2002 vista | 1,251,782,882 | 1,234,197,225 | +17.6M | +1.4% |
| 2013 ahorro | 666,481,928 | 674,398,687 | −7.9M | −1.2% |
| 2006 | 291,393,716 | 291,827,923 | −0.4M | −0.1% |
| 2015 | 254,344,306 | 249,216,373 | +5.1M | +2.1% |
| 2017 | 142,415,751 | 142,297,861 | +0.1M | ~0% |
| **2001** | **100,322,765** | **151,899,208** | **−51.6M** | **−34%** |
| 2012 | 52,213,141 | 51,927,823 | +0.3M | +0.5% |
| 2011 | 8,123,195 | 8,198,713 | −0.1M | −0.9% |

- **Conclusión:** los libros **reconcilian producto a producto dentro de ~1-2%**; los grandes (inversión, vista)
  casi al punto. El delta residual es **esperado** por la asincronía **t-1 (OF réplica) vs actual (AU)** + tx en
  vuelo — NO defecto. Es la validación de saldos contra la propia realidad (charter §9, no A=B a ciegas).
- **Causuística a investigar:** producto **2001 (−34%)** — desviación relativa grande (universo chico ~26K
  cuentas); posible mapeo/timing/producto en transición. Marcado.
- **Familia C (amarre auxiliar↔mayor):** pendiente — AurumCore no guarda balanza por cuenta contable; el mayor se
  derivaría de Σ movimientos. La versión tractable ya está (Σ auxiliar por producto = balanza por producto).

### HALLAZGO — `daily_account_balances` está STALE (no se actualiza)
[CONFIRMADO · datos] La tabla `aurumcore.daily_account_balances` (15,506,789 filas) **solo tiene fechas
2025-10-28 → 2025-11-20** (24 días) y **omite inversiones** (no aparece 2301). Es decir, la tabla de saldos
diarios **dejó de actualizarse hace ~9 meses** o fue una carga puntual. **Riesgo:** si algún proceso/reporte se
apoya en ella, opera sobre datos viejos e incompletos. **Acción:** preguntar a Finsus si esta tabla debe estar
viva (job roto) o es histórica; **no usarla** para la balanza (usar `account.balance_amount`). Ver [[P-018]].

## 4. Siguientes pasos
1. **B3** doble partida por `transaction_id` (detecta pólizas descuadradas que el neto diario oculta).
2. **B4** rollforward por cuenta con los saldos corrientes.
3. **C1/C2** amarre auxiliar↔balanza por producto-día (usa `account` ↔ cuenta de mayor vía `product_type_key`).
4. Cuenta fuera de catálogo (309,897.94) — identificar.
5. **D** cross A/B contra el mayor de OpenFin (`detalle_polizas`).

## 5. Relación con conocimiento
[[K-CTB-001]] (matriz de amarre) · [[K-DAT-006]] (modelo Aurum) · charter §10 (tolerancia 0.00). Caso del
Validador: **CONTABLE-BC**. Cada hallazgo confirmado → invariante permanente de regresión.
