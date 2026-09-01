# Solicitudes levantadas por el AUDITOR (pendientes de escalar a Finsus)

> **Por qué este archivo existe.** `40_validaciones/SOLICITUDES_FINSUS.md` es propiedad del repo de
> validación y **se sobrescribe en cada sincronización del bundle**. El 2026-08-21 escribí ahí una
> solicitud nueva y el export del 2026-08-24 la borró sin dejar rastro — además de chocar con el
> `SOL-015` que ese repo ya había asignado al Manual de Cálculos.
>
> `50_hallazgos/` no viaja en el bundle (`ensamblar.py` no lo incluye), así que es el lugar correcto
> para lo que nace de este lado. **Estas solicitudes no tienen `SOL-###` todavía**: el número lo
> asigna el repo fuente. Se citan con `AUD-###` hasta que se escalen y reciban su id.
>
> Actualizado: 2026-09-01

---

## AUD-001 — Identidad exacta de la suspensión de devengo / IDNC 🔴

**Estado:** levantada 2026-08-21 · **sin escalar todavía** · bloquea el caso `GAPB-IDNC`

**Contexto.** `REFERENCIA_TABLAS_POR_CASO.md §GAPB-IDNC` declara la identidad `io + io_venc = 0`
("suspensión total del devengo en vencida"). Se corrió contra `lc_finantial_data_stage`
(2026-07-01 → 2026-08-18, filas con `io_venc <> 0`, n=45,761) y **no se reproduce**:

| identidad | se cumple en |
|---|---|
| `io + io_venc = 0` | **24,963 / 45,761 = 54.5%** |
| `io + iodnc = 0` | **315,188 / 369,904 = 85.2%** (filas con `iodnc <> 0`) |

Y **no correlaciona con la mora**, que es lo que uno esperaría si midiera la suspensión:
18,074 de 30,582 en el tramo ≥90 días contra 6,889 de 15,179 en <90.

`iodnc` es además lo que `V3_gapB_idnc.sql` anota como *"contra-cuenta (saca interés de resultados)"*,
y el nombre lo dice: **I**nterés **O**rdinario **D**evengado **N**o **C**obrado.

**Por qué no lo resolví solo.** Cambiar la identidad a la variante que pasa más sería ajustar la regla
al dato — all-pass por la puerta de atrás. Ninguna de las dos llega al 100%, así que la pregunta sigue
abierta aunque eligiera la mejor.

**Lo que se pide.** Cuál es la identidad contable correcta de la suspensión de devengo, y por qué
ninguna de las dos variantes cierra al 100%.

**Nota (2026-08-24).** La respuesta de Finsus sobre reserva de intereses toca este terreno: define
`iodnc` = devengado no cobrado vigente e `iodnc_venc` = traspaso a vencido, y aclara que en E3 los
intereses vencidos son **informativos**. Puede que ahí esté la respuesta, pero las **fórmulas exactas
siguen pendientes** en el doc completo, así que el caso no se desbloquea todavía.

---

## AUD-002 — `yield.tax.exempt.uma.amount` duplicado en `system_configuration` 🟠

**Estado:** detectado 2026-08-21 en la corrida de `ISR-03` · **sin escalar**

**Contexto.** El parámetro aparece **dos veces** con el mismo nombre, la misma sucursal y el mismo
valor (`5`), pero distinto `system_configuration_id` y distinta `category`
(`tax exempt amount for yield payment` contra `yield tax`).

Se descubrió porque `(nombre, sucursal)` no era llave única y el outer join elevaba dos filas a cuatro
violaciones. La llave del caso ya es `system_configuration_id`.

**Lo que se pide.** Cuál de las dos filas es la vigente, y si el core lee una en particular o la
primera que encuentra. Un parámetro fiscal duplicado es un riesgo latente: basta con que alguien
actualice una sola de las dos.

**Relacionado.** C-001 sigue abierta y es el hallazgo grande del mismo caso: `yield.tax.exempt.amount`
está configurado en **206,367.60** (5 × UMA 2025) mientras el core **aplica** 213,973.20 (5 × UMA 2026).
Diferencia **7,605.60**, verificada contra la base el 2026-08-21.


