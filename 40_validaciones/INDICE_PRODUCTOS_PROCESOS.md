# Índice maestro de productos y procesos — AurumCore vs Oráculo C

> **Propósito.** Mapa único que lleva, por producto/proceso, a: descripción · condiciones · fórmula(s) ·
> tablas/campos · trazas de log · **fuente oficial (doc + página)** · **módulo/estado en nuestro Oráculo C** ·
> **desviación conocida**. Construido leyendo a conciencia la documentación oficial de AurumCore + los queries
> y docs de Finsus (sin inferir donde hay doc). Base para la **fase de comparación** (¿está documentado? ¿lo
> corroboramos o hay desviación? ¿en qué consiste?).
>
> Estado de la lectura: **5/5 lectores integrados** (rendimientos/GAT/ISR · créditos · IFRS9+GAP · queries+Linko · ciclos transaccionales).
> Actualizado: 2026-08-23.

## Leyenda de fuentes (docs oficiales AurumCore, carpeta `landing/aurum_docs/` y `landing/`)
| Código | Documento | Nota |
|---|---|---|
| **D-REN** | GTM-Pago de Rendimientos (190826) / AurumCore- Cálculo de Pago de Rendimientos (v1.0, 7-ago-2026) | vista, plazo, ISR |
| **D-SPM** | GTM-Saldo Promedio - Módulo Cuentas (170826) | saldo promedio (leído directo) |
| **D-GAT** | GTM-Cálculo de GAT (Cuentas e Inversiones) (180826) | GAT nominal/real |
| **D-CRE** | GTM-Cálculos Motor de créditos (v1.2, 18-ago-2026) / AurumCore_ Cálculo de Intereses de Créditos (v1.0) | crédito, IVA, comisiones, CAT |
| **D-IFR** | Módulo IFRS 9 - Reglas de negocio (v1.0, 23-ene-2026) + Mapa Guía IFRS 9 | reservas, EI/PI/SP, stages |
| **D-REG** | Módulo IFRS 9 - Reportes Regulatorios (v1.1, 23-ene-2026) | reportes 451-457, 417, 419 |
| **D-GAP** | GAP_Analysis_Motores + Linko - AurumCore (observaciones) | 5 motores faltantes |
| **D-QRY** | Queries para data transaccional live captación / pagos a créditos (Finsus) | queries live A vs B |
| **D-CIC** | GTM-Ciclos Transaccionales (v1.0, 26-jun-2026) | ciclos/movimientos, límites, conciliación |

## Leyenda estado Oráculo C
✅ implementado y validado en BD · ◐ implementado, validación parcial/bloqueada · ○ no implementado · ⚠ desviación/contradicción abierta

---

# 1. CAPTACIÓN — Rendimientos y GAT

## 1.1 Rendimiento CUENTA A LA VISTA
- **Descripción.** Rendimiento sobre el **saldo promedio mensual (SPM)** de la cuenta. → D-REN p.2-3, D-SPM.
- **Condiciones/elegibilidad.** Cuenta `ACTIVE`; cliente `ACTIVE` o `SUSPENDED`; existe esquema de rendimientos y (tasa>0% **o** bandera exento_retención=falso). → D-REN p.3.
- **Fórmula.** `Rendimiento = Round2( Trunc20( Trunc20((SPM×Tasa)/100) ÷ DíasAño ) × DíasPeriodo )`. Dos truncamientos a 20 dec; `Round2` final ("redondeo normal"). Base de días = la del esquema (ej. 360). → D-REN p.3.
- **Ejemplo del doc.** SPM 5,000; tasa 7%; 360; julio 31 días → **30.14**. → D-REN p.4.
- **Momento.** Cada día 1° se procesa el mes inmediato anterior (00:00 a 23:59 del último día). Ventana desde fecha del primer depósito si cae en el mes, si no desde el día 1°. → D-REN p.3.
- **Tablas/campos.** Solo "esquema de rendimientos" (config). SPM: ver 1.3.
- **Oráculo C.** ✅ `oraculo_rendimientos.rendimiento_vista(spm,tasa,dias,dias_anio)` — autoprueba 30.14 OK. Pieza [[K-DEV-002]] v4, [[K-DEV-001]] (redondeo). Spec en S-DEV (pendiente formal).
- **Desviación conocida.** ⚠ El **modo de `Round2` no está definido** en el doc para vista (a diferencia de plazo, que sí es half_even). Asumimos half_up. Base 360 vs 365: ver §2.1.

