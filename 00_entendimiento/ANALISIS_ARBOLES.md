# Análisis de árboles — reconciliación día cero (02-03 ago 2026)

Versión: 1 · 2026-08-16 · Fuente: **F-013** (`Árboles - Día Cero.xlsx` + carpeta) y **F-012** (queries Aurum).
Sustento: [[K-MIG-005]] [[K-CAP-001]] [[K-COL-001]] [[K-FIS-003]] [[K-MOV-007]] [[K-DAT-006]]

> **Qué es y qué NO es.** Es la **reconciliación del equipo Finsus/Aurum (motores A vs B)** con su
> propio análisis de causa raíz. **No es el oráculo independiente (C).** Se usa como (1) mapa de
> dónde están las diferencias, (2) fuente de candidatos a hallazgo, y (3) validación de que las
> cifras del "día cero" narradas en F-001 (P-009) son reales. Cada causa auto-reportada se marca
> para **verificación independiente**.

## 0. Metodología del árbol (K-MIG-005)
Por dominio se parte de la **llave** (cliente / cuenta / inversión / crédito / transacción) y se
agregan dimensiones de forma **acumulativa**, midiendo el % que sigue cuadrando:
`En común → +Saldo → +Tasa → +Rendimiento → +ISR`. Cada caída (Diff) y cada Único se explica con
**causas (RCA)** con responsable y estatus. La hoja **Asignaciones** baja al detalle por par de
cuenta contable (~970 pares).

## 1. Clientes
- **En común: 956,331 · Único AC: 1 · Único OF: 1** (prácticamente 100%).
- Únicos: 1 persona moral dada de alta manual en Portal Admin (no está en OF); 1 PF sin datos
  completos en OF (no migró). → casos aislados, sin materialidad.

## 2. Cuentas a la vista (K-CAP-001)
- **En común: 2,046,969** · Único AC 3,061 · Único OF 79,109.
- **Cuadra con saldo: 98.03%** (Diff Saldo 40,327) · **con saldo+tasa: 97.92%** (Diff Tasa 2,110).

| Diferencia | # | Causa principal (RCA equipo) | Clasificación probable (C) |
|-----------|---|------------------------------|----------------------------|
| Único OF | 78,884 | sucursal 201 (fondeadora) no migrada — decisión de negocio | DIFERENCIA_DISENO_AUTORIZADA (excluir) |
| Único AC | 2,977 | **BUG del API** (k_auxiliar → consecutivo de cuenta) | DEFECTO_CORE_NUEVO |
| Diff Saldo | 24,910 | redondeo tras pago rendimientos/intereses | REGLA/redondeo (verificar sesgo, P-014) |
| Diff Saldo | 11,181 | CAPITAL_RETURN / YIELD_PAYMENT (fix Aurum DONE) | DEFECTO_CORE_NUEVO (corregido) |
| Diff Saldo | 3,393+841 | saldo final incorrecto por ingesta / sin movimientos | DEFECTO ingesta (TO DO) |
| Diff Tasa | 2,053 | **producto 2019 mal configurado** en Aurum | DEFECTO_CORE_NUEVO (config) |

## 3. Inversiones (K-FIS-003)
- **En común: 18,599 · Único AC 0 · Único OF 0** (existencia perfecta).
- Diff Fecha 1 · Diff Monto 0 · Diff Tasa 0 · **Diff Rendimiento pagado 89** · **Diff ISR retenido
  4,988 (≈27%)** ← mayor gap de cálculo.
  - **[Corregido con recálculo C, Fase 0]** los 89 son **todos ≤$0.10 y todos AC>OF** (sesgo
    unidireccional; 0 casos >$0.10). El "4,969" del RCA proviene de otra comparación, no de este
    universo. 18,509 cuadran exacto. Ver candidato A13-REND-SESGO.
- Causas ISR: 3,198 por **diff de saldo en cuentas** (cascada desde §2), 1,790 por redondeo <0.8%;
  79 casos donde **un core retiene y el otro no** (los más graves).

## 4. Créditos One Click 5004 (K-COL-001)
- **En común: 7,619 · cuadran 100%** en tasa (IO/IM), monto entregado, fecha/días y monto pagado.
- Único AC 68 = residuo de redondeo <$0.01 al liquidar (mitigado truncando a 2). Único OF 0.
- **Es el dominio más sano.** Falta validar el **devengamiento diario** (no está en este árbol).

## 5. Transacciones (2-ago) (K-MOV-007)
- **En común: 32,539** · Único AC 524 · Único OF 182 (tipo1=97, tipo3=46, tipo183=32, tipo186=2, tipo314=5).
- **Únicas OF:** misma cuenta origen=destino, reversos, cuentas TERMINATED, **SPEI OUT a CLABE
  inválida** (K-MOV-002), SPEI que no llegan a satélites, internas de crédito.
- **Únicas AC:** transacciones internas de plataforma (VIRTUAL1→VIRTUAL2, comisiones, dispersiones,
  consulta saldo Pomelo $0). Mayoría `DIFERENCIA_DISENO_AUTORIZADA`.
- La hoja **Asignaciones** (~970 pares de cuenta contable) es el mapa fino por tipo de transacción.

## 6. Lectura transversal (para el plan)
- **Cascada saldo→ISR:** el gap de ISR es en parte consecuencia del gap de saldo. El oráculo debe
  calcular ISR sobre el **mismo saldo base** para separar defecto-de-ISR de defecto-de-saldo.
- **Redondeo omnipresente:** aparece en cuentas (24,910), inversiones (4,969), créditos (68). Es la
  hipótesis P-014 hecha datos → correr prueba de signo sobre estas distribuciones.
- **Fortalezas:** existencia de clientes, inversiones y créditos casi perfecta; One Click cuadra al 100%.
- **Debilidades reales (candidatos a hallazgo):** BUG del API (2,977), tasa 2019 (2,053), Diff ISR
  (4,988, en parte propagado), SPEI que no llegan a satélites (dinero real), cuentas TERMINATED.

## 7. Naturaleza y límites (veracidad)
- Muchas causas están marcadas "N/A DONE" o "se mitiga al cambio de core" **por el propio equipo**.
  No son verdad verificada por C. La columna **QUIEN/ESTATUS** distingue lo cerrado de lo TO DO.
- Los datos crudos (~1.5 GB, PII) están **fuera de git**; traza en el MANIFEST. El detalle celda a
  celda se re-consulta localmente si se necesita.

## 8. Qué se suma al plan
Estos árboles son la **primera ejecución real de las Fases 2 (completitud) y 7 (arbitraje)** del
plan, hecha por el equipo A/B. Ver `40_validaciones/PLAN_DE_VALIDACION.md` §"Estado real al corte".
El trabajo de C es **re-derivar independientemente** los cálculos con mayor diferencia (ISR,
rendimiento, saldo) y **arbitrar** las causas auto-reportadas.
