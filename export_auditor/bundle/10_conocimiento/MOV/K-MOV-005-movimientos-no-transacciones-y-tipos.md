---
id: K-MOV-005
titulo: OpenFin registra movimientos (no transacciones); tipado 3/183/0
dominio: MOV
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-15
actualizado: 2026-08-15
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85.md
    ubicacion: "@00:08:02, @00:16:09, @00:22:05, @01:04:20, @01:05:06"
    hablante: "SPEAKER_04 (experto OpenFin/Citi, inferido)"
relaciones:
  refina: [K-MOV-001]
  depende_de: [K-DAT-002]
  contradice: []
  usado_por: [00_entendimiento/MODELO_DATOS_OPENFIN.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] OpenFin **no registra transacciones, sólo movimientos de cuenta** (cargo/abono). La
"transacción" de negocio (con comisión e impuestos) vive en el middleware; en OpenFin se ve como
2-3 movimientos separados sin identificador que los una. El **tipo** de un movimiento está en
`detalle_auxiliar_masdatos.tipo_transaccion`.
  → fuente: F-011 @00:08:02

## Tipos (confirmados)
- **`3` = SPEI** — cargo = payout, abono = payin **o** devolución (OpenFin no distingue). → @00:16:09, @01:04:20.
- **`183` = transferencia entre cuentas del mismo banco.**
- **`0` = operaciones internas/manuales** (pago de rendimientos, domiciliación de crédito, ajustes):
  sin contraparte en `masdatos`; se discriminan por string en `referencia`/`concepto`. → @01:05:06.
- ~400 tipos catalogados, **~63 activos** en 2026; **~90% del volumen es tipo 3 + 183**. → @00:19:09, @00:22:05.
- Aurum **no guarda** `tipo_transaccion`: lo reconstruye desde logs/middleware ("masacote"). → @00:20:58.

## Implicaciones para la validación
- El comparador debe **normalizar** los 2-3 movimientos de OpenFin a la unidad atómica de Aurum
  (ver K-MOV-001) y no esperar igualdad de conteos.
- Estrategia 80/20 avalada: cubrir a detalle **tipo 3 y 183** (≈90% del volumen) primero; el otro
  ~10% (60 tipos) es la "última milla". La acreditación/devengo de intereses es el otro foco crítico.
- Para SPEI, cuadrar por `id_external` (K-DAT-003).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-15 | Creada desde F-011. | F-011 |
