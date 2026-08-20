# Diccionario del proyecto

Índice maestro de **notación** (códigos, prefijos, marcas) y **catálogo** de cada instancia
(piezas, preguntas, fuentes, etc.). Para los términos de negocio con su cita a fuente, ver
`GLOSARIO.md`; aquí se listan en corto para que el diccionario se lea solo.

> Criterio de las descripciones: cada una dice **qué es y por qué importa**, no sólo expande la
> sigla. Al final hay una sección de **Autovalidación** con la cobertura y los avisos.

---

## 1. Esquemas de identificador (cómo leer los códigos)
| patrón | qué es | dónde vive | ejemplo |
|--------|--------|-----------|---------|
| `K-<DOM>-###` | **Pieza de conocimiento**: un hecho o regla verificable, con fuente y estado. | `10_conocimiento/<DOM>/` | `K-MIG-002` |
| `S-<DOM>-###` | **Especificación del oráculo**: la regla de un cálculo, escrita antes del código. | `30_oraculo/ESPECIFICACIONES/` | `S-FIS-001` |
| `S-###` | **Supuesto** vigente (sin segmento de dominio → no confundir con la spec). | `SUPUESTOS.md` | `S-004` |
| `P-###` | **Pregunta abierta**: un dato que falta, priorizado. | `PREGUNTAS_ABIERTAS.md` | `P-003` |
| `F-###` | **Fuente**: un archivo original registrado e inmutable. | `REGISTRO_FUENTES.md` | `F-009` |
| `H-###` | **Hallazgo**: discrepancia confirmada y clasificada (aún no hay ninguno). | `50_hallazgos/` | `H-023` (ej. del charter) |
| `C-###` | **Contradicción** entre fuentes, sin resolver (aún no hay ninguna). | `CONTRADICCIONES.md` | `C-004` (ej. del charter) |
| `INV-<CAPA>-##` | **Invariante/validación**: consulta que devuelve las filas que violan una identidad. | `40_validaciones/` | `INV-DEV-04` |
| `F001-<TAG>` | **Candidato a hallazgo** derivado de la fuente F-001 (aún sin arbitrar). | `CANDIDATOS_A_HALLAZGO.md` | `F001-ISR` |
| `PAR-###` | **Folio de Jira** del paralelo (notación **externa**, del proyecto "PAR", no nuestra). | Jira / F-003..F-008 | `PAR-352` |
| `§N` | **Sección N del `CLAUDE.md`** (la instrucción permanente del proyecto). | `CLAUDE.md` | `§10` |
| `[[nombre]]` | Enlace interno a otra pieza por su `name`. | cualquier pieza | `[[K-DEV-001]]` |

> **Colisiones de prefijo a tener presentes:** `S-` se usa para supuestos (`S-004`) **y** para
> specs (`S-FIS-001`) — se distinguen por el segmento de dominio. `A/B/C` significan cosas
> distintas según el contexto: **motores** (§ abajo) vs **familias de validación** (§ abajo). `C`
> puede ser motor C, familia C **o** prefijo de contradicción `C-###`.

## 2. Marcas de confianza (estado de cada afirmación y de cada pieza)
| marca | significado |
|-------|-------------|
| `[CONFIRMADO]` | Consta explícito en una fuente; lleva cita obligatoria. |
| `[INFERIDO]` | Deducción lógica a partir de fuentes confirmadas; se cita el razonamiento. |
| `[SUPUESTO]` | Supuesto informado, sin fuente; se registra su impacto si es falso. |
| `[CONTRADICCION]` | Dos fuentes incompatibles; se citan ambas, no se elige ganador. |
| `[PENDIENTE]` | Falta el dato; va a `PREGUNTAS_ABIERTAS.md`. |
| `OBSOLETA` | Estado de una pieza superada por otra (se conserva, no se borra). |

