---
id: K-ARQ-001
titulo: Inventario de sistemas del ecosistema Finsus (AS-IS) y coexistencia de dos cores
dominio: ARQ
estado: CONFIRMADO
confianza: media          # proviene de un diagrama (pptx); §7.4 exige corroborar con datos/codigo
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/docs/Datos Cliente UnicoV2.pptx
    ubicacion: "láminas 3-6 (AS-IS y Fase 0/1)"
    hablante: "—"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] En el ecosistema Finsus (AS-IS) **coexisten dos cores bancarios**: **OpenFin**
(actual) y **Aurum / AurumCore** (destino), integrados a través de una capa de **Middleware /
Gateway** y un componente **Analyzer**, junto con sistemas satélite.
  → fuente: 20_fuentes/docs/Datos Cliente UnicoV2.pptx, láminas 3-6

## Detalle
Sistemas nombrados explícitamente en las láminas (sólo lo visible):
- **Cores:** Core Bancario (OpenFin) · Core Bancario (Aurum).
- **Integración/datos:** Middleware · Gateway · Analyzer · Cliente Único · F1.
- **Satélites:** ERP / Dynamics · Simetrik · AODB · Card Manager (Pomelo) · WebBanking ·
  FinsusApp · Reportes Unificados · Estados de Cuenta.
- **Plataforma de datos (lámina 7):** capas **BRONZE / SILVER / GOLD**, Data Quality,
  Streaming Analytics, BI & Reports, Data Science & ML.
- El proyecto de la presentación es **"Cliente Único"** (Fase 0 en ejecución), que busca volver
  a Cliente Único la fuente central de información.

## Evidencia
> Lámina 4 (AS-IS): "Core Bancario (Openfin)", "Core Bancario (Aurum)", "ERP / Dynamics",
> "Simetrik", "AODB", "Card Manager (Pomelo)", "WebBanking", "FinsusApp", "Gateway", "F1".

## Implicaciones para la validación
- El punto de comparación openfin↔Aurum pasa por Middleware/Analyzer; el linaje de datos para
  comparar (DAT) debe rastrear ahí. [PENDIENTE] confirmar qué sistema es la fuente de cada dato.
- Simetrik aparece como sistema de conciliación del ecosistema — relevante para las familias de
  validación contable (revisar relación con el oráculo, no depender de él como verdad).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-002 (pptx Cliente Único). | F-002 |
