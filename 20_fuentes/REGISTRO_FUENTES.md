# Registro de Fuentes

Inventario de todo lo que entra a `20_fuentes/`. Carpeta **inmutable**: nunca se edita el
original. Estado de procesamiento: `SIN_PROCESAR` → `EN_PROCESO` → `PROCESADA`.

> Regla: ninguna fuente se lee "de pasada". Primero se registra aquí (§7.0 paso 1 del CLAUDE.md).
> Flujo de intake: los archivos llegan a `/landing/`, se registran, se **mueven** a `20_fuentes/`
> (store inmutable) y se procesan. `/landing/` queda como bandeja vacía para el siguiente lote.

| id | ruta | tipo | fecha contenido | recibida | aportada por | hash (sha256, 16c) | estado |
|----|------|------|-----------------|----------|--------------|--------------------|--------|
| F-001 | v2t/finsus_assessment_20260814_01/ | v2t | 2026-08-14 | 2026-08-14 | [PENDIENTE] (estaba en el repo al arranque) | e5e442b7e5243505 | PROCESADA |
| F-002 | docs/Datos Cliente UnicoV2.pptx | pptx | [PENDIENTE] (sin fecha en el archivo) | 2026-08-14 | usuario (landing/) | 6875eb7438e664e0 | PROCESADA |
| F-003 | datos/JIRA - PARALELO AURUMCORE.xlsx | xlsx | 2026-08-12 (corte "12Ago") | 2026-08-14 | usuario (landing/) | afea212d2dcf5183 | EN_PROCESO |
| F-004 | datos/JIRA Espacio Paralelo AurumCore (comparativo por día).xlsx | xlsx | 2026-08-11 (comparativo 10 vs 11 ago) | 2026-08-14 | usuario (landing/) | 43305348a3d05d7f | PROCESADA |
| F-005 | docs/JIRA Espacio Paralelo AurumCore (evidencias) 11082026.pdf | pdf | 2026-08-11 | 2026-08-14 | usuario (landing/) | 203f148f97595ee6 | PROCESADA |
| F-006 | datos/JIRA Espacio Paralelo AurumCore 10082026.xlsx | xlsx | 2026-08-11 (corte interno "11-ago"; nombre dice 10) | 2026-08-14 | usuario (landing/) | 0e5db9dc0a0f2740 | EN_PROCESO |
| F-007 | datos/JIRA Espacio Paralelo AurumCore 11082026.xlsx | xlsx | 2026-08-11 | 2026-08-14 | usuario (landing/) | bfbe78ea5dc28806 | EN_PROCESO |
| F-008 | docs/OnePager JIRA Espacio Paralelo AurumCore.pdf | pdf | 2026-08-10 (corte) | 2026-08-14 | usuario (landing/) | 77633cec89824eb3 | PROCESADA |
| F-009 | docs/GTM-Pago de Rendimientos-140826-230050.pdf | pdf | 2026-08-07 (v1.0) | 2026-08-14 | usuario (landing/) | 11af95ea28be7496 | PROCESADA |
| F-010 | datos/ISR - Caso 100-10-233102.xlsx | xlsx | 2026-08-02 (cierre del caso) | 2026-08-14 | usuario (landing/) | 1eda5b2f5ae6ab13 | PROCESADA |
| F-011 | v2t/finsus_assessment_02_20260814/ | v2t | 2026-08-14 | 2026-08-15 | usuario (landing/) | 999fb279f9e82c39 | PROCESADA |
| F-012 | datos/Inventario_Queries_AurumCore.xlsx | xlsx | 2026-08 | 2026-08-16 | usuario (landing/) | 0989815d35763f1d | PROCESADA |
| F-013 | datos/analisis_arboles_20260803/ (120 arch, ~1.5 GB, **gitignored**) | datos | 2026-08-02/03 | 2026-08-16 | usuario (landing/) | — (ver MANIFEST) | PROCESADA (nivel ejecutivo) |
| F-014 | datos/aurum_columnas.csv + aurum_tablas.csv | datos (metadatos) | 2026-08-16 | 2026-08-16 | usuario (landing/) | 14005ad691a20294 / f77af5c62fc386b4 | PROCESADA |
| F-015 | datos/openfin_columnas.csv + openfin_tablas.csv | datos (metadatos) | 2026-08-17 | 2026-08-17 | usuario (landing/) | — | PROCESADA |
| F-016 | docs/motores/ (4 PDFs AurumCore: Pago de Rendimientos v1.0, Saldo Promedio, Ciclos Transaccionales, Intereses de Créditos; **confidenciales, gitignored**) | docs | 2026-06/08 (v1.0 rendimientos 7-ago-2026) | 2026-08-18 | usuario (landing/) | — | PROCESADA (FIS/DEV; MOV/COL parcial) |
| F-017 | v2t/finsus_assessment_revision_20260817/ (conversación con Finsus post-Fase 0; **gitignored**) | v2t | 2026-08-17 | 2026-08-18 | usuario (landing/) | a553063c | PROCESADA |
| F-018 | docs/motores/puntos_validacion.jpeg (checklist de puntos de validación de motores 2.1.1–2.1.12; **gitignored**) | docs (imagen) | 2026-08-19 | 2026-08-19 | usuario (landing/) | — | PROCESADA |
| F-019 | docs/motores/GTM-Pago de Rendimientos-190826-000749.pdf (**actualiza F-016**: corrige la proporción ISR a ÷saldo_total; **gitignored**) | docs | 2026-08-19 | 2026-08-19 | usuario (landing/) | — | PROCESADA |
| F-020 | docs/motores/GAP_Analysis_Motores.pdf (análisis de Finsus: 5 motores regulatorios faltantes vs CNBV/Banxico/SAT/LACP; **gitignored**) | docs | 2026-08-19 | 2026-08-19 | usuario (landing/) | — | PROCESADA (nivel comentario; verificación normativa pendiente) |
| F-021 | v2t/finsus_assessment_03_20260819 (sesión Finsus↔Linko: presentación de hallazgos Fase 0/1 + **nueva encomienda**; 1h31; 7 SPEAKERS; 10 frames; **gitignored** — PII/interno) | v2t | 2026-08-19 | 2026-08-19 | usuario (landing/) | — | PROCESADA (ficha `_derivados/2026-08-19_assessment03_ficha.md`) |
| F-022 | v2t/finsus_assessment_03_bis_20260819 (continuación: saldo promedio + motor diario con Sergio; 18min; **gitignored**) | v2t | 2026-08-19 | 2026-08-19 | usuario (landing/) | — | PROCESADA (misma ficha) |
| F-023 | docs/motores/Linko - AurumCore.pdf ("Observaciones Linko": **respuesta oficial de AurumCore a los 5 gaps** de F-020; 11 pág, últ.ed. 7-ago-2026; **gitignored** — confidencial AurumCore) | docs | 2026-08-07 | 2026-08-19 | usuario (landing/) | — | PROCESADA |
| F-024 | datos/queries_finsus/queries seguimiento diario.docx (queries de día cero/diario de Finsus: captación, créditos, cuentahabientes, inversiones, saldos, general; **referencia, NO fuente de verdad**; **gitignored** — **contiene credenciales en claro**) | datos | 2026-08-19 | 2026-08-19 | usuario (landing/) | — | PROCESADA (evaluación; ref. redactada en `40_validaciones/extraccion/REFERENCIA_queries_diario_finsus.md`) |
| — | (dup) Datos Cliente UnicoV2.pptx | pptx | — | 2026-08-14 | usuario (landing/) | 6875eb7438e664e0 | DUPLICADO de F-002 (mismo hash); no reingresado |
| — | (dup) finsus-assessment-...-6452c817 | v2t | — | 2026-08-15 | usuario (landing/) | e5e442b7e5243505 | DUPLICADO de F-001 (venía junto a F-011); no reingresado |

