# Dossier de Validación — migración openfin → AurumCore

**Emisor:** tercero independiente · **Fecha:** 2026-08-20 · **Propósito:** que Finsus **reproduzca y haga
cross-check** de cada validación contra la suya. Todo es **solo lectura**, con las tablas, columnas, filtros,
consultas y fórmulas exactas, más el **razonamiento** de cada enfoque, **lo que tomamos de sus queries/docs**, y
los **supuestos** marcados.

Convención de confianza: `[CONFIRMADO]` (consta en fuente/BD) · `[INFERIDO]` · `[SUPUESTO]` · `[PENDIENTE]`.

---

## 0. Marco — modelo de tres motores y delimitadores

**Tres motores.** **A = openfin** (histórico, *no es la verdad*) · **B = AurumCore** (bajo prueba) ·
**C = oráculo independiente** (implementa la **norma/contrato**, no copia el código de ningún core). Ante una
discrepancia, C es quien dice **cuál está bien**. Matriz: `A=B=C` OK · `A=B≠C` defecto de negocio (ambos) ·
`A=C≠B` defecto AurumCore · `A≠B=C` defecto openfin ya corregido · `A≠B≠C` regla mal especificada.

**Precisión.** Todo cálculo monetario en `decimal.Decimal`, **cero float**; redondeo **explícito** por producto.

**Delimitador "Aurum nativo/vivo"** `[CONFIRMADO en datos, taxonomía por confirmar → SOL-004]`.
`transaction.origin` tiene **semántica mixta**: unos valores son **fuente de migración**
(`FINSUS_INVESTMENT`, `FINSUS_2`, `841`, `FINSUS_YIELD…`), otros **canal/producto vivo** (`DIMO`); y
`origin IS NULL` aparece **desde abr-2026** (periodo shadow/paralelo). Regla que aplicamos:
- **Validar el CÁLCULO de un motor** (¿Aurum computa bien?): universo = **generado por Aurum**. En tablas sin tag
  de canal (`iv_payment_plan` solo FINSUS/null; ISR-retención 100% null) → `origin is null` es limpio.
- **Completitud/transaccional** (¿le llegó todo post-primario?): `created >= cutover (2026-08-02/03)`.

**Hallazgo estructural** `[CONFIRMADO]`. AurumCore **persiste el AUXILIAR** (saldos/movimientos por cuenta) pero
**NO los agregados derivados** (balanza/mayor, tasas contratadas, **saldo base punto-en-tiempo**); se calculan en
el proceso/reporte. Por eso varias validaciones de **cálculo vivo** requieren los **logs del CORE** (SOL-003).

**Qué tomamos de Finsus.** Diccionarios y mapeo de datos; el **árbol de día cero** (universo A/B en común); el
**gap analysis de motores** (F-020) y la **respuesta oficial de AurumCore** (F-023); los **queries "live" de
Sergio** (captación y pago a créditos) — de ellos adoptamos el grano `transaction` y el **filtro `origin`**; los
catálogos `cat_tx_cuadre` (OpenFin) y `cat_finsus_transaction` (AurumCore). Marcamos abajo cada uso.

---

## 1. ISR sobre rendimientos de inversión

### 1.1 Retención al pago (motor B) vs oráculo
**Afirmación.** `[CONFIRMADO]` La retención de ISR que AurumCore asienta **al pago** coincide con la regla.
**Razonamiento.** openfin **devenga** el ISR diario (provisión, tabla `isr_diario` 171.8M); AurumCore **retiene
al pago**. Comparar provisión-devengo contra retención-al-pago da magnitudes distintas — es **diferencia de
modelo**, no defecto. Por eso el árbitro es C (la regla), no A vs B directo.

**Tablas / columnas (AurumCore).** `transaction_detail`, `transaction`, `account` (payer/payee), `accountholder`;
saldo base: `account_balance_tracking`; capital: `account.iv_initial_amount`.
**Firma del asiento** `[CONFIRMADO en semilla]`: `transaction_type='INTERNAL TRANSFER'`,
`transaction_channel='Generic'`, contrapartida = cuenta de ISR producto `0000` (p.ej. `100-0000-438220`);
`isr_retenido = credit_amount`; la **referencia** `Pago de rendimientos-100-2301-<inv>` nombra la inversión.

