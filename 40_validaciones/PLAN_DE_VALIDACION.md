# Plan de Validación — Paralelo OpenFin ↔ AurumCore

Versión: 1 · 2026-08-14 · Estado: BORRADOR para revisión
Sustento: charter §2, §10, §11 · [[K-PRC-001]] [[K-ARQ-002]] [[K-MIG-002]] [[K-DEV-001]] [[K-FIS-002]]

> **Cómo leer este plan.** Faltan tres insumos (modelos de datos, muestras, queries). Por eso cada
> paso separa **DISEÑO** (se puede hacer hoy, sin datos) de **EJECUCIÓN** (requiere el insumo).
> El plan no inventa datos: donde falta algo, se nombra la dependencia y la pregunta abierta.

---

## 1. Objetivo
Producir evidencia **auditable** que sustente el go/no-live, respondiendo cuatro preguntas en
orden (los 4 objetivos declarados por el proyecto, [[K-PRC-001]]):

1. **¿Se come todas?** AurumCore recibe y registra todas las operaciones (ninguna se pierde).
2. **¿Cae bien operativamente?** cada operación se registra donde debe.
3. **¿Cae bien contablemente?** en la cuenta contable del producto.
4. **¿Calcula bien?** rendimientos, ISR y devengo son correctos **según la norma** (no según OpenFin).

Meta declarada: **no cuadrar al 100%, sino explicar el 100%** de las diferencias ([[K-PRC-001]]).

## 2. Principios (charter §10)
- Cada validación es una **consulta que devuelve las filas que violan la identidad**. Cero filas =
  pasa. Nunca un total para comparar a ojo.
- **Tres motores**: A=OpenFin (referencia, no verdad), B=AurumCore (bajo prueba), C=oráculo
  (árbitro). Sin C sólo se concluye "son distintos", no "cuál es correcto".
- **Tolerancias**: identidades contables (familias B y C) = **0.00 sin excepción**; cálculos con
  redondeo (devengo/ISR) = ≤$0.01 por evento **y ausencia de sesgo** (prueba de signo).
- Cada hallazgo confirmado se convierte en **invariante permanente** (red de regresión).

---

## 3. Insumos requeridos (hoy faltantes) y qué bloquean
| insumo | pregunta | lo aporta | bloquea EJECUCIÓN de | permite DISEÑO de |
|--------|----------|-----------|----------------------|-------------------|
| **Queries** de cada core (~8-10, ya existen, en Confluence) | P-004 | equipo OpenFin (Abraham) / Aurum (Mario) | Fases 2-7 | Fases 1-8 |
| **Diccionario de datos / modelo** de OpenFin y Aurum | P-004 | equipos de cada core | correlación 1:1, familia C | Fases 1, 3-6 |
| **Muestra de datos** (día cero limpio, ventana sin ingesta) | P-009 | ingesta sábado→domingo ([[K-MIG-002]]) | Fases 2-8 | validación del propio diseño |
| **Parámetros normativos del ISR** (tasa, UMA, exención, días) | P-010 | Fiscal/Contraloría + norma | código de S-FIS-001 (Fase 6) | spec ya escrita |
| **Definición de "saldo promedio mensual"** | P-006 | Producto | S-DEV-001 (vista) | — |
| **Inventario de operaciones asíncronas y calendario de ingestas** | — | equipo Aurum | Fase 1 (exclusiones) | Fase 1 |
| **NDA / accesos** | — | proyecto | todo lo que toque prod | — |

> **Ruta crítica**: los **queries + diccionario** desbloquean casi todo. Es la primera petición.
> La **muestra limpia** (día cero sábado→domingo) es el segundo desbloqueo. P-010 desbloquea sólo
> el cálculo de ISR, no el resto.

---

## 4. El plan, paso a paso

### Fase 0 — Habilitación
- **Objetivo:** tener con qué trabajar.
- **Qué se hace:** solicitar queries + diccionario de datos; acordar la ventana de "día cero"
  limpio (sábado→domingo, base cerrada, sin ingesta — decisión ya tomada en [[K-MIG-002]]);
  firmar NDA/accesos; obtener el inventario de operaciones asíncronas y el calendario de ingestas.
