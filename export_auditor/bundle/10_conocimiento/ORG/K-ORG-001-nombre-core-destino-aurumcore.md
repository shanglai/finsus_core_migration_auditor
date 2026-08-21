---
id: K-ORG-001
titulo: El core destino es AurumCore (Aurum); la migración es OpenFin → AurumCore
dominio: ORG
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/docs/OnePager JIRA Espacio Paralelo AurumCore.pdf
    ubicacion: "encabezado y cuerpo (p.1-4)"
  - ref: 20_fuentes/datos/JIRA - PARALELO AURUMCORE.xlsx
    ubicacion: "columna Resumen (p.ej. PAR-208, PAR-351: 'AurumCore')"
  - ref: 20_fuentes/docs/Datos Cliente UnicoV2.pptx
    ubicacion: "láminas 4-6 ('Core Bancario (Aurum)')"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: bajo
---
## Enunciado
[CONFIRMADO] El core destino (`<CORE_NUEVO>` en el CLAUDE.md) se llama **AurumCore**, referido
también como **Aurum**. El ejercicio migra de **OpenFin** a **AurumCore**.
  → fuente: F-008 (OnePager), F-003 (Jira PAR), F-002 (pptx)

## Detalle
- Grafías observadas: "AurumCore", "Aurum". Las tres fuentes coinciden.
- **Cierra P-001.** La transcripción F-001 (sin procesar) transcribía "AuronCore"; se explica
  como **ruido de ASR**, no como nombre alterno. No se promueve nada de F-001 hasta procesarla.
- Sustitución del placeholder `<CORE_NUEVO>` → **AurumCore** en el CLAUDE.md: es un cambio
  editorial del charter; se deja anotado como recomendación (ver bitácora), no se aplica en
  silencio.

## Implicaciones para la validación
- Nomenclatura del "Motor B" = AurumCore en todo el repo.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada; cierra P-001. | F-008, F-003, F-002 |
