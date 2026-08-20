# Modelo de datos de OpenFin — apartados de trabajo

Versión: 1 · 2026-08-15 · Fuente: **F-011** (sesión de modelo de datos y queries) + screenshots s009 (deck) y s020 (consulta real).
Sustento: [[K-DAT-002]] [[K-DAT-003]] [[K-DAT-004]] [[K-DAT-005]] [[K-MOV-005]] [[K-MOV-006]] [[K-TMP-001]] [[K-DEV-002]]

> **Confianza.** Todo viene de F-011: la **narración** del experto de OpenFin (Citi) + dos pantallas.
> Los **nombres físicos exactos de columnas** llegan con el `describe` prometido (P-004); aquí se
> marca ✔ lo confirmado por la pantalla s020 y se deja el resto como **campo conceptual (narrado)**.
> Motor: **PostgreSQL**, cliente **SQuirreL SQL Client**. OpenFin = "Core Legacy".

## 0. Advertencias de operación
- [CONFIRMADO] **OpenFin es la fuente de la verdad del saldo** (de ahí salen los reportes
  regulatorios), por encima de middleware/backend. → F-011 @00:33:27.
- [CONFIRMADO] **Producción manda; T-1 no es fuente de verdad** (aparecieron secuencias duplicadas
  en `detalle_auxiliar` en dic-2025). Trabajar en T-1 y validar la cifra contra producción. → @01:12:41.
- [CONFIRMADO] **No correr queries de inversiones con fecha abierta** en producción (tumban el
  ambiente); acotar o `LIMIT`. → @01:12:17.

---

## 1. Diccionario de datos

### 1.1 Tablas núcleo (las 5 de la validación)
| tabla | qué contiene | grano |
|-------|--------------|-------|
| `asociados` | todos los clientes (cualquier estatus) | 1 fila por cliente |
| `acreedores` | cuentas de **captación** (débito) | 1 fila por cuenta |
| `deudores` | cuentas de **crédito** (misma estructura que acreedores) | 1 fila por cuenta |
| `detalle_auxiliar` (`da`) | **movimientos de cuenta** (cargo/abono/saldo) | 1 fila por movimiento |
| `detalle_auxiliar_masdatos` (`dam`) | extensión de cada movimiento (datos adicionales) | 1 fila por movimiento |

> Cadena: `asociados` →(llave cliente)→ `acreedores`/`deudores` →(llave cuenta)→ `detalle_auxiliar`
> →(`secuencia`)→ `detalle_auxiliar_masdatos`. Datos personales/corp van en otra tabla `directorio`
> (fuera de alcance). → @00:15:19, @00:40:06, @00:55:38.

### 1.2 Campos (conceptuales salvo ✔ = visto en s020)
**`asociados`** — `id_sucursal`, `id_role`, `id_asociado` (los 3 = llave cliente), `estatus`.
**`acreedores` / `deudores`** — llave cuenta [`id_suc_aux`, `id_producto`, `id_auxiliar`] + llave
cliente [`id_sucursal`, `id_role`, `id_asociado`]; `fecha_apertura` ("fecha AP", la que se usa),
`fecha_activacion`, `fecha_cancelacion`, `estatus`, `saldo_inicial` (0 en cuenta eje; con valor en
inversiones/crédito). `deudores` añade datos de crédito: `monto_entregado`, `tasa_io`, `plazo`,
`dias_por_plazo`. → @00:36:22–00:44:00, @01:14:55.
**`detalle_auxiliar`** — [`id_suc_aux`, `id_producto`, `id_auxiliar`] (cuenta); `periodo`;
`id_poliza`; `fecha`✔, `hora`✔ (ejecución del movimiento); `cargo`, `abono`, `saldo` (final, **no**
hay saldo anterior); `monto_io` (interés originado); `monto_imp` (impuestos); `monto_*` adicionales✔;
`referencia`; `folio_ticket` (ordena el estado de cuenta); `secuencia`✔ (**PK**). → @00:56:21–01:00:23.
**`detalle_auxiliar_masdatos`** — `secuencia`✔ (FK a `da`); `id_external` (llave cross-sistema);
`tipo_transaccion` (**el que importa**); `concepto`; `referencia`; `id_asociado`; `origen`; "masacote"
de campos, con nulos. → @01:00:28–01:05:00.

### 1.3 Catálogo de productos (`id_producto`)
[CONFIRMADO] `2000`s = **cuentas vista** (eje, `2002`, `2006` apartados, `2015`…); `2301/2302/2307/2308`
= **inversiones**; `3000/4000/5000` = **crédito**; **`5004` = crédito "One Click"** (único crédito que
debe vivir en Aurum). En captación se validan **todos** los productos; en crédito **sólo 5004**.
El revolvente vive en **Pomelo** (~3,000 tarjetas), fuera de esta validación. → @00:37:15, @00:41:16, @01:10:11, @00:51:17.

