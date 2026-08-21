---
id: K-MOV-004
titulo: Tipos de transacción de AurumCore observados (parcial) y su efecto
dominio: MOV
estado: CONFIRMADO
confianza: media          # observado en un caso (F-010); no es el catálogo completo (~400 operaciones)
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/datos/ISR - Caso 100-10-233102.xlsx
    ubicacion: "hoja 'Validación ISR', sección 'Transacciones AurumCore'"
relaciones:
  refina: [K-MIG-004]
  depende_de: []
  contradice: []
  usado_por: []
impacto_validacion: medio
---
## Enunciado
[CONFIRMADO] En el caso F-010, las transacciones de AurumCore traen los campos: `Estatus`,
`Fecha de creación`, `Canal`, `Tipo de transacción`, `Monto`, `Saldo final`, `Cuenta`,
`Entrada/Salida`.
  → fuente: F-010, sección "Transacciones AurumCore".

## Tipos observados (parcial)
| tipo de transacción | Entrada/Salida | canal(es) visto(s) | nota |
|---------------------|----------------|--------------------|------|
| Apertura de inversión | Salida | Open Banking | sale efectivo de la cuenta vista al plazo |
| Retorno de Inversión | Entrada | Genérico | regresa el capital al vencer/reinvertir |
| Pago de rendimiento | Entrada | Genérico | abono del rendimiento |
| ISR AurumCore | Salida | Genérico | retención (ver K-FIS-002) |

## Detalle
- `Estatus` observado: `Confirmada`. `Canal`: `Open Banking`, `Genérico`.
- El ejemplo muestra la **secuencia de postería** al vencimiento: Retorno de Inversión (+) → Pago
  de rendimiento (+) → ISR AurumCore (−), afectando el mismo `Saldo final` encadenado.
- Es **catálogo parcial**: F-001 menciona un inventario de ~400 operaciones (~70-80 recurrentes)
  (K-MIG-004). Esto es una muestra de un caso, no el catálogo MOV completo (§8 sigue [PENDIENTE]).

## Implicaciones para la validación
- Da estructura real para el comparador de detalle de movimientos (campos y signo).
- La transacción "ISR AurumCore" debe **amarrarse** a su pago de rendimiento/retorno de origen.
- Alimenta el diccionario de datos (P-004): nombres de campos y valores de dominio reales.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-010. | F-010 |
