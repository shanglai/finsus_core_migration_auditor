---
id: K-DEV-002
titulo: Cálculo de rendimiento de cuentas a la vista (AurumCore)
dominio: DEV
estado: CONFIRMADO
confianza: alta
version: 3
creado: 2026-08-14
actualizado: 2026-08-19
fuentes:
  - ref: 20_fuentes/docs/GTM-Pago de Rendimientos-140826-230050.pdf
    ubicacion: "§5.1 (p.2-3)"
  - ref: extraccion BD AurumCore (solo lectura)
    ubicacion: "2026-08-19 · aurumcore.transaction_detail JOIN account — queries V/W/X/Y/Z/AA"
  - ref: F-022 v2t/finsus_assessment_03_bis_20260819
    ubicacion: "@00:00:00 (fórmula saldo promedio) · F-021 @01:16 (paga día 1)"
    hablante: "SPEAKER_03 / Abraham (Finsus, inferido)"
relaciones:
  refina: []
  depende_de: [K-DEV-001, K-TMP-001]
  contradice: []
  usado_por: []
  relacionado: [P-013, P-015]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El rendimiento de cuentas a la vista se calcula sobre el **saldo promedio mensual**,
procesando cada **día 1° del mes** el mes inmediato anterior.
  → fuente: F-009 §5.1

## Reglas (F-009 §5.1)
- **Base:** saldo promedio mensual de la cuenta.
- **Ventana:** cada día 1° se procesa el mes inmediato anterior, de 00:00 del primer día a 23:59
  del último. Se cuenta **desde la fecha del primer depósito** si ocurrió en el mes anterior, o
  desde el **día 1°** en caso contrario, hasta fin de mes.
- **Elegibilidad:** cuenta en estado `ACTIVE`; cliente `ACTIVE` o `SUSPENDED`; existe esquema de
  rendimientos asociado; y (tasa > 0% **o** bandera de exento de retención = falso).
- **Parámetros del esquema de rendimientos:** días del año (configurable) y tasa.
- **Fórmula (interpretada del ejemplo):** rendimiento ≈ saldo_promedio × tasa × (días_periodo /
  días_año), con los truncamientos/redondeo de K-DEV-001 (vista).
  Ejemplo F-009: saldo $5,000, tasa 7%, 360 días año, 31 días de julio.

## Estado de ejercicio (evidencia BD AurumCore · 2026-08-19)
[CONFIRMADO] El rendimiento/interés de captación vista-ahorro **SÍ se ejerce**. En
`aurumcore.transaction_detail` se postea como `YIELD PAYMENT` con referencia
**`Capitaliza Interes DD/MM/AAAA, Retencion : N`** y **source = target** (la cuenta capitaliza
sobre sí misma), a cierre de mes.
  → evidencia: queries V/W (src=tgt, `misma=True`), X/AA (productos).

- **Universo (historia migrada ene–jul 2026):** ~**100,058** cuentas cliente, **~$59.7M** en 7 meses
  (~$8.5M/mes). Productos de captación (2º segmento de `account_number`):

  | producto | cuentas | interés capitalizado (7 meses) |
  |---|---|---|
  | 2013 | 55,662 | $24,546,025.81 |
  | 2006 | 808 | $20,308,943.73 |
  | 2017 | 39 | $7,519,919.29 |
  | 2015 | 1,641 | $6,021,138.17 |
  | 2012 | 38,089 | $973,181.98 |
  | 2011 | 3,773 | $340,774.48 |
  | 2019 | 46 | $14,612.65 |

  (`2000`/`0000` = cuentas operativas de Finsus, no cliente; se excluyen.)

- [CONFIRMADO] **No confundir con rendimiento de inversión.** El rendimiento de inversión
  (2301/2307/2308) se postea como `Pago de rendimientos-100-2301-…` con **source = INVESTMENT** y
  **target = la cuenta vista del titular** (destino de liquidación, vía cuentas operativas
  `100-0000-*`/`100-2000-40000*`). Ese flujo NO es interés ganado por la vista.
  → queries N/O/P/R/S. Cruzar por `product_type_key` de source **y** target, no por el código de la
  referencia (el código en la referencia es el de la inversión origen, no el del producto que gana).

- [CONFIRMADO · HALLAZGO] **La corrida viva de AurumCore aún no ocurre.** La capitalización mensual
  aparece sólo en historia migrada y **se detiene el 31-jul-2026** (query Y). Post-cutover sólo hay
  devengo/pago **diario de inversión** (query Z, target sólo INVESTMENT). El **primer cierre de mes
  post-cutover es el 31-ago-2026** → hoy (19-ago) la capitalización viva es **inobservable y sin
  validar**. Ver [[P-015]]. Ligado a `origin` migrado-vs-generado ([[P-013]]).

## Fórmula de saldo promedio (F-022, Finsus) y momento de pago (F-021)
[CONFIRMADO] (confianza media, AFIRMACION de Finsus en sesión, corroborar con logs del CORE)
**Saldo promedio del periodo = (saldo_anterior + Σ saldos de cada día) / número de días del periodo.**
  → fuente: F-022 @00:00:00 (SPEAKER_03). Cierra parcialmente [[P-006]] para saldo promedio.
[CONFIRMADO] **El rendimiento de cuenta a la vista se paga SOLO el día 1° del mes.** Los descuadres de
pago de rendimientos se concentran en **cuentas a la vista** (saldo variable, dependen del saldo promedio),
**NO en plazo fijo** (esas cuadran). → fuente: F-021 @01:16 (Abraham).
[CONFIRMADO] **Se valida contra el oráculo (C), NO contra OpenFin.** Como OF paga a las 18:00 y Aurum a
medianoche, los saldos nunca empatan al momento; la validación correcta es que Aurum calcule bien **acorde
a su propio saldo promedio** (contra C/ley), no contra OF. Acotar el universo a **cuentas con el mismo
saldo promedio** para el análisis. → F-021 @01:04-01:20.

## Puntos abiertos
- [PENDIENTE] Corroborar la fórmula de saldo promedio con los **logs del CORE** (`Calculating with average
  balance`) y precisar si "saldo_anterior" es el saldo de cierre del día previo al periodo. El ejemplo de
  vista del doc quedó cortado en la extracción (resto de [[P-006]]).
- [PENDIENTE] Nombres comerciales de los productos 2006/2011/2012/2013/2015/2017/2019 (el join por
  `account_scheme_id` a `mt_producto` no resolvió; query AA devolvió `None`).

## Implicaciones para la validación
- Confirma el tiempo de K-TMP-001 (vista = cierre/1° de mes). Es la base de S-DEV-001, pendiente de
  fijar la definición de saldo promedio.
- **Nueva tarea:** validar la corrida de capitalización del **31-ago-2026** (oráculo C vs AurumCore B)
  para los 7 productos, cuando exista. Antes de esa fecha no hay dato vivo que validar.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-009. | F-009 |
| 2 | 2026-08-19 | Confirmado el ejercicio en BD (~100K cuentas, $59.7M/7mo, mecanismo `Capitaliza Interes` src=tgt); separado del depósito de rendimiento de inversión; hallazgo: corrida viva pendiente (1er cierre 31-ago). | Extracción BD AurumCore 2026-08-19 |
| 3 | 2026-08-19 | Fórmula de saldo promedio declarada por Finsus `(saldo_ant+Σsaldos_día)/n_días`; vista paga día 1°; se valida contra oráculo (no OpenFin) acotando a mismo saldo promedio. | F-021, F-022 |
