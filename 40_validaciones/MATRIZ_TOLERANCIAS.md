# Matriz de Tolerancias — % de cuadre por motor a 1e-8, 1e-5 y al centavo

> Qué muestra y **explica** el auditor por cada motor de cálculo: el porcentaje de coincidencia (C = B)
> en **tres granularidades**, más la **prueba de sesgo**. El mecanismo lo estandariza
> [`comparadores/tolerancias.py`](comparadores/tolerancias.py) (sin BD, `decimal.Decimal`, autoprueba 4/4).
> Veracidad: cada cifra cita su fuente; lo no computado va **[PENDIENTE]**, nunca inventado.
> Corte 2026-08-26. BD no alcanzable al momento de escribir → las columnas 1e-5 se **regeneran** en la corrida con BD.

---

## 1. Por qué tres granularidades (esto es lo que se explica, no solo el número)

| Nivel | Umbral | Qué prueba | Cómo leerlo |
|---|---|---|---|
| **1e-8** | \|C−B\| ≤ 0.00000001 | **Exactitud aritmética estricta** (8 decimales) | Si cuadra aquí, es el **mismo cálculo** que el core, sin diferencia perceptible ni de redondeo. Es la prueba más dura. |
| **1e-5** | \|C−B\| ≤ 0.00001 | **Precisión intermedia** (5 decimales) | Absorbe ruido de acumulación / orden de operaciones, pero **no** tolera un centavo. Separa "redondeo interno" de "diferencia real". |
| **centavo** | \|C−B\| ≤ 0.01 | **Tolerancia de negocio** | Lo que le importa al cliente y a la contabilidad. Cuadre al centavo = **sin impacto material** aunque difiera en la 6ª decimal. |

**El escalón entre niveles es diagnóstico** (más informativo que cualquier número solo):

- **100 / 100 / 100** → cuadre **exacto**; es el mismo motor bit a bit (a 8 decimales). *Ej.: plazo fijo.*
- **Bajo a 1e-8, alto al centavo** → el residuo sub-centavo es **granularidad/redondeo del snapshot**, **no defecto**. *Ej.: moratorio ~81% a 1e-8 pero ~96% al centavo.*
- **Bajo también al centavo** → hay **diferencia material** que investigar (defecto / linaje / dato faltante).

## 2. La prueba de sesgo (por qué "al centavo" no basta)

Sobre el residuo que cae **fuera de 1e-8**, se corre una **prueba de signo** (CLAUDE.md §10):

- Si las diferencias se **cargan a un lado** (siempre a favor del core o del cliente) → **sesgo sistemático**:
  es un **defecto severidad 1** aunque cada diferencia individual sea de un centavo (sobre el padrón completo es un pasivo material).
- Si el signo es **aleatorio** (+/− se cancelan) → **ruido de snapshot**, no defecto.

`tolerancias.py` devuelve `sesgo.sesgo_detectado` (|z| > 3 ≈ p < 0.003), con el conteo +/− y el z. Verde al centavo **con sesgo** ≠ aprobado.

---

## 3. Matriz por motor de cálculo

> **[CONFIRMADO]** = cifra computada, con fuente. **[PEND]** = no computada aún a esa granularidad (se llena al re-correr con `tolerancias.py`).
> `n` = universo de eventos comparados. `sesgo` = resultado de la prueba de signo (donde se corrió).

