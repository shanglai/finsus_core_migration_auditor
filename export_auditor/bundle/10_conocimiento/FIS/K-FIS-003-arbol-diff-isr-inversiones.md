---
id: K-FIS-003
titulo: Árbol de inversiones — Diff ISR es el mayor gap de cálculo (≈27%)
dominio: FIS
estado: CONFIRMADO
confianza: alta
version: 2
creado: 2026-08-16
actualizado: 2026-08-18
fuentes:
  - ref: 20_fuentes/datos/analisis_arboles_20260803/Árboles - Día Cero.xlsx
    ubicacion: "hoja Árboles (Inversiones) y RCA-CAUSA (causas 22,33)"
  - ref: 20_fuentes/datos/analisis_arboles_20260803/Inversiones/03 08 2026 23_59_59 Diff ISR/44_inversiones (1).xlsx
    ubicacion: "hoja diff_isr_44 (columnas isr AC/OF, DIFF, CAUSA)"
relaciones:
  refina: [K-MIG-005]
  depende_de: [K-FIS-002, K-CAP-001]
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] En inversiones, de **18,599 en común**, la dimensión que más difiere entre cores es el
**ISR retenido: 4,988 casos con diferencia (≈26.9%)**. Es el mayor gap de cálculo del árbol.
  → fuente: F-013

## Cifras (corte 02-03 ago)
- En común (cliente+inversión): 18,599 · Único AC 0 · Único OF 0 (cuadran perfecto en existencia).
- Diff Fecha aper/venc: 1 (fecha_venc NULL en OF, id 1-2301-14994).
- Diff Monto de apertura: 0 · Diff Tasa: 0.
- **Diff Rendimiento pagado: 89** (>$0.1); además 4,969 con diff ≤ $0.1 (redondeo).
- **Diff ISR retenido: 4,988.** Cuadran ISR: 72.6% (13,521); nota "no cero / ceros": 79 casos donde
  **un core retiene y el otro no**.

## Causas (RCA del equipo — a verificar por C)
- **3,198 (≈3,628 inversiones):** ISR distinto porque **el saldo de la cuenta al cierre 02/08 difiere**
  (3,034 clientes) → **propaga del Diff Saldo de cuentas** (K-CAP-001). El ISR depende del saldo total
  del cliente (K-FIS-002), así que una diferencia de saldo mueve el ISR.
- **1,790:** retenciones con diferencia < 0.8% por **redondeo** en la retención.

## RESOLUCIÓN — validado contra BD (2026-08-18): NO es defecto de cálculo, es MODELO
Se contrastó el set de desviación material (|A−B|>0.10 = **3,236 inversiones / 2,774 clientes**)
directamente contra la BD (`fase1_isr_desviacion.py`, solo lectura):
- **3,236 / 3,236 clasifican como MODELO.** Cero `REVISAR_OPENFIN`, cero `REVISAR_AURUM`.
- El "ISR de OpenFin" del árbol es la **provisión-devengo diario** (`isr_diario_aux_log`), no una retención;
  su devengo diario **sigue la regla** (isr_diario.isr = C sobre su propio saldo, aceptando UMA 2026 **o**
  2025 en la ventana de transición). AurumCore **retiene al pago** (C=B, verificado).
- Por tanto el "Diff ISR" del árbol = **provisión-devengo (OF) vs retención-al-pago (AC)** = incomparables
  por evento. Es `A15-ISR-DIARIO`, **degradado de defecto a artefacto de modelo**. Ver REPORTE_FASE1_ISR §9.
- Los "uno retiene, el otro no" (exentos): AurumCore=0 correcto (base < 5×UMA); OpenFin provisiona.
- **Bidireccional casi 50/50** (OF>AC 1,710 / AC>OF 1,526) → confirma que NO es sesgo sistemático de fórmula
  (un error de tasa/exención sería unidireccional); la magnitud correlaciona con la **vida** de la inversión.

## Implicaciones para la validación (actualizado)
- El "Diff ISR" **ya no es candidato a hallazgo de cálculo** — es diferencia de momento de reconocimiento.
- **Lo que queda abierto** (no es el descuadre del árbol): **C-002** (proporción del doc F-016 ÷base_gravable
  vs comportamiento ÷saldo_total), **P-010** (verificación normativa UMA/tasa/exención), **H-J** (parámetros
  divergentes go-forward OpenFin 1.45%/158,469). Ver [[K-FIS-002]] v2, CONTRADICCIONES C-001/C-002.
- Nota: el "Diff Saldo de cuentas" (K-CAP-001) sí sigue vivo como su propio tema (no lo cierra esto).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-16 | Creada desde F-013. | F-013 |
| 2 | 2026-08-18 | **Resuelto contra BD**: 3,236/3,236 del set de desviación = MODELO (provisión-vs-pago). Degradado de defecto a artefacto de modelo. | BD (fase1_isr_desviacion.py) |
