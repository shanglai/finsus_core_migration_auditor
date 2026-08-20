---
id: K-DAT-003
titulo: Llaves de OpenFin — cliente, cuenta, secuencia e id_external
dominio: DAT
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-15
actualizado: 2026-08-15
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85.md
    ubicacion: "@00:16:09, @00:36:22, @00:58:14, @01:02:35"
    hablante: "SPEAKER_04 (experto OpenFin/Citi, inferido)"
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85__s020__00-30-39.jpg
    ubicacion: "screenshot · JOIN por secuencia"
relaciones:
  refina: []
  depende_de: [K-DAT-002]
  contradice: []
  usado_por: [00_entendimiento/MODELO_DATOS_OPENFIN.md, 40_validaciones/PLAN_DE_VALIDACION.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Las llaves de OpenFin son compuestas:
- **Cliente** = (`id_sucursal`, `id_role`, `id_asociado`).
- **Cuenta** = (`id_suc_aux`, `id_producto`, `id_auxiliar`) — `id_suc_aux` ≠ `id_sucursal`.
- **Movimiento (PK)** = `secuencia` (única en `detalle_auxiliar`; join con `masdatos` por `secuencia`).
- **Cross-sistema** = `id_external` (OpenFin↔middleware↔Aurum), garantizado sólo en SPEI.
  → fuente: F-011 @00:16:09, @00:58:14, @01:02:35; JOIN por `secuencia` ✔ en s020.

## Detalle
- Un cliente tiene **N** cuentas (N filas en acreedores/deudores). Se listan por la llave cliente. → @00:38:34.
- `secuencia` es secuencial (next_val por default); "teóricamente" no se repite — salvo el bug de
  T-1 (K-DAT-002). → @00:58:14.
- `id_external`: se **forzó** a guardar la clave de rastreo SPEI aquí; en Aurum aparece como
  `transaction_*`, en middleware con otro id. Puede ser **NULL** fuera de SPEI. → @00:14:32, @01:02:35.
- `folio_ticket` ordena los movimientos en el estado de cuenta. → @00:59:28.

## Implicaciones para la validación
- **Correlación A↔B**: sólo SPEI tiene llave 1:1 real (`id_external`); para el resto hay que usar
  llave sustituta (K-MOV-003) o reconstruir. Esto es la base de la Fase 1 del plan de validación.
- Invariante de unicidad de `secuencia` (familia A).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-15 | Creada desde F-011. | F-011 |