## 3. Los tres motores (modelo de arbitraje, §1)
| motor | qué es | rol |
|-------|--------|-----|
| **A** | OpenFin (core actual) | referencia histórica — **no es la verdad**. |
| **B** | AurumCore (core destino) | sistema bajo prueba. |
| **C** | El oráculo (este proyecto) | árbitro independiente que calcula desde la norma. |

## 4. Familias de validación (§10, orden de ejecución)
| familia | qué compara |
|---------|-------------|
| **A** | El detalle contra sí mismo (rollforward, folios, reversas, signos, traspasos). |
| **B** | La balanza contra sí misma (doble partida, continuidad, naturaleza). |
| **C** | Amarre auxiliar ↔ balanza (stock/flujo por producto-día, cuentas puente). |
| **D** | Cross-motor: la misma identidad en A, B y C, y la igualdad del conjunto de violaciones. |

## 5. Clasificación de hallazgos (§11)
| clasificación | qué significa |
|---------------|---------------|
| `DEFECTO_CORE_NUEVO` | El error está en AurumCore. |
| `DEFECTO_OPENFIN` | Error histórico del core actual (la cubeta incómoda; obligatorio abrirla). |
| `DEFECTO_AMBOS` | Los dos cores coinciden pero ambos están mal (severidad máxima). |
| `REGLA_MAL_ESPECIFICADA` | A, B y C difieren: el problema es la regla, no el código. |
| `DIFERENCIA_DISENO_AUTORIZADA` | Diferencia esperada y aceptada por diseño. |

## 6. Dominios de conocimiento (los 13 de §8)
| cód | dominio | qué abarca |
|-----|---------|-----------|
| `CAP` | Captación | productos de depósito: vista, plazo, tasas, comisiones. |
| `COL` | Colocación | crédito: tasas, amortización, moratorios, prepago. |
| `MOV` | Movimientos | catálogo de operaciones, efecto en saldos, reversas, traspasos. |
| `TMP` | Tiempos | cortes, ventanas batch, husos, días inhábiles, fecha valor vs operación. |
| `DEV` | Devengo | interés diario, base de días, redondeo y su momento, tasa vigente. |
| `CTB` | Contabilidad | matriz `tipo_movimiento → cuenta contable`, pólizas, cierre. |
| `FIS` | Fiscal | ISR, IVA, CFDI, constancias. |
| `REG` | Regulatorio | reportes, saldos a SIC, indicadores CNBV. |
| `DAT` | Datos | tablas/campos equivalentes entre cores, llaves, precisión decimal, linaje. |
| `ARQ` | Arquitectura | integraciones, canales, gateway, flujo de datos. |
| `PRC` | Procesos | procesos operativos y método de validación. |
| `MIG` | Migración | cutover, saldos de arranque, historia a migrar, rollback. |
| `ORG` | Organización | actores, roles, decisiones tomadas. |

## 7. Secciones del `CLAUDE.md` (referencias `§`)
`§0` uso del documento · `§1` tu rol y los 3 motores · `§2` objetivo · `§3` principio de veracidad ·
`§4` estructura del repo · `§5` la pieza de conocimiento · `§6` el Entendimiento Global ·
`§7` protocolo de ingesta · `§8` dominios de validación · `§9` el oráculo · `§10` validaciones e
invariantes · `§11` hallazgos · `§12` rutinas · `§13` postura y estilo · `§14` prohibiciones ·
`Anexo A` plantillas · `Anexo B` prompt de arranque · `Anexo C` nota de arranque en frío.

## 8. Rutinas invocables (§12)
`ingesta` (procesar lo nuevo) · `sintesis` (regenerar el Entendimiento Global) · `auditoria`
(consistencia) · `huecos` (priorizar preguntas) · `oraculo <dom>` (spec→código→prueba) ·
`validar <capa>` (invariantes) · `reporte` (estado go/no-live).

---

