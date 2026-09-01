# PROMPT — Sync auditor interno (2026-09-01) · cierre de AUD-005 + luz verde a push

Eres el **auditor interno** (nuestro Claude Code): mantienes el SPA/tablero, los motores y la suite de sanidad del
oráculo (motor C). Este es un **sync corto** sobre el estado que ya congelaste (corte 2026-09-01). Reconcilia contra
este delta; **no rehagas** lo que ya tienes. Regla rectora intacta: cada afirmación verifica la **verdad de la fuente**
(derivable), no el formato; fallback = `[PEND]` explícito, nunca un default. **Un resultado nuevo no reemplaza uno en
firme sin declararlo** (corte + fecha).

Terminología: **auditor interno = tú**; **grupo auditoría de Finsus** = los auditores (personas, sin ruta a la subred).

## 0. Lo que motiva este sync
Levantaste **AUD-005** en tu reporte de versión congelada. Está **resuelto en origen de mi lado** (Linko) y ya viajó a
`main`. Verifica que tu copia lo refleje.

## 1. AUD-005 (a) — `sanity_check.py` comparaba copia contra copia
- **Antes:** `MATRIZ_REF` estaba **hardcodeada** dentro de `sanity_check.py`; INV-C1 comparaba los claims contra esa
  copia, no contra la matriz real → un cambio en `MATRIZ_TOLERANCIAS.md` no se detectaba (falso SANO).
- **Ahora:** `sanity_check.py` **parsea `MATRIZ_TOLERANCIAS.md`** en tiempo de ejecución (`_parse_matriz()`), así
  INV-C1 verifica **verdad** (claim ↔ matriz-fuente), no copia-vs-copia. Si el archivo no se puede parsear, cae a un
  **fallback declarado** (también corte 01-sep) — nunca a un default silencioso.
- El **self-test de falsabilidad** ahora ubica los bugs por **nombre de motor**, no por índice, y sigue atrapando los
  dos bugs históricos (CAT-1e-8 y MOR-titular-flojo).
- **Acción tuya:** corre `python 40_validaciones/comparadores/sanity_check.py` → debe dar **SANO** + auto-prueba OK.
  Confirma que el parser lee tu `MATRIZ_TOLERANCIAS.md` (no el fallback). Si tu tablero replicaba la matriz hardcodeada,
  reemplázalo por la lectura de la pieza/archivo fuente.

## 2. AUD-005 (b) — VISTA citada con la convención `dt=31` sin etiquetar
- **Antes:** varios documentos del marco citaban VISTA **94.56% / 94.82%** (que es `dt=31` fijo) como titular, sin decir
  la convención.
- **Ahora:** el titular de VISTA en todo el marco es **`dt` por cuenta = 97.47% (1e-8) / 97.65% (centavo)**, con
  `dt=31 → 94.56/94.82` mostrado **como referencia entre paréntesis**. Corregido en: `COMPARACION_C_vs_DOC.md` (A1),
  `CROSSWALK_CRITERIOS_BLOQUEANTES.md` (#8), `INFORME_DETALLADO_AUDITORIA/00_INDICE.md` (tabla maestra + AUD-004) y
  `01_CAPTACION_FISCAL.md` (V-04). Word del crosswalk regenerado. Las 94.56 que **quedan** están solo en
  `RESULTADO_vista_vivo_2026-09-01.md` (tabla comparativa de ambos métodos), donde es correcto.
- **Acción tuya:** alinea cualquier card/número de VISTA de tu tablero a **97.47 / 97.65 (`dt` por cuenta)**; nunca un %
  sin escala; titular = centavo; el estricto (1e-8) debajo. La convención `dt` debe ser visible en la card.

## 3. Cifras vigentes (recordatorio, corte 2026-09-01)
| Motor | 1e-8 | centavo | Nota |
|---|---|---|---|
| Plazo fijo (live) | 100% | 100% | 530,195 periodos, 0 violaciones |
| **VISTA (agosto vivo)** | **97.47%** | **97.65%** | `dt` por cuenta; residual = SPM-de-cierre, no defecto |
| Crédito ordinario | 97.32% | 97.43% | `abs(capital)` — K-DAT-007 |
| Crédito moratorio | 94.66% | 95.38% | 1e-8 se mueve con el corte = snapshot `capital_venc` |
| IVA (cohorte 16%) | 98.91% | 99.46% | + IVA-incluido 16/84 + resto |
| Contable doble partida | $0.00 | — | 7/7 días |

## 4. Estado del versionado (Linko → `main`)
- Mi lado (repo `finsus_core_migration`) **ya está commiteado y en `main`** al corte 2026-09-01 (incluye el fix de
  AUD-005, VISTA agosto vivo, crédito fresco con `abs()`, D2 cerrado, piezas de fórmula canónicas y este bundle).
- **Tus 4 commits locales: luz verde para `main`.** Súbelos. Antes de empujar, verifica el guardarraíl de siempre:
  el bundle y el repo **no** llevan `db_connections.yaml`, PII, `_resultados/`, `.parquet` ni `landing/`
  (`ensamblar.py` los excluye; confírmalo con `git status` antes del push). Material **FINSUS Confidencial** → si algo
  fuera de ese perímetro estuviera por subir, detente y repórtalo.

## 5. Definition of Done de este sync
- `sanity_check.py` → **SANO**, parser leyendo la matriz real (no el fallback), falsabilidad OK.
- VISTA a 97.47/97.65 en todo el tablero, con convención `dt` visible y umbral $0.99 por card.
- Tus 4 commits en `main`, sin material fuera del perímetro confidencial.
- Reporta: qué reconciliaste, qué ya estaba alineado, y cualquier residuo con su dueño.
