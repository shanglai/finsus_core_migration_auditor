---
id: K-MIG-002
titulo: "Día cero" (2-ago-2026) e ingestas on-demand DB→DB para recuadrar
dominio: MIG
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:40:10 y @00:56:37"
    hablante: "SPEAKER_05 (Juan) / SPEAKER_08 (Giancarlo/Yanko, inferido)"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:41:31 y @01:06:34"
    hablante: "SPEAKER_03 / SPEAKER_10"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El **"día cero" fue el 2-ago-2026**: se ingestaron todos los movimientos y saldos
para que agosto **naciera cuadrado** en ambos cores (el pago de rendimientos del 31→1 se hizo
antes). A partir de ahí aparecen descuadres que se resuelven con **ingestas on-demand,
base-de-datos a base-de-datos**, con transformación de modelo de datos en medio.
  → fuente: F-001 @00:40:10 (SPEAKER_05), @00:56:37 (SPEAKER_08)

## Detalle
- [CONFIRMADO] Las ingestas son **on-demand, no calendarizadas** (no hay robot automático); se
  hacen cuando se investiga una transacción. Se busca volverlas diarias. → @00:41:31 (SPEAKER_03).
- [CONFIRMADO] La **migración de la información viva** OpenFin→Aurum (modelos de datos distintos)
  es "el mayor dolor", más que la prueba transaccional. → @00:37:52 (SPEAKER_10).
- [CONFIRMADO] Propuesta en la sesión: otro "día cero" **sábado→domingo**, cerrar la base (no
  ingestar) y correr una semana limpia para observar operación real. Juan coordina. → @01:06.

## RIESGO METODOLÓGICO (crítico)
[CONFIRMADO] SPEAKER_10 (@01:01:54) advierte: **un reporte sobre la totalidad de datos NO prueba
que Aurum calcula**, porque el grueso fue **ingestado** (datos traídos ya calculados). La prueba
de cálculo real se hizo con **transacciones vivas de muestra** nacidas desde la app en A y B.
  → Implica: para el oráculo, distinguir **dato calculado por el core** de **dato ingestado**.

## Implicaciones para la validación
- Las ventanas de comparación deben ubicarse **entre ingestas** (donde el core sí operó), o
  aislar explícitamente los registros ingestados. Una ingesta "recuadra" y borra la señal de
  descuadre → puede ocultar defectos.
- El oráculo debe marcar el linaje: calculado-por-core vs ingestado. (Refuerza P-004.)

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
