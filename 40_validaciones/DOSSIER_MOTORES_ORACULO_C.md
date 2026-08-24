# Dossier de motores — Oráculo C (base de conocimiento del agente conversacional)

> Fuente de verdad, data-rich, por motor: **propósito · fórmula exacta · contra qué se valida (doc/config/
> inferencia) · insumos (tablas/campos) · resultado (% match, cifra) · no-conformes (por qué) · estado de cierre**.
> Es el conocimiento que el **agente conversacional del auditor** usa para explicar todo. Complementa
> `INDICE_PRODUCTOS_PROCESOS.md` (índice/fuentes) y `COMPARACION_C_vs_DOC.md` (comparación).
> Convención: **C** = oráculo independiente (nuestro), **B** = AurumCore, **A** = OpenFin. Corte 2026-08-23.

## Cómo leer los "contra qué se valida"
- **doc**: fórmula/parámetro consta en un GTM oficial (con página).
- **config**: el valor consta en una tabla de configuración de la propia BD de Aurum (validación más fuerte: C = config real).
- **norma**: sustento legal (LISR, CNBV, Banxico).
- **inferencia**: dedujimos la mecánica de los datos (marcado explícito; se pide confirmación en SOL).

## Estados
✅ validado · ◐ parcial/mecánica confirmada · 🔒 bloqueado (dato/tiempo) · ⚪ fórmula lista sin cruce

---

# 1. Rendimiento — cuenta a la VISTA  (ref doc 2.1.1)
- **Propósito.** Interés mensual que gana una cuenta a la vista sobre su saldo promedio.
- **Fórmula (doc GTM-Pago de Rendimientos p.3):**
  `Rendimiento = Round2( Trunc20( Trunc20((SPM × Tasa)/100) ÷ DíasAño ) × DíasPeriodo )`
  Ejemplo del doc: SPM 5,000; tasa 7%; 360; 31 días → **30.14**.
- **Valida contra:** doc. **Insumos:** esquema de rendimientos (tasa, días año); SPM (ver §3).
- **Oráculo:** `oraculo_rendimientos.rendimiento_vista(spm, tasa, dias, dias_anio)` — autoprueba 30.14 ✓.
- **Estado:** 🔒 **bloqueado por TIEMPO.** La vista capitaliza **mensual (día 1°)**; la 1ª corrida viva post-cutover es el **31-ago**. La traza no existe aún (confirmado en logs).
- **No-conformes:** N/A todavía (sin corrida). Riesgo latente: el doc no define el modo del `Round2` (posible ±centavo).

# 2. Rendimiento — INVERSIÓN a plazo fijo  (ref doc 2.1.2)
- **Propósito.** Rendimiento de una inversión a plazo sobre el capital de apertura.
- **Fórmula (doc p.5):**
  `Rendimiento = RoundHalfEven2( Ceil10( Ceil10((Capital × Tasa)/100) ÷ DíasAño ) × DíasTranscurridos )`
  Ejemplo del doc: 1,000 a 100 días @5%, 360 → **13.89**.
- **Valida contra:** doc. **Insumos:** `account.iv_initial_amount`, tasa/días del misceláneo, plan de pagos (`iv_payment_plan`).
- **Oráculo:** `oraculo_rendimientos.rendimiento_plazo(...)` — autoprueba 13.89 ✓.
- **Resultado:** ✅ **100.00%** — `validate_plazo_origin.py`: **0 violaciones en 530,195 periodos** (157,999 cuentas). Es el motor más sólido.
- **No-conformes:** 0.

# 3. Saldo promedio (SPM) — insumo de vista e ISR  (ref doc 2.1.3)
- **Propósito.** El saldo promedio con el que se paga el rendimiento vista (≠ saldo promedio de consulta).
- **Fórmula (doc GTM-Saldo Promedio p.8-9):**
  `SPM = (saldo_cuenta × difference_of_days + acumulado) / elapsed_days`; luego `× tasa/100 × elapsed_days/base`.
  `difference_of_days` = conteo exclusivo; `elapsed_days` = inclusivo desde creación. Ejemplo: `(30,000×8+20,000)/9 = 28,888.88`.
