---
id: K-DEV-001
titulo: Redondeo y truncamiento en el cálculo de AurumCore (vs OpenFin 2 decimales)
dominio: DEV
estado: CONFIRMADO
confianza: alta          # v2: ahora sustentado por la documentación oficial F-009 + caso F-010
version: 2
creado: 2026-08-14
actualizado: 2026-08-14
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:46:41"
    hablante: "SPEAKER_04 (Jorge, inferido)"
  - ref: 20_fuentes/docs/GTM-Pago de Rendimientos-140826-230050.pdf
    ubicacion: "p.3 (ejemplo plazo fijo), p.6 (ejemplo ISR)"
  - ref: 20_fuentes/datos/ISR - Caso 100-10-233102.xlsx
    ubicacion: "hoja 'Validación ISR'"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: [30_oraculo/ESPECIFICACIONES/S-FIS-001.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] AurumCore usa **truncamiento a alta precisión en los pasos intermedios y redondeo a 2
decimales al final**; OpenFin trabaja siempre a 2 decimales. La regla exacta de AurumCore (F-009):

| cálculo | pasos intermedios | paso final |
|---------|-------------------|------------|
| Rendimiento **vista** | truncar a **20 decimales** tras cada operación | **redondeo normal a 2** |
| Rendimiento **plazo fijo** | "redondear a 10 hacia arriba" tras dividir; truncar a 20 | **redondeo a 2 half_even** |
| **ISR** | truncar a 20; **ISR diario truncado a 5 decimales** | **redondeo a 2** |
  → fuente: F-009 p.3, p.6; corrobora F-010.

## Detalle
- La narración de F-001 ("Aurum a 20, corta a 5, luego a 2") era aproximada: el "corta a 5"
  corresponde al **truncamiento del ISR diario a 5 decimales** (F-009 p.6 / F-010 F12); los "20"
  a los pasos intermedios; el "2" al redondeo final.
- **El modo de redondeo NO es uniforme**: vista usa "redondeo normal", plazo usa **half_even**;
  además hay un "redondear a 10 hacia arriba" (ceil a 10 dec) en plazo. Esto importa: el §9.3 exige
  que el modo de redondeo sea **parámetro explícito** en el oráculo, y aquí hay ≥3 modos distintos.

## Implicaciones para la validación
- El oráculo (C) debe implementar cada cálculo con su **modo de redondeo específico** (vista=normal,
  plazo=half_even, ISR=trunc 5 + round 2), en `decimal.Decimal`, sin defaults.
- Riesgo de **sesgo**: "redondear a 10 hacia arriba" (ceil) introduce un sesgo positivo por diseño;
  hay que cuantificarlo con prueba de signo (P-014).

## Historial
| v | Fecha | Cambio | Fuente que lo provocó |
|---|-------|--------|-----------------------|
| 1 | 2026-08-14 | Creada desde narración F-001 (confianza media). | F-001 |
| 2 | 2026-08-14 | Promovida a alta y refinada con la regla oficial (trunc 20 / trunc 5 ISR / modos de redondeo por cálculo). | F-009, F-010 |
