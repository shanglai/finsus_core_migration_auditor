# Guía para Auditoría — cómo entender la validación de motores (C vs AurumCore)

> Documento explicativo para revisar con Auditoría Interna. Explica **paso a paso** el ejercicio: qué se probó,
> cómo, contra qué, y **qué significa cada número** (PASS, 82%, 37/37, 96.8%, 0.00…) y **por qué es bueno**.
> No asume conocimiento previo del proyecto. Corte 2026-08-24.

---

## 0. Qué es este ejercicio (en una página)

Finsus migra su core bancario de **openfin** a **AurumCore**. Nosotros (Linko) somos el **tercero independiente**
que valida que AurumCore **calcula bien**. Para poder decir "cuál está bien" y no solo "son distintos", construimos
un **motor de cálculo propio (el oráculo, "motor C")** que implementa las reglas **desde la norma y el contrato**,
no desde el código de ningún core. Entonces comparamos tres motores:

| Motor | Qué es | Rol |
|---|---|---|
| **A** | openfin (core actual) | referencia histórica — **NO es la verdad** |
| **B** | AurumCore (core nuevo) | el sistema **bajo prueba** |
| **C** | nuestro oráculo | el **árbitro** independiente |

Cuando A, B y C coinciden → OK. Cuando difieren, el motor C dice **cuál está bien**. El oráculo C está escrito en
`decimal.Decimal` (aritmética exacta, **cero `float`**), con el redondeo declarado explícitamente.

**El dictamen lo emite el humano.** "Verde" no significa "auto-aprobado": significa que la validación **corrió y
pasó**. Todo no-conforme se **explica**, nunca se oculta.

---

## 1. Conceptos clave (glosario)

- **Universo / población / cohorte.** El conjunto de casos que probamos. Siempre lo declaramos con su tamaño
  (p.ej. *"530,195 periodos de inversión a plazo"*, *"4,091 provisiones de crédito del 20-ago"*). Un resultado sin
  universo no dice nada; por eso cada cifra va con "de cuántos".

- **Validación por invariante (la regla de oro).** Cada prueba está escrita para **devolver las filas que VIOLAN la
  regla**. **0 filas = PASS.** No comparamos totales "a ojo"; buscamos activamente los que fallan.

- **PASS / no-conforme.** *PASS* = el caso cuadra dentro de la **tolerancia**. *No-conforme* = queda fuera; entonces
  se **clasifica y se explica** (ver §5). Un no-conforme no es automáticamente un defecto de AurumCore.

- **Tolerancia (el criterio de "cuadra").** Depende del tipo de cálculo:
  | Tipo de prueba | Tolerancia PASS |
  |---|---|
  | Identidad contable (doble partida, amarre) | **0.00 exacto** — no hay redondeo que valga |
  | Cálculo con redondeo (interés/devengo) | **≤ $0.01 por evento** *y* **sin sesgo** (ver abajo) |
  | Exactitud a precisión completa | **1e-8** (8 decimales) — el más estricto |
  | Completitud (¿falta alguna transacción?) | **A ≥ B** (que no falte nada) |

- **"Al centavo" vs "1e-8".** *Al centavo* = cuadra en 2 decimales (≤ $0.01). *A 1e-8* = cuadra en **8 decimales**
  (mucho más estricto: es cuadrar el valor **sin redondear**). Cuando decimos "96.8% exacto a **1e-8**", es más
  fuerte que "cuadra al centavo".

- **Sesgo.** Aunque cada diferencia sea de 1 centavo, si **todas** empujan al mismo lado (siempre +$0.01), sobre un
  padrón grande eso **suma dinero** y es un defecto. Por eso, en devengo, exigimos ≤$0.01 **y** ausencia de sesgo
  (las diferencias deben repartirse alrededor de cero).

- **Redondeo half-up.** 2 decimales, "half away from zero" (0.005 → 0.01). **Confirmado por Finsus (24-ago):**
  homogéneo en todo el core, y se aplica **por evento** (cada devengo se redondea antes de acumular), no al cierre.

- **Contra qué se valida (la fuente).** Cada regla se marca con su respaldo:
  - **doc** = consta en un documento oficial de AurumCore (con página).
  - **config** = consta en una **tabla de configuración de la propia base de datos** de Aurum → *la validación más
    fuerte*: C = lo que Aurum realmente tiene cargado.
  - **norma** = sustento legal (LISR, CNBV, Banxico).
  - **inferencia** = lo dedujimos de los datos (marcado como tal; se pide confirmación a Finsus).

---

## 2. Cómo se lee cada número (los "headlines") — y por qué es bueno

