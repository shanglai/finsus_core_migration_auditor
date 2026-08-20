# Cobertura del VALIDADOR — que se corrio, que no y que esta bloqueado

> Generado: 2026-08-20T17:19:28+00:00 · `python cli.py --cobertura`
>
> **NO-CORRIDO NO ES PASO.** Un caso que no se ejecuto no aporta cobertura y no
> puede pintarse verde en ningun tablero. Esta tabla existe para que la ausencia
> de evidencia sea tan visible como la evidencia (charter §5.3).

**0 de 13 casos corridos** · 0 con hallazgo · 13 sin corrida util.

| caso | motor | sev | estado catalogo | ultima corrida | fecha | violaciones | evidencia |
|---|---|---|---|---|---|---|---|
| **COMPLETITUD** | MOV | 1 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CONTABLE-BC** | CTB | 1 | PENDIENTE | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CRED-IO** | COL | 1 | PENDIENTE | NO-CORRIDO · nunca ejecutado | — | — | — |
| **DIARIO-B** | MOV | 2 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **GAPB-IDNC** | REG | 2 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **GAPC-PROSOFIPO** | REG | 2 | HALLAZGO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **ISR-01** | FIS | 1 | VALIDADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **ISR-02** | FIS | 2 | VALIDADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **ISR-03** | FIS | 1 | VALIDADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **REND-PLAZO** | DEV | 1 | VALIDADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **REND-VISTA** | DEV | 1 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **SALDO-PROM** | DEV | 1 | BLOQUEADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **WRITEOFFS** | CTB | 2 | PENDIENTE | NO-CORRIDO · nunca ejecutado | — | — | — |

## Casos que hoy NO se pueden correr (y por que)

| caso | falta | pieza / pregunta abierta |
|---|---|---|
| CONTABLE-BC | oraculo PENDIENTE (falta pieza de conocimiento); SQL de aurum PENDIENTE; Falta la consulta parametrizada. consultas_validacion.sql tiene el catalogo integral (§0 a §6) pero como consultas sueltas de exploracion, no como identidades acotadas por ventana. Convertirlas es trabajo de extraccion, no de regla: K-CTB-001 ya documenta la matriz tipo_mov -> cuenta. | K-CTB-001 |
| CRED-IO | oraculo PENDIENTE (falta pieza de conocimiento); SQL de aurum PENDIENTE; FALTA LA REGLA. No hay pieza de conocimiento que documente el devengamiento de One Click. Escribir el oraculo hoy exigiria leer como lo hace el core, que es exactamente lo que el charter §9.1 prohibe. El desbloqueo es documental (P-006), no tecnico. | K-COL-001, P-006 |
| DIARIO-B | oraculo PENDIENTE (falta pieza de conocimiento); SQL de openfin PENDIENTE; SQL de aurum PENDIENTE; Faltan dos cosas y ninguna es codigo: (1) el detalle completo del catalogo de ~400 tipos contables que dice cuales caen en 2:1 y cuales en 1:1 esta [PENDIENTE] en K-MOV-001 v2; (2) el match a nivel instancia y la explicacion de los NULL "api_dimmer" siguen abiertos en P-016. Sin (1) el oraculo de normalizacion no se puede escribir sin copiar la logica de un core, que es justo lo prohibido (§9.1). | K-MOV-001, K-MOV-004, K-MOV-005, K-MOV-006, P-016 |
| GAPB-IDNC | oraculo PENDIENTE (falta pieza de conocimiento); V3 hoy es un diagnostico de existencia (conteos y sumas), no una identidad por credito. Para escribir el oraculo falta el doc IFRS9 que fije como se calcula la reserva y que cuentas de orden se usan. Sin eso, cualquier oraculo seria una copia de lo que hace el core — prohibido (§9.1). | K-REG-001, F-023 |
| GAPC-PROSOFIPO | oraculo PENDIENTE (falta pieza de conocimiento); No hay oraculo porque no hay motor que recalcular: el hallazgo es la ausencia. Convertirlo en identidad de monto exige que Finsus defina la formula de la cuota, lo que solo tiene sentido si deciden traerla al core. | K-REG-002, F-023 |
| REND-VISTA | SQL de aurum PENDIENTE; SQL de openfin PENDIENTE; Falta la consulta de extraccion: el universo depende del saldo promedio mensual, cuya definicion exacta sigue abierta en P-006, y de la corrida viva del 31-ago (P-015) que aun no existe. El oraculo esta listo y autoprobado; lo que falta es el dato, no la regla. | K-DEV-002, K-DEV-001, K-TMP-001 |
| SALDO-PROM | SQL de aurum PENDIENTE; P-006 abierta. La formula (F-022) esta declarada, pero la correspondencia con lo que el CORE registra no se ha corroborado contra los logs (traza "Calculating with average balance"). Ademas account_balance_tracking arranca ~ago-2025 y no reconstruye cuentas viejas. | K-DEV-002, P-006 |
| WRITEOFFS | oraculo PENDIENTE (falta pieza de conocimiento); SQL de aurum PENDIENTE; Falta la pieza de conocimiento: no hay K-* que documente esta regla, solo una afirmacion en F-023 §1. Primer paso es crear la pieza, no escribir codigo. | F-023, P-006 |

> Cada linea de esta tabla es un hueco de cobertura declarado. Cerrarlo exige
> un insumo (pieza de conocimiento, acceso, log o definicion), no mas codigo.

## Sincronia de indices (§7.4)

`catalogo/*.yaml` y `catalogo/manifest.yaml` estan sincronizados.

Pendiente de sincronizar a mano: `40_validaciones/NORTE_VALIDACION.md` (misma nomenclatura y estado que este catalogo).
