# Comparación — lo que evaluamos (Oráculo C) vs la documentación oficial de AurumCore

> Fase 2. Para **cada motor/métrica que ya evaluamos**: (1) ¿está en la documentación oficial? · (2) ¿lo
> corroboramos (C = doc/BD) o hay desviación? · (3) **si hay desviación, en qué consiste** (foco).
> Base: [INDICE_PRODUCTOS_PROCESOS.md](INDICE_PRODUCTOS_PROCESOS.md) + resultados en `_resultados/`.
> Estado de veracidad: cada fila referencia doc(pág) y/o resultado de BD. Actualizado 2026-08-23.

## Semáforo de la columna (2)
🟢 corroborado (C = doc y/o BD, sin desviación) · 🟡 desviación menor / residuo · 🔴 desviación material o bloqueo · ⚪ documentado pero **aún no evaluado** por C · ⬛ evaluado pero **no documentado** (gap de doc)

---

## A. CAPTACIÓN — Rendimientos

### A1. Rendimiento cuenta a la VISTA (2.1.1)
1. **¿En doc?** Sí — D-REN p.3-4. `Round2(Trunc20(Trunc20((SPM×Tasa)/100)/DíasAño)×DíasPeriodo)`.
2. **Corroboración:** 🟡 fórmula = doc; autoprueba del oráculo da el ejemplo del doc (30.14). **Pero no validado vivo en BD** (la corrida mensual de vista aún no ocurre / requiere saldo promedio de logs).
3. **Desviación (consiste en):** el doc **no define el modo del `Round2`** para vista (a diferencia de plazo, que sí especifica `half_even`). Asumimos half-up. Impacto: ± un centavo por evento, potencial **sesgo** si el modo real difiere → verificar en la primera corrida mensual viva (31-ago) y/o logs `Calculating yield amount Using RATE`.

### A2. Rendimiento INVERSIÓN / PLAZO FIJO (2.1.2)
1. **¿En doc?** Sí — D-REN p.5. `RoundHalfEven2(Ceil10(Ceil10((C×T)/100)/Y)×Dias)`.
2. **Corroboración:** 🟢 fórmula = doc (ejemplo 13.89) **y validado a volumen**: `validate_plazo_origin.py` = **530,195 periodos, 100.00%, 0 violaciones**.
3. **Desviación:** ninguna material. (El más sólido de los motores de cálculo.)

### A3. SALDO PROMEDIO de rendimiento (2.1.3)
1. **¿En doc?** Sí — D-SPM p.7-10. `(saldo×difference_of_days + acumulado)/elapsed_days`; luego `×tasa/100×elapsed_days/base`.
2. **Corroboración:** 🔴 fórmula = doc (autoprueba 28,888.89). **Validación viva bloqueada.**
3. **Desviación (consiste en):** el doc aclara que hay **dos** saldos promedio — el de **consulta** (`account.average_balance_amount`, en BD) y el de **rendimiento** (calculado en el proceso, **puede diferir**, **solo existe en logs**). No es desviación de nuestra fórmula, es **gap de validación**: no podemos reconstruirlo desde la BD; requiere la traza `Calculating with average balance` (barrido con el string exacto, VPN logs). Corrección propia registrada (no usar la columna DB).

### A4. GAT (nominal/real)
1. **¿En doc?** Sí — D-GAT (cuentas p.3-4, inversiones p.5-7), con ejemplos vs Banxico.
2. **Corroboración:** 🟢 **MOTOR VALIDADO.** (a) `oraculo_gat.py` autoprueba 2/2 EXACTA vs los ejemplos del doc. (b) Aurum guarda GAT **solo en INVESTMENT_ACCOUNT** (689,479; `nominal_cgat`). **Prueba no-circular:** el `nominal_cgat` es idéntico para decenas de miles de inversiones del mismo plazo sin importar el monto (term=7: 126,465 con 10.42; term=30: 44,967 con 7.43; term=90: 16,002 con 10.13) = función pura de (tasa, plazo, 360), **exactamente como la fórmula**, y **el oráculo lo reproduce EXACTO** desde la tasa contratada (9.9217%→10.42, 7.1884%→7.43, 9.7665%→10.13). Inflación = `cat_financial_variables.INFLATIONMXN` punto-en-tiempo (3.79→3.84→3.95%, coincide con la despejada).
3. **Desviación:** **ninguna de motor.** El cruce 1-a-1 a volumen requiere mapear cada inversión a su **tramo de tasa** (63 tramos por plazo, por monto/variante); usar el `iv_payment_plan.interest_amount` posteado da 35% (difiere del proyectado en originación por cancelación anticipada / actual). Eso es **data-sourcing** (tabla de tramos de tasa de inversión), no cálculo. → SOL menor.

