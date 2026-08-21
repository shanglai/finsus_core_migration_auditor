# NORTE de Validación — motores, métricas y gaps: qué generar, qué existe y cómo hallarlo

> **Propósito.** Índice maestro de cobertura. Antes de abrir cualquier validación, **anclar aquí**:
> este documento dice, para cada motor de cálculo, cuál es su **regla** (pieza K = fuente de verdad),
> si existe **spec de oráculo**, si existe **validación/SQL**, **dónde está el dato en la BD y cómo
> ubicarlo**, y su **estado**. Evita repetir el desvío de 2026-08-19 (concluir sin anclar en la pieza).
>
> **Regla de uso:** la pieza `K-*` manda sobre la regla; este doc solo mapea existencia y ubicación.
> Si un motor no tiene pieza, **falta conocimiento** → registrar `[PENDIENTE]`, no improvisar.
>
> **FUENTE ÚNICA (decisión C):** este NORTE es a la vez el **panorama humano** y el **catálogo de casos del
> Auditor Independiente** — no hay catálogo paralelo; el auditor espeja estas filas. Al agregar/cambiar un caso
> se actualiza aquí y se propaga vía `export_auditor/` (ver `export_auditor/PROMPT_SYNC_AUDITOR.md`).
>
> Actualizado: 2026-08-20 · Ligado a: `PLAN_DE_VALIDACION.md` (fases 0-9), `CATALOGO_VALIDACIONES.md`
> (invariantes), `30_oraculo/TRAZABILIDAD.md` (pieza→spec→código→test).

## Leyenda de estado
| estado | significado |
|---|---|
| ✅ VALIDADO | regla + oráculo + comparación corrida contra BD, resultado documentado |
| 🟡 PARCIAL | parte hecha (regla o dato o muestra chica); falta cerrar |
| 🟠 PENDIENTE | regla conocida, sin oráculo o sin validación corrida |
| ⛔ BLOQUEADO | falta insumo externo (dato, doc, log, definición) |
| 🔴 HALLAZGO | discrepancia/faltante confirmado, con ficha o pregunta abierta |

---

## 0. Alcance reencuadrado (sesión 2026-08-19, F-021/F-022) — TRES corrientes

Finsus reencuadró el entregable. No es "una validación"; son **dos motores inteligentes + una prueba**,
que deben mantenerse **separados** (no ligarlos evita la "trampa" del contraste de horarios):

| corriente | qué es | dueño del cruce | nuestro rol | estado |
|---|---|---|---|---|
| **Motor A · Validador de motores de cálculo** | A/B/C, C=oráculo con fórmulas oficiales sobre **data cruda** de ambos cores. Responde al top level: *(1) se come todo lo que opera, (2) los motores calculan bien* | nosotros | **construido** (ISR, plazo) / en curso (vista, saldo promedio) → falta **ejecutable/front** para Alberto (ops) y Lluvia (auditora) | 🟡 |
| **Motor B · Validador de la transaccional diaria ("diario")** | cruce **diario Aurum vs OpenFin**, normalizado por tipo (2:1/1:1) y con clasificación de diferencias | **Sergio/"Checo"** + INCO | **insertar nuestro tercero**; comparador propio | 🟢 **CORRIENDO** (`motor_b_diario.py`, 14-ago, **con `origin is null`**): total OF **29,029** vs AU cliente **29,020** = **+0.0%** (antes −1.7%; el filtro `origin` metodológico excluye lo migrado, en línea con Sergio/F-027). Residual por categoría = NULL "api_dimmer" (hueco de la vista de Finsus). Resta: match instancia ([[P-016]]) |
| **Prueba día cero** | empate de **saldos + movimientos** al cutover (4 bloques de datos); **NO** ligar a pago de rendimientos vista | Aurum/INCO (Giancarlo, Julio) | apoyo: check de queries de ingesta, cohorte de cuentas testigo | 🟠 NUEVO (apoyo) |

**Principio rector (repetir a Alberto/auditor):** AurumCore se valida **contra su propia línea de tiempo y
contra el oráculo/ley**, NO contra OpenFin (OF paga 6pm, Aurum medianoche → 6h ⇒ nunca empatan al momento).
El oráculo C es el instrumento correcto: contrasta contra la realidad, no contra el core de al lado.