---

## AUD-003 — `MATRIZ_TOLERANCIAS.md` va atrás de dos corridas nuestras 🟡

**Estado:** detectado 2026-08-28 por el chequeo de sanidad del tablero (INV-C3) · **sin escalar**

**Contexto.** El invariante **INV-C3** de `NORTE_SANIDAD.md` pide que una cifra citada no contradiga
en silencio una corrida más reciente. Al correrlo salieron dos filas donde la matriz sigue en
`[PEND]` y este tablero ya tiene el cuadre computado contra la base:

| motor | matriz | corrida de este tablero (2026-08-28) |
|---|---|---|
| **Rendimiento vista** | `[PEND]` / `[PEND]` / `[PEND]` | **96.37%** / **96.37%** / **96.62%** (n = 20,000) |
| **IFRS 9 — etapas y reserva** | `[PEND]` / `[PEND]` / `[PEND]` | **88.10%** / **88.10%** / **100.00%** (n = 20,000) |

**No es una violación del tablero:** el tablero muestra la cifra fresca y la etiqueta como *calculado
aquí*. Es un pendiente **aguas arriba** — quien lea la matriz sola concluye que esos dos motores no
tienen cuadre medido, y sí lo tienen.

**Lo que se pide.** Actualizar las dos filas de `MATRIZ_TOLERANCIAS.md` (§3), o marcarlas con la fecha
y el puntero a la corrida, para que la matriz y el tablero no digan cosas distintas sobre el mismo
motor.

**Lectura del escalón, para que no se copie el número sin su contexto.**
- VISTA `96.37 → 96.62`: el residuo sub-peso es proxy de fecha de activación (fondeo ≠ activación),
  ya documentado; el escalón es angosto porque las diferencias que quedan **no** son sub-centavo.
- IFRS 9 `88.10 → 100.00`: escalón clásico — el residuo es **precisión de la base** (`capital_venc`
  leído a menos decimales de los que el core usó), **patrón P-019, no defecto de AurumCore**. El
  porcentaje implícito en las filas que fallan sale correcto (75.0000 / 90.0001 / 100.0000).


---

## AUD-004 — Dos discrepancias menores contra el `INFORME_DETALLADO_AUDITORIA` 🟢

**Estado:** detectadas 2026-08-29 · **CERRADAS por acuerdo en el export del 2026-08-31** (`INFORME_DETALLADO_AUDITORIA/00_INDICE.md` §4) · sin impacto en conclusiones

El informe detallado cerró los denominadores contra la base el 2026-08-28 y este tablero los
adoptó. Al cruzarlos aparecieron dos diferencias que se levantan en vez de alinearse en silencio.

**(a) `lc_loan_contract`: 31,866 vs 31,867.** Este tablero midió **31,866** contratos el
2026-08-28 al construir `CAT-01`; el informe dice **31,867**. Un contrato de diferencia, casi
seguro por el instante de la medición. No cambia ninguna conclusión —la partición de estratos y
el 13.2% se sostienen igual— pero si dos partes miden el mismo universo con horas de diferencia y
no coinciden, quien lea los dos documentos tiene que saberlo. **Se pide:** confirmar el conteo con
un corte común, o declarar la hora de cada medición.

**(b) VISTA — dos cifras que no son comparables.** El informe reporta el **ciclo de julio** como
censo de 83,094 cuentas: **94.76% a 1e-8 / 95.03% al centavo**. Este tablero corrió el **cierre de
agosto** sobre una cota de 20,000 filas: **96.37% / 96.62%**. Ciclos y universos distintos — ni se
contradicen ni se promedian. El tablero lo muestra con fecha y nota (INV-C3) en vez de presentar
una sola cifra. **Se pide:** acordar cuál es la cifra de referencia para el informe, y si este
tablero debe re-correr el ciclo de julio con el censo completo para que ambos lados publiquen la
misma. Se resuelve solo con el cierre del 31-ago, que es cuando la matriz sella VISTA.