**Consulta (extracción del ISR retenido):**
```sql
select pa.accountholder_id, pa.account_number as cuenta_cliente, td.created as fecha_pago,
       td.credit_amount as isr_retenido, pe.account_number as cuenta_isr, td.alfanumeric_reference
from aurumcore.transaction_detail td
join aurumcore.transaction t  on t.transaction_id = td.transaction_id
join aurumcore.account pa     on pa.account_id = t.payer_account_id
join aurumcore.account pe     on pe.account_id = t.payee_account_id
where td.transaction_type='INTERNAL TRANSFER' and td.transaction_channel='Generic'
  and split_part(pe.account_number,'-',2)='0000'
  and td.created >= :fecha_ini and td.created < :fecha_fin;
```

**Fórmula del oráculo (C)** `[CONFIRMADO vs doc AurumCore F-019]` — proporción **÷ saldo total**:
```
Monto Exento  = UMA × 5
Base Gravable = Saldo Total − Monto Exento
Proporción    = Trunc20( Saldo Cuenta / Saldo Total )
ISR Diario    = Trunc5( Base Gravable × Trunc20( Tasa / (100 × 365) ) )
ISR Retenido  = Round2( Trunc20( ISR Diario × Días Periodo ) × Proporción )
```
**Universo y resultado** `[CONFIRMADO]`: sobre el árbol de día cero, **18,599 inversiones · 14,913 clientes ·
$621.3M**. Cohorte de desviación material (|A−B|>$0.10): **3,236 inversiones / 2,774 clientes**; descuadre bruto
Σ|A−B| **$34,719** (=**.006% del portafolio**); neto −$10,533 (se cancela; ambas direcciones). **Set completo
3,236/3,236 = MODELO → defecto de cálculo real $0.** `oraculo_isr.py` reproduce casos de oro (5/5: 46.37 /
4.81 / 0.05 / 765.75 / 13.38).

**Lo que usamos de Finsus.** El **árbol de día cero** (universo A/B) y el doc **"Pago de Rendimientos" (F-019)**
para la fórmula; **F-019 corrigió la proporción a ÷saldo total** (antes ÷base gravable, C-002 resuelta).

**Validación nativa viva (ISR-04)** `[PENDIENTE / BLOQUEADA]`. Universo vivo: **59,546 retenciones / $1.51M**
(post-cutover, 100% `origin=None`). Con `isr_live_nativo.py` el oráculo/params son correctos, **pero** validar al
centavo requiere el **saldo base punto-en-tiempo** de cada retención (el snapshot actual solo cuadra ~13% por
deriva de saldo) → **bloqueado por los logs del CORE (SOL-003)**.

### 1.2 Parámetros del ISR vs la norma `[CONFIRMADO]`
| Parámetro | AurumCore | Norma 2026 |
|---|---|---|
| UMA anual | 42,794.64 | INEGI, DOF 9-ene-2026 (vigente 1-feb) |
| Tasa de retención | 0.90% | LIF 2026 Art. 24 (remite LISR 54/135) |
| Exención | 5×UMA = 213,973.20 | LISR Art. 93 fr. XX (beneficio SOFIPO) |
| Días del año | 365 | `tax.days.year` |

**Supuestos/pendientes.** `[SUPUESTO]` UMA vigente desde 1-feb → rezago de ~9 días en feb-2026 (sobre-retención
menor, acotada). `[PENDIENTE]` **H-J**: config go-forward en la tabla de intereses acreedores del producto 2301
(tasa **1.45%** y tope **158,000** al 31-ago) contradice la ley 0.90% / 5×UMA — **a confirmar** (SOL-012).
`[PENDIENTE]` **personas morales**: LISR 54 las excluye; el doc pone exención $0 (SOL-011).

---

## 2. Rendimiento de plazo fijo (2.1.2)

**Afirmación.** `[CONFIRMADO]` El oráculo reproduce `iv_payment_plan.interest_amount` de AurumCore al centavo.
**Razonamiento.** `iv_payment_plan` es solo el calendario (no trae capital/tasa); el capital está en
`account.iv_initial_amount` y los días son `due_date − start_date`. La **tasa** no vive en una tabla limpia
(`account_yield` da 0 para inversión) → se **despeja del periodo 1** y se verifica que la fórmula reproduce
**todos** los periodos (auto-consistencia).