**Cambio de fuente de datos:** apuntar a la **RÉPLICA** (casi tiempo real; sólo la consumen Aurum + nosotros),
**no al T-1**. Acceso por validar. Actualiza [[acceso-bd-finsus]].

**Confirmaciones de Finsus en la sesión:** ISR = diferencia de **modelo**, defecto $0 · Gap B (IDNC) **existe**
(sólo no documentado) · Gap C (Prosofipo) se calcula **por fuera y seguirá por fuera** · gaps de divisas y
tasa variable **N/A** (no hay productos USD ni tasa variable) · H-J (go-forward 1.45%/158K al 31-ago) **escalado
a Finsus** (Juan lo revisa: "no debería cambiar").

---

## 1. Matriz maestra por dominio

### DEV — Devengo e intereses
| # | motor / métrica | regla (pieza) | spec oráculo | validación / código | dato en BD · cómo ubicarlo | estado |
|---|---|---|---|---|---|---|
| 2.1.2 | **Rendimiento plazo fijo** | [[K-DEV-003]] | S-DEV-002 *(por escribir)* | `oraculo_rendimientos.py::rendimiento_plazo` · `validate_plazo_origin.py` · `V5` | `aurumcore.iv_payment_plan` (`origin`, `interest_amount`, `interest_paid`) | ✅ **A=B=C**: oráculo reproduce **migrado (C=A) 97.8%** y **live `origin null` (C=B) 99.7%** (cohortes 300 ctas). Residual = método (tasa despejada) en cuentas con cambios a media vida → cierra con tasa contratada del esquema |
| 2.1.1 | **Interés propio vista/ahorro** (capitalización mensual) | [[K-DEV-002]] v2 | S-DEV-001 *(por escribir)* | `oraculo_rendimientos.py::rendimiento_vista` (autoprueba) | `transaction_detail` `YIELD PAYMENT` · ref `Capitaliza Interes DD/MM/AAAA, Retencion:N` · **source=target** · productos 2006/2011/2012/2013/2015/2017/2019 | 🟡 regla+ejercicio migrado OK · ⛔ **corrida viva 31-ago sin validar** ([[P-015]]) |
| 2.1.3 | **Saldo promedio** (base de vista y de ISR) | [[K-DEV-002]] v3 (fórmula Finsus F-022) + doc F-009 | parte de S-DEV-001 | `oraculo_rendimientos.py::saldo_promedio_rendimiento` (autoprueba) | `account.average_balance_amount` (guardado) · `account_balance_tracking` (difference/elapsed days, **arranca ~ago-2025**) | 🟡 **fórmula ya declarada** `(saldo_ant+Σsaldos_día)/n_días`; falta corroborar con logs del CORE y cerrar reconstrucción histórica ([[P-006]]) |
| — | **Devengo diario / redondeo** (sesgo) | [[K-DEV-001]] v2 | parte de specs DEV | prueba de signo (Fase 8) *(sin correr)* | `transaction_detail` ref `Devengamiento de intereses-…` (post-cutover = solo inversión) | 🟠 redondeo documentado · sesgo sin probar ([[P-014]]) |

### FIS — Fiscal (ISR)
| # | motor / métrica | regla (pieza) | spec oráculo | validación / código | dato en BD · cómo ubicarlo | estado |
|---|---|---|---|---|---|---|
| — | **ISR retención al pago** (motor B, AurumCore) | [[K-FIS-002]] v3 | **S-FIS-001** (escrita) | `entrega_finsus/oraculo_isr.py` (5/5) · `V1_isr_al_pago_aurum.sql` · `fase1_isr_comparador.py` · `fase1_isr_desviacion.py` | `transaction_detail` `YIELD TAX PAYMENT` · asiento a producto `0000` (`100-0000-438220`) | ✅ VALIDADO · set **3,236/3,236 MODELO** · C=B al pago |
| — | **ISR devengo diario** (motor A, OpenFin) | [[K-FIS-003]] v2 | (comparación, no oráculo) | `V2_isr_devengo_openfin.sql` | OpenFin `isr_diario` (nivel cliente/día) | ✅ confirmado **diferencia de MODELO** (provisión-devengo vs pago) |
| — | **Parámetros ISR vs norma** (tasa/UMA/exención/días) | [[K-FIS-004]] | (tabla en S-FIS-001) | — | norma 2026 (INEGI/LIF/LISR) | ✅ CERRADO ([[P-010]]) · residuos: personas morales; **H-J** go-forward 1.45% |
| — | **ISR histórico mal calculado** (OpenFin) | [[K-FIS-001]] | — | — | OpenFin (retenciones por periodo) · PAR-352 | 🔴 defecto histórico · regularización ([[P-007]]) |