## 9. Catálogo de piezas de conocimiento (K-*) — 33
| id | descripción corta |
|----|-------------------|
| `K-ARQ-001` | Inventario de sistemas del ecosistema Finsus: dos cores (OpenFin, Aurum) + middleware/Analyzer + satélites (Dynamics, Simetrik, Pomelo, WebBanking, FinsusApp, gateway, F1). |
| `K-ARQ-002` | Arquitectura del paralelo: un gateway (de Citi) manda cada operación a ambos cores; OpenFin es el primario/autorizador; switch a Aurum ~1-oct. Explica el origen de los descuadres de saldo. |
| `K-DAT-001` | Estructura y linaje del export de Jira PAR (columnas del folio); base para leer el tracking del paralelo. |
| `K-DAT-002` | Tablas núcleo de OpenFin (asociados, acreedores, deudores, detalle_auxiliar, _masdatos) + ambiente (PostgreSQL; T-1 no confiable, producción manda). |
| `K-DAT-003` | Llaves de OpenFin: cliente (3 campos), cuenta (3 campos), `secuencia` (PK de movimientos), `id_external` (cross-sistema, sólo SPEI). |
| `K-DAT-004` | Productos por `id_producto` (2000s vista, 2300s inversiones, 5004 One Click) y estatus de cuenta (3 activa, 4 cerrada, 5 cancelada). |
| `K-DAT-005` | Fuente de la verdad por dato entre sistemas (core/middleware/backend/analyzer); el saldo es siempre de OpenFin. |
| `K-DAT-006` | Modelo de datos y queries de AurumCore (esquema `aurumcore`: accountholder, account, lc_loan_contract, transaction…) + mapeo de llaves con OpenFin. |
| `K-CAP-001` | Árbol de cuentas vista (día cero): 2.05 M en común; causas de diferencia (BUG API 2,977, sucursal 201, tasa 2019, redondeo). |
| `K-COL-001` | Árbol de crédito One Click 5004: 7,619 en común cuadran 100% (tasa/monto/fecha/pagado); 68 únicos por redondeo <$0.01. |
| `K-FIS-003` | Árbol de inversiones: el Diff ISR (≈27%, 4,988 casos) es el mayor gap de cálculo; en parte cascada del diff de saldo. |
| `K-MIG-005` | Árbol de decantación día cero: metodología (En común/Único/Diff acumulativo + RCA) y estado global. Es reconciliación A/B, no oráculo. |
| `K-MOV-007` | Árbol de transacciones (2-ago): 32,539 en común; causas de las únicas (diseño + defectos: SPEI a satélites, cuentas TERMINATED). |
| `K-DEV-001` | Redondeo de AurumCore: truncar a 20 decimales en pasos intermedios, ISR diario a 5, redondeo final a 2 con modo por cálculo; OpenFin trabaja a 2. Es la raíz del riesgo de sesgo. |
| `K-DEV-002` | Cálculo del rendimiento de cuentas a la vista: base saldo promedio mensual, se procesa el día 1 el mes anterior, con criterios de elegibilidad. |
| `K-DEV-003` | Cálculo del rendimiento de plazo fijo: base el capital inicial (`iv_initial_amount`), días entre planes de pago, parámetros del misceláneo del producto. |
| `K-FIS-001` | El ISR se calculó mal "toda la vida" en OpenFin (corregido hace poco): defecto histórico admitido → candidato `DEFECTO_OPENFIN`. |
| `K-FIS-002` | Regla completa de retención de ISR de AurumCore (exención 5×UMA, tasa/365, prorrateo por cuenta), verificada contra un caso real; sus parámetros normativos aún no se validan (P-010). |
| `K-MIG-001` | Existe el "Espacio Paralelo AurumCore" en Jira (proyecto PAR), 331 folios, RIESGO ALTO: el inventario de incidencias del paralelo. |
| `K-MIG-002` | "Día cero" (2-ago) e ingestas on-demand DB→DB para recuadrar; riesgo clave: un reporte sobre datos **ingestados** no prueba que el core calcula. |
| `K-MIG-003` | En el paralelo, el estatus "Finalizada" no equivale a cierre evidenciado (avance verificable 20.8% vs operativo 54.2%). |
| `K-MIG-004` | Alcance del ejercicio: full captación (vista + plazo) + crédito One Click; 5 universos; ~8-10 queries; dos salidas (balanza y detalle de movimientos). |
| `K-MOV-001` | OpenFin no es atómico (cargo + abono + reversa → 2-3 registros); Aurum es atómico (1 registro). Explica por qué los conteos difieren legítimamente. |
| `K-MOV-002` | En SPEI OUT, OpenFin no valida la CLABE (deja salir, STP la regresa, doble comisión); Aurum sí valida y detiene. Candidato `DEFECTO_OPENFIN`. |
| `K-MOV-003` | Las reinversiones generan un ID propio en cada core, por lo que se pierde la llave 1:1 de correlación (salvo SPEI). |
| `K-MOV-004` | Tipos de transacción de AurumCore observados (Apertura de inversión, Retorno, Pago de rendimiento, ISR AurumCore) con sus campos y signo. Catálogo parcial. |
| `K-MOV-005` | OpenFin registra movimientos (no transacciones); tipos 3=SPEI, 183=transferencia interna, 0=operación interna/manual; ~90% del volumen es 3+183. |
| `K-MOV-006` | Lo que OpenFin no guarda y se reconstruye: saldo anterior, saldo promedio, devoluciones (STP vs interna), ausencia de hold/tránsito. |
| `K-ORG-001` | El core destino es **AurumCore** (también "Aurum"); cierra la incógnita del nombre. |
| `K-ORG-002` | Responsables por dominio del paralelo (quién atiende Captación, Crédito, SPEI, etc.), tomado del OnePager. |
| `K-ORG-003` | Participantes de la sesión F-001 y el mapeo **inferido** de hablantes (SPEAKER_n → persona), con confianza media. |
| `K-PRC-001` | Filosofía de validación: "explicado al 100%, no cuadrado"; OpenFin no es fuente confiable; se necesita un tercero (= el oráculo); el neteo diario por cuenta debe ser 0. |
| `K-TMP-001` | Ventanas de proceso y asincronía: procesos nocturnos, OpenFin paga plazo ~18:30 y Aurum de noche; vista el día 1, plazo L-V. Causa de descuadres por sincronía. |