**Tablas / columnas.** `iv_payment_plan` (`origin`, `interest_amount`, `interest_paid`, `start_date`,
`due_date`, `payment_number`), `account.iv_initial_amount`.
**Delimitador.** `origin` en esta tabla solo es `FINSUS` (migrado) o `null` (Aurum-engine) → `origin is null` es
limpio para validar el cálculo.

**Consulta (plan de pagos por inversión):**
```sql
select p.account_number, p.payment_number, (p.due_date - p.start_date) as dias_periodo,
       p.interest_amount as rend_aurum, a.iv_initial_amount as capital
from aurumcore.iv_payment_plan p
join aurumcore.account a on a.account_number = p.account_number
where p.origin is null and p.interest_paid = true and p.interest_amount > 0
order by p.account_number, p.payment_number;
```

**Fórmula del oráculo (C)** `[CONFIRMADO vs doc AurumCore]` — Ceil10/Ceil10/RoundHalfEven2, **base 360**:
```
Plazo = RoundHalfEven2( Ceil10( Ceil10( (Capital × Tasa)/100 ) / DíasAño ) × Días Transcurridos )
```

**Resultado a VOLUMEN** `[CONFIRMADO]`: universo generado por Aurum (`origin null`, ≥2 periodos) =
**157,999 cuentas / 530,195 periodos → 100.00% (0 violaciones)**. Migrado (`origin=FINSUS`, C=A): 97.8%.
**Supuesto.** `[SUPUESTO]` La **tasa** se despeja del periodo 1 → se valida la **fórmula/redondeo**; la **tasa
contratada** vs el esquema del producto es pendiente menor (no defecto).

---

## 3. Rendimiento de cuentas a la vista (2.1.1) y saldo promedio (2.1.3)

**Afirmación.** `[CONFIRMADO]` Existe interés propio de captación vista/ahorro (productos 2006/2011/2012/2013/
2015/2017/2019): ~**100K cuentas**, capitalización mensual (`transaction_detail`, ref `Capitaliza Interes …`,
`source = target`). **Distinto** del rendimiento de inversión que se **deposita** en la vista del titular.

**Fórmula del oráculo (C)** `[CONFIRMADO doc §5.1]`:
```
Vista = Round2( Trunc20( Trunc20( (SaldoProm × Tasa)/100 ) / DíasAño ) × Días Periodo )
Saldo Promedio = ( Saldo_anterior + Σ saldos_día ) / n_días_periodo        [Finsus, F-022]
```
**Estado** `[PENDIENTE / BLOQUEADA]`. (a) La **corrida viva** de AurumCore aún no ocurre — 1er cierre de mes
post-cutover = **31-ago / 1-sep** (lo migrado llega hasta jul-2026). (b) El **saldo promedio exacto** se valida
en los **logs del CORE** (`Calculating with average balance`); `account_balance_tracking` arranca ~ago-2025
(historia incompleta) → **bloqueado por SOL-003**. Migrado (ene-jul) parcialmente validable con `avg_balance` guardado.

---

## 4. Transaccional diaria — "¿no hay faltante de transacciones?" (Motor B)

**Afirmación.** `[CONFIRMADO]` AurumCore recibe y opera las mismas operaciones que openfin (no se cae ninguna),
coherente con su propia realidad. **Es A vs B** (existencia/completitud), no C (una transacción ocurre o no).
**Razonamiento.** openfin es **no atómico** (cargo+abono = 2 registros); AurumCore es **atómico** (1). Hay que
**normalizar** antes de comparar: **2:1** cuenta-a-cuenta (peer) vs **1:1** unidireccional (SPEI/servicios/tarjeta).
Y validar contra la **realidad de Aurum**, no contra openfin (openfin paga 18:00, Aurum medianoche → 6h; nunca
empatan al momento — no es defecto).

**Tablas / columnas.**
- **openfin:** `vista_movimientos_cargos` / `vista_movimientos_abonos` (`tipo_transaccion`, `monto`, `referencia`);
  catálogo `cat_tx_cuadre` (`tipo_transaccion` → `cuenta_contable_cargo/abono`).
- **AurumCore:** `transaction_detail` (`transaction_type`) JOIN `transaction` (`origin`).
- **Crosswalk** `cat_tx_cuadre` ↔ `cat_finsus_transaction` (**misma numeración de tipo**); clasificación **por
  pierna** (SPEI-in = depósito en Aurum).