## 1.2 Rendimiento INVERSIÓN / PLAZO FIJO
- **Descripción.** Base = capital de apertura `account.iv_initial_amount`. → D-REN p.4.
- **Condiciones.** Cuenta `ACTIVE`; `iv_account_state` en `ACTIVE` o `PRECANCELLED`; cliente `ACTIVE`/`SUSPENDED`. → D-REN p.4.
- **Fórmula.** `Rendimiento = RoundHalfEven2( Ceil10( Ceil10((Capital×Tasa)/100) ÷ DíasAño ) × DíasTranscurridos )`. Dos redondeos **hacia arriba** a 10 dec; `RoundHalfEven2` final. → D-REN p.5.
- **Ejemplo del doc.** 1,000 por 100 días @5%, 360 → **13.89**. → D-REN p.5.
- **Días.** "días transcurridos desde el plazo anterior o fecha de creación si es el primero/único del plan de pagos". → D-REN p.4.
- **Tablas/campos.** `account.iv_initial_amount`, `iv_account_state`. Tasa/DíasAño del misceláneo del producto. Plan de pagos: `aurum_iv_payment_plan.sql`.
- **Oráculo C.** ✅ `oraculo_rendimientos.rendimiento_plazo(...)` — autoprueba 13.89 OK. Validado a volumen: `validate_plazo_origin.py` = **530,195 periodos, 100.00%**. Pieza [[K-DEV-003]].
- **Desviación conocida.** Ninguna material (100% a volumen).

## 1.3 SALDO PROMEDIO (transversal — insumo de 1.1 y del ISR)
- **Descripción.** **DOS saldos promedio distintos:** (a) de **consulta** = `account.average_balance_amount` (rolling, en BD); (b) para **pago de rendimiento** = calculado en el proceso, **puede diferir**, y **NO existe en BD** — solo en logs. → D-SPM p.7.
- **Fórmula (rendimiento).** `SPM = (saldo_cuenta × difference_of_days + acumulado) / elapsed_days`. `difference_of_days` = conteo exclusivo (multiplicador); `elapsed_days` = conteo inclusivo desde creación (divisor). → D-SPM p.8-9.
- **Ejemplo del doc.** `(30,000×8 + 20,000)/9 = 28,888.88`; luego `28,888.88 × 0.1 × 9/360 = 72.22`. → D-SPM p.9.
- **Trazas de log (validación oficial).** `Calculating with average balance` (da difference_of_days + ELAPSED DAYS); `Calculating yield amount Using RATE..., DaysOfYear[360|365]` en `trace.log`. → D-SPM p.8, p.10.
- **Tablas/campos.** `account.average_balance_amount` (SOLO consulta), `average_balance_last_updated`; base en esquema/`iv_products.days_in_year`.
- **Oráculo C.** ◐ `oraculo_rendimientos.saldo_promedio_rendimiento(...)` — autoprueba 28,888.89 OK. Validación viva **bloqueada**: requiere la traza `Calculating with average balance` (barrido con string exacto, VPN logs). Pieza [[K-DEV-002]] v4.
- **Desviación conocida.** ⚠ NO usar `average_balance_amount` para reconstruir el rendimiento (el doc dice que difiere del de consulta). SPM **no se define cómo se computa** en D-REN (solo en D-SPM).