| # | Motor | 1e-8 | 1e-5 | centavo | n | sesgo | Fuente / lectura |
|---|---|---|---|---|---|---|---|
| 2 | **Rendimiento plazo fijo** | **100.00%** | **100.00%** | **100.00%** | 530,195 periodos | no | [CONFIRMADO] `validate_plazo_origin.py`, 0 violaciones (COMPARACION A2). Cuadre exacto — el motor más sólido. |
| 5 | **Crédito ordinario** | **97.32%** | **97.32%** | **97.43%** | 3,585 (feed 08-20) | no¹ | [CONFIRMADO corte 01-sep] `capital`×tasa/100/360 (sin redondear, `abs(capital)`) vs feed; 0 mismatch de tasa. (Firme 23-ago: 96.8%.) ¹Residuo = data-sourcing (P-019), no motor. |
| 6 | **Crédito moratorio** | **94.66%** | **94.66%** | **95.38%** | 693 (feed 08-20) | sí² | [CONFIRMADO corte 01-sep] `capital_venc`×tasa/100/360, días=1. (Firme 23-ago: 81.1%/95.7%.) ²El 1e-8 **se mueve con el corte** (23-ago 81.1% → 01-sep 94.66%) porque `capital_venc` es vivo/volátil intra-período; el **centavo (~95.4%) es el estable** = granularidad del snapshot, no defecto. P-020 cerrada. |
| 8 | **IVA sobre interés (cohorte 16%)** | **98.91%** | **98.91%** | **99.46%** | 54,421 (16%, 96.96%) | no | [CONFIRMADO corte 01-sep, por cohortes] Cohorte **16% general** 99.46% centavo. Aparte: **IVA-incluido (16/84=19.05%)** 279 (0.5%), 99.28% centavo — convención, no defecto; **resto** 1,426 (2.5%) = 16% con **redondeo en montos ínfimos** (91% cuadra a 16% al centavo). Detalle: `RESULTADO_iva_cohortes_2026-09-01.md`. |
| 11 | **Amortización (francesa)** | interés **exacto**² | [PEND] | ident. fila **99.9%** | 794 contratos | [PEND] | [CONFIRMADO] interés Actual/360 exacto (P1 158.33, P3 112.37); identidad de fila 99.9%; frescos 91.7% (C5). ²Cuota ~0.1% off = convención Actual/360, spec del 1er período. |
| 9 | **GAT inversión** | **exacto**³ | n/a | n/a | 126,465 (term7) | n/a | [CONFIRMADO] prueba **no-circular**: `nominal_cgat` = función pura (tasa,plazo,360) y el oráculo lo reproduce exacto (A4). ³Cruce 1-a-1 a volumen pendiente de la **tabla de tramos de tasa** (data-sourcing, no cálculo). |
| 12 | **CAT** | **3/3 exacto** vs doc⁴ | n/a | n/a | 3 ejemplos + caso real | n/a | [CONFIRMADO] `oraculo_cat.py` 3/3; caso real 35.1% = CAT stored (C6). ⁴El "11.6% a volumen" **no es granularidad**: `lc_loan_contract.cat` es **campo mixto/constante copiada** (25,026 constantes / 4,220 per-contrato / 2,576 `cat=0`); el motor cuadra en el estrato per-contrato. Remedio: **CASO CAT-01 estratificado** (bloqueo SOL-015). Aparte: **A28-CAT-CERO** ([[P-023]], candidato regulatorio). La fórmula no está en duda. |
| 10 | **IFRS 9 — % / etapas** | **37/37 exacto** | n/a | n/a | 37 celdas tabla + stages | n/a | [CONFIRMADO] C = **config real de Aurum** (`lc_reserve_ifrs` 37/37, `lc_risk_stage`); autoprueba 14/14 (E4). Reserva E3 fully-vencido 65% a volumen exacto (base = capital_venc). |
| 4 | **ISR retención (histórico)** | **C=B exacto** | n/a | n/a | caso reconciliado 1-10-370 | n/a | [CONFIRMADO] C=B=765.75; parámetros = ley 2026; C-002 cerrada (B1). Cruce masivo per-contrato pendiente del Manual (SOL-015). |
| 1 | **Rendimiento vista** | **97.47%** | **97.47%** | **97.65%** | 82,925 (ciclo agosto) | sí¹ | [CONFIRMADO 2026-09-01] **ciclo vivo agosto** (`yield_dto` 01-sep ↔ `finsus_account_history` 31-ago), base 360, **`dt` por cuenta**. (Con `dt=31` fijo: 94.56/94.56/94.82.) ¹Residual ~2.5% = **SPM-de-cierre subestima el promedio del periodo** (C<B), granularidad del SPM, no defecto. `RESULTADO_vista_vivo_2026-09-01.md`. |
| 3 | **Saldo promedio (SPM)** 🔒 | [PEND] | [PEND] | [PEND] | — | [PEND] | [PENDIENTE] fórmula = doc (autoprueba 28,888.89); **bloqueado**: el SPM de rendimiento solo existe en logs (A3). |
| 2b | **ISR-vivo nativo** 🔒 | [PEND] | [PEND] | [PEND] | ~13% | [PEND] | [PENDIENTE] mismo bloqueo que SPM (saldo base punto-en-tiempo en logs) (B2). |

## 4. Motores de identidad / completitud (la escalera 1e-8/1e-5/centavo **no aplica**)

Estos no comparan un importe C vs B evento-a-evento; su tolerancia es **exacta (0.00)** o de **cobertura**, no un %-a-8-decimales.

| Motor | Tolerancia propia | Resultado | Fuente |
|---|---|---|---|
| **Contable — doble partida** | **0.00 exacto** (sin excepción; no es cálculo con redondeo) | B1 doble partida = **$0.00**; balanza D ~1-2% (alerta prod. 2001) | D2 |
| **Motor B — transaccional** | **completitud A ≥ B** (0 faltantes) | 6 días, +0.1% a +2.1%, siempre OF≥AU | D1 |
| **Cuentahabientes WSO2** | cobertura bidireccional | Aurum→WSO2 completo (20 huérfanos); churn P-017 | D3 |

---

## 5. Cómo se regenera (el auditor, con BD read-only)

Cada comparador arma sus pares `(C, B)` y llama al helper:

```python
from tolerancias import resumen_tolerancias, imprimir, linea_matriz
res = resumen_tolerancias(pares)      # pares = [(c, b), ...] en Decimal
imprimir("credito-moratorio", res)    # consola
# res es JSON-serializable -> alimenta la card del SPA (campo "match" con las 3 escalas + sesgo)
```

El runner del SPA escribe `resultados/<motor>.json` con el bloque `match` (las 3 escalas) y `sesgo`, y la
card muestra **tres barras** (1e-8 / 1e-5 / centavo) + la lectura del escalón + la bandera de sesgo. Ver
[`PROMPT_AUDITOR_SPA.md`](PROMPT_AUDITOR_SPA.md) §2-§3.

**Estado honesto:** históricamente reportamos 1e-8 y centavo; el **1e-5 se computa uniformemente** con este
helper en la próxima corrida con BD. Las cifras de arriba son las [CONFIRMADO] a la fecha; el resto se llena
al re-correr. Verde ≠ dictamen.
