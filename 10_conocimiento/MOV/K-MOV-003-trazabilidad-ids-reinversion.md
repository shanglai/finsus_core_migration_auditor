---
id: K-MOV-003
titulo: Pérdida de trazabilidad 1:1 — reinversiones generan ID propio en cada core
dominio: MOV
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:21:54-00:22:53"
    hablante: "SPEAKER_10 (Néstor, inferido)"
relaciones:
  refina: []
  depende_de: [K-ARQ-002]
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Una inversión tiene un **ID único en el gateway** (compartido por ambos cores), pero
las **reinversiones las procesa cada core por separado y genera un ID propio** → se pierde la
relación 1:1 entre la operación de un core y la del otro.
  → fuente: F-001 @00:21:54 (SPEAKER_10)

## Detalle
- El detalle 1:1 sólo se tiene resuelto hoy para **SPEI**; para el resto se hace "por indagatoria"
  (siguiendo secuencias, montos y tracking de saldos). → @00:21:08 (SPEAKER_09).
- No existe (aún) un robot que identifique exactamente qué operación faltó fuera de SPEI.

## Implicaciones para la validación
- **DAT/llaves de correlación (P-004):** para reinversiones no hay llave común entre A y B tras la
  primera generación; el comparador necesita una **llave sustituta** (cliente + producto + monto +
  ventana temporal) o reconstruir la cadena de reinversión.
- Riesgo: sin llave 1:1, un descuadre puede ser falso positivo (misma reinversión con IDs
  distintos). El oráculo debe modelar la cadena de reinversión, no comparar por ID.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
