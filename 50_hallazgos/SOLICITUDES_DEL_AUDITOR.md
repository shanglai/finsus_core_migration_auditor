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
> Actualizado: 2026-08-26

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