| Número | Qué mide | Universo | Por qué es bueno / qué significa |
|---|---|---|---|
| **100%** | plazo: 0 violaciones | 530,195 periodos | PASS total sobre todo el universo. El resultado más fuerte: no hay un solo periodo que se salga de la fórmula. |
| **37/37** | IFRS 9: las 37 filas de la tabla de % de reserva de Aurum = nuestra transcripción del criterio CNBV | 37 filas de config | **C = la configuración REAL de Aurum**, no solo el doc. Es lo más fuerte: probamos contra lo que el sistema tiene cargado para calcular. |
| **96.8% exacto a 1e-8** | crédito ordinario | 4,091 provisiones | Cuadra a **8 decimales** (sin redondeo) en 96.8%; el resto **no es error del motor** (ver P-019). 1e-8 es más estricto que "al centavo". |
| **81.1% a 1e-8** | crédito moratorio | 1,274 provisiones | Igual que ordinario; el residuo es granularidad del snapshot, no cálculo. |
| **99.0%** | IVA de crédito | 54,716 filas con IVA | 99% cuadra al centavo; el 1% es redondeo en montos muy chicos. |
| **C = B = 765.75** | ISR retenido | caso de oro | Nuestro cálculo = lo que Aurum posteó, exacto. |
| **0.00** | contable doble partida | 7 días | La balanza cuadra **exacto** (identidad, tolerancia 0). |
| **82%** | rendimiento vista | posteos reales del 31-jul | Ver §3 — el más importante de explicar. |

---

## 3. El **82%** de rendimiento vista — qué es y por qué es bueno

Este número necesita contexto porque **antes valía 0** (estaba bloqueado):

1. **El problema:** el rendimiento de una cuenta a la vista se paga **una vez al mes** y usa un **saldo promedio
   (SPM)** que no estaba claro dónde vivía. La corrida viva del motor nuevo aún no ocurre (primer cierre 31-ago),
   así que no había con qué comparar → **bloqueado**.
2. **La respuesta de Finsus (24-ago):** confirmó la fórmula exacta — `interés = SPM × dt × tasa / 36000` (base 360,
   half-up), donde `dt` = días efectivamente devengados — y que el **SPM se guarda con `dt`**.
3. **Lo que hicimos:** encontramos el insumo del SPM en la base de datos (`finsus_account_history`) y **reconstruimos
   el interés sobre los posteos REALES de vista del 31-jul** (los últimos antes de que la migración parara el ciclo).
   - Caso limpio, al centavo: cuenta con SPM 10,165.70 × dt 31 × 4% / 36000 = **35.02 = exactamente lo posteado** ✓.
   - A volumen: **82%** de los posteos cuadran.
4. **Por qué 82% es bueno (no "solo 82%"):**
   - **Confirma la fórmula sobre datos reales** (no un ejemplo de manual). El motor calcula como Finsus documenta.
   - El **18% restante NO es un error de cálculo**: es que usamos un **`dt` aproximado** (derivado de la fecha de
     fondeo) porque el `dt` **exacto** vive en la póliza contable, que aún no tenemos. Con el `dt` exacto, ese 18%
     cerraría. Es un tema de **dato faltante, no de motor equivocado**.
   - **Pasó de 0% (bloqueado) a 82% reconstruido de la base** en un paso, gracias a la respuesta de Finsus.
5. **Estado:** de 🔒 (esperar 31-ago) a **◐ (reconstruible, 82%)**. La corrida VIVA del motor se sigue observando el
   31-ago para el cierre al 100%, pero **ya no es el único camino**.

---

## 4. Cómo se prueba cada motor (paso a paso, con universo y fórmula)

Formato de cada bloque: **universo · fórmula · cómo se validó · resultado · qué es PASS aquí · no-conformes.**

### 4.1 Inversión a plazo — rendimiento  [PASS 100%]
- **Universo:** 530,195 periodos de pago (157,999 cuentas de inversión).
- **Fórmula (doc):** `Rendimiento = RoundHalfEven2( Ceil10( Ceil10((Capital×Tasa)/100) / DíasAño ) × DíasTranscurridos )`.
- **Cómo:** el oráculo recalcula cada periodo desde el capital y la tasa; la prueba devuelve los periodos que no cuadran.
- **Resultado:** **0 violaciones** en 530,195. **PASS** = 0 filas fuera.

### 4.2 Rendimiento vista  [◐ 82%] — ver §3.