- **Salida esperada:** repositorio de queries versionado; diccionario `DAT`; ventana de muestra
  agendada; lista de operaciones a excluir por diseño.
- **Dependencias:** ninguna interna; depende de terceros (equipos de cada core).

### Fase 1 — Universo comparable y correlación ("peras con peras")
- **Objetivo:** definir qué es comparable y cómo se cruza A vs B, antes de comparar nada.
- **Qué se hace (DISEÑO, hoy):**
  - Definir **llaves de correlación** por tipo de operación. Para SPEI hay 1:1; para
    reinversiones **no hay llave común** ([[K-MOV-003]]) → definir llave sustituta (cliente +
    producto + monto + ventana).
  - Definir **ventanas de tiempo con delta** y su tratamiento de asincronía ([[K-TMP-001]]).
  - Definir **exclusiones por diseño**: CLABE inválida sin registro en Aurum ([[K-MOV-002]]),
    reversos internos de middleware, no-atomicidad de OpenFin ([[K-MOV-001]] → normalizar cargo+
    abono+reversa a la unidad atómica).
  - Definir el **filtro calculado-vs-ingestado** ([[K-MIG-002]]): marcar registros ingestados y
    trabajar ventanas **entre ingestas**, o aislarlos.
- **Salida esperada:** documento de **reglas de correlación y exclusión** + catálogo de casuísticas
  esperadas (con su clasificación anticipada `DIFERENCIA_DISENO_AUTORIZADA`).
- **Dependencias:** diccionario de datos (para nombrar llaves reales); inventario de asíncronas.

### Fase 2 — Completitud: "¿se come todas?" (familia A)
- **Objetivo:** demostrar que ninguna operación se pierde en Aurum.
- **Qué se hace:** invariante que devuelve **operaciones presentes en A y ausentes en B** (y
  viceversa) dentro del universo comparable y ventana; conteo por tipo/canal/día; explicación de
  cada faltante contra el catálogo de casuísticas de Fase 1.
- **Salida esperada:** `INV-MOV-01..0n` (filas faltantes = violaciones); tabla "faltantes
  explicados vs no explicados" por día. Objetivo operativo: 0 faltantes **no explicados**.
- **Dependencias:** Fase 1; queries + muestra.

### Fase 3 — Consistencia interna del detalle (familia A)
- **Objetivo:** que el detalle de movimientos sea coherente consigo mismo en cada core.
- **Qué se hace:** invariantes de **rollforward diario y por ventana** (saldo_inicial + Σmov =
  saldo_final); **unicidad de folios**; **reversas bien formadas** (todo reverso casa con su
  movimiento); **coherencia de signos y fechas**; **neteo diario por cuenta = 0** entre A y B
  ([[K-PRC-001]]: aunque el nº de transacciones difiera, el saldo del cliente no debe moverse).
- **Salida esperada:** `INV-MOV-1x` con las filas que rompen cada identidad; el **neteo=0** es el
  primer invariante estrella. Tolerancia contable-de-cuenta = 0.00.
- **Dependencias:** Fase 1; queries + muestra.

### Fase 4 — Consistencia contable de la balanza (familia B)
- **Objetivo:** que la balanza de cada core cierre sola.
- **Qué se hace:** **doble partida por póliza y por día** (Σcargos = Σabonos); **rollforward
  contable** entre días; **continuidad** (saldo final día t = inicial día t+1); **naturaleza de
  cuenta**. Se corre por separado en A y en B.
- **Salida esperada:** `INV-CTB-0x` (filas que descuadran). Tolerancia **0.00**.
- **Dependencias:** query de balanza; **matriz `tipo_movimiento → cuenta contable`** (dominio CTB,
  hoy [PENDIENTE]).