### 1.4 Estatus de cuenta
[CONFIRMADO] `1`/`2` = onboarding/prospecto (sin cuenta); `3` = **activa**; `4` = **cerrada** (p.ej.
inversión pagada); `5` = cancelada. **Sólo estatus 3 puede transaccionar.** Interés operativo: 3 y 4.
→ @00:43:55–00:46:49.

### 1.5 Tipos de transacción (`tipo_transaccion` en `dam`)
[CONFIRMADO] `3` = **SPEI** (cargo = payout, abono = payin **o** devolución); `183` = **transferencia
entre cuentas del mismo banco**; `0` = **operaciones internas/manuales** (pago de rendimientos,
domiciliación de crédito) — sin contraparte en `masdatos`, se discriminan por string en
`referencia`/`concepto`. ~400 tipos catalogados, **~63 activos** este año; **~90% del volumen es tipo
3 + tipo 183**. Aurum **no guarda** `tipo_transaccion`: lo reconstruye desde logs/middleware. → @00:16:09, @00:22:05, @01:05:06, @00:20:58.

---

## 2. Llaves
| llave | composición | tabla(s) | nota |
|-------|-------------|----------|------|
| **cliente** | `id_sucursal` + `id_role` + `id_asociado` | asociados, acreedores, deudores | no cambia para un cliente |
| **cuenta** | `id_suc_aux` + `id_producto` + `id_auxiliar` | acreedores, deudores, detalle_auxiliar | `id_suc_aux` ≠ `id_sucursal` (campo distinto) |
| **movimiento (PK)** | `secuencia` | detalle_auxiliar | única; secuencial (next_val por default) |
| **join da↔dam** | `secuencia` | da ⋈ dam | ✔ confirmado en s020 |
| **cross-sistema** | `id_external` | detalle_auxiliar_masdatos | OpenFin↔middleware↔Aurum; **garantizado sólo en SPEI**, puede ser NULL en otros |
| **orden estado de cuenta** | `folio_ticket` | detalle_auxiliar | ordena movimientos |

Un cliente puede tener **N** cuentas (N filas en acreedores y/o deudores). → @00:38:34, @00:58:14, @01:02:35.

---

## 3. Reconstrucción de transacciones
Lo que OpenFin **no** guarda y hay que reconstruir (el corazón de la dificultad del cuadre):

- **Transacción vs movimiento.** OpenFin **no registra transacciones, sólo movimientos** (cargo/
  abono). Una transacción de negocio (con comisión e impuesto) se ve como **2-3 movimientos
  separados** sin identificador que los una; se asocian por **tiempo** o por **póliza** (frágil).
  La transacción "completa" vive en el middleware. → @00:08:02–00:12:26.
- **Saldo anterior.** No se guarda. `detalle_auxiliar` tiene `saldo` (final) y el monto. Reconstruir:
  `saldo_anterior = saldo_final ∓ monto` (según cargo/abono), o mirar el movimiento anterior. → @00:12:29.
- **Saldo promedio.** **No se guarda**; se reconstruye — es la base del rendimiento vista ([[K-DEV-002]]). → @00:13:32.
- **Transferencias (tipo 183).** Migradas se ven **cargo+abono**; en línea, Aurum las registra como
  **un solo registro A→B** → descuadre de conteo esperado. → @00:10:10.
- **Devoluciones.** OpenFin **no distingue** payin de devolución en el tipado (ambos abono tipo 3).
  El middleware sí: **devolución de STP** vs **devolución interna** (error, no llega a Aurum).
  Reconstruir requiere ir al middleware. → @00:16:52, @01:04:20.
- **Sin hold/tránsito.** Sólo cargo firme o abono firme. Un fallo tras el cargo → **reverso + nuevo
  abono a la misma cuenta** (aparece como devolución). Caso frecuente de "falta la operación". → @00:17:18, @00:25:04.
- **Tipo 0 (internas/manuales).** Pago de dividendos, domiciliación de crédito, ajustes: se
  identifican por string en `referencia`/`concepto`; no tienen contraparte en `masdatos`. → @01:05:06.
- **Inversiones activas en un periodo.** Jugar con `fecha_apertura ≤ fin de mes` **y**
  `fecha_cancelacion` dentro del periodo, aunque hoy el estatus sea 4 (reinversión abre cuenta nueva
  y cierra la anterior). → @00:46:16–00:48:44.

