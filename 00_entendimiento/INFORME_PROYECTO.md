# Informe de estado — Validación de migración de core (Finsus)
### OpenFin → AurumCore · conciliación independiente

Versión: 1 · 2026-08-16 · Completitud del entendimiento: ~62% · Piezas de conocimiento: 33
Documento de síntesis. El detalle vive en los artefactos citados (`[[archivo]]`).
**FINSUS · Confidencial** — no distribuir fuera del proyecto.

---

## 1. Qué es el proyecto

Finsus migra su core bancario de **OpenFin** (legacy, "todo en uno") a **AurumCore** (core puro).
Llevan ~3.5 años; hay un **paralelo** donde un *gateway* (construido por Citi) manda cada operación
a **ambos** cores, siendo OpenFin el primario/autorizador. Fechas: **decisión 1-sep**, **deadline
7-sep** para demostrar que la operación existe y calcula, y **switch a Aurum ~1-oct** (si procede).

Nuestro rol (equipo Linko) es el **tercero independiente**: no somos OpenFin ni AurumCore.
Operamos un **modelo de tres motores**:

| Motor | Qué es | Rol |
|-------|--------|-----|
| **A** | OpenFin | referencia histórica — **no es la verdad** |
| **B** | AurumCore | sistema bajo prueba |
| **C** | Nuestro oráculo | **árbitro independiente**: calcula desde la norma/contrato |

La premisa oficial (del propio equipo, no impuesta por nosotros): **no se busca cuadrar al 100%,
sino explicar el 100% de las diferencias**; y como OpenFin no es fuente confiable, se necesita un
tercero que calcule según la norma. Sin el motor C sólo se puede decir "son distintos", nunca
"cuál está bien". Detalle: `[[ENTENDIMIENTO_GLOBAL.md]]`.

---

## 2. Cuáles son los problemas (por qué esto es difícil)

1. **OpenFin registra movimientos, no transacciones.** Todo es cargo/abono; una operación de
   negocio (con comisión e impuesto) se ve como 2-3 movimientos sin identificador que los una. Se
   asocian por tiempo o póliza (frágil). Aurum es atómico (1 registro). → los **conteos difieren
   por diseño**.
2. **Asincronía / desfase de tiempo.** OpenFin paga rendimientos de vista ~18:00 y Aurum a
   medianoche → hay horas donde el saldo difiere y "descuadra" sin que nadie calcule mal.
3. **Redondeo distinto.** Aurum trunca a 20/5 decimales y redondea al final; OpenFin a 2. Genera
   diferencias ≤$0.10 en miles de casos. Riesgo: **sesgo sistemático** (aunque cada centavo parezca ruido).
4. **Las ingestas "recuadran" y borran la señal.** El grueso de los datos de Aurum fue *ingestado*
   (traído ya calculado desde OpenFin). Un reporte sobre datos ingestados **no prueba que Aurum
   calcula**. Hay que comparar en ventanas *entre* ingestas.
5. **No hay llave 1:1 confiable salvo SPEI.** Las reinversiones generan ID propio en cada core; el
   único identificador cross-sistema garantizado es `id_external`, y sólo en SPEI.
6. **Ambientes.** La réplica **t-1 no es fuente de verdad** (tuvo `secuencia` duplicadas en
   dic-2025); producción manda. Reportes Unificados es una capa replicada (no confundir con la fuente).
7. **Defecto histórico de negocio.** El ISR se calculó mal "toda la vida" en OpenFin (corregido
   hace poco) — es la cubeta incómoda: si es sistemático, implica decisión de Comité y posible
   regularización a clientes.
8. **El árbol de comparación existente es del propio equipo (A vs B).** Muy útil como mapa, pero
   sus causas son auto-reportadas ("N/A DONE", "se mitiga al cambio de core"). No es arbitraje
   independiente.

---

## 3. Con qué herramientas contamos

### 3.1 Queries de extracción
- **OpenFin:** el experto (Citi) explicó tabla por tabla y hay ~8-10 queries (clientes, cuentas
  vista, inversiones, crédito 5004, movimientos). Los "generales" quedaron de enviárnoslos por correo.
- **AurumCore:** **ya tenemos los 5 queries con su SQL** (`Inventario_Queries_AurumCore.xlsx`),
  que además revelan el modelo de datos de Aurum. Detalle: `[[MODELO_DATOS_OPENFIN.md]]`,
  pieza K-DAT-006.

