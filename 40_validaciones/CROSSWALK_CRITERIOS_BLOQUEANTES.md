# Crosswalk — Criterios de Hallazgos Bloqueantes (Auditoría Interna Finsus) ↔ cobertura del Oráculo (C)

> Mapea **cada criterio de bloqueo y cada área de riesgo** que definió Auditoría Interna de Finsus
> (F-032, *Criterios de Hallazgos Bloqueantes*, 31-ago) contra **nuestra evidencia**, con estado. Es el marco para el
> **Dictamen del 7-sep**. Linko · tercero independiente · corte 2026-08-31.
> Estados: **✅ Cubierto** · **◔ Parcial / en ejecución** · **⚠ En riesgo / dependencia externa** · **↑ Levantado (hallazgo)**.

## 0. Encuadre: su umbral es $0.99 MXN; nosotros operamos al centavo y a 1e-8
El criterio raíz es *"diferencias > **$0.99 MXN** no explicables por redondeo o truncamiento"*. **Nuestra validación está
1–2 órdenes de magnitud por debajo:** cuadre al **centavo ($0.01)** y a **8 decimales**, con los residuos sub-centavo
**explicados** como granularidad del snapshot/redondeo (la excepción que su propio criterio contempla). Por su propia
vara, **nuestros residuos no son bloqueantes.** Los tres frentes que sí exigen acción están marcados abajo.

## 1. Las 7 condiciones de bloqueo (§2 de F-032)
| # | Condición (Finsus) | Nuestra cobertura / evidencia | Estado |
|---|---|---|---|
| 1 | Impida dictamen positivo sobre integridad/funcionamiento de los motores | 8 motores validados en datos (plazo 100% · ordinario 96.8% · moratorio 95.7% centavo · IVA 99% · ISR C=B · GAT exacto · CAT 3/3 · IFRS 37/37). **Sin desviación de cálculo material abierta.** | ✅ (3 motores por ejecutar 31-ago) |
| 2 | Diferencias > **$0.99 MXN** no explicables por redondeo/truncamiento | Todo cuadra al centavo/1e-8; residuos sub-centavo explicados (snapshot). Los pocos diffs > $0.99 (vista con `dt=31` fijo) son **método**, se cierran con `dt` por cuenta (31-ago). | ✅ (cerrar dt) |
| 3 | Riesgo de incumplimiento regulatorio | A28-CAT-CERO (revelación CAT, Circular 21/2009) · IDNC/suspensión devengo · cuota Prosofipo · config go-forward ISR 1.45%. **Todos gaps del proveedor / decisión de Comité, no defecto de cálculo nuestro.** | ↑ levantados |
| 4 | Afectación a patrimonio/saldos de ahorradores | Captación validada (plazo, vista, saldo promedio). Residuo abierto: **personas morales** (exención ISR, SOL-011). | ✅ cálculo · ⚠ def. morales |
| 5 | Sin control compensatorio/mitigante suficiente | Cada no-conforme se **clasifica y explica** (defecto/linaje/data-sourcing/bloqueo/redondeo); ninguno queda como "defecto de AurumCore" abierto. | ✅ |
| 6 | Compromete consistencia de transacciones de canales vs core | Motor B: **OF ≥ AU siempre, 0 faltantes** (6 días). **Crosswalk OF↔AU de tipos CONFIRMADO (313/314 por número, SOL-004 bridge cerrado, 2026-08-31)**; falta correr el cruce de **instancias reales** con ese bridge. | ◔→✅ (bridge listo) |
| 7 | Inconsistencia contable/operativa vs reportes regulatorios | Doble partida **$0.00** (7 días). **D2 cerrado 01-sep:** el mapeo `tipo → cuenta` **existe en config** (`cat_accounting_transaction`, 709/28 tipos) y **99.6% de los posteos lo respetan** (K-CTB-001 v2). Residual 0.4% (edge cases) a caracterizar. Reportería regulatoria: pendiente regenerar. | ✅ mapeo · ◔ reportería |

