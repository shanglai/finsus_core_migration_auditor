# Solicitudes y preguntas para Finsus — validación de migración openfin → AurumCore

> Tercero independiente. Consolidado al 2026-08-20. Cada ítem: **Contexto · Pendiente · Lo que buscamos**.
> Prioridad: 🔴 bloquea validación · 🟠 mejora/aclara · 🟢 confirmación.

---

## A. Accesos y credenciales

### A.1 — Base de migración OpenFin `openfin_migracion` / esquema `openfin_m` (SOL-001) 🔴
- **Contexto.** Los queries del diario de Finsus (Sergio) corren *desde AurumCore* y jalan OpenFin por `dblink`
  contra `openfin_migracion` (host 10.10.164.25), usando vistas pre-armadas `openfin_m.aurum_transaction_final_complete`,
  `aurum_transaction_credit_complete_live`, `lc_loan_contract_live`. Nosotros solo alcanzamos `openfin_aurum/public`.
- **Pendiente.** Acceso de **solo lectura** a `openfin_migracion` (esquema `openfin_m`).
- **Lo que buscamos.** Hacer el cruce transaccional **a nivel de operación** (hoy `vista_movimientos` no permite
  emparejar cargo↔abono de forma fiable) y **benchmarkear** su mapeo contra nuestra reconstrucción independiente.

### A.2 — Réplica de OpenFin (no el T-1) (SOL-002) 🟠
- **Contexto.** Hoy leemos el **T-1**, que se "plancha" al regenerarse y puede perder permisos. Jorge recomendó
  apuntar a la **réplica** (casi tiempo real, dedicada a Aurum + nosotros).
- **Pendiente.** Acceso de solo lectura a la **réplica**.
- **Lo que buscamos.** Correr el validador diario sobre datos frescos y estables, sin el riesgo del planchado.

---

## B. Logs del CORE

### B.1 — Trazas del CORE de AurumCore (SOL-003) 🔴
- **Contexto.** El doc de "Saldo Promedio" indica que el valor exacto **se valida en los logs del CORE**. La tabla
  `account_balance_tracking` arranca ~ago-2025 y no cubre la vida completa de cuentas más viejas.
- **Pendiente.** El `trace.log` (comprimido o acceso de lectura) con las trazas **`Calculating with average balance`**
  (saldo promedio) y **`Calculating yield amount Using RATE…, DaysOfYear[360|365]`** (rendimiento), para una lista
  de cuentas + fechas que les pasamos. Igual que nos compartieron los de OpenFin.
- **Lo que buscamos.** Validar **al centavo** el **saldo promedio (2.1.3)** y el **rendimiento vista (2.1.1)**;
  hoy es el bloqueo principal de ese motor.

---

## C. Semántica y trazabilidad de los datos

### C.1 — Taxonomía y delimitador de `transaction.origin` (SOL-004) 🔴
- **Contexto.** `origin` es clave para comparar **solo lo que AurumCore calculó** (no lo ingestado de OpenFin).
  Descubrimos que su semántica es **mixta**: unos valores parecen **fuente de migración**
  (`FINSUS_INVESTMENT`, `FINSUS_2`, `FINSUS_INVESTMENT_ACCRUED`, `841`, `FINSUS_YIELD…`), otros parecen
  **canal/producto vivo** (`DIMO` 100% post-cutover; `FINSUS_CREDIT`/`FINSUS_2` con fecha post-cutover). Además
  `origin IS NULL` aparece **desde abril-2026** (antes del cutover).
- **Pendiente.** El **catálogo de valores de `origin`** con su significado, y **cuál es el delimitador oficial**
  de "generado por AurumCore" vs "ingestado".
- **Lo que buscamos.** Fijar el filtro correcto de "Aurum vivo" (hoy usamos `created >= cutover`) para que las
  validaciones de cálculo prueben el **motor vivo**, no la data migrada. Es el punto metodológico #1.

### C.2 — Fecha exacta del cutover y backfills/re-ingestas (SOL-005) 🟠
- **Contexto.** Inferimos cutover el 2-3 ago, pero hay transacciones con `origin` **con nombre fechadas en agosto**
  (post-cutover) y `null` desde abril (periodo shadow/paralelo).
- **Pendiente.** Fecha/hora exacta del cutover a primario; y si hubo **backfills o re-ingestas** después del cutover.
- **Lo que buscamos.** Delimitar sin ambigüedad qué es shadow, qué es migrado y qué es vivo.

### C.3 — Tabla `daily_account_balances` desactualizada (SOL-006) 🟠
- **Contexto.** `aurumcore.daily_account_balances` (15.5M filas) solo tiene fechas **2025-10-28 → 2025-11-20** y
  **omite inversiones**. Parece un **job de saldos diarios detenido** o una carga puntual.
- **Pendiente.** Confirmar si debe estar viva (job roto) o es histórica, y **qué proceso/reporte la consume**.
- **Lo que buscamos.** Descartar que algún reporte opere sobre datos viejos/incompletos. (Nosotros usamos
  `account.balance_amount`, que sí está vigente.)

### C.4 — Ciclo de vida de la identidad en WSO2 (SOL-007) 🟠
- **Contexto.** Conciliación identidad↔padrón: **Aurum→WSO2 completo** (solo 20 clientes sin identidad), pero
  **181,844 identidades WSO2 con roles completos SIN accountholder** en Aurum. `accountholder` es 100% ACTIVE (no
  retiene cerradas). Hipótesis: **churn** (WSO2 conserva la identidad tras el cierre).
