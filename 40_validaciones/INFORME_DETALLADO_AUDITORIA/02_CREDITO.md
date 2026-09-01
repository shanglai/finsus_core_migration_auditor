# Informe Detallado — Crédito e IFRS 9

> Ficha por punto: Alcance · Periodo · Universo y representatividad · Metodología + rationale · Santo y seña ·
> Conciliación. Solo lectura, `decimal.Decimal`. Total de contratos en `aurumcore.lc_loan_contract` = **31,867**
> (verificado 2026-08-28). Corte 2026-08-26.

---

## V-13 · Crédito interés ordinario
- **Alcance — sí:** la **provisión diaria** de interés ordinario que el core escribe en su feed operativo, recalculada
  por el oráculo. **No:** el interés migrado histórico; contratos sin evento de provisión ese día.
- **Periodo:** feed **2026-08-20**. Ejecutado 2026-08-23 18:26.
- **Universo y representatividad:** **4,091 provisiones ordinarias = censo del día** (todas las del feed 08-20). El feed
  tocó **4,945 contratos** con evento ese día, de **31,867** totales (≈15.5% del padrón **por día**; es un censo
  diario, no una muestra del padrón estático). Con capital ≤08-20: 3,585.
- **Metodología + rationale:** se eligió **un día de feed completo** (`credits-closing` 08-20) para no golpear la base
  productiva; el feed de provisión es alta precisión (sin redondear). Ampliable a más días con visto bueno.
- **Santo y seña:** feed `credits-closing-trans-*.gz` (col5=provisión diaria, col6=`contract_id`, col7=tasa,
  col9=tipo `INTEREST PROVISIONING`) ↔ `aurumcore.lc_finantial_data_stage.capital`. Motor
  `comparadores/oraculo_credito.py::interes_ordinario_dia` = `capital × (tasa/100) / 360` (base 360 = `calendar_type 1`).
  Tolerancias `tolerancias.py`.
- **Conciliación:** tasa feed=DB **4,091/4,091** (0 mismatch); **97.32% a 1e-8 / 97.43% al centavo** (3,489/3,585 c/capital, corte 01-sep); (firme 23-ago 96.8%). abs(capital) K-DAT-007. ≤$0.01
  **97.0%**. Sin sesgo. Residuo = **linaje de datos** (tabla de capital punto-en-tiempo, **P-019**), no defecto.
  `RESULTADO_credito_vivo_2026-08-23.md`.

## V-14 · Crédito interés moratorio
- **Alcance — sí:** provisión diaria de interés **moratorio** sobre capital vencido. **No:** contratos sin mora.
- **Periodo / ejecución:** feed 2026-08-20; ejecutado 2026-08-23 18:26.
- **Universo y representatividad:** **1,274 provisiones moratorias = censo del día**; con `capital_venc`: 692.
- **Santo y seña:** mismo feed (`MORATORY PROVISIONING`, col7=tasa moratoria) ↔ `aurumcore.lc_finantial_data.capital_venc`.
  Motor `oraculo_credito.py::interes_moratorio_dia` = `capital_venc × (tasaMor/100) / 360`, días=1, **sin redondear**.
- **Conciliación:** tasa 0 mismatch; **94.66% a 1e-8 / 95.38% al centavo** (656/693, corte 01-sep); (firme 23-ago 81.1%/95.7%). El **1e-8 se mueve con el corte** = granularidad del snapshot de `capital_venc`, no defecto; el centavo (~95.4%) es el estable. ~~≤$0.01 = 95.70%~~ (662). El escalón
  81→95.7 = **granularidad del snapshot de `capital_venc`** (más volátil intra-período), no defecto. Los 30 fuera =
  placeholders (`capital_venc=10M`)/liquidados. P-020 resuelta. **Cifra firme: 95.7% al centavo** (no el 89% que se
  mencionó verbalmente).

## V-15 · Crédito conteo de días
- **Alcance:** que los días de provisión = días del **período de amortización** (no transcurridos).
- **Universo:** 3 contratos (traza de log) — es una **verificación de mecánica**, no de volumen.
- **Santo y seña:** log `CreditAmortizationChargeServiceImpl.java:844 - Days N`; `credito_dias_log_2026-08-23.csv`.
- **Conciliación:** confirmado (Aurum topa al período). Cierra el ~5% de residual histórico del ordinario.

## V-16 · Crédito IVA sobre interés
- **Alcance — sí:** IVA sobre el interés. **No:** productos que no gravan.
- **Universo y representatividad:** **54,716 filas** validadas de **55,636** filas con IVA>0 (**~98%**), de **102,605**
  filas totales en `aurumcore.lc_loan_amortization` (31,970 contratos distintos).