### 3.2 Modelo de datos (ambos cores)
| | OpenFin (PostgreSQL) | AurumCore (esquema `aurumcore`) |
|---|---|---|
| Clientes | `asociados` (id_sucursal·id_role·id_asociado) | `accountholder` (accountholder_number) |
| Cuentas | `acreedores` / `deudores` (id_suc_aux·id_producto·id_auxiliar) | `account` (account_number; producto = 2º segmento) |
| Movimientos | `detalle_auxiliar` (+`_masdatos`), PK `secuencia` | `"transaction"` |
| Tasa | en acreedores | `account_yield.interest_rate` |
| Crédito 5004 | deudores | `lc_loan_contract` + `lc_products` |
| Cross-sistema | `id_external` (SPEI) | `id_openfin` / `transaction` |
Diagramas: `[[MODELO_DATOS_OPENFIN_diagrama.svg]]`, `[[MODELO_DATOS_OPENFIN_ER.md]]`.

### 3.3 Datos que YA tenemos (corte 02-03 ago, en los Excel/CSV del árbol — F-013)
Por dominio, con universos **En común / Único AC / Único OF / Diff**: Clientes, Cuentas vista,
Inversiones, Créditos 5004, Transacciones. ~1.5 GB (con PII → **fuera de git**; traza en el MANIFEST).
Incluye el maestro `Árboles - Día Cero.xlsx` (metodología + causas + asignaciones) y la regla e
insumos de ISR (`44_inversiones`, caso de oro).

### 3.4 Datos/insumos que FALTAN que nos den
| Falta | Para qué | Estado |
|-------|----------|--------|
| **Accesos** (VPN, usuarios, esquema de escritura, datos de conexión de Aurum) | correr el modelo en vivo | **solicitados 15-ago; pendiente infra** (correo respondido 16-ago) |
| `describe` físico formal de las 5 tablas OpenFin | fijar tipos/columnas exactas | prometido por correo |
| Columnas completas de `aurumcore."transaction"` + cómo reconstruyen el tipo | comparador de transacciones | pendiente (resto de P-011) |
| Catálogo de las **63 operaciones** activas | mapear tipos de transacción | prometido por correo |
| Acceso a **producción** OpenFin | cifras de certificación (t-1 no basta) | por gestionar |
| **Parámetros normativos del ISR** (tasa 0.9%, 5×UMA, 365 días) | codificar el oráculo de ISR | **P-010 — bloquea el cálculo** |
| Definición exacta de "saldo promedio mensual" | oráculo de rendimiento vista | P-006 |

### 3.5 El árbol de comparación (metodología)
Por dominio se parte de la **llave** y se agregan dimensiones de forma **acumulativa**
(`En común → +Saldo → +Tasa → +Rendimiento → +ISR`), midiendo el % que sigue cuadrando. Cada caída
(Diff) y cada Único se explica con **causa raíz (RCA)** con responsable y estatus, y baja al detalle
por par de cuenta contable (~970 pares). Detalle: `[[ANALISIS_ARBOLES.md]]`, pieza K-MIG-005.

### 3.6 El oráculo (motor C)
- Primera especificación escrita: **ISR** (`S-FIS-001`), con **caso de oro** verificado
  (46.37 / 4.81 / 0.05). Falta el código, bloqueado por P-010.
- Reglas de cálculo ya documentadas: rendimiento vista, plazo fijo, y el redondeo por cálculo.

---

## 4. El plan (fases 0-9)

| Fase | Qué hace | Estado |
|------|----------|--------|
| 0 · Habilitación | accesos, `describe`, muestra limpia | en curso (accesos solicitados) |
| 1 · Universo comparable | llaves de correlación, ventanas, exclusiones (201, internas) | **diseñable ya** |
| 2 · ¿Se come todas? | faltantes A↔B | ejecutado por A/B (árbol); a re-verificar |
| 3 · Detalle consistente | rollforward, folios, reversas, **neteo diario = 0** | diseñable ya |
| 4 · Balanza | doble partida, continuidad | requiere matriz contable |
| 5 · Amarre auxiliar↔mayor | stock/flujo por producto-día | requiere Fase 3-4 |
| 6 · **Oráculo (¿calcula bien?)** | ISR, rendimiento, saldo — recálculo independiente | **spec ISR lista; código bloqueado por P-010** |
| 7 · Cross-motor / arbitraje | matriz A/B/C, clasificar cada diferencia | árbol A/B existe; falta el arbitraje C |
| 8 · Sesgo y materialidad | prueba de signo (redondeo), impacto anualizado | diseñable ya |
| 9 · Regresión y certificación | invariantes permanentes, veredicto go/no-live | — |
Detalle y dependencias: `[[PLAN_DE_VALIDACION.md]]` y el diagrama `[[PLAN_DE_VALIDACION_flujo.svg]]`.