- **Pendiente.** ¿La identidad WSO2 **persiste tras cerrar la cuenta**? ¿Existe padrón de cuentas cerradas?
- **Lo que buscamos.** Cerrar P-017 y descartar que sea un defecto de migración (vs asimetría de retención esperada).

---

## D. Reglas y definiciones de producto

### D.1 — Regla de cálculo del crédito (SOL-008) 🔴
- **Contexto.** Falta la regla de **interés ordinario/moratorio** y el **devengamiento del One Click**; sin ella no
  podemos escribir el oráculo del motor de crédito (existencia sí valida al 100%, cálculo no).
- **Pendiente.** Contrato/documento de producto de crédito: base de días, tasas/tramos, momento de devengo,
  penalizaciones, prelación de pagos.
- **Lo que buscamos.** Habilitar la validación del motor de crédito (interés, devengo, One Click).

### D.2 — Pólizas de write-off (quitas/condonaciones/castigos/reestructuras) (SOL-009) 🟠
- **Contexto.** AurumCore responde (F-023) que estos eventos **generan póliza individual** enviada al ERP. En
  `transaction_detail` vemos `Condonación`/`Descuento` posteados, pero **no** una tabla/`charge_type` formal de
  quita/castigo/reestructura.
- **Pendiente.** La **tabla o el ejemplo** de la póliza formal de write-off (dónde se registra el evento contable).
- **Lo que buscamos.** Validar en datos que el motor de write-offs opera como documenta el proveedor.

### D.3 — Variable de cobertura Prosofipo en System Configuration (SOL-010) 🟠
- **Contexto.** AurumCore dice (F-023) que el **monto/porcentaje cubierto** del Fondo de Protección se calcula al
  generar el **841**, con el monto configurado en **System Configuration**. Nuestra búsqueda amplia en
  `system_configuration` (cobertura/UDIS/25000/prosofipo/fondo/841) dio **0 resultados**.
- **Pendiente.** El **nombre exacto** de esa variable (o dónde vive), si en efecto existe.
- **Lo que buscamos.** Cerrar el matiz de Gap C: distinguir la **cobertura-841** (sí existe) de la **cuota mensual**
  (falta, se hace por fuera).

### D.4 — Tratamiento de personas morales en ISR (SOL-011) 🟠
- **Contexto.** LISR Art. 54 **excluye** de retención a personas morales; el doc de AurumCore pone **exención $0**
  (retención completa) para ellas.
- **Pendiente.** Confirmar el criterio: ¿se retiene o no a personas morales?
- **Lo que buscamos.** Cerrar el residuo del ISR (impacto bajo: la SOFIPO es casi toda personas físicas).

---

## E. Confirmaciones y decisiones

### E.1 — Parámetros go-forward del ISR en OpenFin (H-J) (SOL-012) 🔴
- **Contexto.** En la tabla de "cálculo de intereses acreedores" del producto de inversión **2301** encontramos, para
  el **31-ago-2026**, una **tasa de retención 1.45%** (vs ley **0.90%**) y un **tope de ISR de 158,000** (vs
  5×UMA = 213,973.20). Juan quedó de revisarlo ("no debería cambiar").
- **Pendiente.** Confirmar si esos parámetros go-forward son correctos o un error de configuración (¿T-1
  desactualizada?).
- **Lo que buscamos.** Cerrar el único residuo material abierto del ISR; parametrizar por año de causación.

### E.2 — Decisión formal sobre la cuota Prosofipo (SOL-013) 🟢
- **Contexto.** La cuota mensual al Fondo de Protección **no** está en el core y **seguirá por fuera** (Finsus lo
  confirmó). Es obligación de ley (LACP Art. 104 Bis).
- **Pendiente.** Registro formal de Comité del **proceso externo** (documentado, con control y conciliación).
- **Lo que buscamos.** Que la excepción quede formalizada para auditoría/regulador (descubrirlo tarde es problema
  regulatorio).

---

### D.5 — Identidad exacta de la suspension de devengo / IDNC (SOL-015) 🔴
- **Contexto.** `REFERENCIA_TABLAS_POR_CASO.md §GAPB-IDNC` declara la identidad
  `io + io_venc = 0`. Al correrla contra `lc_finantial_data_stage`
  (2026-07-01..2026-08-18, filas con `io_venc <> 0`, n=45,761) **se cumple en 54.5%** y
  **no correlaciona con la mora** (18,074/30,582 en ≥90 días vs 6,889/15,179 en <90).
  La variante `io + iodnc = 0` se cumple en **85.2%** (315,188/369,904 filas con `iodnc <> 0`),
  y `iodnc` es lo que `V3_gapB_idnc.sql` anota como "contra-cuenta (saca interés de resultados)".
- **Pendiente.** Cuál es la identidad contable correcta de la suspensión, y por qué
  ninguna de las dos variantes llega al 100%.
- **Lo que buscamos.** Convertir GAPB-IDNC en invariante de regresión. No ajustamos la
  identidad a la que "pasa más": eso sería fijar la regla al dato. El caso queda
  BLOQUEADO por especificación hasta tener la respuesta.

## F. Insumos operativos (menores)
- **F.1 (SOL-014) 🟢** — Queries del diario de **Sergio (Aurum)** y **Abraham (OpenFin)**, y el **mapeo de las ~400
  tx del catálogo de "Ines"** (cuáles 2:1 cuenta-a-cuenta vs 1:1 unidireccional) para acelerar/benchmarkear Motor B.
