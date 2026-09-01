# Versión congelada del auditor interno — corte 2026-09-01

> Paquete entregable al **grupo auditoría de Finsus**, rumbo al **Dictamen del 7-sep**.
> Motor C (oráculo independiente) + tablero + suite de sanidad. Todo solo lectura.

| | |
|---|---|
| **Versión** | `corte-2026-09-01` |
| **Congelada** | 2026-09-01 |
| **Estado de sanidad** | **SANO** — 0 violaciones en 15 invariantes sobre 16 motores |
| **Auto-prueba de falsabilidad** | OK (atrapa los dos bugs históricos: CAT y moratorio) |
| **Pruebas** | 474, sin fallos |
| **Umbral de bloqueo aplicado** | **$0.99 MXN** (F-032, Auditoría Interna de Finsus) |

## 1. Cifras del corte — la tríada 8 / 5 / 2 en todas

| Motor | 1e-8 | 1e-5 | centavo | Universo | Origen |
|---|---:|---:|---:|---|---|
| Plazo fijo (live) | 100.00% | 100.00% | 100.00% | 530,195 periodos (~39.6% de los live-pagados) | **calculado aquí** |
| Rendimiento vista | 97.47% | 97.47% | **97.65%** | 82,925 cuentas (censo ciclo agosto) | citado, corte 01-sep |
| Crédito ordinario | 97.32% | 97.32% | **97.43%** | 3,585 (feed 08-20) | citado, corte 01-sep |
| Crédito moratorio | 94.66% | 94.66% | **95.38%** | 693 (feed 08-20) | citado, corte 01-sep |
| IVA (cohorte 16%) | 98.91% | 98.91% | **99.46%** | 54,421 (96.96% de las filas) | citado, corte 01-sep |
| IFRS 9 etapas + % | 88.10% | 88.10% | **100.00%** | 20,000 filas E3 + 37/37 config | **calculado aquí** |
| CAT (estrato per-contrato) | 27.10% | 27.10% | **32.97%** | 4,480 contratos | **calculado aquí** |
| Contable doble partida | — | — | **$0.00** | 7/7 días | **calculado aquí** |
| GAT inversión | exacto (no-circular) | n/a | n/a | 126,465 de 706,600 | citado |

**El titular siempre es el centavo.** El estricto va debajo, nunca escondido. Ningún porcentaje
se muestra sin su escala.

## 2. Lo que este corte SUSTITUYE (regla de oro: nada se reemplaza en silencio)

| Motor | Cifra en firme anterior | Cifra del corte 01-sep | Por qué cambió |
|---|---|---|---|
| Crédito ordinario | 96.80% @1e-8 (23-ago) | 97.32% | **K-DAT-007**: `capital` se almacena **negativo** y el cruce anterior no aplicaba `abs()`, produciendo falsos ceros. No mejoró el motor: **la medición anterior estaba mal del lado del cruce**. |
| Crédito moratorio | 81.10% / 95.70% (23-ago) | 94.66% / 95.38% | El **1e-8 se mueve con el corte** porque `capital_venc` es un campo vivo. El **centavo es el estable** (95.70 → 95.38). Que el estricto oscile entre cortes *es* la prueba de que el residuo es granularidad del snapshot. |
| IVA | 99.00% global (23-ago) | 98.91% / 99.46% por cohorte | Se **estratifica** por tasa en vez de promediar: 16% general, IVA-incluido (16/84), y resto con redondeo en montos ínfimos. Promediarlos escondía tres fenómenos distintos. |
| Vista | cita de julio 94.76/95.03 · preview propio de agosto 96.62 | 97.47 / 97.65 | Censo del ciclo **vivo de agosto** con `dt` **por cuenta**. Cierra AUD-004(b). |
| CAT | 28.50% al centavo sobre 4,225 (28-ago) | 32.97% sobre 4,480 | El oráculo pasa a usar la **comisión realmente cobrada** (`lc_loan_charge`) en vez de la configurada: medido, reproduce el CAT en **36.81%** de los contratos de un pago contra **33.51%** de la configurada. El universo creció por **deriva de tabla viva** en cuatro días. |