## 1.4 GAT (Ganancia Anual Total) — cuentas e inversiones
- **Descripción.** Metodología GAT nominal y real; validado contra la calculadora GAT de Banxico. → D-GAT p.2.
- **Fórmula cuentas (vista/ahorro, tipo `ACCOUNT`).** `m = DíasAño/DíasPeriodo (360/30=12)`; `GAT Nominal% = Round8((1+Round10(tasa/100)/m)^m − 1)×100`; `GAT Real% = Round2((Round10(GATnom_dec num)/(1+inflación_dec) − 1)×100)`. Ej: tasa 10%, infl 4.18% → **Nominal 10.471307%, Real 6.04%**. → D-GAT p.3-4.
- **Fórmula inversiones (`INVESTMENT_ACCOUNT`).** `m = Round10(DíasAño/DíasInversión)`; `GAT Nom% = Round16(((Inicial+Interés)/Inicial)^m − 1)×100`; GAT Real análoga. Ej: 1,000 a 90 días, interés 200 → **Nominal 107.36%, Real 99.04%**. → D-GAT p.5-7.
- **Condiciones.** Tiene esquema de rendimientos; tipo `ACCOUNT` (cuentas) / `INVESTMENT_ACCOUNT` (inversiones); ejemplos "sin comisiones". → D-GAT p.2, p.5.
- **Oráculo C.** ✅ **Motor validado.** `oraculo_gat.py` (`gat_cuenta`, `gat_inversion`) autoprueba 2/2 EXACTA vs doc + **reproduce exacto** el `account.nominal_cgat` de Aurum (prueba no-circular: idéntico por plazo sin importar monto — term7=10.42 ×126K, term30=7.43, term90=10.13). GAT se guarda **solo en INVESTMENT_ACCOUNT** (689,479). Inflación = `cat_financial_variables.INFLATIONMXN` punto-en-tiempo (3.79→3.84→3.95%).
- **Pendiente (data-sourcing, no motor).** Cruce 1-a-1 a volumen requiere la **tabla de tramos de tasa de inversión** (63 tramos/plazo); el `iv_payment_plan.interest_amount` posteado difiere del proyectado en originación. → SOL menor.

---

# 2. FISCAL — Retención de ISR

## 2.1 ISR al pago de rendimientos
- **Descripción.** ISR se retiene **solo al pagar rendimientos** (no en devengo), sobre la parte gravable del saldo total del cliente, prorrateado por cuenta. → D-REN p.5.
- **Saldo base.** Saldo total = Σ (vista: SPM) + (plazo: capital inicial). Cuenta con bandera "exento de retención" aporta $0. → D-REN p.5.
- **Parte exenta.** `UMA × yield.tax.exempt.uma.amount` (=5) ≈ 213,973.20 (ago-2026); personas morales = $0.00. → D-REN p.5.
- **Fórmula (doc).** `Base Gravable = Saldo Total − Monto Exento`; `ISR Diario = Trunc5(Base Gravable × Trunc20(TasaISRAnual/(100×DíasAño)))`; `ISR Retenido = Round2(Trunc20(ISR Diario × DíasPeriodo) × Proporción Cuenta)`. Días año = `tax.days.year` = **365**. → D-REN p.6.
- **Ejemplo del doc.** Cuenta 30,000; saldo total 513,973.2; tasa 0.9%; 365 → **22.93**. → D-REN p.6-7.
- **Config/tablas.** `system_configuration`: `yield.tax.exempt.uma.amount`, `tax.days.year`; `UMAMXN` (variable financiera); `account_tax` (concepto 'ISR BASE'). Extracción: `aurum_isr_config.sql`, `aurum_isr_al_pago.sql`, `aurum_saldo_base_isr.sql`.
- **Oráculo C.** ✅/◐ `entrega_finsus/oraculo_isr.py` + `fase1_isr_*`, `isr_live_nativo.py`. Validado en BD histórica (C=B=765.75). ISR-vivo nativo **bloqueado** por saldo base punto-en-tiempo (logs). Piezas [[K-FIS-002]] v3, [[K-FIS-004]] (norma).
- **✅ C-002 RESUELTA (no es desviación abierta).** El doc tenía un **error de redacción**: la fórmula dice `÷ Saldo Total` pero el **ejemplo** dividía entre la base gravable. **Finsus corroboró que fue error de su documentación**; lo correcto es **`÷ saldo_total`** (que es lo que hace la BD real y nuestro oráculo, C=B verificado). Residuo cosmético: el ejemplo del doc sigue sin corregir. → cerrado. Ver [[K-FIS-002]] §C-002, CONTRADICCIONES C-002.

---

# 3. CRÉDITO — Interés, IVA, comisiones, CAT

