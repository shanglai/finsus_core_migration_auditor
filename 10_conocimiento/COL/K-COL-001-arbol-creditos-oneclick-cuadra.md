---
id: K-COL-001
titulo: Árbol de crédito One Click (5004) — cuadra 100% salvo 68 por redondeo
dominio: COL
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-16
actualizado: 2026-08-16
fuentes:
  - ref: 20_fuentes/datos/analisis_arboles_20260803/Árboles - Día Cero.xlsx
    ubicacion: "hoja Árboles (Créditos) y RCA-CAUSA (causa 23)"
relaciones:
  refina: [K-MIG-005]
  depende_de: [K-DAT-004, K-DEV-001]
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El crédito **One Click (producto 5004)** es el dominio que **mejor cuadra**: de los
**7,619 en común**, la diferencia es **0 en tasa (IO/IM), monto entregado, fecha de apertura y días,
y monto pagado**.
  → fuente: F-013

## Cifras
- En común: 7,619 · Único AC 68 · Único OF 0 (TOTAL AC 7,681 / OF 7,619).
- Diff Tasa (IO IM) = 0 · Diff Monto entregado = 0 · Diff Fecha aper y días = 0 · Diff Monto pagado = 0.
- **Único AC 68:** créditos que sólo aparecen en AurumCore por no haberse liquidado del todo — por
  **redondeo, al liquidar el monto completo sobraba < $0.01**. Mitigado liberando versión de Aurum
  que **trunca a 2 decimales** (ligado a K-DEV-001).

## Implicaciones para la validación
- **Señal positiva fuerte** para One Click: el motor de crédito reproduce tasa/monto/fecha/pagado sin
  diferencia. Es el mejor candidato para cerrar primero (bajo riesgo).
- El caso de los 68 confirma el patrón de **redondeo** (K-DEV-001): truncar a 2 elimina el residuo <$0.01.
- Falta el **devengamiento diario** del crédito (no está en este árbol; PAR-351 reportaba 1,261 sin
  devengamiento) → verificar aparte con el oráculo.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-16 | Creada desde F-013. | F-013 |
