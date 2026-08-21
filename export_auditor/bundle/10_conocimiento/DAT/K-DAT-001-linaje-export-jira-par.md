---
id: K-DAT-001
titulo: Estructura y linaje del export de Jira PAR (columnas por folio)
dominio: DAT
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/datos/JIRA - PARALELO AURUMCORE.xlsx
    ubicacion: "hoja 'JIRA - PARALELO AURUMCORE 12Ago', fila 1 (encabezados)"
  - ref: 20_fuentes/datos/JIRA Espacio Paralelo AurumCore 11082026.xlsx
    ubicacion: "hoja 'Detalle Folios' (335 filas)"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: medio
---
## Enunciado
[CONFIRMADO] El export de Jira PAR trae, por folio, las columnas: **Folio · Apertura · Resumen ·
Tipo · Prioridad · Estatus · Categoría estatus · Asignado a · Reportado por · Vencimiento ·
Resolución · Actualizado · Etiquetas · Activo · Sin fecha activa · Días de vida · URL Jira**.
  → fuente: F-003, F-006/F-007

## Detalle
- Columnas derivadas por **fórmula** en el archivo (no vienen de Jira): `Activo`
  (`=IF(OR(Estatus="En curso","EN REVISIÓN","Tareas por hacer"),"Sí","No")`), `Sin fecha activa`,
  `Días de vida` (`=IF(Vencimiento<>"",Vencimiento-Apertura,DATE(2026,8,11)-Apertura)`). El
  ancla de "hoy" en la fórmula está **fijada a 2026-08-11**, no es dinámica (§7.3: leer fórmulas).
- `Tipo` incluye `Epic` (las épicas PAR-1..PAR-4 nombran los dominios Captación/Crédito/SPEI/
  Onboarding). El dominio de un folio se determina por la épica padre (F-008, anexo).
- `Reportado por` = quién detecta; `Asignado a` = quién atiende (F-008).

## Implicaciones para la validación
- Estas son columnas del **tracking**, no del core. No confundir con el modelo de datos de
  openfin/AurumCore (ese linaje sigue [PENDIENTE], ver P-004/DAT).
- El ancla de fecha fija (2026-08-11) implica que "Días de vida" no se recalcula solo al reabrir
  el archivo; cuidarlo si se reusa el libro.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-003/F-006/F-007. | F-003 |