## 3.1 Interés ORDINARIO
- **Descripción.** Costo por uso del dinero; se **devenga y provisiona DIARIAMENTE** desde la activación (dispersión). → D-CRE p.3.
- **Base.** **Saldo Insoluto del Capital** (deuda pendiente, sin intereses). → D-CRE p.3 (cita: "su base de cálculo es siempre el Saldo Insoluto del Capital").
- **Fórmula.** `Interés Ordinario = C × (i/100) × (t/DíasAño)`; C=saldo insoluto, i=tasa anual, t=días, DíasAño = 360 (Comercial) / 365-366 (Natural). → D-CRE p.3.
- **Ejemplo del doc.** 50,000 @15% Comercial(360) 1 día → **20.83**. → D-CRE p.5.
- **Tablas/campos.** `lc_loan_contract` (loan_amount, ordinary_interest_rate, calendar_type=1→360, moratorium_interest_rate); `lc_finantial_data_stage/lc_finantial_data`.`capital` (saldo insoluto, **firmado negativo**); `credits-closing-trans` log (provisión diaria alta precisión). Días: log `CreditAmortizationChargeServiceImpl.java:844 - Days N` (= período amortización).
- **Oráculo C.** ✅ `oraculo_credito.interes_ordinario_dia(capital,tasa,360)`. **Validado vivo: 96.8% exacto a 1e-8** vs `capital` DB, 0/4,091 mismatch de tasa (feed 08-20). Pieza [[K-COL-001]].
- **Desviación conocida.** Residual 3% = **linaje** (3 tablas de capital discrepan punto-en-tiempo, P-019), NO defecto de motor.

## 3.2 Interés MORATORIO
- **Descripción.** Cargo por incumplimiento; provisión **diaria** desde el día posterior al vencimiento. → D-CRE p.3.
- **Base.** **Capital Vencido No Pagado** (porción de capital de la cuota exigible), NO el saldo insoluto total. → D-CRE p.3.
- **Fórmula.** `Interés Moratorio = C_vencido × (i_mor/100) × (t_atraso/DíasAño)`. → D-CRE p.3.
- **Ejemplo del doc.** Cap. vencido 500 @36% Comercial 1 día → **0.50**. → D-CRE p.6.
- **Tablas/campos.** `lc_finantial_data(_stage).capital_venc`, `mora_days`; `lc_loan_contract.moratorium_interest_rate`; feed `credits-closing-trans` (MORATORY PROVISIONING). Log `InterestMoraDays db[N]`.
- **Oráculo C.** ✅ `oraculo_credito.interes_moratorio_dia(...)`. **Validado a precisión completa: 81.1% exacto a 1e-8** (95.7% ≤$0.01) vs `lc_finantial_data.capital_venc`, días=1, 0 mismatch de tasa.
- **Desviación conocida.** Ninguna (P-020 **cerrada**: la asimetría era artefacto de comparación —moratorio redondeado vs feed sin redondear—; el motor es exacto). Residual sub-centavo = snapshot de `capital_venc` (clase P-019).

## 3.3 IVA sobre intereses
- **Fórmula.** `IVA = Interés × (TasaIVA/100)`; 16 decimales internos, **Round2 Half Up**; $0 si el producto no grava. → D-CRE p.4.
- **Oráculo C.** ✅ `oraculo_credito.iva_interes(interes,tasa_iva)`.
- **Desviación.** — (tasa IVA nunca dada numéricamente en el doc).

## 3.4 Seguros y comisiones
- **Reglas.** Monto Fijo o Porcentaje. Base: no financiado cobro único = monto autorizado; no financiado recurrente = **saldo insoluto** (se actualiza cada periodo); financiado = monto autorizado total, se descuenta al activar. IVA sobre el cargo. → D-CRE p.4-5.
- **Oráculo C.** ○ No implementado.

## 3.5 Precisión / ajuste a fin de periodo
- **Regla.** Provisión diaria a **15 decimales** internos, 2 al cobro. Al fin de periodo hace **cierre/ajuste** para cuadrar la suma diaria al monto pactado. **NO corrige retroactivamente** datos migrados incorrectos: sobrescribe hasta fin de periodo y genera el cargo oficial. → D-CRE p.4.
- **Relevancia.** Explica el "tope al período" que confirmamos en logs (crédito días = período de amortización). Cifras diarias intermedias de migrados pueden no reconciliar hasta el cierre — **por diseño**.