- **Santo y seña:** `aurumcore.lc_loan_amortization.interest_tax_amount` vs `oraculo_credito.py::iva_interes(interés, 16)`
  = `Round2(interés × 16/100)`, half-up.
- **Conciliación (por cohortes, corte 01-sep):** cohorte **16% general** = 98.91% a 1e-8 / **99.46% al centavo** (96.96% del universo); **IVA-incluido 16/84=19.05%** (0.5%, convención); **resto** = 16% con redondeo en montos ínfimos (RESULTADO_iva_cohortes). ~~99.0% exacto (tasa implícita 16.0% en 95%; resto = redondeo en mon~~tos chicos).

## V-17 · Amortización (tabla francesa)
- **Alcance — sí:** mecánica de la tabla (cuota constante, interés Actual/360, capital=cuota−interés, saldo→0).
  **No:** contratos **con pagos** (el campo `capital_remaining_amount` es **vivo**, no cronograma original).
- **Universo y representatividad:** **794 contratos = subconjunto por linaje** (solo contratos **sin pagos**, para que
  el campo vivo sea válido); identidad de fila sobre 794 contratos frescos.
- **Metodología + rationale:** el recorte NO es por performance sino por **validez del dato**: en contratos con pagos,
  `capital_remaining` ya no es el cronograma; validarlos ahí daría falsos no-conformes.
- **Santo y seña:** `aurumcore.lc_loan_amortization` (cuota, interés, capital, saldo); motor `oraculo_amortizacion.py`.
  Interés = `saldo×tasa/360×días` (Actual/360).
- **Conciliación:** identidad de fila **99.9%**; interés exacto (P1 158.33, P3 112.37). Matiz: cuota ~0.1% off =
  convención Actual/360 (spec del 1er período).

## V-18 · CAT (Costo Anual Total)
- **Alcance — sí:** el CAT per-contrato (Circular 21/2009). **No:** el estrato de `cat` constante (no es un cálculo) ni
  `cat=0` (hallazgo aparte A28).
- **Universo y representatividad:** `lc_loan_contract.cat` es **campo mixto** sobre 31,867: **25,026 constante copiada**
  (no validable — `cat=27.10` en 15,300 contratos con 3,930 montos), **4,220 varía por contrato** (el universo de
  CAT-01), **2,576 cat=0** (A28), 44 sin cat. El cruce global 11.6% ≈ el estrato per-contrato (13.2%).
- **Metodología + rationale:** el 11.6% **no mide el motor**; mide contra un campo mayormente constante. El remedio es
  **estratificar** (CASO CAT-01) sobre los 4,220, no subir el 11.6% (ver `CASO_CAT-01_estratificado.md`).
- **Santo y seña:** `aurumcore.lc_loan_contract.cat`, `lc_loan_amortization`, `lc_account_commission` (comisión
  apertura). Motor `oraculo_cat.py` (`cat_frances` por bisección/IRR). Bloqueo **SOL-015** (convención de días +
  comisión financed vs descontada).
- **Conciliación:** fórmula **3/3 vs doc** + caso real exacto (35.1%). **Hallazgo aparte A28-CAT-CERO ([[P-023]]):**
  2,573 contratos `cat=0` cobran ~28.45% → candidato regulatorio (revelación de CAT).

## V-19 · IFRS 9 — clasificación de etapas + % de reserva
- **Alcance — sí:** las **etapas** (mora → etapa) y los **% de reserva** (config), y la aplicación E3
  `reserva = capital_venc × %`. **No:** E1/E2 amortizando (base exigible sin definir), `reserva_int`, comercio y
  reestructurado (dependen de las 9 tablas / documento pendiente). *Es el ejemplo del "parcial": cuadra al 100%, falta
  ampliar alcance* (F-031 @00:48).
- **Universo y representatividad:** **37/37 celdas = censo de la tabla de config** (`lc_reserve_ifrs`) + etapas
  (`lc_risk_stage`). Es la validación **más fuerte** (config del propio core), **no depende de cohorte** → no aplica %
  de muestra.
- **Metodología + rationale:** el % de C sale de las **Tablas del GTM** (norma), no de `lc_reserve_ifrs`; que además
  coincidan 37/37 es un **resultado**, no el método (no-circular).
- **Santo y seña:** `oraculo_ifrs9.py` (etapas + % + EI/SP/reserva); tablas `aurumcore.lc_reserve_ifrs` /
  `lc_risk_stage`. Cartera Finsus = **CONSUMO** (usa % directo CNBV; el Core no calcula PD).
- **Conciliación:** etapas exactas + **37/37**; autoprueba 14/14; reserva E3 fully-vencido 65% a volumen exacto.