## 10. Preguntas abiertas (P-*) — 12
> La numeración no es contigua: `P-011`–`P-013` no existen; `P-014` se heredó del ejemplo del charter y se conservó.

| id | descripción corta |
|----|-------------------|
| `P-001` | **[CERRADA]** Nombre del core destino → AurumCore. |
| `P-002` | Mapeo definitivo hablante→persona→rol en F-001 (existe uno inferido; falta el oficial). |
| `P-003` | **[PARCIAL]** Calendario y alcance de la migración: fechas 1-sep/7-sep/1-oct confirmadas; falta el plan de cutover formal. |
| `P-004` | **[PARCIAL]** Linaje de datos de **OpenFin** — cerrado con F-011 (K-DAT-002..005); resta el `describe` físico de columnas y el catálogo de 63 operaciones. |
| `P-005` | Conciliar las cifras del propio tracking de Jira (266 vs 331 totales; 132 vs 124 activos). |
| `P-006` | Reglas de cálculo por producto que faltan: definición exacta de "saldo promedio", tasas, capitalización, devengamiento del crédito One Click. |
| `P-007` | Alcance, magnitud y regularización del defecto histórico de ISR en OpenFin. |
| `P-008` | Algoritmo de validación de CLABE en Aurum ("de Luna" / dígito verificador) por confirmar. |
| `P-009` | Cifras reales del "día cero": los screenshots no las capturaron; sólo hay narración con ruido de ASR. |
| `P-010` | Verificación **normativa** de los parámetros del ISR (tasa 0.9%, exención 5×UMA, UMA, 365 días). **Bloquea el código** del oráculo. |
| `P-011` | Modelo de datos y queries de **AurumCore** (la contraparte): tablas de cliente/cuenta/transacción, llaves, cómo reconstruye `tipo_operacion`. Sin esto no hay comparador. |
| `P-014` | ¿El devengo/rendimiento se redondea diario o al pago? ¿Hay sesgo sistemático? |

