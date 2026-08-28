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
| 5 | **Crédito ordinario** | **96.80%** | [PEND] | [PEND] ≥96.8 | 4,091 | no¹ | [CONFIRMADO 1e-8] vs `capital` DB, 0/4,091 mismatch de tasa (C1). ¹El residuo ~12% (P-019) es **data-sourcing de reserva**, no sesgo de motor. |
| 6 | **Crédito moratorio** | **81.10%** | [PEND] | **95.70%** | 1,274 | no | [CONFIRMADO] vs `capital_venc`, días=1 (C2). Escalón clásico 81→96: residuo sub-centavo = **granularidad del snapshot**, no defecto. P-020 cerrada. |
| 8 | **IVA sobre interés** | **99.00%** | [PEND] | [PEND] ≥99 | 54,716 | no | [CONFIRMADO match] vs `interest_tax_amount`; tasa implícita 16.0% en 95%, resto = redondeo en montos chicos (C3b). |
| 11 | **Amortización (francesa)** | interés **exacto**² | [PEND] | ident. fila **99.9%** | 794 contratos | [PEND] | [CONFIRMADO] interés Actual/360 exacto (P1 158.33, P3 112.37); identidad de fila 99.9%; frescos 91.7% (C5). ²Cuota ~0.1% off = convención Actual/360, spec del 1er período. |
| 9 | **GAT inversión** | **exacto**³ | n/a | n/a | 126,465 (term7) | n/a | [CONFIRMADO] prueba **no-circular**: `nominal_cgat` = función pura (tasa,plazo,360) y el oráculo lo reproduce exacto (A4). ³Cruce 1-a-1 a volumen pendiente de la **tabla de tramos de tasa** (data-sourcing, no cálculo). |
| 12 | **CAT** | **3/3 exacto** vs doc⁴ | n/a | n/a | 3 ejemplos + caso real | n/a | [CONFIRMADO] `oraculo_cat.py` 3/3; caso real 35.1% = CAT stored (C6). ⁴Cruce a volumen 11.6%: `cat` almacenado es **nominal-producto** en muchos contratos, no per-contrato (SOL). La fórmula no está en duda. |
| 10 | **IFRS 9 — % / etapas** | **37/37 exacto** | n/a | n/a | 37 celdas tabla + stages | n/a | [CONFIRMADO] C = **config real de Aurum** (`lc_reserve_ifrs` 37/37, `lc_risk_stage`); autoprueba 14/14 (E4). Reserva E3 fully-vencido 65% a volumen exacto (base = capital_venc). |
| 4 | **ISR retención (histórico)** | **C=B exacto** | n/a | n/a | caso reconciliado 1-10-370 | n/a | [CONFIRMADO] C=B=765.75; parámetros = ley 2026; C-002 cerrada (B1). Cruce masivo per-contrato pendiente del Manual (SOL-015). |
| 1 | **Rendimiento vista** ◐ | [PEND] | [PEND] | [PEND] | ~82% reconstruido | [PEND] | [PENDIENTE] fórmula = doc; reconstruido de `finsus_account_history` al ~82%; el **motor vivo se observa el 31-ago** (A1). Se puebla la tríada en esa corrida. |
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
