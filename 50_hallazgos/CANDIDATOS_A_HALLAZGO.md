# Candidatos a Hallazgo (del Espacio Paralelo AurumCore)

> **Qué es esto y qué NO es.** Estos son casos **reportados por el equipo de proyecto** en Jira
> PAR / OnePager (F-008), no hallazgos confirmados por este ejercicio. Aún **no** han pasado por
> el arbitraje de tres motores (A openfin · B AurumCore · C oráculo). Se registran aquí como
> **mapa de riesgo y cola de trabajo del oráculo**: cada uno debe reproducirse y clasificarse de
> forma independiente antes de convertirse en `H-###` en `HALLAZGOS.md` (§11 del CLAUDE.md).
>
> Cita base: `20_fuentes/docs/OnePager JIRA Espacio Paralelo AurumCore.pdf` p.1, corte 10-ago-2026.

| folio | dominio | qué reporta la fuente (cita) | prioridad·estatus (10-ago) | responsable | magnitud declarada | qué debe hacer el oráculo |
|-------|---------|------------------------------|-----------------|-------------|--------------------|---------------------------|
| PAR-352 | FIS/CAP (Inversiones) | "$2,232,566.46 sin retención ISR; el ticket indica más clientes potencialmente afectados" | Highest · Revisión→En curso (11-ago, F-004) | Lilian Gutiérrez | $2,232,566.46 + universo por cuantificar | Recalcular ISR de vencimiento de inversión desde la norma; cuantificar universo e impacto fiscal/contable |
| PAR-351 | DEV/COL (Crédito) | "1,261 créditos [Un Click] no tienen devengamiento calculable en Aurum" | High · En curso | Cristhian Méndez | 1,261 créditos | Calcular devengamiento independiente sobre muestra y total |
| PAR-318 | MOV/COL (Crédito) | "689 créditos liquidados/cancelados siguen activos en Aurum; 1,110 presentan diferencias" | Highest · En curso | Cristhian Méndez | 689 + 1,110 créditos | Conciliar estatus y saldos Un Click A vs B vs C |
| PAR-311 | DAT/COL (Cartera) | "Faltan 1,089 de 7,339 contratos esperados en Aurum (15%)" | Medium · Revisión | Abraham Trejo | 1,089 / 7,339 (14.8%) | Explicar el universo faltante; conciliar conteos |
| PAR-343 | TMP/MOV (SPEI) | "Query de devoluciones pendiente; vencido desde 20-jul-2026 y necesario para conciliar" | Highest · Revisión | Abraham Trejo | — (bloqueante) | Definir la identidad de conciliación de devoluciones SPEI |
| PAR-337 | MOV/CTB (SPEI) | "Una devolución SPEI OUT no refleja movimientos de salida/entrada en Aurum" | Highest · Revisión | Juan M. Vital | ≥1 operación | Trazar contabilización end-to-end de la devolución |
| PAR-338 | TMP/CAP (Inversiones) | "Pendiente confirmar impacto de días inhábiles en inversiones ya aperturadas" | Highest · Revisión | Enrique González | — | Modelar calendario de inhábiles en el devengo/vencimiento (dominio TMP) |

## Otros focos cuantificados en el backlog (para priorizar, sin cita individual aquí)
- Reconciliación de conteos del propio tracking: 266 vs 331 (+65) y 132 vs 124 abiertos (F-008) →
  ver P-005. Antes de confiar en las cifras del paralelo hay que cerrar esta conciliación.

## Candidatos derivados de F-001 (sesión kickoff, 2026-08-14)
Reportados/admitidos en la sesión grabada; **no** verificados por el oráculo. Cita:
`20_fuentes/v2t/.../finsus-assessment-...md`.

