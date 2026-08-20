# Preguntas Abiertas

Priorizadas por impacto en la validación (Anexo A.4). Prioridad: ALTA | MEDIA | BAJA.

### Cerradas
- **P-001** [CERRADA] Nombre del core → **AurumCore** (K-ORG-001).
- **P-003** [PARCIAL] Calendario: deadline 7-sep, decisión 1-sep, switch 1-oct (K-ARQ-002). Falta
  el plan de cutover formal y la lista de historia a migrar.

### P-006 — Reglas de negocio de cálculo por producto
- Prioridad: ALTA · Dominio: CAP/COL/DEV/CTB/FIS · Abierta: 2026-08-14
- Falta: base de días, saldo base, capitalización, tasas/tramos, penalizaciones, comisiones,
  amortización y **devengamiento del crédito One Click** (mencionado como cálculo faltante @00:52:12).
- Cómo cerrarla: contratos de producto, configuración en cada core, normativa. Empezar por
  inversiones/ISR y One Click.
- A quién preguntar: Producto/Contraloría (directorio en K-ORG-002/K-ORG-003).

### P-007 — Alcance, magnitud y regularización del defecto histórico de ISR (OpenFin)
- Prioridad: ALTA · Dominio: FIS · Abierta: 2026-08-14
- Por qué importa: K-FIS-001 confirma que el ISR se calculó mal "toda la vida"; PAR-352 cifra
  $2,232,566.46 sin retención. Si es sistemático e histórico → decisión de Comité (replicar vs
  regularizar con provisión). Riesgo regulatorio.
- Cómo cerrarla: extracción de retenciones ISR por periodo en OpenFin vs cálculo normativo;
  fecha exacta de la corrección; universo afectado.
- A quién preguntar: Contraloría / Fiscal / Lilian Gutiérrez (responsable PAR-352).

### P-014 — ¿El devengo/rendimiento se redondea diario o al pago? ¿Hay sesgo?
- Prioridad: ALTA · Dominio: DEV · Abierta: 2026-08-14
- Por qué importa: K-DEV-001 confirma redondeos distintos (Aurum 20→5→2, OpenFin 2). El §10 exige
  prueba de signo; un sesgo ≠ 0 es defecto severidad 1 aunque cada diferencia sea de $0.01.
- Cómo cerrarla: 30 días de devengo diario a nivel contrato de ambos cores; correr prueba de signo.
- Bloquea: la primera spec del oráculo (S-DEV-001).

### P-002 — Mapeo definitivo hablante (SPEAKER_n) → persona → rol en F-001
- Prioridad: MEDIA (baja de ALTA: hay mapeo inferido en K-ORG-003) · Dominio: ORG
- Cómo cerrarla: lista oficial de asistentes; confirmar las inferencias de K-ORG-003.

### P-004 — Linaje de datos de OpenFin (tablas/campos, llaves, precisión)
- Prioridad: MEDIA (baja de ALTA) · Dominio: DAT · Abierta: 2026-08-14 · **[PARCIAL 2026-08-15]**
- **Cerrado con F-011**: modelo de datos de OpenFin mapeado (K-DAT-002..005, `MODELO_DATOS_OPENFIN.md`):
  5 tablas, llaves, productos, tipos, fuente de la verdad.
- **Resta**: el `describe` de las 5 tablas (nombres físicos y tipos), el diagrama de tablas y el
  catálogo de las 63 operaciones (prometidos por correo). Marcar calculado-vs-ingestado (K-MIG-002).

### P-011 — Modelo de datos y queries de AurumCore (la contraparte)
- Prioridad: MEDIA (baja de ALTA) · Dominio: DAT · Abierta: 2026-08-15 · **[PARCIAL 2026-08-16]**
- **Cerrado con F-012**: los queries de Aurum revelan su modelo (K-DAT-006, esquema `aurumcore`:
  `accountholder`, `account`, `account_yield`, `iv_payment_plan`, `lc_loan_contract`, `"transaction"`…)
  y el mapeo de llaves OpenFin↔Aurum.
- **Acceso a la base `aurumcore` concedido (2026-08-16)** → inventario real de 26 tablas (K-DAT-006 v2).
- **Resta**: (a) resolver duplicados aparentes (`accountholder` vs `account_holder`, `account` vs
  `investment`, `payment_plan` vs `iv_payment_plan`); (b) el nombre real de transacciones
  (`transaction_detail` vs la query `"transaction"`) y sus columnas; (c) cómo reconstruye el tipo.
  Faltan accesos a OpenFin t-1 y Reportes Unificados (en gestión).

### P-005 — Conciliación de las cifras del propio tracking (266 vs 331; 132 vs 124)
- Prioridad: ALTA · Dominio: MIG · (sin cambios; ver F-008).

### P-008 — Algoritmo de validación de CLABE en Aurum ("de Luna")
- Prioridad: BAJA · Dominio: MOV · Abierta: 2026-08-14
- Probable dígito verificador de la CLABE (transcripción dudosa). Confirmar y replicar en el oráculo.

### P-010 — Verificación normativa de los parámetros del ISR · **CERRADA 2026-08-19** ✅
- Prioridad: ALTA · Dominio: FIS · Abierta: 2026-08-14 · **Cerrada: 2026-08-19**
- **Resolución:** los parámetros de AurumCore coinciden con la norma 2026 → [[K-FIS-004]]:
  - Tasa **0.90%** = LIF 2026 **Art. 24** (remite LISR 54/135; subió de 0.50%).
  - Exención **5 × UMA sobre saldo promedio diario** = LISR **Art. 93 fr. XX** (beneficio SOFIPO).
  - **UMA anual 42,794.64** = INEGI (DOF 9-ene-2026, vigente 1-feb-2026). Base exenta 5× = 213,973.20.
  - Retención sobre el **capital** como pago provisional (LISR 54/135); 365 días.