Derivados de extracción (mecánicos, sin interpretación) en
`20_fuentes/docs/_derivados/` y `20_fuentes/datos/_derivados/`.

## Notas por fuente

### F-001 — finsus_assessment_20260814_01
- Conferencia diarizada (`.md`) + `segments.json` + 13 screenshots. `duration 01:10:48`, es,
  `generated_by video2doc v0.1`, `generated_at 2026-08-14T21:16:39Z`.
- Hablantes diarizados `SPEAKER_00..10` + `UNKNOWN`, **sin nombres reales mapeados** (P-002).
- **PROCESADA 2026-08-14.** Ficha: `_derivados/2026-08-14_kickoff-tercero-independiente_ficha.md`.
  Sustenta 11 piezas (K-ARQ-002, K-TMP-001, K-DEV-001, K-MOV-001/002/003, K-FIS-001, K-MIG-002/004,
  K-PRC-001, K-ORG-003). Los 13 screenshots son galería de Teams (no capturaron el dashboard);
  las cifras del "día cero" quedan como narradas/no verificadas (P-009).

### F-002 — Datos Cliente UnicoV2.pptx
- 7 láminas. Proyecto **"Cliente Único"**: arquitectura del ecosistema Finsus (AS-IS) y fases
  0/1, más arquitectura de datos Bronze/Silver/Gold. Sustenta K-ARQ-001.
- Sin fecha ni notas de presentador detectadas. Confianza de diagramas: `media` (§7.4).