### CAP / COL — Productos
| # | motor / métrica | regla (pieza) | spec | validación / código | dato en BD · cómo ubicarlo | estado |
|---|---|---|---|---|---|---|
| — | **Cuentas vista — diff de saldo** | [[K-CAP-001]] | — | árbol día cero (F-013) | `account` product_type_key=`ACCOUNT` | 🟡 diff de saldo cascada a ISR (Fase 0) |
| — | **Crédito One Click — existencia** | [[K-COL-001]] | — | árbol día cero | `lc_loan_contract` / `account` LOAN | ✅ existencia cuadra 100% |
| — | **Crédito One Click — devengamiento** | *(falta pieza)* | — | — | crédito (regla no confirmada) | 🟠 regla pendiente ([[P-006]] @00:52:12) |

### REG — Regulatorio (gaps de motor)
| # | motor / métrica | regla (pieza) | spec | validación / código | dato en BD · cómo ubicarlo | estado |
|---|---|---|---|---|---|---|
| 2.1.7 | **Suspensión de devengo / IDNC** (cartera vencida) | [[K-REG-001]] v3 | — | `V3_gapB_idnc.sql` | `aurumcore.lc_finantial_data_stage` (`io` vs `io_venc`) | ✅ **CONFIRMADA en datos**: `io_venc` cancela exactamente `io` (suspensión); doc F-023 + mecánica reproducida. Resta: barrer población completa y contabilización a cuentas de orden |
| — | **Cuota Prosofipo** (Fondo de Protección) | [[K-REG-002]] v3 | (por definir) | `V4_gapC_prosofipo.sql` | cuota: **no existe** en core (por fuera). Cobertura-841: sí (a tiempo de reporte, System Config — **re-verificar** término) | 🔴 **cuota faltante real** (por fuera, aceptado) · 🟡 cobertura-841 existe |
| 4/5 | **Tasa variable (TIIE/CETES)** y **Revaluación cambiaria/UDIS** | F-023 §4-5 | — | — | — | ✅ **N/A confirmado** (AurumCore: todo tasa fija y sólo MXN; ambos fuera de alcance/roadmap; Finsus no tiene esos productos) |
| — | **Write-offs** (quitas, condonaciones, castigos, reestructuras) | F-023 §1 *(falta pieza K)* | — | — | pólizas individuales por evento → ERP; IFRS9 calcula reservas a cierre | 🟠 AurumCore dice que **sí** genera póliza por evento (contra la marca "proceso externo") — validar en datos + crear pieza |

### CTB — Contable
| # | motor / métrica | regla (pieza) | spec | validación / código | dato en BD · cómo ubicarlo | estado |
|---|---|---|---|---|---|---|
| — | **Doble partida / balanza (familia B)** | [[K-CTB-001]] | — | `contable_bc.py` (DuckDB) · `PLAN_CONTABLE_BC.md` | `transaction_detail` (debit neg/credit pos + `*_accounting_account`) · `cat_accounting_account` (naturaleza) | 🟢 **B1 CUADRA 0.00** (0/7 días); **B3/B4** cerrados via DuckDB: pools dominan, residual cliente pequeño (B3 0.6%, B4 2,975 gaps a investigar). Data-quality: `''` en ~510 mov/día (crédito) |
| — | **Balanza por producto · cross A/B (familia D)** | [[K-CTB-001]] | — | `PLAN_CONTABLE_BC.md §3.quater` | AU `account.balance_amount` ↔ OF `acreedores.saldo` por producto | 🟢 **reconcilia ~1-2%/producto** (2301/2002 casi al punto; delta = t-1 vs actual). **2001 −34% explicado**: concentración en pocas cuentas grandes (OF max $53.5M vs AU $20M) = sync, no defecto. Hallazgo: `daily_account_balances` **STALE** ([[P-018]]) |
| — | **Amarre auxiliar↔mayor (familia C)** | [[K-CTB-001]] | — | (pendiente) | Σ auxiliar por producto = mayor (derivar de movimientos) | 🟠 versión por-producto lista; amarre a cuenta contable pendiente |