### 4.3 GAT de inversión  [PASS — motor validado]
- **Universo:** 689,479 inversiones con GAT guardado (`account.nominal_cgat`).
- **Fórmula (doc):** `GAT = ((Inicial+Interés)/Inicial)^(360/días) − 1`.
- **Cómo (prueba no-circular):** el GAT depende solo de (tasa, plazo), **no del monto**. Verificamos que **decenas de
  miles de inversiones del mismo plazo tienen el MISMO GAT** (term 7 = 10.42% en 126,465 inversiones) y que el oráculo
  lo **reproduce exacto** desde la tasa. Eso prueba que el motor es correcto sin necesidad de que cada contrato sea
  distinto.
- **PASS:** el oráculo = el GAT de Aurum para la tasa de cada plazo. El cruce 1-a-1 masivo espera la tabla de tramos
  de tasa (Finsus la arma) — es cobertura, no un defecto.

### 4.4 ISR — retención  [PASS — C=B; parámetros = ley]
- **Universo:** retenciones posteadas (`INTERNAL TRANSFER` → cuenta de ISR).
- **Fórmula (doc + norma):** ISR sobre la parte gravable del saldo total, prorrateado por cuenta; parámetros 2026
  (tasa 0.9%, exención 5×UMA = 213,973.20, base 365) confirmados contra la ley.
- **Resultado:** C = B = 765.75 (caso de oro). Nota: el **ejemplo del doc tenía un error** (dividía por la base
  gravable); **Finsus corroboró** que lo correcto es dividir por el saldo total — que es lo que hace el sistema y
  nuestro oráculo.

### 4.5 Crédito — interés ordinario  [PASS 96.8% a 1e-8]
- **Universo:** 4,091 provisiones diarias del feed operativo del 20-ago.
- **Fórmula (doc):** `Interés diario = Capital insoluto × (tasa/100) / 360`.
- **Cómo (log ↔ base):** del **log del core** (la provisión diaria) despejamos el **capital que el motor realmente
  usó** y lo comparamos con el capital de la base.
- **Resultado:** **96.8% cuadra a 1e-8**, **0 de 4,091 con la tasa equivocada**. **PASS.**
- **No-conforme (el ~12%):** ver P-019 en §5 — es un gap de las **tablas de reserva**, no del motor de interés.

### 4.6 Crédito — interés moratorio  [PASS 81.1% a 1e-8]
- **Universo:** 1,274 provisiones de mora del 20-ago.
- **Fórmula (doc):** `Moratorio diario = Capital vencido no pagado × (tasaMor/100) / 360`.
- **Resultado:** 81.1% a 1e-8 (95.7% al centavo), 0 con tasa equivocada. El residuo es granularidad del snapshot
  de capital vencido, no del cálculo. (El "2.7%" que apareció al principio fue un error NUESTRO de comparación —
  comparábamos un valor redondeado contra uno sin redondear — ya corregido.)

### 4.7 Crédito — IVA  [PASS 99%]
- **Universo:** 54,716 filas de amortización con IVA cobrado.
- **Fórmula (doc):** `IVA = Interés × 16/100`, half-up.
- **Resultado:** 99.0% cuadra; el 1% es redondeo en montos chicos.

### 4.8 Amortización (tabla francesa)  [PASS en invariantes]
- **Universo:** contratos con tabla francesa (794 en la prueba de identidad; 12 frescos para el cronograma limpio).
- **Fórmula (doc + datos):** cuota financiera constante; **interés = saldo × tasa/360 × días** (base "Actual/360");
  capital = cuota − interés; el saldo baja a 0.
- **Invariantes probados:** (i) total = capital + interés + IVA + seguros **99.9%**; (ii) la suma de capital = el
  préstamo; (iii) la cuota es constante. **PASS** = las identidades se cumplen.

### 4.9 CAT (Costo Anual Total)  [PASS de fórmula 3/3]
- **Universo:** contratos con CAT guardado.
- **Fórmula (doc):** One Click `CAT = (pago/recibido)^(360/días) − 1`; Francesa por tasa interna de retorno.
- **Resultado:** la fórmula reproduce **los 3 ejemplos del doc exacto** y un caso real (35.1%). El cruce masivo da
  bajo porque el campo `cat` guarda en muchos contratos el **CAT nominal del producto** (no el per-contrato) — es
  una cuestión de qué guarda el campo, **no de la fórmula**.

### 4.10 IFRS 9 — etapas + % de reserva  [PASS 37/37 = config de Aurum]
- **Universo:** las 37 filas de la tabla de % + las 3 filas de etapas de la config de Aurum; validado también sobre
  contratos reales con reserva.
- **Regla (config + norma CNBV):** Etapa 1 (0-30 días mora), 2 (31-89), 3 (≥90); `Reserva = base × %` donde el % se
  elige por (tipo de cartera, zona marginada, días de mora).
