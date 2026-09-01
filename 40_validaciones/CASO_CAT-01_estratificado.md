# CASO CAT-01 — CAT estratificado (prompt de construcción + motor)

> Convierte el "CAT 11.60% a volumen" (que **no es una granularidad**) en un **cuadre real calculado aquí** sobre el
> estrato que sí es un CAT per-contrato, con las tres granularidades y su escalón. **Motor:** `comparadores/oraculo_cat.py`
> (ya validado 3/3 vs doc). **Tolerancias:** `comparadores/tolerancias.py`. **Sanidad:** cumple `NORTE_SANIDAD.md`.
> Contexto: `COMPARACION_C_vs_DOC.md` C6. Corte 2026-08-28.

## 1. Por qué (el 11.60% no mide el motor)
`lc_loan_contract.cat` es un **campo mixto / constante copiada**, no la salida de un motor. Sobre 31,867 contratos:

| Estrato | Contratos | % | Qué es |
|---|---|---|---|
| **Constante copiada** (≥100 contratos comparten el mismo `cat`) | 25,026 | 78.5% | **NO validable** — `cat=27.10` cubre 15,300 contratos con 3,930 montos y 521 plazos distintos; un CAT es función de monto y plazo → es una constante, no un cálculo. **data-sourcing, no defecto.** |
| **Varía por contrato** | 4,220 | 13.2% | **El universo de CAT-01** — aquí el campo sí guarda un CAT per-contrato. |
| **`cat = 0`** | 2,576 | 8.1% | **Hallazgo aparte A28-CAT-CERO** (ver §5). |
| sin `cat` | 44 | 0.1% | excluir. |

El cruce global reporta **11.6% ≈ el estrato per-contrato (13.2%)**: el motor cuadra **donde el campo es un CAT real**;
el 88.4% restante es comparar contra algo que no es un CAT. La fórmula **no está en duda** (3/3 vs doc + caso real 35.1%).

## 2. Identidad del caso (universo = los 4,220 per-contrato)
```
C = oraculo_cat.cat_frances(flujos)   # IRR por bisección, Circular 21/2009
    con: disposición = loan_amount − comisión_apertura_descontada  (o + si financed → ver SOL-015)
         flujos = tabla de amortización (lc_loan_amortization)
         comisión = lc_account_commission (type apertura)
comparar C vs lc_loan_contract.cat  → devolver las filas que violan (0 = pasa)
reportar match a 1e-8 / 1e-5 / centavo con tolerancias.py + prueba de sesgo
```
- **Insumos verificados construibles:** los 4,220 tienen **tabla de amortización 4,220/4,220** y **comisión 4,207/4,220**.
- **Producto/método:** francesa (y americana si aplica), comisión **no financiada** como supuesto declarado hasta SOL-015.

## 3. Alcance declarado (NORTE_SANIDAD — honestidad)
- **Se valida:** los **4,220** contratos con `cat` per-contrato → cuadre calculado aquí, tres granularidades + escalón.
- **NO se promete** subir a ~100% sobre los 31,867. Los **25,026 constantes no cuadran y no deben** (un motor no se
  valida contra una constante) → se reportan **aparte** como **data-sourcing**, con su conteo, no como "no-conforme del motor".
- **`cat=0`** se reporta como **A28-CAT-CERO** (§5), no como cuadre.
- El titular del tablero para CAT deja de ser "11.60% a volumen": pasa a **el % al centavo del estrato per-contrato**
  (cuando la corrida exista), con el 1e-8 debajo; y los otros dos estratos etiquetados por lo que son.

## 4. Bloqueo (SOL-015) — qué acota el dictamen
**Parcialmente desbloqueado (F-033, Tabla Consolidada v1):** el motor 9 (Comisiones) aclara que la **comisión
financiada** = *descontada al inicio*, base = **Monto Autorizado**, y el CAT (motor 10.a) iguala el VP de las
**disposiciones netas recibidas** = "Monto Recibido" = monto − comisión descontada. → usar **disposición neta** en
`cat_frances`. **Sigue pendiente la convención de días** del CAT (360 vs Actual). Con esa pieza cerramos SOL-015; sin
ella, el residuo dentro de los 4,220 **no se atribuye a AurumCore** (podría ser convención del oráculo). **El caso se
escribe con alcance declarado; el dictamen sobre el residuo, no** (hasta cerrar la convención de días).

## 5. Hallazgo aparte — A28-CAT-CERO (no es parte del cuadre)
**2,573 contratos `cat=0` que cobran ~28.45% de interés** (≈2,466 activos; activaciones 2023-11-29 → 2026-07-17).
Un CAT de cero en un crédito que cobra 28% es un **campo sin poblar**, no un CAT calculado. **Circular 21/2009** exige
revelar el CAT → **candidato regulatorio, no de cálculo**. Registrado en `PREGUNTAS_ABIERTAS.md` **P-023**. Cierre:
descartar exención del producto + cruce con motor A (openfin). **No minimizar** (charter §11).

## 6. Cómo queda en el tablero (sanidad)
- Mientras no exista la corrida: CAT se **cita** correctamente (volumen 11.60% etiquetado **volumen**, no granularidad;
  tres barras `[PEND]`; "sin escala declarada" si falta respaldo) — INV-H1/H2/H3 de `NORTE_SANIDAD.md`.
- Con CAT-01 corrido: cobertura `datos` sobre 4,220, titular al centavo, escalón visible; estratos constante y `cat=0`
  mostrados **aparte** con su etiqueta. El `sanity_check.py` debe seguir en **SANO**.
