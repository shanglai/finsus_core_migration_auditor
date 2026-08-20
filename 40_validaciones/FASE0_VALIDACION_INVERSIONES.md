# Validación Fase 0 — Rendimiento de inversiones (motor C, offline)

Versión: 1 · 2026-08-16 · Ejecutado por: motor C (oráculo independiente)
Fuente: F-013 (árbol día cero, corte 02-03 ago 2026) · Script: `comparadores/fase0_inversiones_rendimiento.py`
Sustento: [[K-DEV-003]] [[K-DEV-001]] [[K-FIS-003]] · **FINSUS · Confidencial**

> **Sin base de datos.** Toda la Fase 0 corre **local** sobre archivos ya extraídos (F-013), con
> polars + `decimal`. **Cero conexión, queries o escritura** contra ningún core. La lectura en vivo
> (Fase 1) se hará aparte, con doble validación y aviso a Finsus.

## 1. Qué es Fase 0 (y qué no)
Tres cosas, en orden:
1. **Validar los datos existentes** de OpenFin (A) y AurumCore (B) — las extracciones de inversiones.
2. **Construir el motor de cálculo (C)** desde la norma/contrato, no desde ningún core.
3. **Contrastar A, B y C.** Ojo con el matiz: el objetivo de C **no** es "confirmar que A y B hacen
   match". Es ser el **deber ser**: donde **A = B = C**, validamos la regla y ambos cores; donde
   **divergen**, C es el **árbitro** y de ahí sale un **hallazgo**. El valor de Fase 0 es doble:
   (a) el motor validado contra el grueso, y (b) las divergencias aisladas como candidatos.

## 2. Datos y regla
- **Universo:** 18,599 inversiones (Aurum) / 18,598 (OpenFin); **18,598 pareadas** por
  `id_inversion_openfin ↔ id_cuenta`. Corte día cero (saldos planchados → el más limpio).
- **Regla (C), K-DEV-003:** `rendimiento = capital × (tasa_anual/100) × días/360`, redondeo **HALF_EVEN**
  a 2 decimales. `decimal.Decimal`, cero float.
- **Límite del dato:** `rendimiento_pagado` de F-013 es el del **último periodo mensual**, no de toda
  la vida. Las inversiones **multiperiodo (días>32) requieren `iv_payment_plan`** para recalcularse;
  el resumen no basta.

## 3. Resultados

### 3.1 Calibración de la regla (inversiones de 1 periodo, n=7,444)
| comparación | coincidencias (≤ $0.01) | % |
|-------------|-------------------------|---|
| C == Aurum | 7,436 | 99.9% |
| C == OpenFin | 7,433 | 99.9% |
| **C == ambos (A = B = C)** | **7,425** | **99.7%** |
→ [CONFIRMADO] **base 360, interés simple y redondeo half_even quedan validados con datos.**

### 3.2 Reproducción del árbol (independiente)
| bucket | motor C (nuestro) | árbol A/B |
|--------|-------------------|-----------|
| cuadran exacto | 18,509 | 18,509 ✔ |
| con diferencia | 89 | 89 ✔ |
| diferencia > $0.10 | 0 | (el RCA citaba 4,969, de otra comparación) |
→ Nuestra tubería **reproduce la hoja maestra del árbol**. Corrige una etiqueta previa: los 89 son
las diferencias **pequeñas** (≤$0.10), no ">$0.1"; el "4,969" no pertenece a este universo.

### 3.3 Detalle de las 89 diferencias
- **Composición:** 39 de **un solo periodo** + 50 **multiperiodo** (días>32).
- **Magnitud:** las 39 de 1 periodo tienen |diff| en (0.01, 0.05]; **suma total AC−OF = $0.89**,
  **todas positivas** (Aurum ≥ OpenFin, 0 en contra). Tasas: 7.01, 7.19, 7.59, 12.0, 13.0.
- **Prueba de redondeo (las 39 de 1 periodo):**
  | | coincide |
  |---|---|
  | OpenFin == C **truncado** (ROUND_DOWN a 2) | **39 / 39** |
  | OpenFin == C half_even | 19 / 39 (sólo los exactos) |
  | Aurum == C half_even | 20 / 39 |
  | Aurum == C truncado | 0 / 39 |