- **Colaterales:** cierra el residuo de C-001 (UMA vigente 1-feb → el rezago de ~9 días de feb fue real y
  menor) y refuerza H-J (el 1.45% de OpenFin contradice la tasa de ley 0.90%).
- **Residuo menor abierto:** tratamiento de **personas morales** (LISR Art. 54 las excluye de retención;
  el doc de Aurum pone exención $0 = retención completa) — verificar. Impacto bajo (SOFIPO ≈ personas físicas).

### P-016 — Motor B (validador de la transaccional diaria) · **[DESBLOQUEADA — foundation + spec, 2026-08-19]**
- Prioridad: ALTA · Dominio: MOV/DAT/MIG · Abierta: 2026-08-19 (F-021/F-022)
- Por qué importa: Finsus nos encomendó **insertar nuestro tercero independiente** en el **cruce diario
  Aurum vs OpenFin** (Sergio/"Checo" + INCO). Una de las dos corrientes centrales (NORTE §0).
- **Avance (2026-08-19):** foundation de datos establecida **con nuestros accesos** + spec escrito en
  `40_validaciones/PLAN_MOTOR_B_DIARIO.md`. Hallazgos: OF `vista_movimientos_cargos/_abonos` + `cat_tx_cuadre`
  (gemelo de AU `cat_finsus_transaction`) → **crosswalk directo por número de tipo**; 2:1/1:1 clasificable por
  patrón de cuenta. **NO** tenemos `openfin_m`/vistas `aurum_transaction_*` (independencia OK).
- **Resta (acotado):** (1) campo que liga cargo↔abono de una transferencia interna (colapso 2:1); (2) congelar
  el crosswalk 314↔348 tipos (marcar sin-correspondencia y 5xxx crédito); (3) formalizar regla cliente-vs-externo;
  (4) evaluar `cat_tx_cuadre`/vistas OF como **benchmark**; (5) acceso a **réplica**; (6) codificar el comparador.
- A quién preguntar: Sergio (diario), Abraham (OpenFin/mapeo tx), Giancarlo/Julio (día cero).

### P-015 — Validar la corrida VIVA de capitalización de interés de captación (1er cierre 31-ago-2026)
- Prioridad: ALTA · Dominio: DEV/CAP · Abierta: 2026-08-19
- Por qué importa: el interés de captación vista-ahorro (~100,058 cuentas, ~$8.5M/mes; productos
  2006/2011/2012/2013/2015/2017/2019) **se capitaliza a fin de mes** ([[K-DEV-002]] v2). En BD sólo
  existe en **historia migrada (ene–jul 2026)**; post-cutover AurumCore **aún no lo ha corrido**
  (se detiene el 31-jul; post-cutover sólo hay devengo/pago diario de inversión). El **primer cierre
  vivo es el 31-ago-2026**. Hasta esa fecha, el motor B de captación-interés es **inobservable**: no
  se puede afirmar que AurumCore calcule bien lo que OpenFin hacía cada mes.
- Riesgo si sale mal: descuadre sistemático en ~100K cuentas de ahorro, mensual, con impacto en ISR
  retenido asociado. Es el bloque de captación-interés equivalente a lo ya cerrado en inversión.
- Cómo cerrarla: (a) esperar/observar la corrida del 31-ago en `aurumcore.transaction_detail`
  (`Capitaliza Interes 31/08/2026`); (b) correr el oráculo C (saldo promedio × tasa × días, redondeos
  K-DEV-001 vista) contra B por cuenta; (c) pedir los **logs del CORE** de esa corrida
  (`Calculating with average balance`) — [[K-DEV-002]]. Bloqueado por la definición exacta de "saldo
  promedio" (P-006) y por la tasa por esquema de cada producto.
- A quién preguntar: Producto/Contraloría (tasa y saldo promedio) + equipo AurumCore (logs).

### P-013 — ¿Qué significa `transaction.origin` (FINSUS / AURUMCORE)?
- Prioridad: ALTA · Dominio: DAT/MIG · Abierta: 2026-08-16
- Por qué importa: si `origin` distingue de forma confiable la transacción **ingestada** (migrada de
  OpenFin) de la **generada por AurumCore**, resuelve el riesgo metodológico #1 (K-MIG-002): permite
  comparar sólo lo que Aurum realmente calculó, no lo ingestado. Es potencialmente la columna más
  valiosa del modelo.
- Cómo cerrarla: confirmar semántica con el equipo de Aurum; perfilar la distribución de `origin`
  por día y contrastar con las ventanas de ingesta conocidas.

### P-012 — ¿Cuál esquema de AurumCore es la fuente de verdad (`aurumcore` vs `public`)?
- Prioridad: ALTA · Dominio: DAT · Abierta: 2026-08-16
- Por qué importa: la base tiene dos esquemas con tablas del mismo nombre y **estructura distinta**
  (`public.account` 4 cols vs `aurumcore.account` rica; `public.investment` con floats). Leer el
  esquema equivocado corrompería toda la conciliación en silencio.
- Entendido (inferido): la fuente es **`aurumcore.*`** (es lo que usan sus queries F-012); `public`
  parece un subconjunto derivado/staging. **Falta confirmación de Finsus.**
- Cómo cerrarla: mensaje enviado (`90_bitacora/2026-08-16_mensaje_esquemas_aurum.md`) + `\d+ aurumcore.<tabla>`.

### P-009 — Cifras reales del "día cero" — **[CERRADA 2026-08-16]**
- Cerrada con F-013 (árbol día cero 02-03 ago): las cifras narradas en F-001 se confirman con datos
  reales (p.ej. 18,599 inversiones). Detalle en `ANALISIS_ARBOLES.md`.