**Filtros.** `created::date=día`; **sucursal 201 (fondeadora) fuera**; **`origin is null`** (excluye migrado); se
excluye crédito (dispersión/pago), como en los queries de Sergio.

**Resultado (14-ago)** `[CONFIRMADO]`: OF **29,029** ops normalizadas vs AU **29,020** (cliente) = **+0.0% (delta
+9)**. Por categoría: Depósito −2.3% · SPEI +3.0% · Tarjeta +1.8%; Transferencia interna −23% se explica por
**3,506 movimientos que la vista de Finsus deja sin tipo** ("api_dimmer", $89.3M). Monto ≈ $528M/día.

**Lo que usamos de Finsus.** Sus vistas `vista_movimientos_*` y `cat_tx_cuadre`; el **filtro `origin`** (de los
queries de Sergio); el mapeo tx **2:1/1:1** (explicado por Abraham). **No** usamos su vista pre-armada
`openfin_m.aurum_transaction_final_complete` (no tenemos acceso; SOL-001) — **la reconstruimos** (auditable).
**Pendiente** `[PENDIENTE]`: match instancia-a-instancia (requiere `openfin_migracion`, SOL-001).

---

## 5. Contable (familias B, C, D)

### 5.1 Doble partida diaria (B1) `[CONFIRMADO]`
**Modelo.** AurumCore **no guarda póliza/balanza como tabla**; el asiento vive en `transaction_detail`
(`source_accounting_account`/`target_accounting_account`; `debit_amount` **negativo**, `credit_amount`
**positivo**; cada fila = asiento balanceado). Plan de cuentas: `cat_accounting_account` (naturaleza).
**Invariante (tol 0.00):** `Σ(debit) + Σ(credit) = 0` por día.
```sql
select created::date, round(sum(debit_amount),2) sd, round(sum(credit_amount),2) sc,
       round(sum(coalesce(debit_amount,0)+coalesce(credit_amount,0)),2) descuadre
from aurumcore.transaction_detail where created::date >= :d1 and created::date < :d2 group by 1;
```
**Resultado:** 10–16 ago, **0/7 días violan** (descuadre $0.00); 0 asientos sin cuenta; naturaleza correcta.
**B3/B4** (monto vs Δsaldo, continuidad): las "violaciones" se concentran en **cuentas pool/operativas** (cámara
SPEI) y **empates de timestamp** → **no defecto** (residual cliente pequeño, a investigar 2,975 gaps).

### 5.2 Balanza por producto — cross A/B (D) `[CONFIRMADO]`
**AurumCore:** `Σ account.balance_amount` por producto (`split_part(account_number,'-',2)`, excl `201-%`).
**openfin:** `Σ acreedores.saldo` por `idproducto` (`estatus in (1,3,4,5)`, excl sucursal 201).
**Resultado:** reconcilia **~1-2% por producto** (2301 inversión $20.79B vs $20.55B +1.2%; 2002 vista $1.252B vs
$1.234B +1.4%). Delta = asincronía **t-1 (openfin réplica) vs actual (AurumCore)** — no defecto. **Alerta:**
producto **2001 −34%** (a investigar). **Nota** `[CONFIRMADO]`: `daily_account_balances` está **STALE** (solo
oct-nov 2025, sin inversiones) — no usar (SOL-006).

### 5.3 Amarre auxiliar↔balanza (C) `[PENDIENTE]`
AurumCore no persiste una balanza completa → el amarre `Σ activo = Σ pasivo` no cierra con `account.balance_amount`
(faltan capital/caja/resultados). Requiere construir la balanza desde **todos** los movimientos, o **la balanza/
mayor de Finsus** (a solicitar).

---

## 6. Cuentahabientes — identidad WSO2 ↔ AurumCore `[CONFIRMADO]`

**Tablas.** WSO2 (`wso2_identity_shared_db`): `um_hybrid_user_role` (`um_user_name` = teléfono 10 díg,
`um_role_id`), `um_hybrid_role` (clientes = roles CTP). AurumCore: `accountholder` (`username`,
`contact_mobile_phone`, `email`, `accountholder_number`). **Llave:** teléfono 10 díg. **Excl:** sucursal 201.
**Resultado:** **Aurum→WSO2 completo** (solo **20** clientes sin identidad; los 78,881 del bruto eran sucursal
201 fondeadora). **WSO2→Aurum: 181,844 identidades con roles completos sin accountholder** → `accountholder` es
100% ACTIVE (no retiene cerradas) → **asimetría de retención IdP↔core (churn probable), no defecto** — a confirmar
el lifecycle (SOL-007).