### F-003 — JIRA - PARALELO AURUMCORE.xlsx
- Export Jira del proyecto **PAR** ("Paralelo AurumCore"), corte 12-ago. Hojas:
  `JIRA...12Ago` (con fórmulas), `JIRA...12` (valores), `Comparativo 12Ago`. 331 folios.
- Columnas: Folio, Apertura, Resumen, Tipo, Prioridad, Estatus, Categoría estatus, Asignado a,
  Reportado por, Vencimiento, Resolución, Actualizado, Etiquetas, Activo, Sin fecha activa,
  Días de vida, URL Jira. Sustenta K-DAT-002, K-MIG-001.
- Estado `EN_PROCESO`: capturada estructura y ejecutivo; **no** atomizados los 331 folios uno a uno.

### F-004 — comparativo por día
- Cambios de estatus entre corte 10-ago (adjunto) y Jira al 11-ago. 24 folios cambiaron.
  205→218 finalizados (+13); 124→111 activos (-13). Sustenta K-MIG-003.

### F-005 — evidencias 11082026.pdf
- Análisis de calidad de evidencia de 24 folios: avance operativo 54.2% vs avance integral
  verificable 20.8%. Sustenta K-MIG-004.

### F-006 / F-007 — cortes 10/11 ago
- Export Jira PAR con hojas `Resumen Ejecutivo`, `Consolidado Responsable`, `Detalle Folios`
  (335 filas ≈ 331 folios + encabezados) y, en F-006, `Comparativo 10-11 ago`.
- **Discrepancia de nombre:** F-006 se llama `...10082026` pero su corte interno dice "11-ago".
  Registrada tal cual, no se corrige (posible etiquetado). Estado `EN_PROCESO`.

### F-008 — OnePager
- OnePager directivo, "FINSUS · Confidencial", corte 10-ago. Indicadores de control, casos
  críticos con impacto monetario/masivo, backlog por dominio y responsables. 4 páginas.
  Sustenta K-MIG-001, K-ORG-002 y los K de casos críticos (FIS/DEV/MOV/DAT).

### F-009 — GTM Pago de Rendimientos (documentación oficial AurumCore)
- Documento técnico (v1.0, 7-ago-2026, autor "Tech") con las **reglas de cálculo**: rendimientos
  de cuentas a la vista, rendimientos de inversiones a plazo fijo, y **retención de ISR**.
  Incluye fórmulas, criterios de elegibilidad, truncamientos/redondeos y ejemplos numéricos.
- **Fuente normativa/técnica del core destino** → base directa para el oráculo (Motor C).
  Sustenta K-DEV-001 v2, K-DEV-002, K-DEV-003, K-FIS-002.

### F-010 — ISR Caso 100-10-233102 (caso de validación)
- xlsx con un caso real: cliente [PII redactada] (id 100-10-233102), cierre 2026-08-02. Hoja "Validación ISR"
  con fórmulas que implementan la regla de ISR de F-009 y una sección "Transacciones AurumCore"
  con los movimientos posteados (Apertura de inversión, Retorno de Inversión, **ISR AurumCore**,
  Pago de rendimiento). Contiene URLs internas `admin-prod.aurum.finsus.mx`. ~800+ filas.
- Corrobora K-FIS-002 y aporta catálogo parcial de tipos de transacción (K-MOV-004).
- **Dato personal** (nombre de cliente, IDs de cuenta). Ver marca de confidencialidad.

### F-011 — Sesión de modelo de datos y queries de OpenFin (v2t)
- Sesión grabada (1h38, `a86e0f85`) donde el experto de OpenFin (Citi) explica al equipo externo
  el **modelo de datos de OpenFin** tabla por tabla y los **queries** de extracción. Es la fuente
  que **desbloquea P-004** (linaje, llaves, trazabilidad).
- 43 screenshots: **s009** capturó el deck (slide 3, ecosistema/fuente-de-verdad = mismo de F-002);
  **s020** capturó una consulta en SQuirreL SQL Client (`detalle_auxiliar ⋈ detalle_auxiliar_masdatos`
  por `secuencia`, base `openfin_aurum`, usuario `aurumcoreuser`). El resto son webcam/fondos.
- Sustenta K-DAT-002..006, K-MOV-005/006 y los apartados de `00_entendimiento/MODELO_DATOS_OPENFIN.md`.
- Contiene URLs/infra internas y menciona ambientes de producción — confidencial.

### F-012 — Inventario de queries de AurumCore
- 5 queries SQL de AurumCore (clientes, cuentas, inversiones, créditos 5004, transacciones). Revela
  el **modelo de datos de Aurum** (esquema `aurumcore`): tablas `accountholder`, `account`,
  `stored_value`, `account_scheme`, `account_yield`, `iv_account_commission`, `iv_payment_plan`,
  `lc_loan_contract`, `lc_products`, `lc_loan_charge`, `"transaction"`. **Cierra buena parte de P-011.**
  Sustenta K-DAT-006. Es SQL sin datos → se versiona.