---

## 4. Trazabilidad (linaje entre sistemas)
Fuente de la verdad por dato (deck slide 3, **s009**; asterisco = fuente fidedigna):

| sistema | es fuente de la verdad de… |
|---------|----------------------------|
| **Core (OpenFin)** | TASAS, CAT y GAT, Datos de Producto, Datos Fiscales, **Saldos**, **Movimientos**, Cuentas Contables, PLD, Listas |
| **Middleware** | Nivel de Cuenta, Límite Transaccional, Valor de la UDI, **Tipo de Operación** |
| **Backend** | Datos de Cliente, Datos personales, Datos de Contacto (también TDD/TDC) |
| **Analyzer** | Clave SIEC (CVE SIEC), PLD y KYC, Scoring y Buró, Datos del producto (PM/PFAE/PYME), Dictamen Legal |

- El resto de sistemas tienen **réplicas** que pueden descuadrarse; para el **saldo**, la fuente es
  siempre OpenFin. → @00:03:38, @00:33:27.
- **Cross-core (OpenFin↔Aurum):** `id_external` es la única llave 1:1 confiable, y sólo en SPEI
  ([[K-MOV-003]]). Para el resto, Aurum reconstruye `tipo_operacion` desde logs/middleware. → @01:02:35, @00:20:58.

---

## 5. Queries (catálogo; los "generales" se enviarán por correo)
Ambiente: PostgreSQL vía SQuirreL SQL Client (base `openfin_aurum`, user `aurumcoreuser`, schema
`public` — s020). Trabajar en T-1, validar contra producción. **Siempre acotar fechas / `LIMIT`.**

| # | objetivo | esqueleto (narrado) | fuente |
|---|----------|---------------------|--------|
| Q1 | Clientes (sin estatus) | `SELECT * FROM asociados;` | @01:08:19 |
| Q2 | Cuentas vista | `SELECT … FROM acreedores WHERE id_producto IN (<2000s>) ORDER BY id_producto;` | @01:09:20 |
| Q3 | Inversiones | `SELECT … FROM acreedores WHERE id_producto IN (2301,2302,2307,2308);` (acotar fecha) | @01:11:15 |
| Q4 | Crédito One Click | `SELECT … FROM deudores WHERE id_producto = 5004 AND estatus IN (3,4) AND fecha_cancelacion >= <inicio_periodo>;` → trae monto_entregado, tasa_io, plazo, dias_por_plazo | @01:14:55 |
| Q5 | Movimientos del día ✔ | `SELECT da.*, dam.* FROM detalle_auxiliar da LEFT JOIN detalle_auxiliar_masdatos dam ON dam.secuencia = da.secuencia WHERE da.fecha = DATE '2026-08-12' ORDER BY da.fecha, da.hora, da.secuencia;` | s020 |
| Q6 | Tipos de transacción del 2026 | (mencionado) trae qué tipos hubo en 2026, conteo y montos por tipo | @01:00:28 |

> SPEI (tipo 3): con `da` cargo/abono + `dam.tipo_transaccion = 3` → cargo = payout, abono = payin/
> devolución. Es el único tipo con `id_external` al 100% para cuadrar 1:1.

---

## 6. Momento de corte para comparar (TMP)
- **Transaccional:** se puede cortar a las 00:00+1 min y tomar la fecha anterior completa. → @01:18:02.
- **Cálculos (rendimientos):** OpenFin cierra vista **~18:00** y Aurum **a medianoche** → ~6 h de
  descuadre en el saldo promedio; los nocturnos ya corrieron ~06:00. → @01:18:29, @01:17:29. (Refina [[K-TMP-001]].)
- Recomendación de la sesión: comparar **tras el cierre / procesos de fin de día**, en ventana de
  baja transaccionalidad.

---

## 7. Lo que falta para cerrar P-004 (y P-011)
- `describe` de las 5 tablas (nombres físicos y tipos), diagrama de las 5 tablas, catálogo de las 63
  operaciones, y los queries "generales" (se enviarán por correo).
- **La contraparte de Aurum**: sus tablas de cliente/cuenta/transacción y sus queries — hoy **no
  entregadas** (el equipo de Aurum es "receloso"); es la pieza más incómoda del cuadre. → **P-011**.
- Accesos: VPN + usuario de BD (tramita Juan Lozano) con **correo del proveedor** (no de Finsus).

## Mantenimiento
Actualizar cuando llegue el `describe`/diagrama (fija nombres físicos), cuando entren los queries de
Aurum (P-011) y cuando se corran los primeros cuadres. Depende de K-DAT-002..006, K-MOV-005/006.
