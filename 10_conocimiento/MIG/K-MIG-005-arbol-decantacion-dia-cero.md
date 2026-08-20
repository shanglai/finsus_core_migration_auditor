---
id: K-MIG-005
titulo: Árbol de decantación día cero (02-03 ago) — metodología y estado global
dominio: MIG
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-16
actualizado: 2026-08-16
fuentes:
  - ref: 20_fuentes/datos/analisis_arboles_20260803/Árboles - Día Cero.xlsx
    ubicacion: "hojas Árboles, CRITERIO-CAUSA, RCA-CAUSA, Asignaciones"
relaciones:
  refina: [K-PRC-001, K-MIG-002]
  depende_de: []
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Existe un **árbol de decantación** que compara OpenFin vs AurumCore por dominio al
corte **02-03 ago 2026**, dividiendo cada universo en **En común / Único AC / Único OF** y, dentro
del común, **Diff** por dimensión acumulativa; cada Diff se explica con **causas (RCA)** y se
asigna a un responsable/estatus.
  → fuente: F-013 (Árboles - Día Cero.xlsx)

## Metodología (confirmada)
- **Criterio acumulativo**: se parte de la llave (ID cliente + ID cuenta/inversión) y se van
  agregando dimensiones (saldo → tasa → rendimiento → ISR), midiendo el % que sigue cuadrando.
- Cada renglón Diff/Único trae `# identificado`, `# explicado`, `% explicado` y hasta N causas.
- Hoja **RCA-CAUSA**: por causa → IMPACTO, CAUSA, SOLUCIÓN, QUIEN, ESTATUS (TO DO/DONE/N-A).
- Hoja **Asignaciones**: ~970 renglones de pares de cuentas contables (tipo tx origen→destino) con
  su descuadre, % y remediación, por analista.

## Naturaleza de la fuente (importante)
- Es la **reconciliación del equipo Finsus/Aurum (motores A vs B)** con **su propio** análisis de
  causa. **No es el oráculo (C).** Muchas causas se auto-justifican ("se mitiga al cambio de core",
  "N/A DONE"). Se toma como **mapa de dónde están las diferencias y candidatos a hallazgo**, a
  verificar independientemente.
- Confirma con datos reales varias cifras que en F-001 sólo venían por ASR (P-009 parcialmente cerrada).

## Estado global al corte (ver detalle en ANALISIS_ARBOLES.md)
- **Clientes:** 956,332 comparables, prácticamente 100% en común.
- **Cuentas vista:** 2,046,969 en común; 97.9% cuadra con saldo y tasa.
- **Inversiones:** 18,599 en común; **el mayor gap es ISR (≈27% con diferencia)**.
- **Créditos 5004:** 7,619 en común, **cuadran 100%** en tasa/monto/fecha/pagado.
- **Transacciones (2-ago):** 32,539 en común; 524 únicas AC, 182 únicas OF.

## Implicaciones para la validación
- Es el punto de partida real de las Fases 2 y 7 del plan. Las causas se mapean a la matriz de
  clasificación del charter (§11): muchas son `DIFERENCIA_DISENO_AUTORIZADA`, varias `DEFECTO_*`.
- Cada Diff numérico es un **invariante candidato** y un **candidato a hallazgo** (ver CANDIDATOS).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-16 | Creada desde F-013. | F-013 |