---

## B. FISCAL — ISR

### B1. ISR al pago de rendimientos (mecánica + parámetros)
1. **¿En doc?** Sí — D-REN p.5-6; parámetros contra norma en [[K-FIS-004]].
2. **Corroboración:** 🟢 validado en BD histórica (**C = B = 765.75**, cliente 1-10-370); parámetros (tasa 0.9%, 5×UMA=213,973.20, base 365) corroborados contra ley 2026 y config.
3. **Desviación:** ninguna de motor. **Residuo cosmético:** el EJEMPLO del doc sigue con la proporción ÷base_gravable (error de redacción). **C-002 CERRADA — Finsus corroboró que fue error de su documentación**, lo correcto es ÷saldo_total (= C = BD). No cambia nada en C.

### B2. ISR-VIVO nativo (post-cutover)
1. **¿En doc?** Sí (misma mecánica B1).
2. **Corroboración:** 🔴 **bloqueado** (`isr_live_nativo.py`, ~13% match).
3. **Desviación (consiste en):** no es desviación de regla; es **gap de insumo** — el ISR vivo necesita el **saldo base punto-en-tiempo** (saldo promedio del periodo), que **no está en BD** y vive en logs. Mismo bloqueo que A3. Residuo abierto: **personas morales** (D-REN dice exención $0 = retención completa; LISR Art. 54 las excluye) → SOL-011.

---

## C. CRÉDITO

### C1. Interés ORDINARIO
1. **¿En doc?** Sí — D-CRE p.3. `C×(i/100)×(t/DíasAño)`, base = **Saldo Insoluto del Capital**, provisión **diaria**, base 360 (`calendar_type 1`).
2. **Corroboración:** 🟢 **validado vivo: 96.8% exacto a 1e-8** vs `capital` DB, **0/4,091 mismatch de tasa** (feed `credits-closing` 08-20); ejemplo del doc (20.83) reproducido.
3. **Desviación:** ninguna de motor. **P-019 RESUELTO (2026-08-24, log↔DB):** del log despejé el capital que el motor usó → son fracciones amortizadas sensatas (mediana 95.5% del loan) = **motor correcto**. 84.2% stage+fin_data coinciden. El residuo ~12% es un **gap de población de la financial-data/reserva (lote 5004)** intra-mes, NO del motor de interés → **potencial subestimación de RESERVA** (escalar: confirmar cobertura al cierre de mes). Ver P-019b.

### C2. Interés MORATORIO
1. **¿En doc?** Sí — D-CRE p.3. `C_vencido×(i_mor/100)×(t_atraso/DíasAño)`, base = **Capital Vencido No Pagado**.
2. **Corroboración:** 🟢 **validado a precisión completa** — 81.1% exacto a 1e-8 (95.7% ≤$0.01) vs `lc_finantial_data.capital_venc`, sin redondear, días=1; 0/1,274 mismatch de tasa; ejemplo del doc (0.50) reproducido.
3. **Desviación (P-020 RESUELTA):** la "asimetría de precisión" reportada primero (2.7%) era **artefacto de MI comparación** (comparaba el moratorio con `_round2` contra el feed sin redondear, mientras el ordinario iba sin redondear). Apples-to-apples: base=capital_venc, días=1, exacto. Residual sub-centavo = granularidad del snapshot de `capital_venc`; los ~30 "fuera" = placeholders (`capital_venc=10M`)/liquidados (clase P-019). **No hay desviación de motor.** Fix: `interes_moratorio_dia` en `oraculo_credito.py`.