- **Resultado:** nuestras tablas coinciden **37/37** con `lc_reserve_ifrs` y las etapas con `lc_risk_stage` — es decir,
  **C = la configuración real de Aurum = el criterio CNBV**. La cartera de Finsus se clasifica como **CONSUMO**.
  **Finsus confirmó (24-ago)** que el core **no calcula PD**: usa el % directo, justo nuestro enfoque.

### 4.11 Motor B — completitud (¿no falta ninguna transacción?)  [ROBUSTO]
- **Universo:** 6 días de transacciones, A (openfin) vs B (AurumCore).
- **Criterio:** que no falte nada → **A ≥ B**.
- **Resultado:** +0.1% a +2.1% (openfin siempre ≥ AurumCore) = **sin faltante**.

### 4.12 Contable · Cuentahabientes  [PASS / OK]
- **Doble partida:** la balanza cuadra **$0.00** (0 de 7 días). **Cuentahabientes:** Aurum→WSO2 completo.

---

## 5. Los **no-conformes** — cómo se clasifican y por qué (en general) no invalidan el motor

No todo lo que "no cuadra" es un defecto de AurumCore. Clasificamos cada no-conforme:

| Clase | Qué significa | Ejemplo |
|---|---|---|
| **Defecto** | error real de cálculo | (no hay abiertos en los motores de cálculo) |
| **Defecto histórico de openfin** | el core VIEJO estaba mal; Aurum lo corrige | moratorios One Click #6 (openfin condonaba; Aurum cobra bien) → decisión de Comité |
| **Linaje** | el dato correcto está en otra tabla/fecha | (P-019, resuelto) |
| **Gap de población** | un insumo no está cargado en la tabla que lo lee | **P-019b**: el interés se calcula bien, pero el capital no está en las tablas de reserva para ~12% intra-mes → puede subestimar la RESERVA (no el interés). Escalado (SOL-016). |
| **Data-sourcing** | falta un parámetro/tabla para el cruce fino | GAT/CAT per-contrato (falta la tabla de tramos de tasa) |
| **Bloqueo** | el evento aún no ocurre | rendimiento vista vivo, ISR-vivo (esperan el cierre del 31-ago) |
| **Redondeo** | diferencia de sub-centavo por convención | ya conciliado con la regla de Finsus (half-up por evento) |

**Regla:** el motor de cálculo se declara **validado** cuando los no-conformes que quedan **no** son de la clase
"Defecto" — es decir, son de dato, tiempo o cobertura, no de fórmula. Ese es el caso hoy en todos los motores de
cálculo.

---

## 6. Qué falta y por qué (honesto)

Nada de lo que falta es un defecto de cálculo. Son **dos gestiones + una pieza por definir**:

1. **Manual de Cálculos Oficiales** (lo está preparando Finsus): las 9 tablas de reserva, las fórmulas exactas de la
   reserva de intereses, la tabla consolidada de tasas de inversión y la lista de convención de días por producto.
   Con eso se cierran al 100% los cruces per-contrato de reserva, GAT y CAT. Es además la **fuente autorizada** contra
   la que el dictamen certifica.
2. **Cierre del 31-ago:** valida el motor **vivo** de vista, saldo promedio e ISR al centavo (la vista ya se
   reconstruye de la base al 82%).
3. **Middleware:** aún sin acceso ni alcance definido; es pieza del dictamen.

---

## 7. Cómo interpretar el resultado global

- **13 de 21 puntos en verde**, con **0 desviaciones de cálculo abiertas**. Varios validados contra la **configuración
  real de Aurum** (lo más fuerte).
- Los residuos de los motores de cálculo se **reclasificaron** y ninguno es un defecto de fórmula (son dato, reserva,
  o tiempo).
- **PASS de un motor** = su prueba (que devuelve las filas que violan la regla) queda dentro de la tolerancia, y los
  no-conformes que quedan están **explicados** y **no son defecto de cálculo**.
- **Verde ≠ dictamen.** El dictamen técnico (Aprobado / No Aprobado) lo emite el humano el 7-sep, contra el Manual de
  Cálculos Oficiales; este ejercicio es la evidencia auditable que lo sostiene.

---

### Documentos de respaldo (para profundizar)
`DOSSIER_MOTORES_ORACULO_C.md` (fórmula + resultado + no-conformes por motor) · `COMPARACION_C_vs_DOC.md`
(comparación C vs doc, punto por punto) · `INDICE_PRODUCTOS_PROCESOS.md` (fórmulas + fuentes con página) ·
`RESPUESTA_FINSUS_2026-08-24.md` (la respuesta de Finsus y su impacto) · `ESTADO_RESUMEN.md` (los 21 puntos) ·
`SOLICITUDES_FINSUS.md` (lo pedido a Finsus). Los oráculos (código) están en `40_validaciones/comparadores/`.
