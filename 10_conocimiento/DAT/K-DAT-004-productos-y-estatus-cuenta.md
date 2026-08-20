---
id: K-DAT-004
titulo: Catálogo de productos (id_producto) y estatus de cuenta en OpenFin
dominio: DAT
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-15
actualizado: 2026-08-15
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85.md
    ubicacion: "@00:37:15, @00:41:16, @00:43:55, @01:10:11"
    hablante: "SPEAKER_04 (experto OpenFin/Citi, inferido)"
relaciones:
  refina: [K-MIG-004]
  depende_de: []
  contradice: []
  usado_por: [00_entendimiento/MODELO_DATOS_OPENFIN.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] **Productos por `id_producto`:** `2000`s = cuentas vista (eje, `2002`, `2006`
apartados, `2015`…); `2301/2302/2307/2308` = inversiones; `3000/4000/5000` = crédito;
**`5004` = crédito "One Click"**. Se valida **toda captación** y, en crédito, **sólo el 5004**.
  → fuente: F-011 @00:37:15, @00:41:16, @01:10:11

## Detalle
- El crédito **revolvente** vive en Pomelo (~3,000 tarjetas), **fuera** de esta validación. → @00:51:17.
- **Estatus de cuenta:** `1`/`2` = onboarding/prospecto (sin cuenta); `3` = activa; `4` = cerrada
  (p.ej. inversión pagada); `5` = cancelada. **Sólo estatus 3 puede transaccionar.** Interés
  operativo: 3 y 4. → @00:43:55–00:46:49.
- Reinversión: abre cuenta nueva; la anterior queda en estatus 4 con `fecha_cancelacion`. → @00:44:59.

## Implicaciones para la validación
- Filtros base de los queries de extracción (K-DAT-005/MODELO_DATOS). El universo de crédito en
  Aurum debe ser **exactamente** el producto 5004 (otros que aparezcan son pruebas/ingestas).
- Invariante: no debe haber movimientos contra cuentas fuera de estatus 3.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-15 | Creada desde F-011. | F-011 |
