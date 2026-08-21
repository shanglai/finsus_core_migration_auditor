---
id: K-MOV-006
titulo: Lo que OpenFin no guarda y hay que reconstruir (saldo anterior/promedio, devoluciones)
dominio: MOV
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-15
actualizado: 2026-08-15
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85.md
    ubicacion: "@00:12:29, @00:13:32, @00:17:18, @00:25:04, @01:05:06"
    hablante: "SPEAKER_04 (experto OpenFin/Citi, inferido)"
relaciones:
  refina: []
  depende_de: [K-DAT-002, K-MOV-005]
  contradice: []
  usado_por: [00_entendimiento/MODELO_DATOS_OPENFIN.md, 10_conocimiento/DEV/K-DEV-002-rendimiento-cuenta-vista.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] OpenFin no guarda varios valores clave; hay que **reconstruirlos** desde los
movimientos. Es la principal fuente de dificultad del cuadre.
  → fuente: F-011 @00:12:29–00:13:32

## Qué se reconstruye
- **Saldo anterior:** `detalle_auxiliar` sólo tiene `saldo` (final) y el monto → `saldo_anterior =
  saldo_final ∓ monto` (según cargo/abono) o el movimiento previo. → @00:12:29.
- **Saldo promedio (mensual):** **no se guarda**; se reconstruye — base del rendimiento vista
  ([[K-DEV-002]]). → @00:13:32.
- **Devoluciones:** OpenFin no distingue payin de devolución (ambos abono tipo 3). El middleware sí:
  **STP** vs **interna** (error, no llega a Aurum). Reconstruir requiere ir al middleware. → @00:16:52, @01:04:20.
- **Sin hold/tránsito:** sólo cargo/abono firme; un fallo tras el cargo → reverso + nuevo abono a la
  misma cuenta (aparece como devolución). Caso frecuente de "falta la operación en Aurum". → @00:17:18, @00:25:04.
- **Transferencias a la misma cuenta / de la sucursal 201** (clientes que "ya no transaccionan" pero
  sí lo hacen): generan descuadres reales por decisiones de ingesta. → @00:24:07, @00:26:09.

## Implicaciones para la validación
- Muchos "descuadres" son artefactos de reconstrucción/diseño, no defectos de cálculo. El objetivo
  es **explicar la causa** (K-PRC-001), no forzar el 100%.
- El oráculo debe reconstruir el saldo promedio con la misma lógica que OpenFin para poder arbitrar.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-15 | Creada desde F-011. | F-011 |
