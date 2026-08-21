---
id: K-MOV-001
titulo: OpenFin opera no-atómico (cargo+abono+reversa); Aurum opera atómico
dominio: MOV
estado: CONFIRMADO
confianza: alta
version: 2
creado: 2026-08-14
actualizado: 2026-08-19
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:23:54-00:24:54"
    hablante: "SPEAKER_10 (Néstor, inferido)"
  - ref: F-021 v2t/finsus_assessment_03_20260819
    ubicacion: "@01:21:09-01:22:37"
    hablante: "Abraham (SPEAKER_02, QA OpenFin, inferido)"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] **OpenFin no hace una transacción atómica**: hace un **cargo** y luego un **abono**;
si el abono falla por regla de negocio, **reversa el cargo** → quedan 2-3 registros de intento
por una sola operación de negocio. **Aurum hace la operación atómica** (un solo registro).
  → fuente: F-001 @00:23:54 (SPEAKER_10)

## Detalle
- Caso éxito: OpenFin puede mostrar 2 registros donde Aurum muestra 1 → comparación 2-contra-1.
- Caso error: OpenFin deja cargo + reverso; Aurum no deja registro (no ejecuta nada). Ej. citado:
  SPEI a CLABE inexistente (ver K-MOV-002).
- Premisa oficial derivada: **"no van a empatar 100%, jamás"**, porque el funcionamiento del core
  A y el B es distinto por diseño. → @00:23:54.

## Regla precisa de correspondencia (F-021, Abraham) — para el Motor B / diario
[CONFIRMADO] La correspondencia OpenFin→Aurum **depende del tipo de operación**:
- **Cuenta-a-cuenta entre clientes Finsus (peer-to-peer):** **2 tx OpenFin (cargo + abono) → 1 tx Aurum.**
- **Unidireccionales (SPEI-in, SPEI-out, pago de servicios, etc.):** **1:1** — el cargo corresponde a un
  cargo y el abono a un abono en ambos cores.
- Universo: son las **~400 del catálogo contable ("de Ines")**. Abraham conoce el patrón general pero
  **no el detalle de las 400** → `[PENDIENTE]` mapear cuáles caen en 2:1 y cuáles en 1:1 (revalidar).
  → fuente: F-021 @01:21:09.

## Implicaciones para la validación
- El comparador de **detalle de movimientos** (Motor B/diario) debe **normalizar según el tipo**: agrupar
  cargo+abono de OpenFin en 1 de Aurum **solo** para las cuenta-a-cuenta; las unidireccionales se comparan 1:1.
- El comparador de **detalle de movimientos** debe **normalizar** la operación de negocio antes de
  comparar conteos: agrupar cargo+abono(+reversa) de OpenFin en la unidad atómica de Aurum.
- Los **conteos de transacciones diferirán legítimamente**; el saldo neteado por cuenta no debe
  moverse (ver K-PRC-001). Clasificación probable de estas diferencias:
  `DIFERENCIA_DISENO_AUTORIZADA`, sujeta a validar caso por caso.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
| 2 | 2026-08-19 | Regla precisa 2:1 (cuenta-a-cuenta) vs 1:1 (unidireccionales); catálogo ~400 de Ines; pendiente el detalle por tipo. | F-021 |