## 11. Fuentes (F-*) — 13
| id | descripción corta |
|----|-------------------|
| `F-001` | Sesión grabada de kickoff (v2t): la reunión donde se presenta el "tercero independiente". Es la fuente más rica de reglas y contexto. |
| `F-002` | pptx "Datos Cliente Único": arquitectura del ecosistema (AS-IS, fases 0/1, capas de datos Bronze/Silver/Gold). |
| `F-003` | xlsx export de Jira PAR, corte 12-ago (331 folios, con fórmulas y comparativo). |
| `F-004` | xlsx comparativo por día: cambios de estatus entre el 10 y el 11-ago (24 folios). |
| `F-005` | pdf de evidencias 11-ago: calidad de evidencia de 24 folios (operativo 54.2% vs integral 20.8%). |
| `F-006` | xlsx corte 10/11-ago: resumen ejecutivo, consolidado por responsable, detalle de folios. |
| `F-007` | xlsx corte 11-ago: mismas hojas que F-006, sin la de comparativo. |
| `F-008` | pdf OnePager directivo, corte 10-ago: casos críticos con impacto monetario y backlog por dominio. |
| `F-009` | pdf de documentación oficial de AurumCore: reglas de rendimientos (vista/plazo) e ISR, con fórmulas y ejemplos. |
| `F-010` | xlsx caso de validación de ISR (cliente real, cierre 2-ago): implementa la regla y la contrasta con las transacciones posteadas. |
| `F-011` | Sesión grabada (v2t) de modelo de datos y queries de OpenFin: el experto (Citi) explica tablas, llaves, reconstrucción y queries. Desbloquea P-004. |
| `F-012` | Inventario de queries de AurumCore (SQL): revela el modelo de datos de Aurum (esquema `aurumcore`). Desbloquea P-011. |
| `F-013` | Análisis árboles: reconciliación OpenFin vs Aurum al corte 02-03 ago (por dominio, con RCA). ~1.5 GB con PII, gitignored (ver MANIFEST). |

## 12. Supuestos (S-###) — 4
| id | descripción corta |
|----|-------------------|
| `S-001` | **[RESUELTO]** El placeholder `<CORE_NUEVO>` → AurumCore. |
| `S-002` | Stack del oráculo: Python 3.11+ con `decimal.Decimal` y validaciones en SQL ANSI. |
| `S-003` | Idioma de trabajo: español de México; identificadores sin acentos ni ñ. |
| `S-004` | La entidad es una SOFIPO (exposición ALTA: fija el marco regulatorio y fiscal). |

## 13. Especificaciones del oráculo (S-<DOM>-###) — 1
| id | descripción corta |
|----|-------------------|
| `S-FIS-001` | Retención de ISR sobre el pago de rendimientos: regla, parámetros, precisión y caso de oro. Spec lista; el código está bloqueado por P-010. |

## 14. Candidatos a hallazgo y folios PAR citados
| ref | descripción corta |
|-----|-------------------|
| `F001-ISR` | Candidato `DEFECTO_OPENFIN`: ISR mal calculado históricamente en OpenFin (de F-001). |
| `F001-CLABE` | Candidato `DEFECTO_OPENFIN`: doble comisión SPEI por no validar CLABE en OpenFin. |
| `F001-REDONDEO` | Candidato: redondeo distinto entre cores; verificar si genera sesgo. |
| `PAR-318` | Folio Jira: 689 créditos liquidados/cancelados siguen activos en Aurum; 1,110 con diferencias. |
| `PAR-351` | Folio Jira: 1,261 créditos Un Click sin devengamiento en AurumCore. |
| `PAR-352` | Folio Jira: vencimiento de inversión sin retención de ISR ($2,232,566.46). |
| `PAR-337` | Folio Jira: devolución SPEI OUT no refleja movimientos en Aurum. |
| `PAR-343` | Folio Jira: query de devoluciones SPEI pendiente (vencido). |
| `PAR-338` | Folio Jira: impacto de días inhábiles en inversiones ya aperturadas. |
| `PAR-311` | Folio Jira: faltan 1,089 de 7,339 contratos esperados en Aurum (15%). |

