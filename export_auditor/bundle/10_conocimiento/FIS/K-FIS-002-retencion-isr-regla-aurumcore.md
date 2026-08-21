---
id: K-FIS-002
titulo: Regla de retención de ISR sobre rendimientos (AurumCore)
dominio: FIS
estado: CONFIRMADO
confianza: alta          # MECÁNICA confirmada (F-016) + VALIDADA en BD (C=B) + PARÁMETROS confirmados contra norma (K-FIS-004, P-010 cerrada)
version: 3
creado: 2026-08-14
actualizado: 2026-08-19
fuentes:
  - ref: 20_fuentes/docs/GTM-Pago de Rendimientos-140826-230050.pdf
    ubicacion: "§6 (p.4-6)"
  - ref: 20_fuentes/docs/motores/AurumCore- Cálculo de Pago de Rendimientos.pdf
    ubicacion: "§6 Retención de ISR (p.5-7), spec oficial v1.0 7-ago-2026"
  - ref: 20_fuentes/datos/ISR - Caso 100-10-233102.xlsx
    ubicacion: "hoja 'Validación ISR' (caso cierre 2026-08-02)"
  - ref: 40_validaciones/_resultados/REPORTE_FASE1_ISR.md
    ubicacion: "§7-9 (validación en BD real, 2026-08-18)"
relaciones:
  refina: []
  depende_de: [K-DEV-001, K-DEV-002, K-DEV-003, K-FIS-004]
  contradice: []
  usado_por: [30_oraculo/ESPECIFICACIONES/S-FIS-001.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] La retención de ISR se aplica **únicamente al momento del pago de rendimientos** (no
durante el devengamiento), sobre la **parte expuesta** del saldo total del cliente, prorrateada por
cuenta.
  → fuente: F-009 §6; corrobora F-010.

## Regla completa (F-009 §6, verificada contra el caso F-010)
1. **Saldo total del cliente** = Σ (vista: saldo promedio mensual) + (plazo: capital inicial).
   Una cuenta con bandera "exento de retención" aporta $0.00.
2. **Parte exenta** = 5 × UMA (personas morales: $0.00).
   - En F-010: `UMA = 42,794.64`, `Multiplicador = 5.0` → base exenta = **213,973.20**
     (coincide con F-009: "≈ $213,973.20" para agosto 2026).
3. **Aplica retención** si saldo total > base exenta.
4. **Parte expuesta** = saldo total − base exenta.
5. **ISR diario del cliente** = (tasa_anual / 365) × parte_expuesta.
   - En F-010: `tasa = 0.009` (0.9%), 365 días → ISR diario = (0.009/365) × 97,162.87 = 2.395796795.
6. **ISR por cuenta/inversión** = días_transcurridos × proporción_de_la_cuenta × ISR_diario_cliente,
   con `proporción = monto_cuenta / saldo_total_expuesto`; redondeo final a 2 (K-DEV-001).
   - Ej. F-010: 120 días × 0.161289 × 2.395797 = 46.37; 7 días × 0.286611 × 2.395797 = 4.81.

## Parámetros — estado tras F-016 (spec oficial) + validación en BD (2026-08-18)
- [CONFIRMADO en config+doc] **Tasa anual 0.9%** (`account_tax` concepto 'ISR BASE', `base_period_type=2`;
  F-016 ejemplo usa 0.9% agosto 2026). Resta fundamento en Ley de Ingresos 2026 → P-010.
