# PROMPT — Cierre de versión del auditor interno (corte 2026-09-01)

Eres el **auditor interno** (nuestro Claude Code): construyes/mantienes el SPA/tablero, los motores y la suite de
sanidad del oráculo (motor C). Este es el **prompt de cierre**: congela una **versión entregable** al grupo auditoría
de Finsus, rumbo al **Dictamen del 7-sep**. Reconcilia contra este estado; no rehagas lo que ya tienes.

Terminología: **auditor interno = tú**; **grupo auditoría de Finsus** = los auditores (personas, sin ruta a la subred).
Regla rectora: cada afirmación verifica la **verdad de la fuente** (derivable), no el formato; fallback = "no lo sé"
explícito (`[PEND]`), nunca un default. **Un resultado nuevo no reemplaza uno en firme sin declararlo** (corte + fecha).
Fuentes: `00_START_HERE.md`, `NORTE_SANIDAD.md`, `PLAN_ACTUALIZACION_AUDITOR_INTERNO.md`.

## 0. Empieza por `00_START_HERE.md` y alinea la navegación del tablero a su mapa.

## 1. Cifras vigentes — CORTE DECLARADO 2026-09-01 (adoptar, con la tríada 8/5/2)
| Motor | 1e-8 | 1e-5 | centavo | Nota |
|---|---|---|---|---|
| Plazo fijo (live) | 100% | 100% | 100% | 530,195 periodos, 0 violaciones |
| **VISTA (ciclo agosto)** | 97.47% | 97.47% | 97.65% | `dt` por cuenta; residual = SPM-de-cierre, no defecto. AUD-004 cerrado |
| **Crédito ordinario** | 97.32% | 97.32% | 97.43% | firme 23-ago 96.8%; `abs(capital)` |
| **Crédito moratorio** | 94.66% | 94.66% | 95.38% | firme 81.1%; el **1e-8 se mueve con el corte** = snapshot de `capital_venc` |
| **IVA (cohorte 16%)** | 98.91% | 98.91% | 99.46% | + IVA-incluido 16/84 (0.5%) + resto redondeo montos ínfimos |
| IFRS 9 etapas+% | 37/37 config | n/a | n/a | = config real de Aurum |
| GAT / CAT | exacto / 3-3 doc | n/a | n/a | CAT: campo `cat` mixto → CASO CAT-01 |
| Contable doble partida | $0.00 | — | — | 7/7 días |

Nunca muestres un % sin su escala; titular = centavo; el estricto (1e-8) va debajo.

## 2. Qué cambió (delta) y qué hacer
1. **Piezas canónicas de fórmula (NUEVO):** cada motor tiene su fórmula exacta como pieza K (K-COL-002..008, K-DEV-004,
   K-CAP-002, K-REG-003, y K-DEV-002/003/K-FIS-002 actualizadas). El tablero/agente **citan la pieza K**, no una copia.
2. **Capital negativo — K-DAT-007 (CRÍTICO):** `capital`/`capital_venc` se almacenan **NEGATIVOS**; usar **`abs()`**.
   Omitirlo da **falsos 0%**. El oráculo ya lo hace; cualquier cruce nuevo también.
3. **D2 CERRADO:** el mapeo `tipo → cuenta` existe en config (`cat_accounting_transaction`, 709/28 tipos) y **99.6% de
   los posteos lo respetan** (K-CTB-001 v2). En el crosswalk, criterios #5/#7 pasan a verde.
4. **SOL-004 bridge:** crosswalk OF↔AU de tipos **confirmado 313/314** por número (nivel catálogo). El cruce de
   **records** por-tipo aún necesita el mapeo semántico OF-descr↔AU-texto (pendiente).
5. **IVA por cohortes:** no un número global — 16% / IVA-incluido / resto, cada uno con su explicación.

## 3. Mostrar dónde se atiende cada observación de Finsus (OBLIGATORIO)
El material debe **mapear cada criterio/observación de Auditoría Interna de Finsus → dónde se atiende**. Base:
`CROSSWALK_CRITERIOS_BLOQUEANTES.md` (los 7 criterios + 8 áreas, con estado y evidencia). El tablero debe hacerlo
**navegable**: por cada criterio, un enlace a la card/motor/documento que lo atiende. Umbral $0.99 explícito en cada card.

## 4. Qué NO cambiar / sigue pendiente (honesto)
- **Bloqueados por insumo (no falla del motor):** SPM (logs), ISR-vivo (base punto-en-tiempo, SOL-003).
- **Pendientes:** Motor B instancia-a-instancia (mapeo semántico), CAT-01 (SOL-015 días), IVA-incluido a confirmar en
  config, los 13 pares no catalogados de D2 (0.4%), comisiones/seguros (fórmula sí, oráculo no).
- No promuevas a "calculado aquí" sin corrida; no fuerces un número global (estratifica como CAT/IVA).

## 5. Verificación (Definition of Done)
- `python 40_validaciones/comparadores/sanity_check.py` → **SANO** + auto-prueba OK.
- Autopruebas de fórmula N/N. Cada card: escala · procedencia · alcance · representatividad · **umbral $0.99** · badge
  de sanidad · botón honesto. Cada motor de alcance crítico ejecutado o etiquetado "insumo externo".
- Crosswalk sin bloqueante de cálculo abierto; hallazgos levantados con dueño (A28, IDNC, Prosofipo).

## 6. Congelar la versión
Etiqueta la versión con el **corte 2026-09-01** (fecha/universo/hora declarados). Regenera el bundle, y deja el paquete
listo para el grupo auditoría (con `ACCESO_Y_RED.md` para su provisión). Reporta qué quedó dentro y qué pendiente y por qué.
