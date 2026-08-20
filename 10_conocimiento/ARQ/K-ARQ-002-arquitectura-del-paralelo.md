---
id: K-ARQ-002
titulo: Arquitectura del paralelo — gateway doble core, OpenFin primario, switch a Aurum
dominio: ARQ
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:05:30-00:06:31"
    hablante: "SPEAKER_05 (rol: contexto técnico del paralelo; nombre inferido 'Juan')"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:52:45"
    hablante: "SPEAKER_05"
relaciones:
  refina: [K-ARQ-001]
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Todas las operaciones de los canales (FinsusApp, Web Banking) entran a un **gateway
—construido por el equipo de Citi—** que las **deriva a ambos cores** (OpenFin y Aurum). Durante
el paralelo, el **core primario y autorizador es OpenFin**.
  → fuente: F-001 @00:05:30 (SPEAKER_05)

## Detalle
- [CONFIRMADO] Plan de corte: si la decisión del **1-sep-2026** es proceder, el **1-oct-2026** se
  cambia el switch y **Aurum pasa a primario/autorizador**; OpenFin seguiría recibiendo para
  tener switchback. → @00:05:30, @00:52:45.
- [CONFIRMADO] Deadline **7-sep-2026** para "demostrar que la operación existe, calcula y
  funciona". Proyecto lleva ~3.5 años. → @00:00:03 (SPEAKER_04). **Cierra parte de P-003.**
- [INFERIDO] Como OpenFin autoriza, el saldo que ve el cliente sale de OpenFin; esto origina
  descuadres intradía cuando un proceso ya cayó en OpenFin y aún no en Aurum (ver K-TMP-001).

## Implicaciones para la validación
- El punto de captura para comparar A vs B es el gateway (misma operación a ambos). El oráculo (C)
  no depende del gateway: recibe extracciones de cada core.
- La ventana OpenFin-primario (hasta ~1-oct) explica por qué muchas diferencias son de **saldo/
  sincronía**, no de cálculo (ver K-TMP-001, K-PRC-001).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
