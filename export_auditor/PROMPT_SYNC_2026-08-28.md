# PROMPT — Sincronización del auditor con el export 2026-08-28

Eres el **auditor independiente** que construye el SPA/tablero y los casos ejecutables (motor C) a partir del bundle
de Linko. Acaba de llegar un **export nuevo**. Este prompt te dice **qué cambió** y **qué ajustar**. No rehagas lo que
ya tienes; **reconcilia** contra estas fuentes y corre las verificaciones al final.

Regla rectora (no negociable): cada afirmación del tablero verifica **la verdad de la fuente** (derivable), no el
formato; el fallback de "no derivable" es un "no lo sé" explícito, **nunca un default**. Fuente de sanidad:
`40_validaciones/NORTE_SANIDAD.md`.

## 0. Lo que probablemente "te faltaba" = ALCANCE por punto
Antes no estaba el detalle de **qué se valida y qué NO**, ni el **universo/representatividad** por punto. Ahora sí:
**lee primero `40_validaciones/INFORME_DETALLADO_AUDITORIA/`** (00_INDICE + 01/02/03). Cada punto trae **Alcance
(sí/no) · Periodo · Universo y representatividad · Metodología + rationale · Santo y seña · Conciliación**. El tablero
debe **reflejar ese alcance** por card (qué se toma y qué no), no solo el %.

## 1. Qué cambió en este export (delta) y qué hacer con cada cosa
1. **`INFORME_DETALLADO_AUDITORIA/` (NUEVO).** Por cada card, muestra/enlaza: **qué se valida, qué NO**, el **universo
   total** y el **% de representatividad**, y el **rationale** del subconjunto. Reconcilia los universos del tablero
   con estos números (denominadores verificados en BD 2026-08-28):
   - Plazo live: **530,195 de 1,339,023 periodos live-pagados = ~39.6%** (censo del cohorte ≥2 pagos; mono-pago no es
     validable por el método no-circular). **NO lo muestres como "100% de lo live".**
   - IVA: 54,716 de 55,636 (~98%). GAT: 126,465 de **706,600** (`account.nominal_cgat>0`). Contratos crédito: 31,867.
2. **`NORTE_SANIDAD.md` + `comparadores/sanity_check.py` (NUEVO).** Implementa/porta los invariantes H/E/C/T sobre el
   JSON del tablero y muestra un **badge de status global** (SANO/NO SANO) en el home, con **auto-prueba de
   falsabilidad** (inyecta los 2 bugs históricos CAT/MOR y confirma que se atrapan). Ver `PROMPT_AUDITOR_SPA.md` §12.
   Alinea tu suite de pruebas con el NORTE (tu invariante "escala verdadera" = INV-H2).
3. **`PROMPT_AUDITOR_SPA.md` (ACTUALIZADO).** Aplica §3.2 (config vs sin-cruce — no escondas cobertura tras un `—`),
   §3.3 (motores **citados**: tres granularidades + **titular al centavo**, **ningún % sin su escala**), §11 (guía de
   casos: independencia, half-up por evento, **playbook del sesgo**), §12 (sanidad).
4. **CAT — corregido.** `COMPARACION` C6 / `MATRIZ_TOLERANCIAS` / `DOSSIER` §12 ahora dicen **campo mixto** (no
   "nominal-producto"): 25,026 constante / **4,220 per-contrato** / 2,576 `cat=0`. El "11.6% a volumen" **no es
   granularidad** (ya lo sabías). Construye **CAT-01** con `CASO_CAT-01_estratificado.md` (motor `oraculo_cat.py`),
   alcance declarado. Y registra el hallazgo **A28-CAT-CERO** (2,573 `cat=0` cobrando ~28% → regulatorio, Circular
   21/2009), no como cuadre.
5. **VISTA — ahora calculado.** Nuevo motor `comparadores/oraculo_vista_finsus_history.py` (ciclo julio: **94.76% a
   1e-8 / 95.03% al centavo**, base 360·dt 31; residuo = `dt` intra-mes, no defecto). **Matiz de honestidad:**
   `MATRIZ_TOLERANCIAS` sigue citando VISTA como `[PEND]` **a propósito** (se sella con el ciclo vivo del 31-ago). Si
   el tablero muestra el 94.76% calculado y la matriz dice `[PEND]`, es **INV-C3 (stale)** → muéstralo con **fecha y
   nota** ("calculado julio; se sella 31-ago"), no como contradicción silenciosa.
6. **Cifra del moratorio:** el firme es **95.7% al centavo / 81.1% a 1e-8** (no "89%").

## 2. Qué NO cambiar / preservar
- No promuevas a "calculado aquí" nada sin corrida con datos. No subas el CAT global del 11.6% (los 25,026 constantes
  son data-sourcing, no cuadran ni deben). No inventes umbrales de pago sostenido ni bases de E1/E2 (siguen `[PEND]`
  por documento).

## 3. Verificación antes de dar por hecho el ajuste
- `python 40_validaciones/comparadores/sanity_check.py` → **STATUS GLOBAL: SANO** + auto-prueba OK.
- Autopruebas de fórmula: `oraculo_credito.py`, `oraculo_rendimientos.py`, `oraculo_gat.py`, `oraculo_ifrs9.py`,
  `oraculo_amortizacion.py`, `oraculo_cat.py`, `tolerancias.py` (todas N/N).
- Cada card: ¿tiene escala en todo %? ¿titular al centavo cuando existe? ¿alcance (sí/no) + representatividad visibles?
  ¿badge de sanidad global? ¿botón "Ejecutar" honesto (solo con feed+caso)?

## 4. Reporta de vuelta
Qué ajustaste (por punto), qué quedó pendiente y por qué, y el status de sanidad final. Si algo del alcance del
informe detallado no te cuadra con lo que tienes, **levántalo** — es exactamente lo que la auditoría quiere ver.
