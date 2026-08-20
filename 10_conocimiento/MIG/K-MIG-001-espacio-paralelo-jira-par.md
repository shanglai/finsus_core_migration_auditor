---
id: K-MIG-001
titulo: El "Espacio Paralelo AurumCore" se gestiona en Jira (proyecto PAR)
dominio: MIG
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/docs/OnePager JIRA Espacio Paralelo AurumCore.pdf
    ubicacion: "p.1 (indicadores) y nota de alcance"
  - ref: 20_fuentes/datos/JIRA - PARALELO AURUMCORE.xlsx
    ubicacion: "hoja 'JIRA - PARALELO AURUMCORE 12Ago' (331 filas de folios)"
  - ref: 20_fuentes/datos/JIRA Espacio Paralelo AurumCore 11082026.xlsx
    ubicacion: "hoja 'Resumen Ejecutivo'"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Existe un ejercicio de operación en paralelo openfin↔AurumCore cuyas incidencias se
registran en **Jira, proyecto PAR** ("Paralelo AurumCore"). Al corte 12-ago-2026 hay **331
folios** históricos (desde 01-ene-2026).
  → fuente: F-003 (hoja 12Ago, 331 filas), F-008 (OnePager)

## Detalle (cifras al corte, citando la fuente)
- Corte **10-ago** (F-008): 331 totales = 205 finalizados + 124 activos + 2 cancelados.
  Backlog activo: 63 revisión · 29 en curso · 32 por hacer. 49 High/Highest. 16 vencidos.
  108 sin fecha. 103 con antigüedad > 30 días. Lectura PMO: **RIESGO ALTO**.
- Corte **11-ago** (F-006/F-007): mismos encabezados; "fuente de verdad: consulta directa de Jira".
- Corte **12-ago** (F-003): 331 folios.
- Dominios del paralelo (F-008): **Captación 47 · Crédito 45 · SPEI 22 · Onboarding 8 · TDD/TDC 2**
  (= 124 activos al 10-ago).
- **Conciliación advertida por la propia fuente** (F-008): el dashboard informaba 266 totales vs
  331 por JQL directo (+65 sin confirmar); "abiertos" 132 informados vs 124 activos. No se
  resuelve en la fuente → ver P-005.

## Relación con este proyecto (importante)
El Jira PAR es la vista del **equipo de proyecto** sobre las discrepancias. Es un **mapa de dónde
buscar**, NO la verdad de negocio ni un sustituto del Motor C. Sus folios "Finalizada" no
acreditan cierre por sí solos (ver K-MIG-003). Cada caso material es **candidato a hallazgo** a
verificar de forma independiente con el oráculo (§1, §9.1 del CLAUDE.md).

## Implicaciones para la validación
- El backlog PAR alimenta el **mapa de riesgo** (ENTENDIMIENTO_GLOBAL §9) y la priorización.
- La distribución por dominio orienta qué dominios de §8 poblar primero (Captación/Crédito/SPEI).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-003/F-006/F-007/F-008. | F-003, F-008 |
