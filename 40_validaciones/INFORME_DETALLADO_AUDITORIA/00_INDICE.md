# Informe Detallado de Auditoría — alcance, periodo y representatividad por validación

> **Respuesta a la petición de la auditoría (reunión 28-ago, F-031):** por cada punto de validación, la **metodología
> de selección del subconjunto** (cuántos y **por qué**), **cuánto representa del universo total**, **qué se valida y
> qué NO**, y el **santo y seña** (tablas, columnas, filtros, llave, motor, tolerancias, corte). Complementa —no
> reemplaza— el `PAQUETE_AUDITOR_DATOS/` (más alto nivel). Linko · tercero independiente · corte 2026-08-26.

## 0. Lo primero que hay que entender: censo vs muestreo

La mayoría de estas validaciones **NO son muestreos estadísticos** — son **censos del alcance elegido**: dentro del
subconjunto definido, se comparan **todos** los registros (la herramienta puede correr el universo completo; no
extrapola de una muestra). La "representatividad" se responde así:

- **Censo pleno:** se tomó **el 100%** de un alcance bien definido (p.ej. *todas* las inversiones live `origin IS NULL`;
  *todas* las provisiones de un día; *todas* las celdas de la tabla de config). Repr. = 100% **de ese alcance**.
- **Subconjunto acotado:** se tomó un recorte **con rationale explícito** (rendimiento/no degradar la base productiva,
  o un campo vivo que solo es válido en cierto estrato). Se declara el **n**, el **universo total** y el **% real**.

**Por qué se acotó (rationale general, F-031 @00:28–00:31):** para **no degradar** AurumCore (base productiva) se
eligieron subconjuntos que cumplían criterios (varios días seguidos, `origin IS NULL`, contratos sin pagos…). Con
visto bueno de la auditoría, **cualquiera de estos se puede correr al universo completo** (no hay límite de muestreo);
el freno fue operativo (performance/concurrencia), no metodológico.

## 1. Tabla maestra de representatividad

> `n` = registros efectivamente comparados. Tipo: **censo** (100% del alcance) / **subconjunto** (con rationale).
> Denominadores de universo total **verificados en BD 2026-08-28** (ver §3).

| Punto   | Motor                   | Tipo                            | n (probado)                | Universo / alcance                                                                                                | Repr.                            | Periodo datos               | Ejecutado        |
| ------- | ----------------------- | ------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------- | -------------------------------- | --------------------------- | ---------------- |
| V-01    | Plazo fijo (live)       | **censo del cohorte aplicable** | 530,195 per / 157,999 ctas | de **1,339,023** periodos live-pagados (36,905,411 totales)                                                       | **~39.6%** (cohorte ≥2 pagos)    | corte 08-20                 | 2026-08-21 17:04 |
| V-02    | Plazo fijo (migrado)    | muestra                         | 3,748 per / 300 ctas       | de **32,986,518** periodos migrados (`origin='FINSUS'`)                                                           | muestra de contraste             | corte 08-20                 | 2026-08-20 18:49 |
| V-07/08 | ISR inversiones         | **censo**                       | 18,599 inv / 14,913 cli    | universo **común A∩B** de inversiones                                                                             | 100% del común                   | corte 08-03                 | 2026-08-17/18    |
| V-13    | Crédito ordinario       | **censo del día**               | 4,091 provisiones          | **todas** las prov. ordinarias del feed 08-20 (de 4,945 contratos con evento ese día; total contratos **31,867**) | 100% del día                     | feed 08-20                  | 2026-08-23 18:26 |
| V-14    | Crédito moratorio       | **censo del día**               | 1,274 provisiones          | **todas** las prov. moratorias del feed 08-20                                                                     | 100% del día                     | feed 08-20                  | 2026-08-23 18:26 |
| V-16    | IVA s/ interés          | **censo**                       | 54,716 filas               | de **55,636** filas con IVA>0 (102,605 amort.)                                                                    | ~98% de las filas con IVA        | corte crédito               | ad-hoc 08-23     |
| V-17    | Amortización            | subconjunto                     | 794 contratos              | contratos **sin pagos** (campo `capital_remaining` es vivo)                                                       | subconjunto por linaje           | corte crédito               | ad-hoc 08-23     |
| V-06    | GAT inversión           | subconjunto-prueba              | 126,465 (term7)            | de **706,600** cuentas de inversión (`account.nominal_cgat>0`)                                                    | estrato de prueba no-circular    | corte 08-20                 | ad-hoc 08-23     |
| V-19    | IFRS 9 (etapas+%)       | **censo config**                | 37/37 celdas               | **toda** la tabla `lc_reserve_ifrs` + `lc_risk_stage`                                                             | 100% de la config                | corte crédito               | ad-hoc 08-23     |
| V-18    | CAT                     | subconjunto (ver CAT-01)        | 4,220 per-contrato         | de 31,867 (25,026 constante / 2,576 cat=0)                                                                        | 13.2% es el estrato con CAT real | corte crédito               | ad-hoc 08-28     |
| V-03    | Vista (integridad feed) | **censo del día**               | 30,769 pagos               | del día 08-18 (DB día completo 38,921)                                                                            | subconj. de 1 pod                | 08-18                       | 2026-08-23 17:15 |
| V-04    | Vista (oráculo, **agosto vivo**) | **censo del ciclo**    | 82,925 ctas                | pagos vista de agosto (≈83,071); base 360·dt31: **94.56% 1e-8 / 94.82% centavo**                                   | ~100% de pagadores ago           | cierre 31-ago / pago 01-sep | 2026-09-01       |
| V-20    | Motor B diario          | **censo por día**               | 6 días (21K–29K ops/día)   | **todas** las ops de esos días                                                                                    | 100% de 6 días                   | 08-10→08-18                 | 2026-08-23 13:10 |
| V-21/22 | Contable doble partida  | **censo por día**               | 7 días (17K–220K asientos) | **todos** los asientos de esos días                                                                               | 100% de 7 días                   | 08-10→08-16                 | 2026-08-20 14:53 |
| V-23    | Cuentahabientes WSO2    | **censo bidireccional**         | 20 / 181,850 / 295         | **todo** el padrón vs WSO2                                                                                        | 100%                             | corte 08-20                 | 2026-08-20 13:58 |

