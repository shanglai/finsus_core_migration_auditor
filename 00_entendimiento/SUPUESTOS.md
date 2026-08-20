# Supuestos vigentes

Registro de supuestos `[SUPUESTO]` y su exposición: qué conclusiones caen si resultan falsos
(formato Anexo A.3 del CLAUDE.md). Un supuesto no es un hueco ignorado: es un hueco señalizado
con su impacto visible.

> Al arranque sólo existen los supuestos declarados en el §0 del propio CLAUDE.md. No provienen de
> una fuente del proyecto; son supuestos de arranque del documento.

### S-001 — [RESUELTO 2026-08-14] El core destino se referencia como `<CORE_NUEVO>`
- Estado: RESUELTO → el core destino es **AurumCore** (Aurum). → K-ORG-001, cierra P-001.
- Confirmado por F-002/F-003/F-008 (procesadas). Ya no es supuesto.
- Pendiente editorial: sustituir el placeholder `<CORE_NUEVO>` por "AurumCore" en el CLAUDE.md
  (cambio del charter; se deja como recomendación, no se aplica en silencio).

### S-002 — El oráculo se implementa en Python 3.11+ con `decimal.Decimal`; validaciones en SQL ANSI
- Estado: VIGENTE · Creado: 2026-08-14 · Dominio: ARQ
- Por qué se asume: CLAUDE.md §0.
- Qué depende de esto: todo `30_oraculo/` y `40_validaciones/`.
- Qué lo confirma o refuta: decisión de arquitectura del proyecto.
- Impacto si es falso: MEDIO — cambia el stack, no las reglas.

### S-003 — Idioma de trabajo: español de México; identificadores sin acentos ni ñ
- Estado: VIGENTE · Creado: 2026-08-14 · Dominio: ORG
- Por qué se asume: CLAUDE.md §0.
- Qué depende de esto: convención de nombres de archivos e identificadores.
- Impacto si es falso: BAJO.

### S-004 — La entidad es una SOFIPO mexicana (CNBV, Ahorro y Crédito Popular)
- Estado: VIGENTE · Creado: 2026-08-14 · Dominio: REG
- Por qué se asume: CLAUDE.md §0.
- Qué depende de esto: el marco regulatorio y fiscal (REG, FIS).
- Qué lo confirma o refuta: constancia societaria / regulatoria de la entidad.
- Impacto si es falso: ALTO — cambia el marco normativo aplicable a la validación regulatoria.