**Nota de método.** La corrección de V-01 (de "100% de lo live" a **~39.6% de los periodos
live-pagados**) llegó del informe de Linko y **este tablero la adoptó tal cual**: era
sobre-afirmación de cobertura, que es el mismo problema-espejo en su dirección fácil.


### Cierre acordado de AUD-004 (export 2026-08-31)

**(a) `lc_loan_contract`.** El cierre **no es alinear la cifra**, es **declarar la hora de cada
medición**: 31,867 (Linko, 2026-08-28) vs **31,866 (este tablero, 2026-08-28 14:29 UTC)**. Un
contrato de diferencia = deriva de tabla viva. La cifra de referencia del informe es 31,867; la
tarjeta de CAT muestra ambas con su hora.

**(b) VISTA.** Referencia vigente = **ciclo de julio, censo de 83,094 cuentas (94.76% a 1e-8 /
95.03% al centavo)**. La corrida de este tablero —agosto sobre cota de 20,000 → 96.62%— queda
etiquetada como **preview**, no como cifra de referencia. Se unifica con el cierre del 31-ago.

> Por qué importa la forma del cierre: alinear la cifra sin explicar la diferencia habría
> producido dos documentos que coinciden y ninguno que se pueda auditar. Declarar la hora deja la
> discrepancia **explicada**, que es lo que un tercero aporta.


---

## AUD-005 — Dos inconsistencias dentro del bundle del corte 2026-09-01 🟠

**Estado:** detectadas 2026-09-01 al adoptar el corte · **no cambian ninguna cifra; sí cambian cómo se leen**

**(a) `sanity_check.py` quedó atrás de su propia matriz.** `MATRIZ_REF` está **hardcodeada** con las
cifras pre-01-sep:

| motor | `MATRIZ_REF` (hardcodeado) | `MATRIZ_TOLERANCIAS.md` (corte 01-sep) |
|---|---|---|
| CRED-ORD | 96.80% @1e-8 | **97.32%** |
| CRED-MOR | 81.10% / 95.70% | **94.66% / 95.38%** |
| IVA | 99.00% @1e-8 | **98.91%** |

El chequeo dice **SANO** porque su lista `CLAIMS` también trae las cifras viejas: es internamente
consistente consigo mismo, pero **ambos lados quedaron atrás de la fuente**. Hoy su **INV-C1
compara una copia contra otra copia**, así que no puede detectar la discrepancia que existe para
detectar. Es exactamente el defecto que el propio NORTE_SANIDAD advierte —"prohibido el default
fabricado"— aplicado a la referencia.

**Se pide:** que `MATRIZ_REF` y `CLAIMS` se **deriven de `MATRIZ_TOLERANCIAS.md`** en vez de
copiarse. De este lado ya se hace así (`auditor_spa/backend/sanidad.py::leer_matriz` parsea el
documento), y por eso mi INV-C1 sí ve la diferencia. Mientras tanto, mi prueba de cruce con su
`sanity_check.py` acota la excepción a esa clase conocida —cualquier violación de otro tipo sigue
rompiendo la suite— y falla sola cuando ustedes actualicen, para recordar quitarla.

**(b) VISTA: la cifra peor se cita sin decir su convención.** La misma corrida da dos números
según la convención de `dt`:

- `dt` **por cuenta** → **97.47% / 97.47% / 97.65%** ← la vigente
- `dt = 31` fijo → 94.56% / 94.56% / 94.82%

`MATRIZ_TOLERANCIAS.md` lo dice bien (declara ambas y cuál manda). Pero
`CROSSWALK_CRITERIOS_BLOQUEANTES.md` §2 área #8 y `INFORME_DETALLADO_AUDITORIA/00_INDICE.md`
citan **94.56/94.82 sin mencionar la convención**. Un lector del crosswalk —que es el marco del
Dictamen— concluye que VISTA está en 94.82% cuando la cifra vigente es 97.65%.

Es el mismo principio que ya aplicamos a la escala: **ningún porcentaje sin el contexto que lo
hace legible**. Aquí el contexto no es la granularidad sino la convención.

**Se pide:** alinear crosswalk e índice a la cifra vigente, declarando la variante como hace la
matriz. El tablero ya muestra ambas con su etiqueta.