### C3b. IVA sobre interés — [CONFIRMADO] validado en datos
1. **¿En doc?** Sí — D-CRE p.4 (`IVA = interés × tasaIVA/100`, 16 dec, Round2 Half Up).
2. **Corroboración:** 🟢 **99.0% exacto** — `iva_interes(interés, 16%)` = `lc_loan_amortization.interest_tax_amount` (54,716 filas con IVA; tasa implícita 16.0% en 95%, resto = redondeo en montos chicos).
3. **Desviación:** ninguna. Cierre completo del IVA.

### C3. Crédito DÍAS (mecánica de conteo)
1. **¿En doc?** Sí — D-CRE p.4 (provisión diaria; **ajuste a fin de periodo**; NO corrige retroactivo migrados).
2. **Corroboración:** 🟢 log confirma `Days N` = **días del período de amortización** (topa al período), consistente con el "cierre/ajuste" del doc.
3. **Desviación:** ninguna. Cierra el residual histórico del ordinario (usábamos días transcurridos).

### C4. IVA sobre interés
1. **¿En doc?** Sí — D-CRE p.4. `Interés×(TasaIVA/100)`, 16 dec, Round2 Half Up.
2. **Corroboración:** 🟡 fórmula implementada = doc; **no validada aún en BD** (falta cohorte con IVA gravado).
3. **Desviación:** el doc **nunca da la tasa de IVA numérica** (siempre variable). Sin impacto si el producto no grava.

### C5. Amortización (Francesa) / One Click / CAT
1. **¿En doc?** Sí — D-CRE p.6-11 (Francesa §8.6; CAT One Click/Francesa; excluye moratorios/IVA/prepago).
2. **Corroboración AMORTIZACIÓN:** 🟢/🟡 `oraculo_amortizacion.py` — **mecánicas confirmadas** vs `lc_loan_amortization`: francesa = **cuota financiera (cap+int) constante**; **interés = Actual/360** (`saldo×tasa/360×días`, exacto: P1 158.33, P3 112.37); capital=cuota−interés; saldo→0. Invariantes: **identidad de fila 99.9%** (794 contratos); en contratos **frescos** rollforward/Σcapital/cuota constante **91.7%**. CAT: **no implementado aún** (siguiente motor; se cruza vs `lc_loan_contract.cat`).
3. **Desviación / pendiente:** (a) **cuota exacta ~0.1% off** (929.15 vs anualidad 928.09) — Aurum ajusta la cuota por la convención **Actual/360** (días reales), no es anualidad de períodos iguales → spec del primer período. (b) **Linaje:** `capital_remaining_amount` es campo **VIVO** (se actualiza con pagos), no cronograma original → validar solo en contratos sin pagos. (c) Americana/Italiana/Alemana sin fórmula en el doc.

### C6. CAT (Costo Anual Total)
1. **¿En doc?** Sí — D-CRE §8 (One Click cerrado; Francesa por VP/IRR, Circular 21/2009 Banxico).
2. **Corroboración:** 🟢 **fórmula validada** — `oraculo_cat.py` autoprueba **3/3 vs los ejemplos del doc** (One Click 45.80% y 289,458,538.17%; Francesa 34.48% por bisección). Caso real exacto: fa618d44 (loan 100, comisión apertura **3.99%** de `lc_account_commission`, 161 días) → **35.1% = CAT stored**. Comisión de apertura sourceada de `lc_account_commission` (type=2, `financed`).
3. **Desviación / pendiente (afinado 2026-08-28, cruce a BD):** el cruce a volumen **11.6%** NO mide el motor: mide
   contra un campo `lc_loan_contract.cat` que es **mixto y mayormente constante copiada**, no la salida de un motor.
   Estratos (31,867 contratos): **25,026 (78.5%) constante** (≥100 contratos comparten el mismo `cat`; `cat=27.10`
   cubre **15,300** contratos con **3,930 montos** y **521 plazos** distintos — imposible para un CAT real, que es
   función de monto y plazo) · **4,220 (13.2%) varía por contrato** · **2,576 (8.1%) `cat=0`** · 44 sin `cat`. El
   cruce **11.6% ≈ el estrato per-contrato (13.2%)**: el motor cuadra **donde el campo sí guarda un CAT per-contrato**;
   el 88.4% restante es comparar contra algo que no es un CAT. **Corrección al [antes]:** el campo **no** es
   "nominal-por-producto" (27.10 aparece en 7 productos; el producto dominante trae 1,381 valores distintos) → es
   **mixto**. La fórmula **NO está en duda** (3/3 vs doc + caso real 35.1%). Remedio: **CASO CAT-01 estratificado**
   (ver `CASO_CAT-01_estratificado.md`): correr C sobre los 4,220 per-contrato con alcance declarado; los 25,026
   constantes son **data-sourcing**, no defecto (un motor no se valida contra una constante). Bloqueo: **SOL-015**
   (convención de días + comisión `financed` vs descontada). **Hallazgo aparte A28-CAT-CERO → [[P-023]]:** 2,573
   contratos `cat=0` cobran ~28.45% de interés (campo sin poblar; Circular 21/2009 exige revelar CAT → candidato
   regulatorio, no de cálculo).

