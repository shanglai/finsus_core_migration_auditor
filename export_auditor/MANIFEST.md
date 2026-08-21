# export_auditor/ — paquete para el repo del Auditor Independiente

Esta carpeta es el **punto de exportación** hacia el repo donde vive (y se construye) el *Validador /
Auditor Independiente del motor C*. Aquí se ensambla, de forma reproducible, todo lo que ese repo necesita.

## Cómo se usa
```bash
python export_auditor/ensamblar.py      # arma export_auditor/bundle/ desde las fuentes de este repo
# luego: copiar export_auditor/bundle/  al repo del auditor
```
`ensamblar.py` copia la **lista blanca** (ver el script) preservando estructura y regenera
`bundle/BUNDLE_MANIFEST.md` con hash de cada archivo → así se **detecta qué cambió** entre exports.

## Qué contiene el bundle (resumen)
- **`PROMPT_CONSTRUCTOR_VALIDADOR.md`** — el brief con el que el auditor se construye.
- **`NORTE_VALIDACION.md`** — **fuente única** (panorama + catálogo de casos; decisión C).
- **Oráculos** (`oraculo_isr.py`, `oraculo_rendimientos.py`) · **comparadores** (`motor_b_diario.py`,
  `contable_bc.py`, `cuentahabientes_wso2.py`, `fase1_isr_*`).
- **SQL** (V1–V5, `consultas_validacion.sql`, `wso2_cuentahabientes.sql`) · **planes/spec/referencias**.
- **`10_conocimiento/`** — las piezas de conocimiento (las reglas que citan los casos).
- **`db_connections.example.yaml`** — formato de credenciales (sin valores reales).

## Regla dura de exportación (seguridad)
El bundle **NUNCA** incluye: `db_connections.yaml` (credenciales), `landing/`, `**/_resultados/`,
`*.parquet`, ni CSVs de datos. `ensamblar.py` los excluye por lista `PROHIBIDO`. `bundle/` es **gitignored**.

## Changelog de exports (qué es nuevo cada ciclo)
> Regla: al ensamblar, anota aquí **qué cambió** desde el export anterior (para que la sesión del auditor
> sepa qué re-correr / re-sincronizar). Ver `PROMPT_SYNC_AUDITOR.md`.

| fecha | novedades para el auditor |
|-------|---------------------------|
| 2026-08-20 | **Export inicial.** Casos sembrados: ISR-01/02/03, REND-PLAZO/VISTA, SALDO-PROM, DIARIO-B (Motor B, −1.7%), GAPB-IDNC (**confirmado en datos**), GAPC-PROSOFIPO, WRITEOFFS, **CUENTAHAB-01** (nuevo), **CONTABLE-BC** (B1 cuadra 0.00; B3/B4 via DuckDB). Comparadores nuevos: `contable_bc.py`, `cuentahabientes_wso2.py`. |
| 2026-08-20 (b) | **Metodología `origin` + validaciones vivas.** Regla nueva: delimitar "Aurum vivo" por **`created >= cutover`** (NO `origin is null` — semántica mixta, P-013 reabierta). Motor B re-corrido con filtro → **+0.0%**. Nuevos: `validate_plazo_origin.py` (plazo A=B=C: migrado 97.8% / live 99.7%), `isr_live_nativo.py` (ISR vivo, **bloqueado por saldo base → logs SOL-003**), `REFERENCIA_TABLAS_POR_CASO.md`, `SOLICITUDES_FINSUS.md` (14 solicitudes). Contable D (balanza A/B ~1-2%), producto 2001 explicado. **Re-correr en el auditor** los casos con el delimitador `created>=cutover`. |
