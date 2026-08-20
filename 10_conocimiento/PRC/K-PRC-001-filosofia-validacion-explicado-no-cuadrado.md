---
id: K-PRC-001
titulo: Filosofía de validación — "explicado al 100%, no cuadrado al 100%"; tercero independiente
dominio: PRC
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:07:32-00:08:56"
    hablante: "SPEAKER_05 (Juan)"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:26:48-00:28:32"
    hablante: "SPEAKER_02 (David, inferido)"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:57:37"
    hablante: "SPEAKER_08 (Giancarlo/Yanko)"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] La premisa oficial del ejercicio: **no se busca que los cores cuadren al 100%, sino
que las diferencias estén explicadas al 100%**; y como OpenFin no es fuente confiable, se necesita
un **tercero independiente** que calcule según la norma para arbitrar. Esto **es exactamente el
Motor C** del CLAUDE.md.
  → fuente: F-001 @00:08:32 (SPEAKER_05); @00:28:33 (SPEAKER_04)

## Detalle (métodos acordados/propuestos en la sesión)
- [CONFIRMADO] **Conciliación en ventanas de tiempo con delta** y a distintas amplitudes; medir el
  % de diferencia y ver si a ventanas mayores las pendientes cierran. → @00:26:48 (SPEAKER_02).
- [CONFIRMADO] **El neteo diario por cuenta debe ser 0**: aunque el nº de transacciones difiera
  (por reversos/no-atomicidad), el saldo del cliente no debe moverse. → @00:27:47, @00:31:45.
  (Esto es una **identidad candidata a invariante**, familia A del §10.)
- [CONFIRMADO] **Roll-forwards** por ventanas. → @00:32:16 (SPEAKER_02).
- [CONFIRMADO] **"Explicación diaria, no conciliación diaria"**: árbol de decantación de
  casuísticas (se hizo manual ~10 días; se busca automatizar). → @00:57:37 (SPEAKER_08).
- [CONFIRMADO] Universos comparables: acotar "peras con peras" quitando casuísticas que no aplican.
  → @00:34:26 (SPEAKER_10).

## Objetivo declarado (SPEAKER_04, @00:30:34) — orden de demostración
1. Aurum **se come todas** las transacciones (no deja ninguna afuera).
2. Caen bien **operativamente** (se registran donde deben).
3. Caen bien **contablemente** (cuenta contable por producto).
4. **Calcula correctamente** (devengamiento, rendimiento, ISR).

## Implicaciones para la validación
- Alinea 1:1 con el patrón de invariantes del §10 (familias A/B/C/D). El neteo-cuenta=0 y el
  roll-forward por ventana son los primeros invariantes a escribir.
- El oráculo (C) provee el paso 4 ("calcula bien") de forma independiente.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