## 3.6 CAT (Costo Anual Total)
- **Regla general.** `Σ A_j/(1+i)^t_j = Σ B_k/(1+i)^s_k` (Circular 21/2009 Banxico). Incluye capital, interés ordinario, comisiones/seguros obligatorios; **excluye** IVA, moratorios, penalizaciones, prepagos voluntarios. → D-CRE p.6-7.
- **One Click.** `CAT = [(Pago sin IVA / Monto recibido)^(360/días) − 1]×100`; interés a 17 dec. Ej 1 día: CAT 289,458,538.2% (esperado, no error). → D-CRE p.8-9.
- **Francesa.** Cuota `= Capital × [tasa_mensual/(1−(1+tasa_mensual)^−n)]`; tasa_mensual = anual/12; ajuste de centavos en último periodo. Ej 10,000 @22% 12m → cuota 935.94, CAT 34.5%. → D-CRE p.9-11.
- **Oráculo C.** ○ No implementado (CAT). One Click de crédito: existencia validada [[K-COL-001]]; cálculo de interés vía §3.1.
- **Desviación.** — (amortización Americana/Italiana/Alemana: listadas sin fórmula en el doc).

---

# 4. IFRS 9 / RESERVAS (crédito) — D-IFR + D-REG

## 4.1 Clasificación por etapas (stages)
- **Regla.** Etapa 1: 0-30 días mora (pérdida esperada 12m); Etapa 2: 31-89 (vida completa); Etapa 3: ≥90 (incumplimiento). → D-IFR p.21 Tabla 4.
- **Tablas/campos.** `lc_risk_stage` (config; 3 filas = E1 0-30, E2 31-89, E3 90-10000). Campo reporte "ETAPA DE RIESGO DE CRÉDITO".
- **Oráculo C.** ✅ `oraculo_ifrs9.etapa()` — **C = config de Aurum `lc_risk_stage`** (exacto).

## 4.2 Reserva Consumo / Microcrédito / Vivienda (% directo por mora)
- **Regla.** `Reserva = Reserva capital + Reserva intereses = Exigibles × %`. % por días de mora y zona marginada (Tabla 1 Consumo, Tabla 3 Microcrédito, Tabla 2 Vivienda). → D-IFR p.7-8, p.18-21.
- **Oráculo C.** ✅ `oraculo_ifrs9.pct_consumo/pct_microcredito/pct_vivienda` — **C = config de Aurum `lc_reserve_ifrs` (37/37 exacto)** = doc. Autoprueba 14/14.
- **Aplicación (parcial).** `reserva_cap = base × %`. **Finsus cartera = CONSUMO.** Base = `capital_venc` para E3 fully-vencido (65% a volumen exacto). Residual = definición de **"capital exigible"** (porción exigible vs saldo completo en amortizando) → SOL. `reserva_int` análoga sobre intereses exigibles.

## 4.3 Reserva Comercial (modelo EI × PI × SP)
- **EI (Exposición al Incumplimiento).** E1/E2: capital insoluto + intereses exigibles al cierre; E3: intereses exigibles **solo hasta día 89**. `EI = EI_capital + EI_intereses`. → D-IFR p.9-10.
- **PI (Probabilidad de Incumplimiento).** Por tipo acreditado/persona/actividad; con avales solidarios 100% se toma el **PI más bajo** entre acreditado y avales. Tabla de valores NO en el doc. → D-IFR p.10.
- **SP (Severidad).** Sin garantía E1/E2: Ent.Fed./Mpio/Fin=45%, PM/PF empresarial=55%; E3 ajusta por meses en E3 (Tabla 5, hasta 100%). Garantías financieras: `EI*=Max(0,EI−C×(1−Hc))`, `SP*=SP×(EI*/EI)`. Garantías no financieras: coeficientes C*/C**/SP** (Tabla 6), `SP total = [Σ(SPᵢ×EIᵢ_cub)+(SP_base×EI_exp)]/EI_total`. → D-IFR p.10-13, p.22-23.
- **Reserva.** E1 o E3: `Reserva = EI×PI×SP`. E2 (vida completa): `Reserva = (PI×SP×EI)/(r+PI)×[1−((1−PI)^n/(1+r)^n)]`, r=tasa anual (si 0 usar 0.00001%), `n=max(días_remanentes/365.25, 1)`; final `= Max(vida completa, PI×SP×EI)`. → D-IFR p.13-15.
- **Oráculo C.** ◐ `oraculo_ifrs9.ei/sp_sin_garantia/reserva_comercial` implementado (SP Tabla 5 = doc; vida completa E2). **PI es parámetro** (el doc no trae tabla numérica de PI → SOL). Menos relevante para Finsus (cartera = CONSUMO, usa % directo §4.2).
- **⚠ Ambigüedades del doc** (ver extracción D): dos cortes de etapa distintos (EI usa 1-2 vs 3; reserva usa 1/3 vs 2); precedencia de paréntesis en vida completa a verificar; PI sin tabla numérica.