- **Valida contra:** doc. **Trazas de log:** `Calculating with average balance` (ilustrativa; el string real difiere).
- **Oráculo:** `oraculo_rendimientos.saldo_promedio_rendimiento(...)` — autoprueba 28,888.89 ✓.
- **Estado:** 🔒 **bloqueado.** El SPM de rendimiento **solo existe en logs**, en la corrida mensual (31-ago). La columna `account.average_balance_amount` es el SPM de **consulta** (rolling) — el doc dice que **puede diferir**; NO usarla para reconstruir el rendimiento.
- **No-conformes:** N/A (sin corrida).

# 4. ISR — retención sobre rendimientos
- **Propósito.** ISR que se retiene **al pagar** rendimientos (no en devengo), sobre la parte gravable del saldo total del cliente, prorrateado por cuenta.
- **Fórmula (doc p.6):** `Base Gravable = Saldo Total − Exención`; `ISR Diario = Trunc5(Base × Trunc20(Tasa/(100×365)))`;
  `ISR Retenido = Round2(Trunc20(ISR Diario × DíasPeriodo) × Proporción)`, **Proporción = saldo_cuenta / saldo_total**.
  Parámetros 2026: tasa **0.9%**, exención **5×UMA = 213,973.20**, base **365**, personas morales exentas $0.
- **Valida contra:** doc + **norma** (LISR 54/135, LIF 2026 Art.24, UMA DOF 9-ene-2026) + **config** (`system_configuration.tax.days.year`, `yield.tax.exempt.uma.amount`).
- **Insumos:** `transaction_detail` (INTERNAL TRANSFER/Generic → cuenta ISR 100-0000-438220), `account`, `iv_initial_amount`.
- **Oráculo:** `oraculo_isr.isr_retenido(saldo_total, saldo_cuenta, dias)`.
- **Resultado:** ✅ histórico **C = B = 765.75** (cliente 1-10-370); parámetros = ley 2026.
- **No-conformes / notas:** el **ejemplo del doc** tenía un error (÷base_gravable); **Finsus corroboró** que lo correcto es ÷saldo_total (C-002 cerrada). El **ISR-vivo nativo** al centavo está 🔒 bloqueado (necesita saldo base punto-en-tiempo = 31-ago). Personas morales: SOL-011.

# 5. Crédito — interés ORDINARIO
- **Propósito.** Interés por el uso del dinero; se **devenga/provisiona diariamente** desde la dispersión.
- **Fórmula (doc GTM-Motor de créditos p.3):** `Interés = C × (i/100) × (t/DíasAño)`, C = **Saldo Insoluto del Capital**, DíasAño **360** (Comercial, `calendar_type 1`). Ejemplo: 50,000 @15% 1 día → **20.83**.
- **Valida contra:** doc. **Insumos:** `lc_loan_contract` (loan_amount, ordinary_interest_rate, calendar_type); `lc_finantial_data(_stage).capital` (firmado negativo); feed log `credits-closing-trans`.
- **Oráculo:** `oraculo_credito.interes_ordinario_dia(capital, tasa, 360)`.
- **Resultado:** ✅ **96.8% exacto a 1e-8** vs `capital` DB; **0/4,091 mismatch de tasa** (feed 08-20).
- **No-conformes (el 3%):** **linaje** (P-019) — tres tablas de `capital` (stage/fin_data/current) discrepan en el valor punto-en-tiempo; **no es defecto de motor** (los saldos implícitos son fracciones amortizadas sensatas).

# 6. Crédito — interés MORATORIO
- **Propósito.** Cargo por incumplimiento; provisión **diaria** desde el día posterior al vencimiento.
- **Fórmula (doc p.3):** `Moratorio = C_vencido × (i_mor/100) × (t_atraso/DíasAño)`, base = **Capital Vencido No Pagado** (no el saldo insoluto total). Ejemplo: 500 @36% 1 día → **0.50**.
- **Valida contra:** doc. **Insumos:** `lc_finantial_data.capital_venc`, `mora_days`; `lc_loan_contract.moratorium_interest_rate`; feed `credits-closing-trans` (MORATORY PROVISIONING).
- **Oráculo:** `oraculo_credito.interes_moratorio_dia(capital_venc, tasa_mor, 360)` (sin redondear, para cruzar el feed).
- **Resultado:** ✅ **81.1% exacto a 1e-8** (95.7% ≤$0.01) vs `capital_venc`, días=1, 0 mismatch de tasa.
- **No-conformes:** P-020 fue **falsa alarma** (comparaba el moratorio redondeado vs el feed sin redondear); resuelto. Residual sub-centavo = granularidad del snapshot de `capital_venc`; ~30 "fuera" = placeholders (`capital_venc=10M`)/liquidados (clase P-019).