**Decisión de método (nuestro challenge, ya acordada):** el "Golden Master" de casos
(cuadra / explicable / descuadre) lo **etiqueta el motor C recalculando desde la norma**, no un
modelo entrenado sobre las etiquetas del equipo A/B (eso lavaría su RCA y no probaría nada). Un
modelo/ML sólo se usa para *rutear* casuísticas, nunca para dar el veredicto de "calcula bien".

---

## 5. Qué podemos hacer AHORITA (sin esperar accesos)

Tenemos datos (F-013), reglas (F-009/F-010) y las llaves de ambos cores (F-011/F-012). Con eso:

1. **Arrancar el oráculo por ISR de inversiones** — el mayor gap (~27%). Recalcular el ISR desde la
   norma sobre el universo "en común" y **sobre el mismo saldo base**, para separar *defecto de ISR*
   de *defecto de saldo* (son cascada). *Requiere cerrar P-010* (parámetros normativos).
2. **Diseñar la Fase 1** (correlación y exclusiones) con las llaves reales: `id_external` para SPEI,
   llave sustituta para el resto; excluir sucursal 201 (fondeadora) y transacciones internas de plataforma.
3. **Construir el Golden Master etiquetado por C** — congelar N casos por casuística con el veredicto
   esperado (ya tenemos el primero: el caso ISR de F-010).
4. **Escribir las specs faltantes** (rendimiento vista/plazo) y dejar los tests listos.
5. **Prueba de sesgo de redondeo** sobre las distribuciones que ya tenemos (cuentas 24,910 +
   inversiones 4,969 + créditos 68).

---

## 6. Qué hallazgos existen

> **Separación honesta:** lo `[CONFIRMADO]` consta en fuente; lo demás son **candidatos** del árbol
> A/B **por verificar con el motor C**. Nada aquí es todavía arbitraje independiente.

### 6.1 Señales positivas (confirmadas por datos)
- **Crédito One Click (5004) cuadra 100%** en tasa, monto, fecha y monto pagado (7,619 en común).
  Es el dominio más sano — buen candidato para cerrar primero.
- **Existencia casi perfecta**: clientes, inversiones y créditos coinciden ~100% entre cores.

### 6.2 Diferencias materiales (candidatos a hallazgo — verificar con C)
| ref | dominio | qué se observa | # casos | clasificación probable |
|-----|---------|----------------|---------|------------------------|
| A13-ISR | FIS | Diff ISR retenido en inversiones (mayor gap de cálculo) | 4,988 (~27%) | mixto (saldo + redondeo) |
| A13-API | DAT/CAP | BUG del API duplica cuentas fantasma en Aurum | 2,977 | DEFECTO_CORE_NUEVO |
| A13-TASA2019 | CAP | Tasa del producto 2019 mal configurada en Aurum | 2,053 | DEFECTO_CORE_NUEVO (config) |
| A13-SALDO | CAP | Diff de saldo por ingesta / sin movimientos | 4,236 | DEFECTO ingesta (TO DO) |
| A13-SPEI-SAT | MOV | SPEI (in/out) que no llegan a satélites — **dinero real** | decenas | DEFECTO operativo |
| A13-REDONDEO | DEV | Redondeo en cuentas + inversiones + créditos | ~30k | ver sesgo (P-014) |

### 6.3 La cubeta incómoda — `DEFECTO_OPENFIN` (obligatorio abrirla)
| ref | qué | impacto |
|-----|-----|---------|
| F001-ISR / PAR-352 | ISR mal calculado históricamente en OpenFin | Jira PAR-352 cifra **$2,232,566.46** sin retención |
| F001-CLABE | OpenFin no valida CLABE en SPEI OUT → doble comisión | costo real evitable |

### 6.4 Del tracking Jira (proyecto PAR, 331 folios, RIESGO ALTO)
PAR-318 (689 créditos liquidados siguen activos), PAR-351 (1,261 créditos sin devengamiento en
Aurum), PAR-352 (ISR), PAR-337/343 (devoluciones SPEI). Nota transversal: el estatus "Finalizada"
**no** equivale a cierre evidenciado (avance verificable 20.8% vs operativo 54.2%).

---

## 7. Riesgo principal hoy

El mayor riesgo no es técnico sino **metodológico**: certificar sobre datos **ingestados** o sobre
la reconciliación **auto-reportada** del equipo A/B daría una falsa certeza. El valor que aportamos
—y la razón de existir del proyecto— es el **motor C**: recalcular de forma independiente los
cálculos con mayor diferencia (ISR, rendimiento, saldo) y **arbitrar** las causas, no adoptarlas.

El siguiente movimiento concreto: **cerrar P-010** (parámetros normativos del ISR) para codificar
`S-FIS-001` y emitir el primer veredicto independiente.
