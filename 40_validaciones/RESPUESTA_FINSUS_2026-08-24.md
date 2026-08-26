# Respuesta de Finsus — 2026-08-24 (parcial; documentación completa pendiente)

> Respuesta a las solicitudes (SOL-015 y afines). Documentación formal en preparación. Marcado
> **[CONFIRMADO por Finsus 2026-08-24]** con caveat "pendiente el doc con fórmulas exactas".
> Fuente: comunicación Finsus relayed por el usuario (registrar F-### en REGISTRO_FUENTES al llegar el doc).

## 1. PD por tipo de acreditado/actividad (IFRS 9) — **[RESUELTO — el Core NO calcula PD]**
- **[CONFIRMADO]** El Core **no calcula PD**. Calcula reserva con la **metodología CNBV (criterio DOF 04/jun/2012)**:
  un **% de reserva directo por días de mora**, seleccionando tabla por tipo de préstamo (consumo/comercio/vivienda),
  microcrédito y si es reestructurado.
- Entregarán las **9 tablas de porcentajes** tal cual parametrizadas. NO son PD y **no se abren por actividad
  económica** (la actividad solo es dato de reporte C0451, nunca en el cálculo). El PD de IFRS 9 vendría de
  Riesgos/Finanzas, no del sistema.
- **Impacto en C:** **confirma nuestro enfoque** — el % directo (que validamos 37/37 vs `lc_reserve_ifrs`) ES el
  método real. El modelo comercial **EI×PI×SP con PI** de `oraculo_ifrs9` **NO aplica al Core** (dejarlo marcado
  como "no usado por el motor de Aurum"). **Nuevo:** validar también las variantes **comercio** y **reestructurado**
  cuando lleguen las 9 tablas (hoy validamos consumo/micro/vivienda).

## 2. Intereses / capital exigible como base de reserva — **[RESUELTO — define reserva_int]**
- **[CONFIRMADO]** Componentes: `io` = interés ordinario devengado; `iodnc` = devengado no cobrado vigente;
  `iodnc_venc` = traspaso a vencido (interés total − intereses en cuentas de orden); `io_impuesto` = IVA del
  devengado no cobrado. Base = **EPRC cubierta + EPRC expuesta + EPRC intereses vencidos**, afectada por el
  **régimen transitorio**.
- **Detalle clave:** en **cartera vencida (E3) los intereses vencidos quedan como INFORMATIVOS y NO forman parte
  del requerimiento.** → Fórmulas exactas en el doc.
- **Impacto en C:** **explica por qué mi `reserva_int` no cuadraba** (io/iodnc_venc/io_impuesto sueltos) — la base
  es una composición EPRC y en E3 el interés vencido es informativo. Cierra la definición de la base de reserva de
  intereses (pendiente las fórmulas exactas para implementarla al centavo).

## 3. Tramos de tasa de inversión — **[RESUELTO — tabla en construcción]**
- **[CONFIRMADO]** Existen, pero en **dos estructuras**: tramos por **monto** (tabla de tasas por producto y fecha)
  y tramos por **plazo en días** (curva de rangos, una para PF y otra para PM). **No hay hoy una sola tabla
  producto+plazo+monto; la arman y la pasan.**
- **Nota clave:** la **tasa contratada puede venir del canal de originación**; el sistema **solo cae a la tabla
  cuando no la recibe**.
- **Impacto en C:** **explica el residuo del cruce per-contrato de GAT/CAT** — la tasa real no siempre está en la
  tabla (viene del canal), por eso el interés posteado ≠ el nominal. Desbloquea el cruce 1-a-1 de GAT/CAT cuando
  llegue la tabla consolidada.

## 4. Redondeo — **[RESUELTO]**
- **[CONFIRMADO]** **Homogéneo en todo el Core: 2 decimales half-up (half away from zero)**, tanto en interés de
  crédito como en vista.
- **Clave:** se aplica **por concepto y por evento, NO al cierre**: en crédito **cada devengo se redondea antes de
  acumular**; el **IVA se calcula por cada abono por separado** (para no arrastrar centavos); en vista el interés
  mensual se redondea **sin arrastre del sub-centavo**.
- **Convención de días = parámetro por producto (30/360/365)** — entregan la lista producto por producto.
- **Impacto en C:** **confirma half-up** (nuestros oráculos usan `ROUND_HALF_UP` ✓). El matiz **"redondear cada
  devengo antes de acumular"** explica los residuos sub-centavo del ordinario/moratorio: el cargo del período es
  **Σ de diarios ya redondeados**, no la suma exacta redondeada al final. → ajustar el cruce del período (no el
  diario, que ya cuadra) para acumular redondeando por evento.

## 5. Saldo promedio (SPM) — **[RESUELTO + posible DESTRABE del 31-ago]**
- **[CONFIRMADO]** Está **medido y conciliado**. El **saldo promedio se calcula y se GUARDA en la póliza de
  intereses junto con los días devengados (`dt`)**.
- Promedia sobre los **días efectivamente devengados** (no días naturales del mes); conteo **inclusivo en ambos
  extremos** y **el día de fondeo no cuenta**.
- **Base 360:** `interés = saldo_promedio × dt × tasa / 36000` (= SPM × dt × tasa/100 / 360). **Reconcilia al centavo.**
- **Siempre leer SPM junto con `dt`.**
- **Impacto en C — el más grande. [VERIFICADO 2026-08-24]:** el insumo del SPM **está en la BD** — tabla
  **`aurumcore.finsus_account_history`** (105M filas, por cuenta-por-día: `average_balance_amount`, `interest_rate`,
  `balance_amount`, `iv_term_days`). **La fórmula de Finsus se confirmó al centavo** en el caso limpio:
  cuenta 6de5351e, SPM 10,165.70 × dt 31 × tasa 4% / 36000 = **35.02 = posteado** ✓. A volumen sobre los posteos
  reales de vista del 31-jul (`Capitaliza Interes`, `YIELD PAYMENT`): **82.1%** cuadran con `dt` derivado de la fecha
  de fondeo (70.7% con dt=31 fijo). El residuo ~18% es la **convención exacta de `dt`** (inclusivo ambos extremos,
  día de fondeo no cuenta) + el **SPM-de-rendimiento** (que Finsus dice se guarda en la póliza y *puede diferir* del
  average de consulta; en `transaction_detail` NO está — vive en la póliza contable/doc pendiente).
- **NETO:** el rendimiento vista **pasa de 🔒 bloqueado (esperar 31-ago) a ◐ reconstruible de la BD (82%)**; la
  **fórmula queda validada**. El cierre al 100% necesita el `dt` exacto + el SPM-de-rendimiento de la póliza (doc
  pendiente). La corrida VIVA del motor de Aurum sí se observa en el 31-ago, pero ya no es el único camino.
  **Bonus:** esto también acerca el **ISR-vivo** (su saldo base = Σ vista SPM + plazo capital; el componente vista
  ya es leíble de `finsus_account_history`).

---

## Delta de estado tras esta respuesta
| Cierre | Antes | Ahora |
|---|---|---|
| IFRS 9 PI comercial | pendiente Manual | **RESUELTO**: el Core no usa PD; % directo confirmado. Faltan 9 tablas (comercio/reestructurado nuevos). |
| IFRS 9 reserva_int / base exigible | pendiente Manual | **DEFINIDO** (EPRC; vencido informativo en E3); pendiente fórmulas exactas. |
| GAT/CAT per-contrato | pendiente Manual | **DESBLOQUEO en camino**: arman la tabla producto+plazo+monto; ojo tasa del canal. |
| Redondeo | pendiente Manual | **RESUELTO**: half-up, por evento (no al cierre); días param por producto. |
| Saldo promedio / vista | 🔒 31-ago | **DESTRABADO ◐**: fórmula validada al centavo; reconstruido de BD (`finsus_account_history`) al **82%**. Falta dt exacto + SPM-rendimiento de la póliza. |

**Pendiente aún:** las **9 tablas de %**, las **fórmulas exactas de reserva de intereses**, la **tabla consolidada
de tasas de inversión**, y la **lista de convención de días por producto**. Es la "documentación completa" que Finsus
está preparando.
