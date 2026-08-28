# Cobertura del VALIDADOR — que se corrio, que no y que esta bloqueado

> Generado: 2026-08-28T10:42:53+00:00 · `python cli.py --cobertura`
>
> **NO-CORRIDO NO ES PASO.** Un caso que no se ejecuto no aporta cobertura y no
> puede pintarse verde en ningun tablero. Esta tabla existe para que la ausencia
> de evidencia sea tan visible como la evidencia (charter §5.3).

**5 de 16 casos corridos** · 3 con hallazgo · 11 sin corrida util.

| caso | motor | sev | estado catalogo | ultima corrida | fecha | violaciones | evidencia |
|---|---|---|---|---|---|---|---|
| **BALANZA-D** | CTB | 2 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **COMPLETITUD** | MOV | 1 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CONTABLE-B1** | CTB | 1 | VALIDADO | corrido · cero violaciones | 2026-08-28 | 0 | CONTABLE-B1_2026-08-28_abc2e91de338 |
| **CONTABLE-C** | CTB | 1 | PENDIENTE | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CRED-IO** | COL | 1 | PENDIENTE | NO-CORRIDO · nunca ejecutado | — | — | — |
| **CUENTAHAB-01** | MIG | 2 | BLOQUEADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **DIARIO-B** | MOV | 2 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
| **GAPB-IDNC** | REG | 2 | BLOQUEADO | corrido · CON VIOLACIONES | 2026-08-21 | 20798 | GAPB-IDNC_2026-08-21_ea327ce3bee7 |
| **GAPC-PROSOFIPO** | REG | 2 | HALLAZGO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **ISR-01** | FIS | 1 | PARCIAL | NO-CORRIDO · error de ejecucion | 2026-08-21 | — | ISR-01_2026-08-21_06d1a7859246 |
| **ISR-02** | FIS | 2 | VALIDADO | NO-CORRIDO · nunca ejecutado | — | — | — |
| **ISR-03** | FIS | 1 | VALIDADO | corrido · CON VIOLACIONES | 2026-08-21 | 1 | ISR-03_2026-08-21_a61c52894d7e |
| **REND-PLAZO** | DEV | 1 | VALIDADO | corrido · cero violaciones | 2026-08-28 | 0 | REND-PLAZO_2026-08-28_62b2d08afb0a |
| **REND-VISTA** | DEV | 1 | PARCIAL | corrido · SESGO DETECTADO (severidad 1) | 2026-08-28 | 424 | REND-VISTA_2026-08-28_4f276056500d |
| **SALDO-PROM** | DEV | 1 | PARCIAL | NO-CORRIDO · nunca ejecutado | — | — | — |
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
| ISR-01 | SQL de aurum PENDIENTE; SQL de openfin PENDIENTE; La consulta del universo NO funciona y se retira a borrador. Corrida del 2026-08-21: el lado B extrae BIEN — aparecieron 46.37, 4.81 y 0.05, que son exactamente las tres retenciones del caso de oro de S-FIS-001 — pero el universo esta mal armado en dos puntos:
  1. El apareo evento-de-ISR <-> inversion. Tres intentos fallaron: unir por
     accountholder da producto cartesiano y agota el statement_timeout; unir
     contra la cohorte con ON TRUE FABRICA filas (3 eventos -> 27); extraer la
     cuenta de `alfanumeric_reference` por patron vuelve a agotar el timeout
     porque no hay indice que lo soporte. El prefijo de la referencia ademas
     NO es estable ('-100-2301-X', 'Pago de rendimientos-100-2301-X',
     'Pago de rendimientos 10-100-2301-X').
  2. `saldo_total_cliente` sale 0 en todas las filas: el join a
     account_balance_tracking no resuelve, aunque la tabla si tiene datos en
     la ventana (2025-08-22..2026-08-20). Con base 0 el oraculo devuelve 0 y
     las 27 diferencias salieron todas del mismo signo.
