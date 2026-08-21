---
id: K-MIG-004
titulo: Alcance del paralelo — universos comparables, queries y salidas (balanza + detalle)
dominio: MIG
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:11:42-00:13:38"
    hablante: "SPEAKER_04 (Jorge)"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:42:28 y @00:19:05 y @00:56:37"
    hablante: "SPEAKER_09 / SPEAKER_05 / SPEAKER_08"
relaciones:
  refina: [K-MIG-001]
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El alcance actual del ejercicio de queries es **full captación** más el crédito
**One Click**. Se organiza en ~5 universos y se extrae con ~8-10 queries por core, con dos
"salidas" finales: **balanza** (agregado contable) y **detalle de movimientos** (auxiliares).
  → fuente: F-001 @00:11:42-00:13:38 (SPEAKER_04)

## Detalle
- **Universos** (un "cuero" por colección): (1) clientes, (2) cuentas vista, (3) cuentas plazo,
  (4) transacciones/movimientos, (5) créditos One Click. → @00:12:11, @00:56:37 (SPEAKER_08).
- [CONFIRMADO] El **crédito One Click está amarrado a los plazos** y **domicilia a las cuentas
  vista**; por eso altera saldos y movimientos de captación. → @00:12:11.
- [CONFIRMADO] **Salidas:** balanza = agregado (registrado operativa y contablemente); detalle de
  movimientos = el detalle que alimenta la balanza. → @00:13:03. Precisión (SPEAKER_09 @00:15:51):
  la balanza es **contable** y no siempre refleja transacciones; hay movimientos contables que no
  son transaccionales → conviene comparar **transacción vs transacción** y **contable vs contable**
  por separado.
- [CONFIRMADO] **Volumetría:** ~20 mil transacciones diarias; resultados de queries son resúmenes
  (decenas de miles). → @00:42:28 (SPEAKER_09).
- [CONFIRMADO] **Inventario ~400 operaciones**, ~70-80 recurrentes. → @00:19:05 (SPEAKER_05).
- [CONFIRMADO] Los queries de OpenFin y de Aurum **ya existen y empatan** entre sí; documentados
  en Confluence (parcialmente). Hay una MSP de pruebas funcionales. → @00:37:51, @01:01:32.
- [CONFIRMADO] Días críticos (quincenas) se evita pegarle a la operación al correr queries.
  → @00:42:46 (SPEAKER_09).

## Implicaciones para la validación
- Define el perímetro inicial del oráculo: captación (vista + plazo) + One Click. Crédito general
  y devengamiento de intereses quedan como siguiente cálculo faltante (@00:52:12).
- Confirma DAT: dos capas de comparación (transaccional y contable) — no colapsarlas.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