# 7. Crédito — conteo de DÍAS
- **Propósito.** Confirmar cómo Aurum cuenta los días de devengo.
- **Mecánica (log CORE):** `CreditAmortizationChargeServiceImpl.java:844 - Days N` = días del **período de amortización** (topa al período), no días transcurridos. `InterestMoraDays db[N]` = días de mora.
- **Valida contra:** inferencia confirmada en log + doc (ajuste a fin de período, no corrige retroactivo).
- **Resultado:** ✅ confirmado. Cierra el residual histórico del ordinario (usábamos días transcurridos).

# 8. Crédito — IVA sobre interés
- **Fórmula (doc p.4):** `IVA = Interés × (TasaIVA/100)`, 16 dec, Round2 **Half Up**.
- **Valida contra:** doc + datos. **Insumos:** `lc_loan_amortization.interest_amount` / `interest_tax_amount`.
- **Oráculo:** `oraculo_credito.iva_interes(interes, 16)`.
- **Resultado:** ✅ **99.0% exacto** (54,716 filas con IVA; tasa implícita 16.0% en 95%). No-conformes = redondeo en montos chicos.

# 9. GAT (Ganancia Anual Total) — inversión
- **Propósito.** Rendimiento anual efectivo publicado al cliente (nominal y real), vs calculadora Banxico.
- **Fórmula (doc GTM-GAT p.5):** `m = DíasAño/DíasInversión`; `GAT Nom% = Round16(((Inicial+Interés)/Inicial)^m − 1)×100`;
  GAT Real usa inflación. Ejemplo: 1,000 a 90d, interés 200 → **107.36% / 99.04%**.
- **Valida contra:** doc + **prueba no-circular en datos.** **Insumos:** `account.nominal_cgat`/`real_cgat` (solo INVESTMENT_ACCOUNT, 689,479); inflación `cat_financial_variables.INFLATIONMXN` (3.79→3.84→3.95% punto-en-tiempo).
- **Oráculo:** `oraculo_gat.gat_inversion(...)` — autoprueba 2/2 ✓.
- **Resultado:** ✅ **motor validado.** El `nominal_cgat` es **función pura de (tasa, plazo)** — idéntico para decenas de miles sin importar el monto (term7=10.42 en **126,465** inv.; term30=7.43; term90=10.13), y el oráculo lo reproduce **exacto** desde la tasa contratada.
- **No-conformes:** el cruce 1-a-1 masivo da 35% porque el `iv_payment_plan.interest_amount` posteado ≠ el proyectado en originación (cancelación anticipada / tasa real ≠ nominal 22%); falta la **tabla de tramos de tasa** (SOL-015). No es defecto de motor.

# 10. IFRS 9 — clasificación de etapas + reserva por %
- **Propósito.** Clasificar el crédito por riesgo y calcular la estimación preventiva (reserva).
- **Reglas (doc GTM-IFRS9):** Etapa 1: 0-30 días mora; Etapa 2: 31-89; Etapa 3: ≥90. `Reserva = (capital + intereses exigibles) × %`, % por (cartera, zona marginada, días mora) — Tablas 1/2/3.
- **Valida contra:** doc + **config real de Aurum** (la validación más fuerte). **Insumos:** `lc_risk_stage` (etapas), `lc_reserve_ifrs` (% por cartera/zona/mora), `lc_finantial_data` (capital_venc, io, reserva_*).
- **Oráculo:** `oraculo_ifrs9.etapa()`, `pct_consumo/pct_microcredito/pct_vivienda`, `reserva_pct`, `ei`, `sp_sin_garantia`, `reserva_comercial` — autoprueba 14/14 ✓.
- **Resultado:** ✅ **C = config de Aurum**: etapas = `lc_risk_stage` (exacto); % = `lc_reserve_ifrs` (**37/37 exacto**) = doc. **Cartera de Finsus = CONSUMO.** Aplicación `reserva_cap = capital_venc × %` en E3 vencido = **65%**.
- **No-conformes / pendiente:** la **base "capital/intereses exigibles"** para E1/E2 amortizando y la composición de `reserva_int` **no cuadran con un solo campo** (dependen del spec → SOL-015). La **tabla de PI** comercial no está en el doc (SOL-015).