| ref | dominio | qué se afirma en la sesión | clasificación probable | magnitud | qué debe hacer el oráculo |
|-----|---------|----------------------------|------------------------|----------|---------------------------|
| F001-ISR | FIS | ISR "se calculó mal toda la vida" en OpenFin; corregido recientemente (@00:08:32) | **DEFECTO_OPENFIN** histórico | [PENDIENTE] universo/periodo; posible ligado a PAR-352 ($2.23M) | Calcular ISR desde la norma; contrastar A y B; cuantificar histórico y evaluar regularización (P-007) |
| F001-CLABE | MOV/SPEI | OpenFin no valida CLABE en SPEI OUT → doble pago de comisión (~$0.75 ida + vuelta); Aurum sí valida (@00:06:32) | **DEFECTO_OPENFIN** (costo evitable) | nº eventos × 2 × comisión SPEI [PENDIENTE] | Cuantificar eventos de CLABE inválida y comisión doble pagada en OpenFin |
| F001-REDONDEO | DEV | Redondeo distinto (Aurum 20→5→2 vs OpenFin 2) genera diferencias ≤$0.10 (@00:46:41) | posible **DEFECTO_AMBOS** o REGLA_MAL_ESPECIFICADA si hay sesgo | [PENDIENTE] prueba de signo | Prueba de sesgo sobre distribución de diferencias (P-014) |

> F001-ISR y F001-CLABE son la **cubeta incómoda** `DEFECTO_OPENFIN` (§11): obligatorio abrirlas,
> prohibido suavizarlas. Descubrirlas antes del go-live es problema de proyecto; después, problema
> regulatorio.

> **Actualización F-010 (caso ISR 100-10-233102):** AurumCore **sí reproduce su propia regla de
> ISR** documentada (transacciones "ISR AurumCore" = cálculo de K-FIS-002, al centavo). Esto NO
> cierra F001-ISR: (1) el defecto es de **OpenFin**, no de Aurum; (2) falta verificar que la regla
> de AurumCore sea **normativamente correcta** (P-010). Si la regla estuviera mal, sería caso ≠≠≠
> (regla mal especificada), no defecto de core.

## Candidatos derivados de F-013 (árbol día cero 02-03 ago)
Diferencias reales OpenFin vs Aurum reportadas por el equipo A/B; **a verificar por el oráculo C**.
Cita: `20_fuentes/datos/analisis_arboles_20260803/Árboles - Día Cero.xlsx`.

| ref | dominio | qué se observa | # casos | clasificación probable | acción de C |
|-----|---------|----------------|---------|------------------------|-------------|
| A13-ISR | FIS | Diff ISR retenido en inversiones (mayor gap de cálculo) | 4,988 (~27%) | mixto (cascada saldo + redondeo) | recalcular ISR desde norma sobre mismo saldo; aislar los 79 "uno retiene, otro no" |
| A13-API | DAT/CAP | BUG del API: k_auxiliar → consecutivo → 2,977 cuentas fantasma en Aurum | 2,977 | DEFECTO_CORE_NUEVO | verificar unicidad de llave de cuenta en Aurum |
| A13-TASA2019 | CAP | Tasa del producto 2019 mal configurada en Aurum | 2,053 | DEFECTO_CORE_NUEVO (config) | contrastar tasa configurada vs contrato/norma |
| A13-SALDO | CAP | Diff Saldo por ingesta / sin movimientos (TO DO) | 4,236 | DEFECTO ingesta | verificar saldo por rollforward de movimientos |
| A13-SPEI-SAT | MOV | SPEI (in/out) que no llegan a satélites — **dinero real** | ~decenas | DEFECTO (operativo) | trazar end-to-end; cuantificar importe |
| A13-TERMINATED | MOV/CAP | Cuentas TERMINATED en Aurum que en OF sí transaccionan | varias | REGLA (homologar estatus) | confirmar regla de estatus (Regcheck) |
| A13-REDONDEO | DEV | Redondeo en cuentas (24,910) + inversiones (4,969) + créditos (68) | ~30k | ver P-014 | prueba de signo (sesgo) sobre las 3 distribuciones |
| A13-REND-SESGO | DEV | **[Fase 0, C]** Rendimiento inversiones: 89 diffs, **todas AC>OF** (sesgo unidireccional, ≤$0.05 c/u, suma $0.89). En las 39 de 1 periodo: **OpenFin = truncado a 2 dec en 39/39**; Aurum = half_even = C en ~20 | 89 (39 de 1 periodo + 50 multiperiodo) | **DEFECTO_OPENFIN (redondeo)** en ~20 (OpenFin trunca/subpaga); ~19 por arbitrar (Aurum≠C: ¿defecto Aurum o convención de días?); sesgo → posible sev 1 (§10) | cuantificar la truncación de OpenFin **a escala** (histórico); cerrar multiperiodo con `iv_payment_plan` (Fase 1). Detalle: `40_validaciones/FASE0_VALIDACION_INVERSIONES.md` |