### MOV / TMP / DAT / MIG — Estructura y tiempos (habilitadores)
| motor / métrica | regla (pieza) | estado |
|---|---|---|
| Atomicidad de transacciones (OpenFin no atómico vs Aurum atómico) | [[K-MOV-001]], [[K-MOV-005]], [[K-MOV-006]] | 🟡 mapeado; reconstrucción de tipo en OpenFin |
| Tipos de transacción AurumCore observados | [[K-MOV-004]] | 🟡 catálogo parcial |
| CLABE / SPEI-out | [[K-MOV-002]] | 🟠 algoritmo CLABE ([[P-008]]) |
| Trazabilidad ids reinversión | [[K-MOV-003]] | 🟠 falta llave 1:1 |
| Ventanas de proceso / asincronía / cutover | [[K-TMP-001]] | 🟡 día 1 vista, corte, ingestas |
| Modelo de datos OpenFin / AurumCore / llaves | [[K-DAT-002]]..[[K-DAT-006]] | 🟡 casi cerrado (P-004/P-011) |
| Día cero e ingestas · migrado vs generado | [[K-MIG-002]], [[K-MIG-005]] | 🔴 riesgo metodológico #1 ([[P-013]]) |

---

## 2. Localizadores de datos en la BD (el "cómo buscarlo", preciso)

**Producto real de una cuenta** (no confiar en el código de la referencia de texto):
- `aurumcore.account.product_type_key` ∈ {`INVESTMENT_ACCOUNT`, `ACCOUNT` (vista/ahorro), `LOAN_ACCOUNT`}.
- 2º segmento de `account.account_number`: `2301/2307/2308`=inversión · `2006/2011/2012/2013/2015/2017/2019`=ahorro con interés · `2002`≈cheques (tasa 0%) · `100-0000-*` y `100-2000-40000*`=**cuentas operativas de Finsus** (holder `ce099c46…`), excluir del universo cliente.

**Flujos de interés/rendimiento** (`transaction_detail.transaction_type`, `alfanumeric_reference`):
| flujo | cómo se reconoce | source → target |
|---|---|---|
| Rendimiento de **inversión** | `YIELD PAYMENT` + ref `Pago de rendimientos-100-2301-…` | INVESTMENT → **vista del titular** (destino de liquidación) |
| **Interés propio vista/ahorro** | `YIELD PAYMENT` + ref `Capitaliza Interes DD/MM/AAAA, Retencion:N` | **source = target** (autocapitalización) |
| Devengo diario | ref `Devengamiento de intereses-…` | (post-cutover: solo inversión) |
| **ISR** retenido | `YIELD TAX PAYMENT` · asiento a `100-0000-438220` | — |

> **Regla de oro:** para saber *quién gana* un rendimiento, cruzar `product_type_key` del **source**;
> para *quién lo recibe*, del **target**. Nunca deducir el producto del código en la referencia (ese
> código es el de la inversión origen, aun cuando el dinero caiga en una cuenta vista).

**Plazo fijo:** `aurumcore.iv_payment_plan` (`interest_amount`, cronograma) · JOIN `account`.
**Saldo promedio:** `account.average_balance_amount` (valor guardado) · `account_balance_tracking`
(`difference of days`/`elapsed days`; **historia parcial ~desde ago-2025** → no reconstruye cuentas
viejas; valor exacto se valida en **logs del CORE**, traza `Calculating with average balance`).
**Fórmula (Finsus, F-022):** `saldo_promedio = (saldo_anterior + Σ saldos_diarios) / n_días_periodo`.

