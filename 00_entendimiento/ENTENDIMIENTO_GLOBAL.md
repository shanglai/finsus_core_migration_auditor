# Entendimiento Global del Proyecto

Versión: 6 · Actualizado: 2026-08-16 · Piezas de conocimiento: 33
Nivel de completitud estimado: ~62% · Preguntas abiertas críticas: 5

> **Honestidad de completitud (Anexo C).** Con F-001 procesada ya hay **arquitectura del paralelo,
> modelo de tiempos, primeras reglas (redondeo, atomicidad, SPEI/CLABE) y la filosofía de
> validación** — que resulta ser exactamente el diseño de tres motores del charter. Falta el grueso
> de reglas de cálculo por producto (devengamiento de crédito, tasas, capitalización, ISR desde la
> norma) y todo el linaje de datos de los cores. Por eso ~30%: hay esqueleto sólido y algo de carne,
> falta la mayor parte del cálculo verificable.

## 1. Resumen ejecutivo
[CONFIRMADO] Finsus migra de **OpenFin** a **AurumCore**; lleva ~3.5 años. Deadline **7-sep-2026**
para demostrar operación; decisión **1-sep**, y si procede, **1-oct** Aurum pasa a primario.
→ K-ORG-001, K-ARQ-002.
[CONFIRMADO] Opera un **paralelo**: un gateway (Citi) deriva cada operación a ambos cores; OpenFin
autoriza. Las incidencias se llevan en **Jira PAR** (331 folios, RIESGO ALTO). → K-ARQ-002, K-MIG-001.
[CONFIRMADO] La premisa oficial es **"explicado al 100%, no cuadrado al 100%"**, y **OpenFin no es
fuente confiable** → se necesita un **tercero independiente de cálculo**. Ese tercero es este
proyecto (Motor C). → K-PRC-001.
[CONFIRMADO] Riesgo político/operativo: el área de operaciones desconfía ("Aurum no calcula, pegan
los datos"); y un reporte sobre datos **ingestados** no prueba que Aurum calcula. → K-MIG-002.

## 2. Contexto de la entidad y los sistemas
[CONFIRMADO] Dos cores (OpenFin, Aurum) + gateway (Citi) + middleware/Analyzer + satélites
(Dynamics, Simetrik, Pomelo, WebBanking, FinsusApp, AODB, F1). → K-ARQ-001, K-ARQ-002.
[CONFIRMADO] Equipos: Finsus/proyecto (Jorge, Juan, Néstor, Giancarlo, Abraham…), **Citi** (gateway),
y un **equipo externo de data** (Reinier/David/José, vía "Abascal") que construye el tercero. → K-ORG-003.
[SUPUESTO] Entidad SOFIPO (S-004), sin corroborar en fuente.

## 3. Mapa de productos y su comportamiento
[CONFIRMADO] Alcance actual: **captación (cuentas vista + cuentas plazo) + crédito One Click**
(amarrado a plazos, domicilia a vista). → K-MIG-004.
[CONFIRMADO] Comportamientos de tiempo confirmados: rendimientos **vista = día 1 del mes**;
**plazo = L-V**; procesos nocturnos asíncronos. → K-TMP-001.
[CONFIRMADO] **Rendimiento vista**: base saldo promedio mensual, se procesa el día 1 el mes
anterior; elegibilidad por estado de cuenta/cliente y esquema de rendimientos. → K-DEV-002.
[CONFIRMADO] **Rendimiento plazo fijo**: base capital inicial (`iv_initial_amount`), días entre
planes de pago, parámetros del misceláneo del producto. → K-DEV-003.
[PENDIENTE] Definición exacta de "saldo promedio", tasas por producto, capitalización, One Click,
devengamiento de crédito, comisiones (P-006).

## 4. Arquitectura y flujo de datos
[CONFIRMADO] Canales → gateway → ambos cores; OpenFin primario. → K-ARQ-002. Dos capas de
comparación: **transaccional** y **contable (balanza)**, que no siempre coinciden. → K-MIG-004.
[CONFIRMADO] OpenFin registra **movimientos, no transacciones** (cargo/abono); la transacción vive
en middleware. → K-MOV-005. Fuente de la verdad por dato repartida core/middleware/backend/analyzer
(K-DAT-005); el saldo es siempre de OpenFin.
[CONFIRMADO] Trazabilidad 1:1 sólo resuelta para SPEI (`id_external`); reinversiones y demás pierden
la llave común. → K-MOV-003, K-DAT-003. Linaje de OpenFin mapeado (K-DAT-002..005); falta el de Aurum (P-011).

## 5. Modelo de tiempos
[CONFIRMADO] Asincronía estructural: OpenFin paga plazo ~18:30, Aurum en la noche; robots de
conciliación c/4h (SPEI/onboarding) y nocturno (asíncronas). → K-TMP-001. Es la causa principal de
descuadres de **saldo/sincronía** (no de cálculo). Focos: PAR-338 (inhábiles), PAR-121 (fecha valor).

## 6. Modelo de datos relevante
[CONFIRMADO] **Modelo de datos de OpenFin** mapeado (F-011) → artefacto
`00_entendimiento/MODELO_DATOS_OPENFIN.md`. 5 tablas (`asociados`, `acreedores`, `deudores`,
`detalle_auxiliar`, `detalle_auxiliar_masdatos`); llaves cliente/cuenta de 3 campos, `secuencia` (PK
de movimientos), `id_external` (cross-sistema, sólo SPEI). Productos (2000s vista, 2300s inversiones,
5004 One Click) y estatus (3/4/5). Motor PostgreSQL; producción manda (T-1 no confiable). → K-DAT-002..005.
[CONFIRMADO] Nombres físicos de columnas de OpenFin confirmados por extracciones reales (K-DAT-002 v2).
[CONFIRMADO] **Modelo de datos de AurumCore** revelado por sus queries (K-DAT-006, esquema `aurumcore`:
`accountholder`, `account`, `lc_loan_contract`, `iv_payment_plan`, `"transaction"`…) → **P-011 casi cerrada**.
[PENDIENTE] Columnas completas de `aurumcore."transaction"` y cómo Aurum reconstruye el tipo. Separar
linaje calculado-por-core vs ingestado (K-MIG-002).

## 7. Reglas de negocio consolidadas
Reglas confirmadas (índice):
- **Rendimiento vista** → K-DEV-002. **Rendimiento plazo fijo** → K-DEV-003.
- **ISR** (regla completa AurumCore, verificada con caso real) → K-FIS-002. Parámetros normativos
  (tasa 0.9%, exención 5·UMA, 365 días) por verificar (P-010).
- **Redondeo:** trunc 20 dec intermedio, trunc 5 en ISR diario, redondeo final a 2 con modo por
  cálculo (vista normal, plazo half_even); OpenFin 2 dec → K-DEV-001 v2.
- **Atomicidad:** OpenFin cargo+abono+reversa; Aurum atómico → K-MOV-001.
- **SPEI/CLABE:** OpenFin no valida CLABE, Aurum sí → K-MOV-002.
- **Tiempos:** vista día 1, plazo L-V, asincronía nocturna → K-TMP-001.
- **Tipos de transacción AurumCore** (parcial): Apertura inversión, Retorno, Pago rendimiento, ISR → K-MOV-004.
[PENDIENTE] Devengamiento de crédito One Click, tasas por producto, comisiones (P-006).

## 8. Estado de la validación
[CONFIRMADO] **Ya existe una primera ejecución real (Fases 2 y 7) del equipo A/B**: el árbol de
decantación día cero (02-03 ago, F-013) — ver `ANALISIS_ARBOLES.md` y §"Estado real al corte" del
plan. Resumen: clientes/inversiones/créditos con existencia ~100%; **One Click cuadra 100%**; el
mayor gap de cálculo es **ISR de inversiones (≈27%)**, en parte cascada del diff de saldo. Es
reconciliación A/B, no arbitraje C: el trabajo de C es re-derivar los cálculos discrepantes.
[CONFIRMADO] **Primera spec del oráculo escrita: S-FIS-001 (ISR)**, con caso de oro de F-010
(reproducir 46.37 / 4.81 / 0.05 al centavo). Falta el código (bloqueado por P-010, parámetros
normativos). Specs de rendimientos (S-DEV-001 vista, S-DEV-002 plazo) por escribir sobre K-DEV-002/003.
[CONFIRMADO · 2026-08-19] **Captación vista-ahorro SÍ genera interés propio** (corrección de un cierre
previo erróneo): se capitaliza a fin de mes (`Capitaliza Interes`, source=target) en ~**100,058 cuentas**,
~$8.5M/mes; productos 2006/2011/2012/2013/2015/2017/2019 ([[K-DEV-002]] v2). **Hallazgo:** sólo existe en
historia migrada (ene–jul); AurumCore vivo **aún no corre** ese cierre — 1º post-cutover = **31-ago-2026**
→ motor B de captación-interés **inobservable/sin validar** hasta esa fecha ([[P-015]]). El rendimiento de
inversión (2301/2307/2308) se **deposita** en la vista del titular (destino), no es interés ganado por la vista.
**Plan de validación por fases** escrito: `40_validaciones/PLAN_DE_VALIDACION.md` (fases 0-9, con
insumos faltantes y dependencias). Objetivos de demostración (se come todas · operativo · contable ·
calcula bien → K-PRC-001) mapean a las familias A/B/C/D del §10. Invariantes candidatos: **neteo diario por cuenta = 0**, **roll-forward
por ventana**. Candidatos a hallazgo: 7 de Jira PAR + 3 de F-001 (ISR histórico, CLABE, redondeo).

## 9. Mapa de riesgo
1. **FIS/ISR:** defecto histórico admitido en OpenFin (K-FIS-001) + PAR-352 ($2.23M). Ya hay regla
   AurumCore documentada y verificada contra un caso (K-FIS-002); Aurum reproduce su propia regla.
   **Pero** los parámetros normativos (tasa 0.9%, 5·UMA, 365 días) aún no se verifican contra la
   norma (P-010) — si la regla misma no es normativamente correcta, ambos cores podrían estar mal.
2. **DEV/redondeo:** riesgo de **sesgo sistemático** (K-DEV-001 v2): el "redondear a 10 hacia arriba"
   (ceil) del plazo es sesgo positivo por diseño — material sobre el padrón aunque cada diff sea ≤$0.01.
3. **DEV/Crédito:** devengamiento One Click (PAR-351, 1,261 créditos) — regla aún no confirmada.
4. **MOV/Crédito:** conciliación Un Click (PAR-318).
5. **Metodológico:** reportes sobre datos ingestados no prueban cálculo (K-MIG-002) — riesgo de
   falsa certificación. Diseñar comparaciones **entre ingestas** o aislando ingestados.
6. **DAT:** falta de llave 1:1 en reinversiones (K-MOV-003) → falsos positivos/negativos.
7. **SPEI:** CLABE/devoluciones (K-MOV-002, PAR-337/343).
Transversal: confiabilidad del tracking (266 vs 331; evidencia 20.8%).

## 10. Lo que NO sabemos
Espejo de `PREGUNTAS_ABIERTAS.md`: **parámetros normativos del ISR (tasa/UMA/exención/días) — P-010,
bloquea el código del oráculo**; reglas de cálculo por producto (P-006); alcance/regularización del
ISR histórico (P-007); algoritmo CLABE (P-008); cifras reales del día cero (P-009); momento del
redondeo y sesgo (P-014, ahora con datos: redondeo en 3 dominios); P-011 (Aurum) **casi cerrada**
—resta columnas de `"transaction"`—; P-004 (OpenFin) **casi cerrada** —resta el `describe` formal—;
P-009 (cifras día cero) **cerrada** con datos reales (F-013); mapeo de hablantes (P-002).

## 11. Supuestos vigentes y su exposición
S-001 RESUELTO (AurumCore). Vigentes: S-002 (stack oráculo), S-003 (idioma), S-004 (SOFIPO,
exposición ALTA — fija el marco REG/FIS y el cálculo de ISR).

## Changelog
| v | Fecha | Qué cambió en el entendimiento | Fuente que lo provocó |
|---|-------|--------------------------------|-----------------------|
| 1 | 2026-08-14 | Documento vacío de arranque. | — |
| — | 2026-08-19 | **[parche, no v-bump]** Captación vista-ahorro genera interés propio (~100K ctas); hallazgo: corrida viva pendiente 31-ago (K-DEV-002 v2, P-015). **Nota: el documento está rezagado (v6, no refleja cierre de P-010 ni set ISR 3,236/3,236); pendiente `sintesis` completo.** | Extracción BD 2026-08-19 |
| — | 2026-08-19 | **[parche]** Sesión F-021/F-022: **alcance reencuadrado a 3 corrientes** (Motor A cálculo + Motor B diario + prueba día cero); Finsus confirma ISR-modelo/Gap B/Gap C; reglas nuevas (saldo promedio, tx 2:1, vista día 1°); fuente → réplica; cutover 1-oct. Ver NORTE §0, K-DEV-002 v3, K-MOV-001 v2, K-REG-002 v2, P-016. | F-021, F-022 |
| 2 | 2026-08-14 | Ingesta F-002..F-008: core, sistemas, mecanismo del paralelo, riesgo. 0%→~12%. | F-002..F-008 |
| 3 | 2026-08-14 | Ingesta F-001: arquitectura del paralelo, modelo de tiempos, primeras reglas (redondeo/atomicidad/CLABE), filosofía de validación (= diseño del charter), 2 candidatos DEFECTO_OPENFIN. **Antes** teníamos marco sin reglas; ahora hay primeras reglas verificables y el porqué metodológico. ~12%→~30%. | F-001 |
| 4 | 2026-08-14 | Ingesta F-009 (doc oficial rendimientos+ISR) y F-010 (caso ISR real): reglas de cálculo de rendimientos vista/plazo, **regla completa de ISR con caso de oro**, refinamiento del redondeo. **Primera spec del oráculo S-FIS-001**. **Antes** el ISR y el redondeo eran narración; ahora son regla documentada e implementable (falta verificar parámetros normativos, P-010). ~30%→~42%. | F-009, F-010 |
| 5 | 2026-08-15 | Ingesta F-011 (modelo de datos y queries de OpenFin): 6 piezas DAT/MOV + artefacto `MODELO_DATOS_OPENFIN.md` con 5 apartados (diccionario, reconstrucción, llaves, trazabilidad, queries). **Antes** el §6 estaba vacío (P-004 abierta); ahora el linaje de OpenFin está mapeado. Nueva P-011 (falta la contraparte de Aurum). ~42%→~52%. | F-011 |
| 6 | 2026-08-16 | Ingesta F-012 (queries de Aurum → modelo de datos de Aurum, P-011) y F-013 (árbol de decantación día cero, 1.5 GB gitignored): 6 piezas + `ANALISIS_ARBOLES.md` + estado real en el plan + 7 candidatos a hallazgo. **Antes** teníamos solo el marco y OpenFin; ahora hay la reconciliación real A/B con números y causas, y el modelo de Aurum. One Click cuadra 100%; ISR es el mayor gap. ~52%→~62%. | F-012, F-013 |