Las 27 violaciones de esa corrida son defecto de ESTA consulta, no de AurumCore, y asi quedaron registradas. Reconstruir el universo siguiendo el metodo de comparadores/isr_live_nativo.py es el siguiente paso. | K-FIS-002, K-FIS-004, S-FIS-001, K-DEV-001, C-002 |
| SALDO-PROM | SQL de aurum PENDIENTE; [DESTRABADO PARCIAL 2026-08-24] Ya NO se depende de esperar al 31-ago. Finsus confirmo la formula y su insumo esta en la BD: `aurumcore.finsus_account_history` (105M filas, por cuenta y por dia: average_balance_amount, interest_rate, balance_amount, iv_term_days). Base 360:
    interes = SPM x dt x tasa / 36000
Reconcilio al centavo en el caso limpio (cuenta 6de5351e: 10,165.70 x 31 x 4% / 36000 = 35.02 = posteado) y al 82.1% a volumen sobre los posteos reales del 31-jul. Lo que FALTA para cerrar: (1) la convencion exacta de `dt` — inclusivo en ambos extremos y el dia de fondeo no cuenta — y (2) el SPM-de-RENDIMIENTO, que Finsus dice se guarda en la poliza de intereses y PUEDE DIFERIR del average de consulta. Ese SPM no esta en transaction_detail. Mientras (2) no se resuelva, el 18% residual no se puede atribuir ni al motor ni al metodo. | K-DEV-002, P-006 |
| WRITEOFFS | oraculo PENDIENTE (falta pieza de conocimiento); SQL de aurum PENDIENTE; Falta la pieza de conocimiento: no hay K-* que documente esta regla, solo una afirmacion en F-023 §1. Primer paso es crear la pieza, no escribir codigo. | F-023, P-006 |

> Cada linea de esta tabla es un hueco de cobertura declarado. Cerrarlo exige
> un insumo (pieza de conocimiento, acceso, log o definicion), no mas codigo.

## Hallazgos de la ultima corrida

### GAPB-IDNC — Suspension de devengo en cartera vencida — io_venc cancela io

- veredicto: **VIOLACIONES** · violaciones: **20798** de 45761 filas
- celda dominante de la matriz A/B/C: `grupos`
- matriz: {'grupos': 45761, 'descuadrados': 20798}
- evidencia: `GAPB-IDNC_2026-08-21_ea327ce3bee7`

### ISR-03 — Parametros de ISR configurados en el core = norma del anio de causacion

- veredicto: **VIOLACIONES** · violaciones: **1** de 4 filas
- celda dominante de la matriz A/B/C: `B=C (sin A)`
- matriz: {'B=C (sin A)': 3, 'B!=C (sin A)': 1}
- evidencia: `ISR-03_2026-08-21_a61c52894d7e`

### REND-VISTA — Interes y capitalizacion de cuenta vista/ahorro

- veredicto: **SESGO** · violaciones: **424** de 5000 filas
- celda dominante de la matriz A/B/C: `B=C (sin A)`
- matriz: {'B=C (sin A)': 4576, 'B!=C (sin A)': 424}
- **sesgo detectado** (p=9.81241e-82): Sesgo positivo (C > B): 411 de 447 diferencias no nulas caen del mismo lado. Severidad 1 (charter §1.7): el agregado esta mal aunque cada evento respete la tolerancia.
- evidencia: `REND-VISTA_2026-08-28_4f276056500d`

> Recordatorio (§7.3): **cada hallazgo confirmado se convierte en un invariante**
> permanente en `tests/`. La red de regresion solo crece.

## Sincronia de indices (§7.4)

`catalogo/*.yaml` y `catalogo/manifest.yaml` estan sincronizados.

Pendiente de sincronizar a mano: `40_validaciones/NORTE_VALIDACION.md` (misma nomenclatura y estado que este catalogo).
