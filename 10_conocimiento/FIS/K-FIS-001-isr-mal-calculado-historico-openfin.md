---
id: K-FIS-001
titulo: Retención de ISR calculada incorrectamente "toda la vida" en OpenFin (corregida recientemente)
dominio: FIS
estado: CONFIRMADO
confianza: alta          # confirmado que se DIJO; la magnitud/alcance es [PENDIENTE]
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:08:32-00:08:56"
    hablante: "SPEAKER_05 (Juan, inferido)"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] En la sesión se afirma que **la retención de impuestos (ISR) se había calculado mal
en OpenFin "toda la vida"** y que **recientemente se modificó** tras compararlo contra fórmulas en
Excel.
  → fuente: F-001 @00:08:32 (SPEAKER_05)

## Detalle
- Es un ejemplo explícito de que **OpenFin no es base confiable** (motiva el Motor C).
- [PENDIENTE] Magnitud, universo afectado, fecha de la corrección y si hubo regularización a
  clientes/provisión. No se dio en la sesión.
- Conecta con el candidato **PAR-352** (vencimiento de inversión sin retención ISR, $2,232,566.46)
  del Jira PAR — posiblemente el mismo hilo o uno relacionado. Verificar.

## Implicaciones para la validación
- **Candidato a `DEFECTO_OPENFIN` histórico** — la cubeta incómoda y obligatoria (§11). Si el
  cálculo de ISR estuvo mal por años, implica decisión de Comité (replicar documentado vs
  regularizar con provisión). **Prohibido suavizarlo** (§14.9).
- El oráculo (C) debe implementar la retención de ISR **desde la norma** (LISR por verificar,
  marcar referencia normativa [PENDIENTE]) y contrastar contra A y B por separado.
- Prioridad máxima en el mapa de riesgo (ver ENTENDIMIENTO_GLOBAL §9).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
