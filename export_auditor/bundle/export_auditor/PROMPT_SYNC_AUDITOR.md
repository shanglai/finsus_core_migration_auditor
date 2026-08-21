# PROMPT ADICIONAL — Sincronización hacia el Auditor Independiente

> Regla de comportamiento permanente para las sesiones de **este** repo (el de validación). Define cómo se
> propaga cualquier novedad hacia el repo del Auditor, con **fuente única** (decisión C). Léelo junto con
> `CLAUDE.md §6.2` (propagación) y `40_validaciones/PROMPT_CONSTRUCTOR_VALIDADOR.md`.

## Principio: fuente ÚNICA
`40_validaciones/NORTE_VALIDACION.md` es **la única fuente de verdad** — sirve a la vez como (a) panorama
humano y (b) **catálogo de casos** del auditor. **No** se mantiene un catálogo paralelo. El
`PROMPT_CONSTRUCTOR_VALIDADOR.md` **apunta** al NORTE; no lo duplica.

## Regla de propagación (al cerrar cualquier análisis)
Cuando una sesión genera un caso o insight nuevo, en el MISMO turno:
1. **Pieza de conocimiento** (`10_conocimiento/`) — la regla/norma. Sube versión si cambió.
2. **NORTE** — fila del caso en la matriz maestra (id, motor, regla-pieza, código/SQL, dato/localizador,
   **estado**). El NORTE es el catálogo del auditor.
3. **Código/SQL** — el comparador/oráculo/query en `40_validaciones/…` (reutilizar, no duplicar).
4. **Si es hallazgo confirmado** → convertirlo en **invariante de regresión permanente** (no all-pass).
5. **Bitácora** — registrar el delta del día.

## Regla de exportación al repo del auditor
Cuando haya novedades relevantes para el auditor (caso nuevo, oráculo/comparador nuevo, regla cambiada,
hallazgo confirmado):
1. Correr `python export_auditor/ensamblar.py` → regenera `export_auditor/bundle/` + `BUNDLE_MANIFEST.md`.
2. Anotar en `export_auditor/MANIFEST.md` (changelog) **qué cambió** desde el export anterior — en lenguaje
   que le diga a la sesión del auditor **qué re-correr / re-sincronizar**.
3. Copiar `export_auditor/bundle/` al repo del auditor (paso manual del usuario, o el que se defina).
4. En la sesión del auditor: leer el changelog → actualizar los `catalogo/*.yaml` de los casos nuevos/cambiados,
   re-correr los afectados, y actualizar su `cobertura.md`.

## Seguridad (dura)
El bundle **NUNCA** lleva credenciales (`db_connections.yaml`), PII, `landing/`, `_resultados/` ni datos
(`*.parquet`/CSV). `ensamblar.py` los excluye; `bundle/` es gitignored. Si un archivo nuevo debe exportarse,
agregarlo a la lista blanca `INCLUYE` de `ensamblar.py`, nunca relajar la lista `PROHIBIDO`.

## Qué NO hacer
- No mantener dos catálogos (NORTE + otro). Un caso vive en el NORTE; el auditor lo espeja.
- No exportar resultados ni credenciales "por conveniencia".
- No marcar un caso como OK en el NORTE si no se corrió (no-corrido ≠ aprobado).