- **Interpretación (2 causas):**
  1. **~20 casos → `DEFECTO_OPENFIN` (redondeo):** OpenFin **trunca** la fracción de centavo;
     Aurum = half_even = C (correcto por K-DEV-001). OpenFin **subpaga** sistemáticamente.
  2. **~19 casos → por arbitrar:** Aurum ≠ C (ni half_even ni truncado). Puede ser defecto de Aurum
     **o** una nuance de la **convención de días** de mi recálculo (uso `cierre−apertura`; sin
     `iv_payment_plan` no fijo el día exacto). **No arbitrable en Fase 0.**

### 3.4 Sesgo (relevante por §10)
El signo de la diferencia es **unidireccional (89 AC>OF, 0 en contra)**. Por el §10 del charter, un
sesgo estadísticamente ≠ 0 es **candidato a severidad 1 aunque cada diferencia sea de centavos**. La
causa dominante confirmada es la **truncación de OpenFin**. Registrado: **A13-REND-SESGO**.

### 3.5 Decantamiento acumulativo (independiente) — diagrama `decantamiento_inversiones.svg`
Filtrando de forma **acumulativa** (una inversión sobrevive sólo si A y B coinciden en TODAS las
variables previas):

| # | variable | sobreviven | cae | notas |
|---|----------|-----------:|----:|-------|
| 0 | cliente + inversión (pareadas) | 18,599 | — | |
| 1 | + fecha apertura/venc | 18,599 | 0 | |
| 2 | + monto de apertura | 18,599 | 0 | |
| 3 | + tasa | 18,599 | 0 | |
| 4 | + rendimiento pagado **[C]** | 18,509 | 90 | sesgo: 90 AC>OF (0 en contra) |
| 5 | + ISR retenido **[A/B]** | **13,521** | 4,988 | bidireccional; ver desglose |
| | **cuadran TODO** | **13,521 (72.7%)** | | |

Desglose de las caídas:
- **Rendimiento (90):** 39 de 1 periodo (**OpenFin trunca**, 39/39) + 51 multiperiodo (req. `iv_payment_plan`).
- **ISR (4,988):** **bidireccional** (2,480 AC>OF · 2,508 AC<OF → NO es sesgo, es cascada de saldo);
  **3,221 material (>$0.10)** + 1,767 redondeo (≤$0.10) + **664 "un core retiene y el otro no"**
  (297 AC=0 · 367 OF=0). El ISR aún **no está arbitrado por C** (requiere P-010 + mismo saldo base).

> Contraste clave: el **rendimiento** falla con **sesgo** (OpenFin trunca) → señal de defecto de
> redondeo; el **ISR** falla de forma **simétrica y material** → señal de que arrastra el descuadre
> de saldo de cuentas, no un error unidireccional de cálculo. Son dos naturalezas distintas.

## 4. Materialidad y extrapolación
- En este corte, el impacto absoluto es mínimo (**$0.89** en 89 eventos).
- **Pero** la truncación de OpenFin es un **comportamiento sistemático**: si aplica a todos los pagos
  de rendimiento históricos (millones de eventos), es un patrón de subpago recurrente de sub-centavo.
  Es la **misma clase** que el riesgo de redondeo/sesgo del ISR (P-014). **A cuantificar a escala** en Fase 1.

## 5. Limitaciones (qué NO cierra Fase 0)
- **60% multiperiodo** (11,155): requiere `iv_payment_plan` (Fase 1).
- **~19 de las 89**: requieren la convención de días exacta + el plan para arbitrar Aurum vs C.
- **ISR** (el gap grande, ~27%): requiere `system_configuration` (params) y cerrar **P-010**.
- Todo esto es sobre **extracciones resumidas** (F-013), no sobre el crudo de los cores.

## 6. Conclusión
- La **regla y el motor C de rendimiento de plazo están validados** (99.7% de acuerdo A=B=C en 1 periodo).
- Primer **hallazgo independiente confirmado**: **OpenFin trunca** el rendimiento (subpago sistemático
  de sub-centavo) → `DEFECTO_OPENFIN`, a cuantificar a escala.
- **Siguiente paso:** Fase 1 — extraer `iv_payment_plan` (multiperiodo) y `system_configuration` (ISR),
  para cerrar el 60% restante y el ISR.

## 7. Reproducibilidad
`python 40_validaciones/comparadores/fase0_inversiones_rendimiento.py` (offline). Los resultados con
datos de cliente se escriben a `40_validaciones/_resultados/` (gitignored).