---

## D. TRANSACCIONAL / CONTABLE

### D1. Motor B diario (A vs B transaccional)
1. **¿En doc?** Parcial — D-CIC documenta los **ciclos/tipos** de transacción (SPEI, Pomelo, Authorizer, P2P, ajustes, tarjetas) y su afectación a **límites**; D-QRY da la **lógica de extracción** live (Sergio).
2. **Corroboración:** 🟡 A vs B robusto (6 días, +0.1% a +2.1%, siempre OF≥AU = sin faltante).
3. **Desviación (consiste en):** (a) el delimitador **`origin is null`** aparece en los queries oficiales **solo en subconsultas de exclusión** de crédito, no en el WHERE principal → su semántica como "live" **no está confirmada** (P-013/SOL-004); (b) **matriz oficial de tipo_transacción → efecto está "por incorporar" (vacía)** en el doc → no hay referencia oficial de tipos; (c) campo temporal A=`created` vs B=`last_updated` (posible desalineación).

### D2. Contable B1/B3/B4 (doble partida, amarre)
1. **¿En doc?** ⬛ **NO.** D-CIC **no mapea tipo_movimiento → cuenta contable de mayor** (sin pólizas, sin cargo↔abono, sin naturaleza); las 3 capas de saldo (contable/disponible/retenido) no se definen formalmente. Los docs IFRS remiten la contabilidad a "R04 A-0417 fuera de alcance".
2. **Corroboración:** 🟡 B1 doble partida = **$0.00** (auto-consistente); balanza D ~1-2%.
3. **Desviación (consiste en):** **gap de documentación** — nuestra matriz de amarre [[K-CTB-001]] se construyó de **datos observados**, no de fuente oficial. No hay contra qué corroborarla. **Acción:** pedir a Finsus el **catálogo tipo_movimiento → cuenta contable** (SOL nuevo). Alerta abierta: producto 2001 −34% en balanza; `daily_account_balances` stale.

### D3. Cuentahabientes WSO2 ↔ padrón
1. **¿En doc?** No (fuera de estos docs de cálculo).
2. **Corroboración:** 🟡 Aurum→WSO2 completo (20 huérfanos); WSO2→Aurum 181,844 churn (P-017).
3. **Desviación:** ciclo de vida de identidad no documentado → asimetría de retención esperada, por confirmar (SOL-007).

---

## E. REGULATORIO — Gaps que evaluamos

### E1. Suspensión de devengo / IDNC (Etapa 3)
1. **¿En doc?** Sí, **como gap declarado** — D-GAP B: "AurumCore reporta el saldo pero **no documenta el motor** de cancelación automática del devengo"; R452 tiene los campos IDNC; IFRS corta intereses de EI al día 89.
2. **Corroboración:** 🔴 **es un gap regulatorio** (CNBV C-16 / IFRS 9) reconocido por el propio proveedor. Nuestra [[K-REG-001]] lo documenta.
3. **Desviación (consiste en):** el motor de **suspensión de devengo contable + reverso de IDNC a cuentas de orden** a los 90 días **no está en el motor de crédito** (calcular reserva ≠ suspender devengo). Requiere **decisión de Comité**; descubrirlo post-go-live = problema regulatorio.