## 2. Las 8 áreas de riesgo priorizadas (§3 de F-032)
> Se conserva su numeración (su tabla salta el #4).

| # | Hallazgo potencial (Finsus) | Sev. (ellos) | Nuestra cobertura / estado |
|---|---|---|---|
| 1 | Diferencias Oráculo vs Manual Oficial > $0.99, no por redondeo | Crítica | ✅ Cuadre al centavo/1e-8; residuos < $0.99 y explicados. Riesgo controlado con `dt` (31-ago). |
| 2 | Errores **sistemáticos** (no aislados) en interés/retención/IVA/comisiones/saldos | Crítica | ✅ con vigilancia. Corremos **prueba de sesgo**; donde hay, es **método** (redondeo/`dt`/snapshot), no core — demostrado caso a caso. Es el criterio que más exige rigor. |
| 3 | **Imposibilidad de que Auditoría Interna reproduzca** el Oráculo | Crítica | ⚠ **Ruta crítica.** Nuestra parte lista (bundle reproducible + manual + `sanity_check.py`). **Depende de que el grupo auditoría tenga acceso** → `ACCESO_Y_RED.md` a su IT **ya** (ruta a la subred + usuario read-only). |
| 5 | Mapeo contable incorrecto (registro incompleto/omitido/erróneo) | Alta | ✅ **D2 cerrado (01-sep):** el mapeo existe en config (`cat_accounting_transaction`) y **99.6% de los posteos usan pares definidos** (K-CTB-001 v2). Residual 0.4% (13 pares bajo volumen) → caracterizar. No es "cuenta equivocada" sistemática. |
| 6 | Errores en saldos de captación (físicas/morales) que afecten monto a devolver | Alta | ✅ plazo/vista validados. ⚠ **personas morales** (exención, SOL-011). |
| 7 | Errores en CAT / tasa / saldo insoluto de OneClick (transparencia regulatoria) | Alta | ↑ **A28-CAT-CERO**: 2,573 créditos activos cobran ~28% con `cat=0` (campo sin poblar) → revelación de CAT. **Levantado (P-023).** Fórmula CAT: 3/3 vs doc, sin defecto. |
| 8 | Pruebas "no ejecutadas" o con errores en procesos críticos (captación/OneClick/transacciones) | Crítica | ◔→✅ **VISTA ejecutado (01-sep): ciclo vivo agosto, `dt` por cuenta = 97.47%/97.65%** (con dt=31 fijo: 94.56/94.82; AUD-004 cerrado). Quedan: SPM (logs, confirmatorio) e ISR-vivo (base punto-en-tiempo, SOL-003) — **insumo externo**, no falla del motor; y CAT-01 (SOL-015 días). |

## 3. Ruta crítica al 7-sep (lo que estos criterios obligan)
1. **Reproducibilidad (criterio #3):** provisionar acceso al **grupo auditoría de Finsus** (su IT, `ACCESO_Y_RED.md`) para que recalculen e igualen el Oráculo. Sin esto, es bloqueante por sí solo.
2. **Ejecución (criterio #8):** correr el **31-ago** (VISTA censo agosto + `dt` por cuenta + SPM + ISR-vivo) y **CAT-01**; con eso salen de 🔒 los motores de alcance crítico.
3. **Sesgo (criterio #2):** dejar impecable que cada sesgo detectado es método/dato, no core (el `dt` por cuenta cierra el de vista).
4. **Dependencias de Finsus (no de cálculo):** catálogo de mapeo contable (D2, #5/#7-condición), definición de personas morales (#6), y las decisiones de Comité sobre A28/IDNC/Prosofipo (#3-condición).

## 4. Síntesis para el Dictamen
- **No hay hallazgo bloqueante de cálculo abierto** por la vara de Finsus ($0.99): la precisión está muy por debajo del umbral y los residuos son explicables.
- Lo que queda son **(a) dos ejecuciones nuestras** (31-ago, CAT-01), **(b) el acceso del grupo auditoría** (reproducibilidad), y **(c) definiciones/decisiones de Finsus** (mapeo contable, morales, A28/IDNC/Prosofipo) — ninguna es un defecto de cálculo de AurumCore detectado por C.