## 2. Estructura del informe

- `01_CAPTACION_FISCAL.md` — plazo, vista, saldo promedio, GAT, ISR.
- `02_CREDITO.md` — ordinario, moratorio, días, IVA, amortización, CAT, IFRS 9.
- `03_CONTABLE_PADRON.md` — Motor B, contable, cuentahabientes.
  Cada ficha: **Alcance (qué sí / qué no) · Periodo · Universo y representatividad · Metodología de selección +
  rationale · Santo y seña (tablas/columnas/filtros/llave/motor/tolerancias) · Conciliación (A/B/C) y resultado.**

## 3. Denominadores (cerrados 2026-08-28 con VPN)

- `iv_payment_plan`: **36,905,411** periodos totales · **3,918,893** live (`origin IS NULL`) · **1,339,023** live-pagados
  · **32,986,518** migrados (`origin='FINSUS'`).
- `lc_loan_amortization`: **102,605** filas · **55,636** con IVA>0 · **31,970** contratos distintos.
- `lc_loan_contract`: **31,867** contratos.
- **Corrección de honestidad:** V-01 se reportaba antes como "100% de lo live" — es **~39.6% de los periodos
  live-pagados**; el resto (mono-pago) **no es validable por el método no-circular** (se declara en la ficha, no se
  esconde). El resultado (0 violaciones en 530,195) no cambia; el **denominador sí**.
- GAT: no existe tabla `investment_account`; las inversiones son filas de **`aurumcore.account`** (8,325,509 total) con
  **`nominal_cgat>0` = 706,600** (el doc citaba 689,479, corte previo). Denominador de GAT **cerrado**.
- El "qué NO se valida" por punto responde también a la petición de ver *"qué se está tomando"* (F-031 @00:49). → P-024.
- **Hora de medición:** los denominadores de arriba se midieron en `aurumcore` el **2026-08-28** (VPN Linko). Las tablas
  vivas pueden derivar entre mediciones.

## 4. Conciliaciones abiertas (AUD-004, levantadas por el auditor)

> Se declaran, no se alinean en silencio.

- **`lc_loan_contract`: 31,867 (Linko, 2026-08-28) vs 31,866 (auditor, 2026-08-28).** Diferencia = **1 contrato** =
  deriva de **tabla viva** (una activación/baja entre mediciones a horas distintas). No cambia ninguna conclusión.
  **Cierre:** corte común o —lo que hacemos aquí— **declarar la hora de cada medición**. La cifra de referencia para el
  informe es **31,867 @2026-08-28**; la del auditor, 31,866 @2026-08-28.
- **VISTA — cifra de referencia [CERRADO 2026-09-01]:** se corrió el **ciclo de agosto vivo, censo completo (82,925
  cuentas) → 94.56% a 1e-8 / 94.82% al centavo** (base 360·dt31). Consistente con el censo de julio (94.76% / 95.03%):
  dos ciclos independientes dan la misma cifra → **cifra de referencia única = agosto vivo 94.56% / 94.82%**. Se retira
  la cota de 20,000 (preview) y la cita de julio como referencia. AUD-004 (VISTA) **cerrado**.