### F-013 — Análisis árboles (reconciliación día cero 02-03 ago)
- Árbol de decantación OpenFin vs AurumCore por dominio (Clientes, Cuentas, Créditos, Inversiones,
  Transacciones) con universos En común / Único AC / Único OF / Diff (saldo, tasa, rendimiento, ISR,
  fecha) y un maestro `Árboles - Día Cero.xlsx` (hojas Árboles, CRITERIO-CAUSA, RCA-CAUSA, Asignaciones).
- **Es la reconciliación del equipo Finsus/Aurum (motor A vs B, con su propio RCA)** — no arbitraje
  independiente. Se usa como mapa y candidatos a hallazgo (a verificar con el oráculo C).
- Datos crudos ~1.5 GB con **PII de clientes** → **gitignored**; traza en
  `datos/analisis_arboles_20260803_MANIFEST.md`. Sustenta K-MIG-005, K-CAP-001, K-COL-001,
  K-FIS-003, K-MOV-007 y `00_entendimiento/ANALISIS_ARBOLES.md`.

### F-014 — Diccionario de datos y volumetría de AurumCore (metadatos)
- `aurum_columnas.csv`: **240 tablas / 3,529 columnas** del esquema `aurumcore` (information_schema).
  Es el diccionario de datos completo. `aurum_tablas.csv`: filas y peso por tabla (volumetría real).
- Sólo **metadatos** (nombres/tipos/conteos) — sin datos ni PII → se versiona.
- Volumetría destacada: `transaction` 38 GB / 31 M filas, `transaction_detail` 31 GB, `account`
  13 GB / 8.2 M, `finsus_account_history` 28 GB / 77.7 M, `authorization` 29 GB. **La base es de
  cientos de GB** → la extracción debe ir por ventanas de fecha, no full-scan.
- Scripts de extracción (con host/usuario internos) en `utils/extraccion_aurum/` (**gitignored**);
  método sanitizado en `utils/README_extraccion_aurum.md`. Sustenta K-DAT-006.

### F-015 — Diccionario de datos y volumetría de OpenFin t-1 (`openfin_aurum`, metadatos)
- `openfin_columnas.csv`: 39 esquemas; **public = 767 tablas / 6,308 columnas**. Cierra el
  diccionario de OpenFin (K-DAT-002 v3). `openfin_tablas.csv`: volumetría (detalle_auxiliar 65 GB,
  isr_diario 29 GB, isr_diario_aux_log 42 GB, oflog 43 GB…).
- Sólo metadatos, sin PII → versionado. Scripts en `utils/extraccion_openfin/` (gitignored).
- **Hallazgo:** OpenFin calcula ISR **diario** (`isr_diario`) — diferencia de modelo vs Aurum (al pago).

## Marca de confidencialidad
Las fuentes F-002..F-010 son confidenciales: contienen nombres de empleados, URLs internas
(Jira `finsus-digital.atlassian.net`, `admin-prod.aurum.finsus.mx`), impactos fiscales
cuantificados y, en **F-010, datos personales de un cliente** (nombre + IDs de cuenta). Ver
decisión de publicación en `90_bitacora/2026-08-14.md`. Esto refuerza no pushear al remoto sin
autorización explícita del alcance.

## Convención de ids
`F-###` en orden de recepción. Un `id` nunca se reasigna ni se reutiliza.

## Archivos con sufijo `(1)`, `(4)`, `(6)` — NO son duplicados (verificado 2026-08-20)

El sufijo entre paréntesis parece artefacto de re-descarga y tienta a borrarlos. Se
verificó por contenido y **no lo son**: comparando las partes de datos del `.xlsx`
(ignorando metadatos y orden interno del zip), estos pares **difieren en los datos**:

- `inversiones_openfin_20260803(1).xlsx` vs `inversiones_openfin_20260803.xlsx`
- `44_inversiones (1).xlsx` vs `Histórico/44_inversiones.xlsx`

Son **exportaciones distintas**, probablemente con filtros o cortes distintos. Se conservan
las dos. Antes de eliminar cualquiera, determinar cuál corresponde a qué corte y registrarlo
aquí — un archivo de evidencia borrado no se recupera.

Barrido de duplicados exactos (sha256) sobre todo el repositorio: el **único** duplicado
byte-idéntico era `oraculo_rendimientos.py` (huérfano en `comparadores/`, eliminado; ver
`30_oraculo/TRAZABILIDAD.md`). Los pares `.csv`/`.xlsx` del mismo dataset **no** son
idénticos: son el mismo dato en dos formatos y se conservan ambos.