### Fase 5 — Amarre auxiliar ↔ balanza (familia C)
- **Objetivo:** que el detalle (auxiliar) y la balanza (mayor) amarren.
- **Qué se hace:** **amarre de stock** por producto-día (Σ saldos auxiliares = saldo contable);
  **amarre de flujo** por tipo de movimiento-día; **cobertura bidireccional** movimiento↔póliza;
  **asientos manuales aislados**; **cuentas puente** explicadas línea por línea. Ojo con el matiz
  de [[K-MIG-004]]: la balanza es contable y no siempre refleja transacciones.
- **Salida esperada:** `INV-CTB-1x` (partidas sin amarre). Tolerancia **0.00**.
- **Dependencias:** Fases 3-4; matriz de amarre CTB; diccionario.

### Fase 6 — Oráculo / "¿calcula bien?" (motor C)
- **Objetivo:** calcular de forma independiente y contrastar contra A y B.
- **Qué se hace (DISEÑO ya iniciado):**
  - **ISR**: implementar [[S-FIS-001]] (spec lista, caso de oro 46.37/4.81/0.05) — **requiere
    P-010** para los parámetros.
  - **Rendimiento vista** (S-DEV-001, por escribir sobre [[K-DEV-002]]) — requiere definición de
    saldo promedio (P-006).
  - **Rendimiento plazo** (S-DEV-002, sobre [[K-DEV-003]]).
  - Redondeo como **parámetro explícito por cálculo** ([[K-DEV-001]] v2), `decimal.Decimal`, cero float.
- **Salida esperada:** módulo `30_oraculo/src` + tests que reproducen los casos de oro; por cada
  contrato-día, un valor C comparable con A y B.
- **Dependencias:** P-010 (ISR), P-006 (vista); muestra de datos para correr sobre casos reales.

### Fase 7 — Cross-motor y arbitraje (familia D)
- **Objetivo:** clasificar cada discrepancia con la matriz de decisión del charter.
- **Qué se hace:** evaluar la **misma identidad en A, B y C**; comparar el **conjunto de
  violaciones** entre motores; aplicar la matriz (=,=,≠ → defecto de ambos; =,≠,= → defecto Aurum;
  ≠,=,= → defecto OpenFin; ≠,≠,≠ → regla mal especificada). Abrir ficha de hallazgo por cada uno.
- **Salida esperada:** `50_hallazgos/H-###` con {A,B,C}, clasificación, severidad, alcance,
  impacto. Los candidatos actuales entran aquí: F001-ISR, F001-CLABE, F001-REDONDEO y los 7 de Jira PAR.
- **Dependencias:** Fases 2-6.

### Fase 8 — Sesgo y materialidad
- **Objetivo:** distinguir el centavo aleatorio del pasivo material.
- **Qué se hace:** sobre las diferencias de devengo/ISR/redondeo, **prueba de signo** para detectar
  sesgo ([[K-DEV-001]] v2: el "ceil a 10" del plazo sesga positivo por diseño); cuantificar impacto
  (alcance × diferencia media) y **anualizarlo** sobre el padrón.
- **Salida esperada:** por cada cálculo, {media de diferencia, sesgo sí/no, impacto anualizado}.
  Sesgo ≠ 0 = **severidad 1** aunque cada diferencia sea de $0.01.
- **Dependencias:** Fase 6 corrida sobre volumen (no muestra mínima).

### Fase 9 — Regresión y certificación
- **Objetivo:** convertir el ejercicio en algo repetible y emitir el veredicto.
- **Qué se hace:** cada hallazgo confirmado → **invariante permanente** en la batería; correr la
  batería completa sobre una ventana limpia; emitir el reporte de estado (cobertura, hallazgos por
  severidad, avance a go/no-live). Los `DEFECTO_OPENFIN` (ISR histórico, CLABE) escalan a Comité.
- **Salida esperada:** batería de regresión versionada + reporte ejecutivo go/no-live.
- **Dependencias:** todo lo anterior.

---

## 4.bis Estado real al corte 02-03 ago (árbol día cero) — F-013
Ya existe una **primera ejecución de las Fases 2 y 7** hecha por el equipo A/B (motores OpenFin vs
Aurum), en `00_entendimiento/ANALISIS_ARBOLES.md`. Resumen por dominio y qué debe hacer C:

| dominio | en común | estado | lo que C debe re-derivar/arbitrar |
|---------|----------|--------|-----------------------------------|
| Clientes | 956,331 | ~100% | nada material |
| Cuentas vista | 2,046,969 | 97.9% con saldo+tasa | BUG API (2,977), tasa 2019 (2,053), diff saldo por ingesta/redondeo |
| Inversiones | 18,599 | existencia 100%; **ISR ≈27% diff** | recalcular ISR desde la norma sobre el mismo saldo base (separar cascada) |
| Créditos 5004 | 7,619 | **100% cuadra** | validar el devengamiento diario (no está en el árbol) |
| Transacciones (2-ago) | 32,539 | 524/182 únicas | clasificar causas; confirmar SPEI que no llegan a satélites (dinero real) |

Implicaciones para el plan:
- **Fase 1 (exclusiones):** sucursal 201 (fondeadora) fuera del universo; internas de plataforma
  (VIRTUAL1/2, dispersiones, consulta Pomelo $0) marcadas como diseño.
- **Fase 6 (oráculo):** prioridad ISR de inversiones (mayor gap) y saldo promedio (cascada). One
  Click cuadra → cerrar primero (bajo riesgo).
- **Fase 8 (sesgo):** el redondeo ya aparece en 3 dominios; correr prueba de signo sobre esas distribuciones.
- **Naturaleza:** las causas del árbol son **auto-reportadas** por A/B; C las verifica, no las asume.

## 5. Qué se puede adelantar HOY (sin datos)
1. **Fase 1 completa**: reglas de correlación y exclusión, catálogo de casuísticas.
2. **Diseño de invariantes** (Fases 2-5) como SQL parametrizado contra un esquema supuesto,
   listo para conectar cuando llegue el diccionario. Marcar los nombres de tabla/campo como
   `[SUPUESTO]` hasta P-004.
3. **Oráculo (Fase 6)**: terminar S-DEV-001/002; codificar S-FIS-001 salvo los parámetros (P-010);
   dejar los **tests de caso de oro** listos.
4. **Esqueleto de `CATALOGO_VALIDACIONES.md`** con cada invariante planeado (id, familia, identidad,
   piezas, severidad, tolerancia).

## 6. Criterios de go/no-live (borrador, a acordar)
- **Bloquea go-live (sev 1):** cualquier faltante no explicado de operación; descuadre contable ≠
  0.00; sesgo sistemático en devengo/ISR; `DEFECTO_OPENFIN` de ISR sin decisión de Comité.
- **Bloquea el ciclo (sev 2):** casuística sin explicar por encima de un umbral a acordar.
- **Documentar (sev 3):** diferencias explicadas y autorizadas por diseño.

## 7. Riesgos del propio plan
- **Ingestas que borran la señal** ([[K-MIG-002]]): si se valida sobre datos ingestados, se
  certifica humo. Mitigación: ventanas entre ingestas / marca calculado-vs-ingestado (Fase 1).
- **Regla normativa incorrecta** (P-010): si el ISR de AurumCore está mal especificado, A y B
  pueden coincidir y ambos estar mal (caso ≠≠≠). El oráculo desde la norma es la única defensa.
- **Falta de llave 1:1** ([[K-MOV-003]]): falsos positivos/negativos en reinversiones. Mitigación:
  llave sustituta y reconstrucción de la cadena.
- **Confiabilidad del tracking** (266 vs 331; evidencia 20.8%): no confiar en "Finalizada" como cierre.

## 8. Dependencias — vista resumida
```
Fase 0 (insumos) ─┬─> Fase 1 (correlación) ─┬─> Fase 2 (completitud) ─┐
                  │                          ├─> Fase 3 (detalle) ─────┤
   P-004 ─────────┘                          ├─> Fase 4 (balanza) ─────┼─> Fase 7 (arbitraje) ─> Fase 9
   P-006/P-010 ──────────────> Fase 6 (oráculo) ─┘   Fase 5 (amarre) ──┘        │
                                                     Fase 6 ──> Fase 8 (sesgo) ─┘
```