### E2. Cuota Prosofipo / IPAB (fondo de protección)
1. **¿En doc?** Sí, **como gap** — D-GAP C: cobertura se calcula al generar el **reporte 841** (campos 46-47, min(saldo, 25,000 UDIS)), **no** la cuota mensual por cliente.
2. **Corroboración:** 🔴 gap confirmado; [[K-REG-002]]. La cuota mensual (LACP Art. 104 Bis) **seguirá por fuera** del core (Finsus lo confirmó).
3. **Desviación (consiste en):** distinguir la **cobertura-841** (sí existe en el core) de la **cuota mensual al fondo** (NO está; proceso externo). Formalizar en Comité (SOL-013).

### E3. Otros 3 gaps del GAP Analysis (no evaluados por C)
Write-offs (A), tasa variable TIIE/CETES (D), revaluación cambiaria/UDIS (E). ⚪ documentados como gaps; corroborados en fuente Aurum (R419/R452, MONEDA=0, Hfx=0). No implican motor nuestro; son alcance del dictamen.

---

### E4. IFRS 9 — reservas (stages + % por cartera)
1. **¿En doc?** Sí — D-IFR (stages p.21, Tablas 1/2/3 p.18-20) + D-REG (reportes).
2. **Corroboración:** 🟢 **parte determinista validada al máximo nivel** — `oraculo_ifrs9.py` autoprueba 14/14, y **C = config real de Aurum**: etapas = `lc_risk_stage` (exacto), % = `lc_reserve_ifrs` (**37/37 exacto**). Finsus cartera = **CONSUMO**. Aplicación `reserva=base×%` validada para E3 fully-vencido (base=capital_venc, 65% a volumen exacto).
3. **Desviación:** ninguna en tablas/stages/%. Pendiente (no desviación): (a) definición de **"capital exigible"** como base para E1/E2 amortizando (porción exigible vs saldo) → 65%/30% de match, es data-def; (b) **tabla numérica de PI** para el modelo comercial (no en doc) → SOL; menor para Finsus (usa % directo).

## F. Documentado pero AÚN NO evaluado por C (cobertura pendiente de nuestro oráculo)
| Proceso | Doc | Por qué importa para el dictamen |
|---|---|---|
| **IVA** en datos | D-CRE | fórmula lista, falta cohorte de BD con IVA gravado |
| **GAT vista** (cuenta) | D-GAT | motor GAT ya validado en inversión; vista no lo guarda Aurum (`nominal_cgat`=0 en ACCOUNT) |
| **IFRS reserva comercial** (EI×PI×SP) | D-IFR | oráculo listo; falta tabla de PI (SOL); menor (Finsus = consumo) |
| **CAT** cruce per-contrato | D-CRE | fórmula validada 3/3; falta confirmar si `cat` stored es per-contrato o nominal-producto (SOL) |

---

## Síntesis (foco: desviaciones)
- **Desviación de cálculo material abierta:** **ninguna.** P-020 (moratorio) se **cerró** (era artefacto de comparación; el motor es exacto). Ordinario y moratorio validados a precisión completa.
- **Bloqueos de validación (no desviación de regla):** A3 saldo promedio y B2 ISR-vivo — mismo insumo faltante (saldo base punto-en-tiempo, logs).
- **Gaps de documentación (evaluamos, el doc no lo cubre):** D2 mapeo contable, D1 semántica de `origin`/matriz de tipos "por incorporar".
- **Gaps de motor reconocidos por el proveedor:** E1 suspensión devengo/IDNC, E2 cuota Prosofipo, + write-offs/tasa variable/cambiario.
- **Corroborados sin desviación:** A2 plazo (100%), C1 ordinario (96.8% exacto), C2 moratorio (81.1%), C3 días, C5 amortización (Actual/360 + invariantes 99.9%), **C6 CAT (fórmula 3/3 vs doc)**, B1 ISR mecánica/parámetros, **A4 GAT inversión**, **E4 IFRS 9 etapas+% (C = config de Aurum, 37/37)**.
- **Cobertura pendiente de C:** IVA en datos, GAT vista, IFRS reserva comercial/PI, cierres per-contrato de GAT/CAT (valor almacenado nominal-producto → SOL).
