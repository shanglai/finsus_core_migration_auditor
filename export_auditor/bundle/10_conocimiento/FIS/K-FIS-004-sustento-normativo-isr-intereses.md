---
id: K-FIS-004
titulo: Sustento normativo del ISR sobre intereses (SOFIPO) — cierre de P-010
dominio: FIS
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-19
actualizado: 2026-08-19
fuentes:
  - ref: INEGI · Comunicado 1/26 (valor UMA 2026)
    ubicacion: "DOF 9-ene-2026, vigente 1-feb-2026 · https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2026/uma/uma2026.pdf"
  - ref: Ley de Ingresos de la Federación 2026 · Art. 24 (tasa de retención ISR sobre intereses)
    ubicacion: "https://www.diputados.gob.mx/LeyesBiblio/pdf/LIF_2026.pdf ; corrobora russellbedford.mx, siemprecontable.net, dfk.com.mx, amcpdf.org.mx"
  - ref: LISR Art. 54 y 135 (retención por el sistema financiero) · Art. 93 fr. XX (exención de intereses)
    ubicacion: "https://sdv.com.mx/compendio/ley-isr/articulo-54/ y /articulo-93/ (texto vigente 2026)"
  - ref: Tratamiento fiscal de intereses en SOFIPOs (exención Art. 93 aplicable a SOFIPO)
    ubicacion: "https://www.yimt.com.mx/no-pagues-de-mas-entiende-el-tratamiento-fiscal-en-mexico-de-los-intereses-en-sofipos/"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: [10_conocimiento/FIS/K-FIS-002-retencion-isr-regla-aurumcore.md, 30_oraculo/ESPECIFICACIONES/S-FIS-001.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Los parámetros del ISR sobre intereses que aplica AurumCore **coinciden con la norma
vigente para 2026**. Cierra **P-010** (la verificación normativa que le da a C su valor de árbitro).

## Parámetros verificados contra la norma
| parámetro | AurumCore | norma 2026 | fuente |
|-----------|-----------|-----------|--------|
| **UMA anual** | 42,794.64 | **42,794.64** (diaria 117.31 · mensual 3,566.22) | INEGI, DOF 9-ene-2026, vigente **1-feb-2026** |
| **Tasa de retención anual** | 0.9% (0.009) | **0.90%** sobre el capital, como pago provisional | LIF 2026 **Art. 24** (remite LISR Art. 54/135); subió desde 0.50% (2025) |
| **Exención** | 5 × UMA sobre el saldo (total del cliente) | **5 × UMA** sobre el **saldo promedio diario** de la inversión | LISR **Art. 93 fr. XX**; sólo se grava el excedente |
| **Base exenta 2026** | 213,973.20 | 5 × 42,794.64 = **213,973.20** | (derivado) |
| **Días del año** | 365 (`tax.days.year`) | tasa anual prorrateada; 365 estándar | práctica; LISR no fija 360 para este cálculo |
| **Personas morales** | exención = $0 | el sistema financiero **no retiene** a personas morales (LISR Art. 54) | ver Nota |

## Detalle normativo
- [CONFIRMADO] **Retención = tasa × capital, como pago provisional.** LISR Art. 54/135: las instituciones
  del sistema financiero retienen aplicando la tasa que fija el Congreso en la LIF, **sobre el monto del
  capital** que da lugar a los intereses (no sobre los intereses). Es anticipo, se acredita en la anual.
- [CONFIRMADO] **Tasa 2026 = 0.90%** (LIF 2026 Art. 24). Es un **aumento fuerte** desde 0.50% en 2025 y 2024.
- [CONFIRMADO] **Exención Art. 93 fr. XX**: los intereses pagados por instituciones de crédito (aplica a
  **SOFIPO** — es uno de sus beneficios fiscales, ver fuente Yimt) están **exentos** si el **saldo promedio
  diario** de la inversión no excede **5 UMA elevadas al año**; sólo se grava el excedente. Referencia 2024:
  5 × 39,606.36 = 198,031.80; **2026: 5 × 42,794.64 = 213,973.20** = el valor que aplica AurumCore.
- [CONFIRMADO] **Vigencia UMA**: la UMA 2026 aplica **desde el 1-feb-2026**; en enero sigue la UMA 2025
  (41,273.52 anual → 5× = 206,367.60). Esto **cierra el residuo de C-001**: en `isr_diario` se vio un bloque
  del **2026-02-03 al ~02-11** con exención 206,367.60 (UMA 2025) → fue un **rezago real** de la
  actualización (debió aplicar 213,973.20 desde el 1-feb) → sobre-retención menor y acotada esos ~9 días.

## Implicaciones para la validación
- **P-010 CERRADA:** ya no se prueba sólo "Aurum hace lo que dice su doc", sino "hace lo que dice la ley".
  Los parámetros del oráculo C ([[K-FIS-002]], [[S-FIS-001]]) quedan **confirmados contra la norma**.
- **Refuerza H-J:** la config go-forward de OpenFin (`tasa_ret = 1.45%`, efectiva 2026-08-31) **contradice
  la ley** (la tasa 2026 es 0.90%); si se aplicara, OpenFin **sobre-retendría** de forma indebida. Además,
  una tasa no puede cambiar a media anualidad (es anual por LIF). H-J sube de "riesgo" a **hallazgo probable**.
- **Nota personas morales (a afinar):** LISR Art. 54 excluye de retención a personas morales residentes
  (acumulan y declaran). El doc de AurumCore pone su "exención = $0" (retención completa). Verificar si Aurum
  **omite la retención** a morales por otra bandera, o si efectivamente les retiene (sería discrepancia).
  Para Finsus (SOFIPO) el grueso son personas físicas, así que el impacto es menor, pero conviene cerrarlo.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-19 | Creada: verificación normativa de los parámetros del ISR (UMA, tasa, exención) → cierra P-010. | INEGI, LIF 2026, LISR |
