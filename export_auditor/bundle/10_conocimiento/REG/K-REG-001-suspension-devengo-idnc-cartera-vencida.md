---
id: K-REG-001
titulo: Suspensión de devengo e IDNC en cartera vencida — Gap B de Finsus REFUTADO
dominio: REG
estado: CONFIRMADO
confianza: alta
version: 2
creado: 2026-08-19
actualizado: 2026-08-19
fuentes:
  - ref: F-020 GAP_Analysis_Motores.pdf (Finsus) — Gap B
    ubicacion: "Motor de Suspensión de Devengo e IDNC"
  - ref: F-023 Linko - AurumCore.pdf (respuesta oficial AurumCore) — §2
    ubicacion: "Motor de Suspensión de Devengo e IDNC (p.5-7); ejemplo crédito 123-1515-1837, IO_VENC $1,843.74"
  - ref: F-016/motores AurumCore_ Cálculo de Intereses de Créditos.pdf (v1.0, 3-feb-2025)
    ubicacion: "§2-3 (devengo diario ord/mor); NO menciona suspensión ni IDNC"
  - ref: Norma CNBV (SOFIPO/EACP), criterios contables alineados a IFRS 9 (marzo 2020)
    ubicacion: "Anexos CNBV: https://www.cnbv.gob.mx/Anexos/Anexo%204%20CUIFE.pdf ; https://www.cnbv.gob.mx/Anexos/Anexo%20D%20EACP.pdf ; R04-C SOFIPOS"
  - ref: BD AurumCore (aurumcore) — lc_finantial_data_stage (solo lectura, 2026-08-19)
    ubicacion: "iodnc/imdnc/capital_venc/stage; 2,651,935 filas"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El **Gap B de Finsus** ("falta el motor de suspensión de devengo / IDNC en cartera vencida")
es un **gap de DOCUMENTACIÓN, no de funcionalidad**: AurumCore **sí implementa** la suspensión del
reconocimiento en resultados y el registro de **intereses devengados no cobrados (IDNC)**. El mecanismo
vive en el módulo **IFRS9/staging** (`lc_finantial_data_stage`), no en el doc del motor de intereses.

## Lo que exige la norma (verificado)
[CONFIRMADO] Para SOFIPO/EACP (criterios contables CNBV, alineados a IFRS 9, modificados marzo 2020):
- **Etapas por atraso:** Etapa 1 (<30 días), Etapa 2 (30–89), **Etapa 3 = ≥90 días = cartera vencida**.
- **Suspensión:** "No deberán reconocerse en resultados los intereses devengados sobre operaciones
  vencidas, sino hasta que hayan sido efectivamente cobrados."
- **IDNC:** los intereses devengados no cobrados de cartera vencida se registran en **cuentas de orden** y
  se **reservan al 100%** (Criterio B-4). No se incluyen en el saldo sujeto a calificación.

## Lo que dice el doc de AurumCore (por qué Finsus lo marcó)
[CONFIRMADO] El PDF "Cálculo de Intereses de Créditos" (v1.0, 3-feb-2025) sólo cubre el **devengo diario**
de interés ordinario (sobre saldo insoluto) y moratorio (sobre capital vencido). **No menciona** la
suspensión al pasar a Etapa 3 ni el IDNC a cuentas de orden. Finsus hizo su gap analysis desde este doc →
por eso lo marcó como faltante.

## Lo que muestra la BD (el mecanismo existe y opera) — evidencia
[CONFIRMADO] La tabla `aurumcore.lc_finantial_data_stage` (2,651,935 filas, fechas 2023-10 a 2026-08)
tiene campos y valores de IDNC:
- `iodnc` (Interés Ordinario Devengado No Cobrado): poblado en **2,339,027** filas; suma **−$4,564,129,742.71**
  (negativo = contra-cuenta que **saca** el interés de resultados).
