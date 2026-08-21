# Cobertura del VALIDADOR — que se corrio, que no y que esta bloqueado

> Generado: 2026-08-21T17:45:53+00:00 · `python cli.py --cobertura`
>
> **NO-CORRIDO NO ES PASO.** Un caso que no se ejecuto no aporta cobertura y no
> puede pintarse verde en ningun tablero. Esta tabla existe para que la ausencia
> de evidencia sea tan visible como la evidencia (charter §5.3).

**0 de 16 casos corridos** · 0 con hallazgo · 16 sin corrida util.

| caso | motor | sev | estado catalogo | ultima corrida | fecha | violaciones | evidencia |
|---|---|---|---|---|---|---|---|
| **BALANZA-D** | CTB | 2 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **COMPLETITUD** | MOV | 1 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CONTABLE-B1** | CTB | 1 | VALIDADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CONTABLE-C** | CTB | 1 | PENDIENTE | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CRED-IO** | COL | 1 | PENDIENTE | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CUENTAHAB-01** | MIG | 2 | BLOQUEADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **DIARIO-B** | MOV | 2 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **GAPB-IDNC** | REG | 2 | VALIDADO | NO-CORRIDO · nunca ejecutado | — | — | — |
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
| BALANZA-D | oraculo PENDIENTE (falta pieza de conocimiento); SQL de aurum PENDIENTE; SQL de openfin PENDIENTE; Falta el script `contable_d_balanza.py` (el NORTE lo marca pendiente) y las dos consultas de extraccion. La regla y los localizadores ya estan; lo que falta es construirlo. | K-CTB-001, K-DAT-004 |
| CONTABLE-C | SQL de aurum PENDIENTE; Falta la consulta. AurumCore NO persiste el mayor/balanza como tabla: hay que derivarlo de los movimientos, y la version por cuenta contable aun no esta construida. Ademas PLAN_CONTABLE_BC.md documenta ~510 movimientos/dia de credito con '' en la cuenta contable, que es precisamente lo que rompe este amarre y hay que resolver antes. | K-CTB-001 |
| CRED-IO | oraculo PENDIENTE (falta pieza de conocimiento); SQL de aurum PENDIENTE; FALTA LA REGLA. No hay pieza de conocimiento que documente el devengamiento de One Click. Escribir el oraculo hoy exigiria leer como lo hace el core, que es exactamente lo que el charter §9.1 prohibe. El desbloqueo es documental (P-006), no tecnico. | K-COL-001, P-006 |
| CUENTAHAB-01 | SQL de identityshared PENDIENTE; SQL de aurum PENDIENTE; Doble bloqueo. (1) Falta la respuesta de Finsus sobre si la identidad WSO2 persiste tras cerrar la cuenta y si existe padron de cuentas cerradas (SOL-007): sin eso, 181,844 diferencias no se pueden interpretar. (2) La base `identityshared` esta marcada `sensible: true` en db_connections.yaml, asi que el motor NO extrae de ella sin --permitir-sensible explicito. | K-DAT-005, P-017 |
| DIARIO-B | oraculo PENDIENTE (falta pieza de conocimiento); SQL de openfin PENDIENTE; SQL de aurum PENDIENTE; El agregado ya reconcilia; lo que falta es el match a nivel INSTANCIA (P-016) y el acceso a `openfin_migracion`/`openfin_m` (SOL-001), sin el cual `vista_movimientos` no permite emparejar cargo contra abono de forma fiable. Ademas el detalle del catalogo de ~400 tipos (cuales 2:1 y cuales 1:1) sigue [PENDIENTE] en K-MOV-001 v2 (SOL-014): sin el, el oraculo de normalizacion no se puede escribir sin copiar la logica de un core, que es lo prohibido (§9.1). | K-MOV-001, K-MOV-004, K-MOV-005, K-MOV-006, P-016 |
| GAPC-PROSOFIPO | oraculo PENDIENTE (falta pieza de conocimiento); No hay oraculo porque no hay motor que recalcular: el hallazgo es la ausencia. Convertirlo en identidad de monto exige que Finsus defina la formula de la cuota, lo que solo tiene sentido si deciden traerla al core. | K-REG-002, F-023 |
| REND-VISTA | SQL de aurum PENDIENTE; SQL de openfin PENDIENTE; Falta la consulta de extraccion: el universo depende del saldo promedio mensual, cuya definicion exacta sigue abierta en P-006, y de la corrida viva del 31-ago (P-015) que aun no existe. El oraculo esta listo y autoprobado; lo que falta es el dato, no la regla. | K-DEV-002, K-DEV-001, K-TMP-001 |
| SALDO-PROM | SQL de aurum PENDIENTE; P-006 abierta. La formula (F-022) esta declarada, pero la correspondencia con lo que el CORE registra no se ha corroborado contra los logs (traza "Calculating with average balance"). Ademas account_balance_tracking arranca ~ago-2025 y no reconstruye cuentas viejas. | K-DEV-002, P-006 |
| WRITEOFFS | oraculo PENDIENTE (falta pieza de conocimiento); SQL de aurum PENDIENTE; Falta la pieza de conocimiento: no hay K-* que documente esta regla, solo una afirmacion en F-023 §1. Primer paso es crear la pieza, no escribir codigo. | F-023, P-006 |

> Cada linea de esta tabla es un hueco de cobertura declarado. Cerrarlo exige
> un insumo (pieza de conocimiento, acceso, log o definicion), no mas codigo.

## Sincronia de indices (§7.4)

`catalogo/*.yaml` y `catalogo/manifest.yaml` estan sincronizados.

Pendiente de sincronizar a mano: `40_validaciones/NORTE_VALIDACION.md` (misma nomenclatura y estado que este catalogo).