**La corrida propia de VISTA (preview, 20,000 filas) no se borró:** sigue publicada en su tarjeta,
etiquetada como preview, con su scatter y sus no conformes. Borrarla habría perdido cobertura en
silencio; publicarla de titular habría contradicho el corte.

## 3. Verificado midiendo, no citando

- **K-DAT-007 comprobado contra la base:** `lc_finantial_data_stage.capital_venc` es **100%
  negativo** (206,674 negativos, 0 positivos). El caso IFRS9 ya aplicaba `abs()` en ambos lados;
  `lc_loan_amortization` es positivo, así que CAT-01 no se ve afectado.
- **PLAZO y CONTABLE re-corridos** al corte de hoy: 100.00% ambos, sin cambio.

## 4. Qué queda fuera, y por qué

**Insumo externo faltante** (no es falla del motor):
- **SPM** — el saldo promedio *de rendimiento* sólo existe en logs. Confirmatorio; VISTA ya no depende de él.
- **ISR-vivo** — falta el saldo base **punto-en-tiempo** al momento del pago (SOL-003). El ~13% citado
  **no es un resultado de validación**, es la señal del bloqueo.

**Pendientes de definición o de terceros:**
- **Motor B instancia-a-instancia** — el bridge de tipos OF↔AU está confirmado 313/314 por número;
  falta el mapeo semántico OF-descr ↔ AU-texto.
- **CAT-01** — SOL-015 (convención de días y comisión `financed` vs descontada). El residuo **no se
  atribuye a AurumCore** hasta cerrarlo.
- **IVA-incluido** — la convención 16/84 falta confirmar en config.
- **D2** — 13 pares no catalogados (0.4%) por caracterizar.
- **Personas morales** — definición de la exención (SOL-011).
- **Comisiones y seguros** — fórmula sí, oráculo no.

**Fuera de nuestro control:** la **reproducibilidad por el grupo auditoría** (criterio A3) depende de
que su IT provisione ruta a la subred y usuario read-only → `40_validaciones/ACCESO_Y_RED.md`. Es la
ruta crítica del Dictamen y **este tablero no la controla**.

## 5. Discrepancias levantadas, no alineadas en silencio

- **AUD-004** (cerrada por acuerdo): `lc_loan_contract` 31,866 @14:29 UTC vs 31,867 — deriva de tabla
  viva, se cierra **declarando la hora**. VISTA: referencia = censo, preview etiquetado.
- **AUD-005** (abierta): `sanity_check.py` tiene `MATRIZ_REF` **hardcodeada** con cifras pre-01-sep,
  así que su INV-C1 compara una copia contra otra copia; y el crosswalk cita la variante `dt=31` de
  VISTA **sin decir la convención**, lo que se lee como 94.82% cuando la vigente es 97.65%.
- **Hallazgos con dueño:** A28-CAT-CERO (regulatorio, P-023), IDNC (AUD-001), Prosofipo, parámetro
  fiscal duplicado (AUD-002).

## 6. Cómo reproducirlo

```bash
python 40_validaciones/comparadores/sanity_check.py     # SANO + auto-prueba
python auditor_spa/backend/sanidad.py                   # los 15 invariantes del tablero
python -m pytest auditor_spa validador 60_informe -q    # 474 pruebas
python auditor_spa/backend/servidor.py --puerto 8777    # el tablero
```

Guía completa: [`COMO_REVISAR_EL_AUDITOR.md`](COMO_REVISAR_EL_AUDITOR.md) · punto de entrada del
bundle: `export_auditor/00_START_HERE.md`.

---

**Verde no es dictamen.** Cada validación devuelve las filas que violan la regla; cero filas
significa cero violaciones **en ese universo**, no que el motor esté bien fuera de él. Y estar por
debajo del umbral de $0.99 no es "todo pasa": el criterio de Finsus exige además que el residuo
esté **explicado**, que es lo que hace cada tarjeta en su sección de no conformes.