- `imdnc_*` (moratorio DNC): poblado en 338,275 filas. `capital_venc`: 261,984 filas.
- `io` (interés ordinario en resultados): +$6,094,823,698.61. `capital_venc`: $3,208,501,492.56.
- Clasificación por `stage` (1/2/3) vía `cat_severity_no_coverage` / `cat_loan_accounting_classification.risk_stage_level`.
- Tablas de reporte IFRS: `lc_ifrs_report`, `lc_ifrs_report_452_manual_data`, `lc_report419_monthly_balance`.

→ El interés se devenga (io) pero una parte grande se reclasifica a IDNC (iodnc, negativo) → consistente
con "no reconocer en resultados el devengo sobre cartera vencida". **El motor NO falta.**

## La lógica ahora está DOCUMENTADA por AurumCore (F-023, respuesta oficial)
[CONFIRMADO] AurumCore respondió a la observación con el detalle del tratamiento (cierra el "gap de
documentación"). En sus palabras: al día **90 de mora → cartera vencida**:
- Se **detiene el devengo** en cuentas normales de resultados.
- El interés ordinario acumulado se identifica como **intereses vencidos** (ejemplo: `IO_VENC = $1,843.74`).
- Ese devengado no cobrado se **aprovisiona al 100%** en `RESERVA_INT_RESULT` y `RESERVA_INT_ACTIVO` ($1,843.74).
- Los nuevos intereses ya **no se reconocen como ingreso**; se devengan/controlan en **cuentas de orden**.
- Mantiene **separados** impuestos e IDNC para trazabilidad contable.
- Ejemplo de crédito: **123-1515-1837** (con estados en cartera vigente vs vencida; las pólizas van como
  imágenes en el PDF — no extraídas por texto).
→ Coincide con la norma (CNBV C-16 / IFRS9). **Confianza de diseño: alta.** Es diseño declarado por el
proveedor (§7.4/§9): falta corroborar los **montos en datos**.

## Implicaciones para la validación
- **Gap B REFUTADO como "motor faltante".** Es un gap de documentación (el motor de intereses no lo
  documenta; el módulo IFRS9/staging sí lo hace **y AurumCore ya lo documentó en F-023**). Ejemplo del valor
  del tercero independiente: no se acepta la lista de gaps de Finsus sin verificar (§1, §3).
- **[PENDIENTE — validación 2.1.7, ya con doc]** Validar que la lógica documentada se cumpla **en datos**:
  reproducir el ejemplo `123-1515-1837` (transición vigente→vencida), verificar umbral 90 días, IO_VENC,
  reserva 100% en `RESERVA_INT_RESULT`/`RESERVA_INT_ACTIVO`, y el devengo posterior sólo en cuentas de orden.
  Ya **no** está bloqueado por falta del doc (F-023 lo aporta); ahora es cuadre en BD. Notas a revisar: todos
  los `estado='PENDIENTE'` (¿un solo estado?) y las bandas de `cat_severity_no_coverage` (stage 3 con 271–360
  días — son buckets de severidad de reserva, distintos del umbral de 90 días de cartera vencida).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-19 | Creada: norma verificada + BD muestra IODNC/IMDNC activos → Gap B (Finsus) refutado como motor faltante. | F-020, norma CNBV, BD |
| 2 | 2026-08-19 | AurumCore documenta la lógica (F-023): 90d, IO_VENC, reserva 100% RESERVA_INT_*, cuentas de orden, ejemplo 123-1515-1837. Cierra el bloqueo de doc; queda cuadre en datos. | F-023 |
| 3 | 2026-08-19 | **Mecánica CONFIRMADA en datos:** `io_venc` es la contra-cuenta negativa que **cancela exactamente** `io` (io+io_venc=0 en créditos con suspensión total); último corte 88 vencidas reversando $137K vs 61 vigentes. Ej. contrato con io=+20,521.11 / io_venc=−20,521.11 / capital_venc=−92,000. La suspensión del devengo **opera**. | Extracción BD 2026-08-19 (lc_finantial_data_stage) |