- [CONFIRMADO en config+doc] **Días año = 365** (`system_configuration.tax.days.year`; F-016: "la normativa
  en México menciona 365 días").
- [CONFIRMADO en doc] **Exención = UMA × `yield.tax.exempt.uma.amount` (=5)**; F-016: "agosto 2026 ≈ $213,973.20";
  personas morales = $0.00.
- [CONFIRMADO en BD] **Valor APLICADO de la exención = 213,973.20** (UMA 2026), verificado despejándolo del
  ISR real posteado (cliente 1-10-370: 765.75). Ver [[C-001]]: el `system_configuration.exempt.amount=206,367.60`
  (UMA 2025) es config **stale/no usada** salvo un rezago de ~9 días en la transición anual de la UMA (feb-2026).
- [CONFIRMADO contra norma · P-010 CERRADA] Los parámetros coinciden con la ley 2026: **UMA anual 42,794.64**
  (INEGI, DOF 9-ene-2026), **tasa 0.90%** (LIF 2026 Art. 24), **exención 5×UMA sobre saldo promedio diario**
  (LISR Art. 93 fr. XX, beneficio SOFIPO) = 213,973.20, retención sobre el capital como pago provisional
  (LISR Art. 54/135). Ver [[K-FIS-004]].

## Validación en BD real (2026-08-18) — [CONFIRMADO]
El ISR que AurumCore **postea al pago** (transacción `INTERNAL TRANSFER`/`Generic` → cuenta ISR
`100-0000-438220`, `isr = credit_amount`) coincide con el oráculo C: cliente 1-10-370 → **B=765.75, C=765.76**.
OpenFin **devenga** el ISR diario (`isr_diario`/`isr_diario_aux_log`, `provisionar=True`) → el "OF≫AC" del árbol
es **provisión-devengo vs retención-al-pago**, no sobre-retención (ver REPORTE_FASE1_ISR §9).

## [CONTRADICCION C-002] Proporción por cuenta: doc (F-016) ≠ comportamiento (F-010 + BD)
- **F-016 (spec oficial)** escribe: `Proporción Cuenta = Trunc20(Saldo de la Cuenta / Base Gravable)`, con
  `ISR Diario = Base Gravable × tasa_diaria` → al prorratear, cada cuenta paga tasa sobre su saldo COMPLETO
  (la exención sólo "abre la puerta", no reduce proporcionalmente). Ejemplo del doc: 30k de 513,973 → 22.93.
- **F-010 (caso de oro) + BD real** usan: `proporción = saldo_cuenta / saldo_TOTAL` → la exención reduce
  proporcionalmente. Ej. verificado: 1-10-370 → 765.75 (÷saldo_total) vs 2,670.41 (÷base_gravable, F-016);
  oro inv1 → 46.37 (÷saldo_total) vs 148.49 (÷base_gravable).
- La versión ÷saldo_total **suma, sobre todas las cuentas, al ISR total correcto del cliente**; la del doc
  **sobre-retiene** (cobra ISR sobre la parte exenta). El comportamiento REAL es ÷saldo_total (correcto).
- **No se resuelve por cuenta propia** (§3.3): o el doc F-016 tiene un error de redacción (probable), o —si el
  doc es el objetivo— AurumCore **sub-retiene** hoy. Escalar a Finsus (sesión). Registrado en CONTRADICCIONES.
- El oráculo C usa **÷saldo_total** (coincide con la BD). No cambiar sin resolver C-002.

## Relación con el defecto histórico de OpenFin
- [[K-FIS-001]]: OpenFin calculó ISR mal "toda la vida". Con esta regla independiente (desde la
  norma, no desde ningún core), el oráculo **puede arbitrar** si el ISR de OpenFin y/o Aurum es
  correcto. En el caso F-010, las transacciones "ISR AurumCore" (46.37, 4.81, 0.05) **coinciden**
  con el ISR calculado por la hoja → evidencia de que Aurum aplica la regla como está documentada
  (no prueba aún que la regla sea la normativamente correcta: eso es P-010).

## Implicaciones para la validación
- Base directa de la spec S-FIS-001. Alto impacto: el ISR es la cubeta regulatoria (K-FIS-001,
  PAR-352 $2.23M).
- Ojo con el orden de postería en el caso: "ISR AurumCore" es una transacción de **Salida** propia;
  hay que amarrarla al "Pago de rendimiento" / "Retorno de Inversión" que la origina (K-MOV-004).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-009 + F-010. | F-009, F-010 |
| 2 | 2026-08-18 | F-016 (spec oficial) confirma mecánica y parámetros (0.9%, 365, 5×UMA, 213,973.20, personas morales 0, ISR al pago). Validación en BD real (C=B, 765.75). Se abre **C-002** (proporción doc ÷base_gravable vs comportamiento ÷saldo_total). | F-016, BD (REPORTE_FASE1_ISR) |
| 3 | 2026-08-19 | **P-010 CERRADA**: parámetros confirmados contra la norma ([[K-FIS-004]]). **C-002 RESUELTA** (F-019 corrige a ÷saldo_total). | K-FIS-004, F-019 |