> El árbol es reconciliación A/B, no arbitraje C. Un "DONE / se mitiga al cambio de core" del equipo
> **no** cierra el candidato: se cierra cuando C lo re-deriva desde la norma (§10, §11 del charter).

## Candidato derivado de F-015 (esquema OpenFin)
| ref | dominio | qué se observa | clasificación probable | acción de C |
|-----|---------|----------------|------------------------|-------------|
| A15-ISR-DIARIO | FIS/DAT | OpenFin tiene `isr_diario` (170 M filas) e `isr_diario_aux_log` → **calcula/acumula ISR DIARIO**; Aurum (F-009) aplica ISR **sólo al pago** | **DIFERENCIA_DISENO** (modelos distintos) — probable causa de parte del gap de ISR (K-FIS-003) | normalizar antes de comparar: sumar el ISR diario de OpenFin del periodo vs el ISR al pago de Aurum; C recalcula ambos desde la norma. **Clave para el deep-dive del ISR y para explicarlo a Finsus.** |

## Candidatos derivados del barrido del campo `lc_loan_contract.cat` (2026-08-28, auditoría propia)

Estos **sí** salen de una corrida propia contra AurumCore (solo lectura, `n = 31,866` contratos),
no de un reporte de terceros. Se registran aquí y no en `HALLAZGOS.md` porque falta el paso (2) de
la regla de promoción: evaluarlos con A/B/C. El motor A (openfin) todavía no se cruzó para CAT.

| ref | dominio | qué se observa (medido) | clasificación probable | magnitud | acción de C |
|-----|---------|-------------------------|------------------------|----------|-------------|
| A28-CAT-CONSTANTE | COL/DAT | `cat` guarda un **valor constante** en 25,026 de 31,866 contratos (78.5%). `cat = 27.10` cubre 15,300 contratos que abarcan **521 plazos distintos** y **3,930 montos distintos** — un CAT no puede ser el mismo con plazo y monto distintos, así que en esas filas el campo **no es la salida de un cálculo per-contrato** | **DIFERENCIA_DISENO** o campo no poblado — *no* defecto del motor de CAT | 25,026 contratos | Estratificar el universo y comparar C **solo** contra el estrato donde `cat` varía (4,220). El 11.6% citado a volumen mide la mezcla, no el motor |
| A28-CAT-CERO | COL/REG | **2,466 contratos ACTIVOS con `cat = 0`**, y **2,376 de ellos sí cobran interés** (2,463 con tasa ordinaria > 0, promedio **28.43%**). Un CAT de cero en un crédito que cobra 28% no es un CAT: es un campo sin poblar. Activaciones de 2023-11-29 a 2026-07-17 | **DEFECTO_CORE_NUEVO** (candidato) — la Circular 21/2009 exige revelar el CAT | 2,466 contratos activos | Confirmar si el producto tiene CAT que revelar; si lo tiene, es hallazgo regulatorio, no de cálculo |

**Por qué el segundo no se promueve todavía a `H-###`.** Falta descartar que esos productos tengan
una exención (por ejemplo, si no son crédito al consumo sujeto a la Circular). Lo que ya **no** puede
sostenerse es que el cero sea un CAT calculado: el contrato cobra interés.

## Regla de promoción
Un renglón pasa a `H-###` en `HALLAZGOS.md` **sólo** cuando: (1) se reprodujo el caso mínimo,
(2) se evaluó con A/B/C, (3) se clasificó (DEFECTO_CORE_NUEVO / DEFECTO_OPENFIN / DEFECTO_AMBOS /
REGLA_MAL_ESPECIFICADA / DIFERENCIA_DISENO_AUTORIZADA) y (4) se cuantificó con evidencia propia.
