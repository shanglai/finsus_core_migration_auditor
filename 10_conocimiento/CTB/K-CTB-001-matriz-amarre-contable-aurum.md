---
id: K-CTB-001
titulo: Matriz de amarre contable de AurumCore (cat_accounting_transaction)
dominio: CTB
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-16
actualizado: 2026-08-16
fuentes:
  - ref: acceso directo a la base aurumcore (\d+ aurumcore.cat_accounting_transaction / aurumcore.transaction_detail)
    ubicacion: "2026-08-16"
relaciones:
  refina: []
  depende_de: [K-DAT-006]
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] AurumCore tiene la **matriz de amarre `tipo → cuenta contable`** en la tabla
`aurumcore.cat_accounting_transaction`, y cada movimiento contable lleva sus cuentas contables en
`aurumcore.transaction_detail`. Esto habilita el dominio CTB (familias B y C del §10).
  → fuente: acceso directo aurumcore (2026-08-16)

## Estructura
- **`cat_accounting_transaction`** — PK `(source_accounting_id, target_accounting_id, branch_id)`.
  Columnas: `transaction_type`, `transaction_description`, `accounting_type`, `cost_center`,
  `transaction_number` ("ID based on source and target accounting accounts"), `status`, `created`.
  → mapea el **par de cuentas contables (origen, destino)** a un tipo/descripción/naturaleza contable.
- **`transaction_detail`** trae en cada fila: `accounting_account`, `source_accounting_account`,
  `target_accounting_account` y `transaction_number` → el amarre movimiento ↔ cuenta contable es directo.

## Vínculo con el árbol (F-013)
Los archivos del árbol "Transacciones/Por tipo de transaccion/`detalle_SRC___TGT_TOTALES_.xlsx`"
están **keados por par de cuentas contables** (source___target) = el `transaction_number` de esta
matriz. Es decir, el árbol de transacciones ya está organizado por la llave contable de Aurum.

## Implicaciones para la validación
- Habilita la **Fase 4 (balanza)** y **Fase 5 (amarre auxiliar↔mayor)**: se puede reconstruir la
  póliza por transacción y amarrar por cuenta contable-día.
- El oráculo (C) puede verificar la **matriz `tipo_movimiento → cuenta contable`** contra la norma/
  catálogo, no sólo contra lo que hace cada core.
- [PENDIENTE] La contraparte en OpenFin (mapeo a sus cuentas contables) — falta su matriz equivalente
  (`id_poliza`, cuentas contables en detalle_auxiliar). Correlacionar por cuenta contable.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-16 | Creada desde acceso directo aurumcore. | acceso aurumcore |