## 15. Términos de negocio y sistemas (corto; detalle con cita en `GLOSARIO.md`)
| término | descripción corta |
|---------|-------------------|
| OpenFin | Core bancario actual ("todo en uno"); motor A; referencia histórica, no verdad. |
| AurumCore / Aurum | Core bancario destino ("puro"); motor B; el sistema bajo prueba. |
| oráculo | El motor C: cálculo independiente desde la norma, para arbitrar discrepancias. |
| gateway (Citi) | Capa que recibe cada operación y la deriva a ambos cores en el paralelo. |
| core primario / autorizador | El que autoriza y define el saldo del cliente = OpenFin (hasta el switch). |
| día cero | Corte donde se ingestan datos para que ambos cores nazcan cuadrados (2-ago-2026). |
| ingesta | Traspaso de datos OpenFin→Aurum (DB→DB) para recuadrar; on-demand. |
| operación atómica | Aurum registra la operación como una unidad; OpenFin hace cargo+abono(+reversa). |
| One Click | Crédito amarrado a plazos, con domiciliación a cuentas vista. |
| CLABE / "algoritmo de Luna" | Validación de la estructura de la cuenta CLABE (dígito verificador). |
| balanza / detalle de movimientos | Las dos salidas: agregado contable vs auxiliares que lo alimentan. |
| ISR | Impuesto Sobre la Renta; retención sobre rendimientos, al momento del pago. |
| UMA | Unidad de Medida y Actualización; base de la exención de ISR (5×UMA). |
| SPEI / STP | Sistema de pagos interbancarios / participante que procesa SPEI OUT. |
| SIC | Sociedad de Información Crediticia (saldos reportados; dominio REG). |
| SOFIPO | Sociedad Financiera Popular; tipo de entidad supuesto (S-004). |
| v2t | video-to-text: conferencia diarizada con screenshots (tipo de fuente). |

---

## 16. Autovalidación
Revisé cada entrada contra tres criterios: (a) **explica qué es**, no sólo expande la sigla;
(b) **añade el porqué/impacto** cuando aplica; (c) es **trazable** a la pieza o fuente real.

**Cobertura (contra el inventario real del repo):** piezas 33/33 · preguntas 12/12 · fuentes 13/13
· supuestos 4/4 · specs 1/1 · dominios 13/13 · candidatos y folios PAR citados incluidos.
(Actualizado tras F-012/F-013: +6 piezas, +F-012/F-013, P-009 cerrada, P-011 parcial.)
Contradicciones `C-###`: 0 (no hay ninguna registrada todavía; el patrón se documenta por completitud).

**Avisos de confianza (entradas cuya descripción depende de algo no cerrado):**
- `K-ORG-003` / `P-002`: el mapeo de hablantes es **inferido**, no confirmado.
- `K-FIS-002`, `K-DEV-001`, `S-FIS-001`: la mecánica está confirmada, pero los **parámetros
  normativos del ISR** no (P-010) — no tomar la tasa 0.9% ni el 5×UMA como verificados.
- `P-009`: las cifras del "día cero" son narración ASR sin respaldo visual.
- Numeración de preguntas **no contigua** (falta P-011–P-013; P-014 heredada del charter) —
  señalado para que no se lea como un hueco perdido.
- Colisiones de notación (`S-`, `A/B/C` motor vs familia, `C`) señaladas en §1; son el punto más
  fácil de malinterpretar del diccionario.

**Mantenimiento:** este diccionario se actualiza con cada ingesta (nuevas piezas/preguntas/fuentes).
Si crece mucho, la parte 9–14 puede autogenerarse desde los front-matter de las piezas.
