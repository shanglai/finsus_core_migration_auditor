---
id: K-DEV-003
titulo: Cálculo de rendimiento de inversiones a plazo fijo (AurumCore)
dominio: DEV
estado: CONFIRMADO
confianza: alta
version: 2
creado: 2026-08-14
actualizado: 2026-08-16
fuentes:
  - ref: 20_fuentes/docs/GTM-Pago de Rendimientos-140826-230050.pdf
    ubicacion: "§5.2 (p.3-4)"
relaciones:
  refina: []
  depende_de: [K-DEV-001]
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El rendimiento de plazo fijo se calcula sobre el **capital de apertura**
(`account.iv_initial_amount`), por los **días del periodo** (entre planes de pago).
  → fuente: F-009 §5.2

## Reglas (F-009 §5.2)
- **Base:** capital inicial `account.iv_initial_amount`.
- **Elegibilidad:** cuenta `ACTIVE`; `iv_account_state` en `ACTIVE` o `PRECANCELLED`; cliente
  `ACTIVE` o `SUSPENDED`.
- **Días del periodo:** días transcurridos desde el plazo anterior, o desde la fecha de creación
  si es el primer/único plazo del plan de pagos.
- **Parámetros:** días del año y tasa, tomados del **misceláneo del producto**.
- **Fórmula (del ejemplo, F-009 p.3):** capital × tasa → /100 → /días_año → ×días_periodo, con
  truncamientos a 20 dec y **redondeo final half_even a 2** (K-DEV-001).
  Ejemplo: $1,000 a 100 días, tasa 5%, 360 días → renglón resuelto 30.14 (para $5,000/31 días).

## Validación empírica (Fase 0, oráculo C offline sobre F-013)
[CONFIRMADO] Recalculando `C = capital × (tasa/100) × días/360` (HALF_EVEN) sobre las inversiones de
**un solo periodo** (días ≤ 32; n=7,444), **C coincide con AMBOS cores en 7,425 (99.7%)** al centavo.
→ **base 360, interés simple y redondeo half_even quedan validados con datos.**
- [CONFIRMADO] `rendimiento_pagado` en las extracciones es el del **último periodo mensual**, no el de
  toda la vida (ej.: $202,000 × 12% × 31/360 = $2,087.33). → las inversiones **multiperiodo (días>32,
  ~11,155 = 60%) requieren `iv_payment_plan`** (días por periodo) para recalcularse; el resumen del
  árbol no basta. Justifica ese campo en el extracto de Fase 1.

## Implicaciones para la validación
- Base de la spec S-DEV-002 (plazo). Los campos `iv_initial_amount` / `iv_account_state` son
  nombres reales de AurumCore → alimentan el diccionario de datos (P-004).
- **Contraste con el crédito One Click** (amarrado a plazos): verificar que su devengamiento use
  la misma base/días (K-MIG-004; PAR-351 reporta 1,261 créditos sin devengamiento).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-009. | F-009 |
| 2 | 2026-08-16 | Validación empírica Fase 0: base 360/simple/half_even confirmada (99.7%); multiperiodo requiere iv_payment_plan. | F-013 (recálculo C) |
