---
id: K-MOV-002
titulo: SPEI OUT — OpenFin no valida estructura de CLABE; Aurum sí (algoritmo de control)
dominio: MOV
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:06:32-00:08:32"
    hablante: "SPEAKER_05 (Juan, inferido)"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:29:34-00:30:34"
    hablante: "SPEAKER_04"
relaciones:
  refina: []
  depende_de: [K-MOV-001]
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] En SPEI OUT, **OpenFin no valida la estructura de la cuenta CLABE**: deja salir el
dinero a una CLABE mal conformada, STP lo regresa, y Finsus **paga la comisión de ida y de
vuelta** (~$0.75 + ~$0.75). **Aurum sí valida** (se menciona un "algoritmo de Luna" — probable
dígito de control/Luhn) y **detiene** la operación, sin generar registros.
  → fuente: F-001 @00:06:32 (SPEAKER_05), @00:29:34 (SPEAKER_04)

## Detalle
- [PENDIENTE] Confirmar el algoritmo exacto ("de Luna" es transcripción; probable dígito
  verificador de la CLABE). Nota "posible error de transcripción" (§7.1).
- Efecto en cifras: OpenFin genera **2 operaciones** (salida + entrada por el rechazo de STP);
  Aurum **0**. El saldo neto no se mueve en ninguno, pero el conteo y la comisión sí difieren.
- SPEAKER_04 lo califica como **entrega de valor de Aurum** (evita el doble pago de comisión).

## Implicaciones para la validación
- **Candidato a `DEFECTO_OPENFIN`**: el doble pago de comisión por CLABE inválida es un costo real
  evitable. Cuantificable: nº de eventos × 2 × comisión SPEI. Registrado en
  `50_hallazgos/CANDIDATOS_A_HALLAZGO.md`.
- El comparador SPEI debe tratar estos casos como diferencia esperada (Aurum sin registro) y
  cuantificar el impacto económico en OpenFin, no marcarlo como "falta operación en Aurum".

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