# 11. Amortización (tabla francesa)
- **Propósito.** El cronograma de pagos: cuota, desglose capital/interés por período, saldo insoluto.
- **Mecánica confirmada (doc §8.6 + datos):** francesa = **cuota financiera (cap+int) constante**; **interés = Actual/360** (`saldo × tasa/360 × días`); capital = cuota − interés; saldo → 0.
- **Valida contra:** doc + datos (`lc_loan_amortization`). **Insumos:** `capital_amount`, `interest_amount`, `total_amount`, fechas.
- **Oráculo:** `oraculo_amortizacion.cuota_francesa/interes_periodo` + invariantes — autoprueba 6/6 ✓.
- **Resultado:** ◐ mecánicas confirmadas; interés Actual/360 exacto (P1 158.33, P3 112.37); **identidad de fila 99.9%** (794 contratos); en contratos **frescos** rollforward/Σcapital/cuota constante **91.7%**.
- **No-conformes:** (a) `capital_remaining_amount` es campo **VIVO** (se actualiza con pagos) → validar solo en frescos; (b) cuota exacta ~0.1% off (ajuste Actual/360 vs anualidad); (c) Americana/Italiana/Alemana sin fórmula en el doc.

# 12. CAT (Costo Anual Total) — crédito
- **Propósito.** Costo anual efectivo publicado al cliente (Circular 21/2009 Banxico).
- **Fórmula (doc §8):** One Click `CAT = [(pago_sin_iva/monto_recibido)^(360/días)−1]×100`; Francesa = i que iguala VP(disposición)=VP(pagos), por IRR. Pago para CAT = capital + interés + comisión/seguro **sin IVA** (excluye moratorios/IVA/prepago). Monto recibido = monto − comisión inicial.
- **Valida contra:** doc + datos. **Insumos:** `lc_loan_contract.cat`, `lc_loan_amortization` (cap+int), `lc_account_commission` (apertura, ej. 3.99% type=2).
- **Oráculo:** `oraculo_cat.cat_oneclick / cat_frances` — autoprueba **3/3 vs doc** (45.80%, 289,458,538.17%, 34.48%). Caso real exacto: 35.1%.
- **No-conformes:** cruce masivo 11.6% porque `lc_loan_contract.cat` guarda en muchos contratos el CAT **nominal del producto** (miles con `cat=27.1`), no el per-contrato — la **fórmula no está en duda**. Falta confirmar semántica del campo + convención de días (SOL-015).

---

# Motores transversales (no de cálculo puro)

## Motor B — transaccional diaria (completitud A vs B)
- **Propósito.** ¿No falta ninguna transacción entre OpenFin y AurumCore? **Oráculo:** `motor_b_diario.py` (clasifica PEER 2:1 / UNI 1:1). **Resultado:** ✅ robusto — 6 días, **+0.1% a +2.1%** (OF≥AU siempre = sin faltante). **Nota:** `origin is null` en los queries oficiales aparece solo en subconsultas de exclusión (P-013/SOL-004).

## Contable — doble partida y amarre
- **Oráculo:** `contable_bc.py`. **Resultado:** ✅ B1 doble partida = **$0.00** (0/7 días). **No-conformes:** el doc **NO mapea tipo_movimiento → cuenta contable** (matriz "por incorporar"); nuestra matriz de amarre es **observada** → pedir catálogo. Alerta: producto 2001 −34% en balanza.

## Cuentahabientes — WSO2 ↔ padrón
- **Oráculo:** `cuentahabientes_wso2.py`. **Resultado:** ✅ Aurum→WSO2 completo (20 huérfanos); WSO2→Aurum 181,844 sin cuenta = churn (SOL-007).

---

# Mapa de cierre (para el agente conversacional)
Los motores están **construidos y validados hasta donde el dato alcanza**. Lo que resta = **2 desbloqueos**:
1. **Manual de Cálculos Oficiales (SOL-015)** → cierra: IFRS aplicación (base exigible + PI + reserva_int), GAT/CAT per-contrato (tramos de tasa + semántica), y modo de redondeo.
2. **Cierre mensual 31-ago (SOL-003 logs)** → cierra: rendimiento vista, saldo promedio, ISR-vivo al centavo.

**Regla de honestidad:** cada "% match" se sostiene en una validación que devuelve **las filas que violan la regla**; los no-conformes se explican, nunca se ocultan. Verde ≠ auto-aprobado.
