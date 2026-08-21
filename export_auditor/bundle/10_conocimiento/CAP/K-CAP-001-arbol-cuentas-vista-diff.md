---
id: K-CAP-001
titulo: Árbol de cuentas a la vista (02-03 ago) — universos y causas de diferencia
dominio: CAP
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-16
actualizado: 2026-08-16
fuentes:
  - ref: 20_fuentes/datos/analisis_arboles_20260803/Árboles - Día Cero.xlsx
    ubicacion: "hojas Árboles (Cuentas a la vista) y RCA-CAUSA (causas 3-19)"
relaciones:
  refina: [K-MIG-005]
  depende_de: [K-DAT-004]
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] En cuentas a la vista, **2,046,969 (cliente+cuenta) están en común**; el árbol
descompone las diferencias así:
  → fuente: F-013

## Cifras (corte 02-03 ago)
- **En común (cliente+cuenta):** 2,046,969 · Único AC 3,061 · Único OF 79,109 (TOTAL AC 2,050,030 / OF 2,126,078).
- **Cuadra con saldo:** 98.03% (2,006,642). **Diff Saldo: 40,327.**
- **Cuadra con saldo + tasa:** 97.92% (2,004,532). **Diff Tasa: 2,110.**

## Causas (RCA del equipo — a verificar por C)
- **Único OF 79,109:** 78,884 = cuentas de la **sucursal 201 (fondeadora) no migradas** (decisión
  de negocio: excluir del universo comparable); 206 = TERMINATED en AC; el resto por hasheo/ingesta.
- **Único AC 3,061:** **2,977 = BUG del API** (toma el k_auxiliar y lo asigna al consecutivo de la
  cuenta; productos 2011=1689, 2013=1097, 2012=189); 82 = ingestadas que hoy no existen en OF; 2 admin.
- **Diff Saldo 40,327:** 24,910 = **redondeo** tras pago de rendimientos/intereses; 11,181 =
  CAPITAL_RETURN/YIELD_PAYMENT (fix de Aurum, DONE); 3,393 = saldo final incorrecto por ingesta (TO DO);
  841 = cuentas sin movimientos con saldo 0 en AC (TO DO); 2 casos puntuales.
- **Diff Tasa 2,110:** tasas mal configuradas en AC — **producto 2019 = 2,053 casos**, 2015=38,
  2004=12, 2005=6, 2002=1. Causa: configuración de tasas (FINSUS).

## Implicaciones para la validación
- **Candidatos a hallazgo:** BUG del API (2,977 cuentas fantasma en AC), tasa 2019 mal configurada
  (2,053), diff de saldo por ingesta (4,236 TO DO). Ver CANDIDATOS.
- **Exclusión de diseño:** sucursal 201 (fondeadora) sale del universo comparable (Fase 1 del plan).
- El diff de saldo **propaga al ISR de inversiones** (K-FIS-003): mismo cliente, saldo distinto → ISR distinto.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-16 | Creada desde F-013. | F-013 |