## 4.4 Reportes regulatorios (mensuales)
| Reporte | Qué | Decimales/notas |
|---|---|---|
| 451 | Alta de créditos | datos de originación |
| 452 | Seguimiento comercial/consumo/vivienda | **el más rico**: devengo, tasas, mora, IDNC al traspaso E3, IDNC en cuentas de orden, castigos/quitas=0, FREC.REVISIÓN TASA=0 (tasa fija) |
| 454 | Reservas consumo/vivienda/microcrédito | zona marginada 1/2; % 6 dec |
| 455 | Reservas comerciales | PI 8 dec; sustitución PI garante 1/2 |
| 456 | Severidad comercial (excl. microcrédito) | SP ajustada 6 dec; Hfx=0 |
| 457 | PI comercial | PI 2 dec; SIC 700/750; SCIAN 1/2/3 |
| 417 | Calificación de cartera | catálogo 27 subtipos de cartera |
| 419 | Movimientos en estimación preventiva | castigos/quitas/venta cartera = **fuera de alcance** |
→ D-REG p.3-35. **Oráculo C.** ○ No implementado.

---

# 5. GAPS — 5 motores faltantes (D-GAP / Linko)

| # | Motor faltante | Brecha (textual) | Corrobora en fuente | Nuestra pieza |
|---|---|---|---|---|
| A | Write-offs (quitas/condonaciones/castigos/venta cartera) | "procesos externos a la plataforma... información por default" | R419 p.34-35, R452 p.21 | — |
| B | Suspensión de devengo / IDNC (E3) | "reporta el saldo pero no documenta el motor de cancelación automática del devengo" | R452 IDNC campos; EI corta al día 89 | [[K-REG-001]] |
| C | Cuota IPAB/Prosofipo (fondo protección) | "no incluye este cálculo en sus motores de captación"; se calcula al generar **reporte 841** (campos 46-47), cobertura = min(saldo, 25,000 UDIS) | R04-0841 §III | [[K-REG-002]] |
| D | Ajuste a tasa variable (TIIE/CETES) | "opera sobre tasas fijas o revisiones con frecuencia 0" | R452 p.19 FREC=0 | — |
| E | Revaluación cambiaria / UDIS | "no existe motor de revaluación diaria contable... frente al FIX" | MONEDA=0, Hfx=0 | — |
- **Cuentas contables IFRS observadas (Linko, screenshots — confianza media):** `RESERVA_CAP_ACTIVO/RESULT`, `RESERVA_INT_ACTIVO/RESULT`, `CAPITAL`, `CAPITAL_VENC`, `IO`/`IO_VENC`/`IO_IMPUESTO`, `IDNC`, `IM`/`IM_IMPUESTO`, `IODNC_ECO_CA/AB`, `IMDNC_ECO_CA/AB`, `SALDO_FAVOR` (= columnas de `lc_finantial_data`). Pólizas: "Quita 5004", "Condonación 5004", "Castigo 5004".

---

# 6. TRANSACCIONAL — Ciclos Transaccionales (D-CIC, v1.0 26-jun-2026, 20 pág)

## 6.1 Ciclos / tipos de transacción documentados (por API/canal)
| Ciclo | Canal / componente | Endpoint | Estados (nodos End) | Efecto en saldo | Pág |
|---|---|---|---|---|---|
| **SPEI IN** (cobranza) | STP · `ms-stp`,`core` | `/cobranza` | Rejected · Confirmed · Refund | actualiza saldo (entrada) | p.2 |
| **SPEI OUT** (domestic payment) | STP · `ms-payments`,`ms-stp` | `/domestic-payments` | Rejected · Confirmed · Devolución · Refund | valida saldo, liquida (salida); espera 2 min callback | p.3 |
| **P2P** (entre usuarios) | `ms-payments` | `/domestic-payments` | Rejected · Confirmed | atómico: debita origen + acredita destino | p.5-6 |
| **Pomelo compra/retiro ATM** | `ms-pomelo-authorizer` | `/authorizations/debit` | End · Confirmed | Cuenta Monedero; clearing+settlement | p.4 |
| **Authorizer autorizar** (tercero) | `ms-authorizer` | `/payment/authorize` | Authorize · Rejected | **retiene** saldo (no liquida) | p.4 |
| **Authorizer confirmar** | `ms-authorizer` | `/payment/confirm` | Confirm · Rejected | **libera** saldo → confirmada | p.5 |
| **Portal Admin ajuste dual** | `ms-portal-admin` | `/portal/balance/adjustment/authorize`+`/confirm` | Autorizada · Confirmada · fallo | retiene origen → libera "por confirmar" + abona destino | p.6 |
| **Tarjetas: Reversal** | Pomelo/red | `adjustments/credit` | AUTHORIZED→REVERSED | libera fondos (full amount) | p.8 |
| **Tarjetas: Refund** | Pomelo/red | (Authorizer) | original→CONFIRMED; devolución nace AUTHORIZED | nueva tx de devolución | p.9 |
| **Tarjetas: Reject/Cancel** | Pomelo/red | — | REJECT→CANCELLED | devuelve fondos; en reporte = `INTERNAL TRANSFER` "Cancelacion de: <id>" | p.7-8 |
| **Settlement** | Pomelo cron | — | CONFIRMED | ajuste 0 pesos; clearing 6×/día, 1-7 días | p.9 |