**Consulta (export WSO2, se corre con `\copy`):**
```sql
select ur.um_user_name as phone, bool_or(ur.um_role_id=42) r_created, bool_or(ur.um_role_id=41) r_confirmed,
       bool_or(ur.um_role_id=43) r_accounts, bool_or(ur.um_role_id=46) r_investments, count(*) total_roles
from public.um_hybrid_user_role ur where ur.um_role_id in (40,41,42,43,45,46,47,48) group by 1;
```

---

## 7. Gaps de motores (análisis de Finsus F-020, verificado)

| Gap | Resultado | Evidencia |
|---|---|---|
| **B · Suspensión devengo / IDNC** | ✅ **existe + confirmado en datos** | `lc_finantial_data_stage`: `io_venc` cancela exacto a `io` (io+io_venc=0 en suspensión total); doc F-023 (90d, reserva 100% `RESERVA_INT_*`, cuentas de orden). |
| **C · Cuota Prosofipo** | 🔴 **motor faltante (por fuera)** | `system_configuration` = 0 para cobertura/UDIS/prosofipo/fondo. La cobertura-841 la calcula al reporte (F-023); la **cuota mensual** se hace por fuera y seguirá por fuera (LACP Art. 104 Bis). Re-verificar variable (SOL-010). |
| **Write-offs** | 🟡 parcial | `Condonación`/`Descuento` se postean en `transaction_detail`; no hay tabla/`charge_type` formal de quita/castigo → pedir póliza (SOL-009). |
| **Tasa variable / Divisas-UDIS** | ✅ **N/A** | F-023: todo tasa fija, sólo MXN; fuera de alcance/roadmap. Finsus no tiene esos productos. |

**Consulta Gap B (identidad de suspensión):**
```sql
select lc_contract_id, round(io,2) io, round(io_venc,2) io_venc, round(capital_venc,2) cap_venc
from aurumcore.lc_finantial_data_stage
where information_date = (select max(information_date) from aurumcore.lc_finantial_data_stage) and io_venc < 0;
```

---

## 8. Supuestos y validaciones vs los documentos de Finsus (resumen)

| # | Tema | Estado vs documento |
|---|---|---|
| 1 | Proporción ISR ÷ **saldo total** | `[CONFIRMADO]` Finsus **corrigió** el doc (F-019) — antes ÷base gravable (C-002 resuelta). |
| 2 | Parámetros ISR (UMA/tasa/exención/días) | `[CONFIRMADO]` vs INEGI/LIF/LISR. |
| 3 | Tasa go-forward 1.45% (H-J) | `[PENDIENTE]` contradice ley — a confirmar (SOL-012). |
| 4 | Gap B (IDNC) | `[CONFIRMADO]` la lógica de F-023 coincide con CNBV C-16/IFRS9 + datos. |
| 5 | Gap C (Prosofipo) | `[CONFIRMADO]` la **cuota** falta (F-023 solo cubre cobertura-841). |
| 6 | Tasa contratada de plazo | `[SUPUESTO]` despejada del periodo 1 (fórmula validada; tasa vs esquema pendiente). |
| 7 | Saldo base / saldo promedio | `[PENDIENTE]` requiere logs del CORE (SOL-003). |
| 8 | Taxonomía de `origin` | `[PENDIENTE]` semántica mixta — a confirmar (SOL-004). |
| 9 | Delimitador Aurum-vivo | `[SUPUESTO]` `created >= cutover` (o `origin null` para cálculo) — a confirmar. |

---

## 9. Solicitudes pendientes a Finsus
Ver **`SOLICITUDES_FINSUS.md`** (14 ítems SOL-001..014). Bloqueo maestro: **SOL-003 (logs del CORE)** — destraba
ISR vivo, saldo promedio y rendimiento vista al centavo.

---

*Reproducibilidad: los scripts (`oraculo_isr.py`, `oraculo_rendimientos.py`, `motor_b_diario.py`, `contable_bc.py`,
`cuentahabientes_wso2.py`, `validate_plazo_origin.py`, `isr_live_nativo.py`) y los `.sql` (`V1..V5`,
`consultas_validacion.sql`, `wso2_cuentahabientes.sql`) acompañan este dossier. Todo solo lectura; sin PII a git.*
