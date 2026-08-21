---
id: K-DAT-002
titulo: Tablas núcleo de OpenFin y ambiente (PostgreSQL, T-1 vs producción)
dominio: DAT
estado: CONFIRMADO
confianza: alta
version: 3
creado: 2026-08-15
actualizado: 2026-08-17
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85.md
    ubicacion: "@00:12:29, @00:15:19, @00:40:06, @00:55:38, @01:12:41"
    hablante: "SPEAKER_04 (experto OpenFin/Citi, inferido)"
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85__s020__00-30-39.jpg
    ubicacion: "screenshot · consulta SQuirreL (nombres da/dam)"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: [00_entendimiento/MODELO_DATOS_OPENFIN.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] La validación de OpenFin se apoya en 5 tablas: **`asociados`** (clientes),
**`acreedores`** (cuentas de captación), **`deudores`** (cuentas de crédito), **`detalle_auxiliar`**
(movimientos) y **`detalle_auxiliar_masdatos`** (extensión del movimiento).
  → fuente: F-011 @00:15:19; nombres `detalle_auxiliar`/`detalle_auxiliar_masdatos` ✔ en s020.

## Detalle
- `detalle_auxiliar` guarda **cargo, abono y saldo final** (no saldo anterior). → @00:12:29.
- `detalle_auxiliar_masdatos` es la extensión, unida por `secuencia` (ver K-DAT-003). → @00:14:32.
- Datos personales/corporativos del cliente viven en otra tabla `directorio` (fuera de alcance). → @00:55:38.
- **Motor: PostgreSQL**, cliente SQuirreL SQL Client. Muchas tablas sin foreign keys declaradas.

## Campos físicos confirmados (F-013, extracciones reales)
- **`detalle_auxiliar` / movimientos** (de `transacciones_02082026_V2`): `idsucaux, idproducto,
  idauxiliar, idsucpol, periodo, tipopol, idpoliza, fecha, hora, cargo, abono, saldo, montoio,
  montoim, montoimp, montocomision, tipomov, referencia, notas, folio_ticket, secuencia`, y en la
  extensión: `id_external, tipo_transaccion, transaction_id, concepto, origen, moneda, customer_id,
  idasociado, numero_autorizacion, descripcion, jdata`, más campos de cartera `am_*` para crédito.
- **`deudores`/`acreedores`** (de `data-credito`): `idsucursal, idrol, idasociado, idsucaux,
  idproducto, idauxiliar, estatus, fechaape, fechaactivacion, montoentregado, tasaio, tasaim,
  plazo, diasxplazo`. Confirma los nombres físicos que en v1 eran conceptuales (P-004 casi cerrada).

## OpenFin — esquema real confirmado (t-1 `openfin_aurum`, `\d+`, F-015)
[CONFIRMADO] La base `openfin_aurum` (t-1) tiene **39 esquemas**; las tablas núcleo de captación están
en **`public`** (767 tablas; 6,308 columnas). DDL confirmado de las 5:
- **`asociados`** (PK idsucursal+idrol+idasociado): + idsucdir/iddir (→ `directorio`, datos personales),
  **estatus 0-3** (del cliente), kasociado (surrogate), ingreso/suspendido/baja.
- **`acreedores`** (cuentas captación; **hereda `auxiliares`**; PK idsucaux+idproducto+idauxiliar):
  fechaape, fechaactivacion, fechacancelacion, **estatus 1-5**, saldoinicial, **saldo**, **tasa**,
  plazo, diasxplazo, **montocontrato** (capital de inversión), **retxaplicar** (ISR por aplicar).
- **`deudores`** (crédito; hereda auxiliares): tasaio/tasaiodesc/tasaim, montosolicitado/autorizado/
  **entregado**, estatuscartera, reservacapital, jdata(jsonb).
- **`detalle_auxiliar`** (movimientos, **65 GB**): cargo/abono/**saldo** (final), montoio/im/imp/comision,
  **tipomov 0-5**, idpoliza/periodo/tipopol, fecha/hora, folio_ticket, **secuencia (PK)**, `am_*`
  (snapshot de amortización de crédito por movimiento), dict(text[]).
- **`detalle_auxiliar_masdatos`** (PK secuencia): **id_external**(text), **tipo_transaccion**(int 3/183/0),
  transaction_id, concepto, origen, customer_id, jdata.

### Hallazgo de modelo — ISR (clave para el gap)
[CONFIRMADO] OpenFin tiene **`isr_diario`** (170 M filas, 29 GB) e **`isr_diario_aux_log`** (42 GB) →
**OpenFin acumula/calcula ISR DIARIO**. AurumCore (F-009) aplica ISR **sólo al pago**. Es una
**diferencia de modelo**: el ISR diario de OpenFin y el ISR-al-pago de Aurum **no son comparables por
evento** sin normalizar. Probablemente explica parte del gap de ISR (K-FIS-003). → candidato A15-ISR-DIARIO.

### Otros esquemas (de los 39) y su relevancia
`ofcore` (núcleo), `contae`/`sic` (contable/buró), `pld` (AML), `migra`; **ETL**:
`etl_saldo_prom_mensual` (saldo promedio → P-006), `etl_tdc_pomelo`, `etl_csf_validations`. Otras
tablas grandes: `pago_intereses_log` (4.5 GB), `inversiones_vencimiento` (4.5 GB), `oflog` (43 GB).

## Ambiente (crítico para la validación)
- [CONFIRMADO] **Producción es la fuente de verdad; T-1 no lo es**: aparecieron **secuencias
  duplicadas** en `detalle_auxiliar` en dic-2025 que rompieron cuadres mensuales. Trabajar en T-1 y
  **validar la cifra contra producción**. → @01:12:41.
- [CONFIRMADO] No correr queries de inversiones con fecha abierta (tumban el ambiente); acotar/LIMIT. → @01:12:17.

## Implicaciones para la validación
- Define el perímetro físico de extracción de OpenFin. Falta el `describe` (nombres físicos de
  columnas y tipos) prometido → P-004.
- El riesgo de secuencias duplicadas en T-1 obliga a un invariante de **unicidad de `secuencia`**
  (familia A) y a fijar el ambiente de extracción.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-15 | Creada desde F-011. | F-011 |
| 2 | 2026-08-16 | Se añaden nombres físicos de columnas confirmados por extracciones reales. | F-013 |
| 3 | 2026-08-17 | Acceso directo a OpenFin t-1: 39 esquemas, DDL confirmado de las 5 tablas, y **hallazgo ISR diario** (isr_diario vs Aurum al-pago). | F-015 |