- **Máquina de estados AurumCore (observada):** `AUTHORIZED → CONFIRMED / CANCELLED / REVERSED`. Estatus Pomelo: `APPROVED/REJECTED/HELD`. Campos `transaction`: `external_id`, `transaction_id`, `state`, `gross_amount`, `original_transaction_id`, `origin`. `transaction_detail`: ver §7.3.
- **`INTERNAL TRANSFER`** (tipo en reporte) = firma de cancelaciones y **también del posteo de ISR** (K-FIS-002). Aparece sin ciclo propio en el doc.

## 6.2 Conciliación (Cron Pomelo) — reglas de match
Busca `TRANSACTION_ID` en `transaction.external_id`; clasifica por `TRANSACTION_TYPE` (BALANCE_INQUIRY→omite; PURCHASE/WITHDRAWAL, REFUND, REVERSAL_*). Match: existencia + `LOCAL_CURRENCY=MXN` + `LOCAL_AMOUNT=gross_amount` + `STATUS`/`state`. REFUND crea tx de devolución vía Authorizer (source `100-2002-140` "Operativa de Pomelo" → target cuenta usuario). Códigos ERROR ID 01-17. → D-CIC p.10.

## 6.3 Matriz de afectación (LÍMITES/acumulados, NO contable) — p.18-19
Por transacción: afecta monto entrada (diario/mensual) · salida · **saldo promedio**. Ejemplos: SPEI IN → entrada Sí, saldo Sí; SPEI OUT/P2P/PURCHASE/WITHDRAWAL → salida Sí, saldo Sí; **Authorizer Authorize → No/No/No** (solo retiene). Límites en **UDIS** (`Límite = nº UDIS × valor UDI`, Catálogo Variables Financieras). Jerarquía `Cuenta→Esquema Cuenta→Esquema Límites→Reglas`. Control **preventivo** (rechaza antes de aplicar). → D-CIC p.11-19.

## 6.4 Nuestro lado y desviaciones
- **Oráculo/validación C.** `motor_b_diario.py` (A vs B diario, clasifica PEER 2:1 / UNI 1:1), `contable_bc.py` (B1 doble partida $0.00, B3/B4 amarre). Piezas [[K-MOV-004]], [[K-MOV-005]] (tipos observados), [[K-CTB-001]] (matriz de amarre), [[K-MOV-001]] (OpenFin no atómico vs Aurum atómico — confirmado: P2P/ajustes son atómicos débito+crédito).
- **⚠ GAP del doc.** El doc **NO mapea tipo_movimiento → cuenta contable de mayor** (sin pólizas, sin cargo↔abono, sin naturaleza). La "Matriz de afectación transaccional" por tipo está **"Por incorporar" (vacía)**. Tampoco define las 3 capas de saldo (contable/disponible/retenido) formalmente, aunque sí usa retención/liberación. → Nuestra matriz de amarre [[K-CTB-001]] se construyó de datos observados, NO de doc oficial → **pedir a Finsus el catálogo tipo_movimiento→cuenta contable** (SOL nuevo).

---

# 7. DATOS / QUERIES LIVE — D-QRY