**Mapeo de transacciones OpenFin↔Aurum (F-021, para el Motor B/diario):** NO es 1:1 uniforme —
**cuenta-a-cuenta entre clientes Finsus: 2 tx OF (cargo+abono) → 1 tx Aurum**; **unidireccionales
(SPEI in/out, pago de servicios): 1:1** (cargo→cargo, abono→abono). Son las **~400 del catálogo contable
("de Ines")**; el detalle completo de cuáles caen en cada caso está **[PENDIENTE]** ([[K-MOV-001]] v2).

**Fuente de datos:** usar la **RÉPLICA** (no T-1). El T-1 se "plancha" y puede perder permisos; la réplica
es casi tiempo real y dedicada. Acceso por validar.
**IDNC / cartera vencida:** `aurumcore.lc_finantial_data_stage`.
**OpenFin (motor A):** `isr_diario` (devengo diario nivel cliente) · tablas núcleo [[K-DAT-002]].

**Llaves de correlación:** `account.account_number` → `accountholder_id`; `external_id`=interno de
7 dígitos (no "100-10-X"); OpenFin `kasociado` ↔ (`idsucursal`,`idrol`,`idasociado`).

**Migrado vs generado por AurumCore** (crítico, [[K-MIG-002]]): referencia **NULL** o `created` < cutover
(~2026-08-03) ⇒ **migrado**; con referencia y ≥ cutover ⇒ **generado por AurumCore**. Confirmar con la
columna `origin` cuando se resuelva [[P-013]].

---

## 3. Qué existe hoy vs qué falta (resumen ejecutivo)

**Existe y está validado:** ISR al pago (motor B, 3,236/3,236) · ISR devengo = modelo (motor A) ·
parámetros ISR vs norma (P-010) · rendimiento plazo (775/775) · oráculos autoprobables
(`oraculo_isr.py` 5/5, `oraculo_rendimientos.py` 3/3) · paquete `entrega_finsus/` (V1–V5 + catálogo).

**Existe la regla, falta cerrar el oráculo o la corrida:**
- Interés vista/ahorro → escribir **S-DEV-001**, y **validar el cierre vivo del 31-ago** ([[P-015]]).
- Saldo promedio → **definición exacta** + logs del CORE ([[P-006]]).
- Devengo/redondeo → **prueba de sesgo** (Fase 8) sin correr ([[P-014]]).
- Gap B/IDNC → validar **lógica** (umbral, reserva, cuentas de orden), falta doc IFRS9.
- Contable (familias B/C) → invariantes **sin construir**.

**Faltante de motor confirmado (hallazgo):** Prosofipo ([[K-REG-002]]).
**Regla faltante:** devengamiento One Click de crédito ([[P-006]]).
**Deuda de índices:** `TRAZABILIDAD.md` y `CATALOGO_VALIDACIONES.md` están casi vacíos y deben
poblarse con las specs/validaciones ya existentes; `ENTENDIMIENTO_GLOBAL.md` está en v6 (rezagado).

---

## 4. Orden recomendado (de aquí en adelante)
1. **S-DEV-001** (saldo promedio + interés vista) — desbloquea 2.1.1, 2.1.3 y el ISR-vista; se puede
   escribir ya salvo la definición fina de saldo promedio (marcar `[PENDIENTE]`, no bloquear).
2. **Pedir logs del CORE** de AurumCore (saldo promedio + `Capitaliza Interes`) con lista de
   cuentas+fechas → cierra P-006 y prepara la validación del 31-ago.
3. **Validar la corrida del 31-ago** (P-015) en cuanto exista.
4. **Escalar rendimiento plazo** a muestra grande.
5. **`sintesis`** para des-rezagar `ENTENDIMIENTO_GLOBAL.md` y poblar `TRAZABILIDAD`/`CATALOGO`.
6. Abrir **familias contables B/C** (tolerancia 0.00) y la **prueba de sesgo** (Fase 8).

> **Producto final / auditor:** `PROMPT_CONSTRUCTOR_VALIDADOR.md` es el prompt que, en otra sesión, hace que
> Claude Code **construya** el *Validador Independiente* (pre-auditor de nuestro motor C + entregable a Finsus):
> catálogo de casos + motor determinista DuckDB/Polars/Decimal, violaciones-como-salida, NO all-pass. Este NORTE
> es su fuente de "qué se valida".