## 7.1 Query captación live (A vs B)
- **AurumCore.** `aurumcore.transaction` (t) + `transaction_detail` (td) + `accountholder` (ah1/ah2) + `account` (a1/a2); excluye dispersiones (`lc_loan_dispersion`, contratos producto '5004'/'1101') y pagos de crédito (cuentas de `lc_loan_contract.account_id/subaccount_id/subaccount_2nd_id`), ambos con `NOT EXISTS`. Ventana `t.created` parametrizada. → D-QRY captación p.1-3.
- **OpenFin.** `openfin_m.aurum_transaction_final_complete` (vista consolidada, host 10.10.164.25), filtra `last_updated`. Empareja por mismos nombres de columna. → D-QRY p.4.
- **Nuestro lado.** `motor_b_diario.py` (A vs B diario); `extraccion/*.sql`. Acceso a `openfin_m` = **SOL-001** (grant pendiente).
- **⚠ Nota P-013.** En estos queries oficiales `origin is null` aparece **solo en las subconsultas de exclusión** de crédito, no en el WHERE principal de captación → revisar si `origin is null` es realmente el delimitador "live" o solo un criterio de exclusión. Campo temporal A=`created` vs B=`last_updated` (desalineación posible).

## 7.2 Query pagos a crédito live (A vs B)
- **AurumCore.** `lc_loan_charge` (charge_type in 'VNT'/'MORA', status in 1,3, `origin_transaction_id`) + `transaction` + `lc_loan_contract` (3 UUID producto: normal/black/white) + `accountholder`; `trans.created::date = CURRENT_DATE`. → D-QRY pagos p.1.
- **OpenFin.** `detalle_auxiliar` + `deudores`; `pago = abono + montoio + montoim + montoimp`; `contract_number = concat_ws('-',idsucaux,idproducto,idauxiliar)`; `idproducto=5004`. → D-QRY pagos p.2.
- **Nuestro lado.** `oraculo_credito.py`; validación crédito §3.1-3.2.

## 7.3 Tablas núcleo AurumCore (semántica de queries)
`transaction`(transaction_id, payer_id/payee_id→accountholder, payer_account_id/payee_account_id→account, created, gross_amount, origin) · `transaction_detail`(transaction_number, source_accounting_account, alfanumeric_reference, credit/debit_amount, source/target_concept) · `lc_loan_contract`(id, contract_number, lc_product_id, account_id, subaccount_id, subaccount_2nd_id) · `lc_loan_charge`(charge_type VNT/MORA, status 1/3, origin_transaction_id) · `lc_loan_dispersion`. Pieza [[K-DAT-006]]. Catálogos por confirmar con Finsus: `lc_loan_charge.status` 1/3, valores de `origin`.

---

## Desviaciones/contradicciones ya detectadas (insumo de la fase de comparación)
| # | Dónde | Consiste en |
|---|---|---|
| ~~C-002~~ **CERRADA** | ISR §2.1 | Error de redacción del doc (ejemplo ÷base_gravable). **Finsus corroboró**; correcto = ÷saldo_total (BD=C). No es desviación de motor. |
| P-019 | Crédito ord §3.1 | 3 tablas de `capital` discrepan punto-en-tiempo (linaje, no motor). |
| ~~P-020~~ **CERRADA** | Crédito mor §3.2 | Falsa alarma: era artefacto de comparación (redondeo). Moratorio exacto a 1e-8 (81.1%), base=capital_venc, días=1. |
| — | Rendim. vista §1.1 | Modo de `Round2` no definido en doc (sí en plazo). |
| — | Saldo prom §1.3 | Dos SPM distintos (consulta≠rendimiento); rendimiento solo en logs. |
| — | Ciclos §6.4 | Doc NO mapea tipo_movimiento→cuenta contable; matriz de tipos "por incorporar". |
| — | IFRS §4.3 | Dos cortes de etapa (EI 1-2/3 vs reserva 1-3/2); PI sin tabla numérica; precedencia vida completa a verificar. |
| 5 GAPs | §5 | Write-offs, suspensión devengo/IDNC, Prosofipo, tasa variable, revaluación cambiaria: fuera de motor. |

## Pendientes de este índice
- [ ] Registrar D-* en `REGISTRO_FUENTES.md` con hash/fecha (fuentes oficiales nuevas).
- [ ] **Fase de comparación** (lo que pediste): por cada motor/métrica evaluado → (1) ¿está en doc? (2) ¿corroboramos o desviación? (3) ¿en qué consiste la desviación?
