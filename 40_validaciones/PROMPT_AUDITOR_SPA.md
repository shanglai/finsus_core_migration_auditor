# PROMPT — Construcción del SPA del Auditor + Agente Conversacional (motor C)

> Este documento es el **brief de construcción** para la sesión del auditor independiente. Complementa
> `PROMPT_CONSTRUCTOR_VALIDADOR.md` (arquitectura del validador) y `PROMPT_ARRANQUE_AUDITOR.md` (guardrails).
> Lee además `DOSSIER_MOTORES_ORACULO_C.md` (el cerebro), `NORTE_VALIDACION.md`, `INDICE_PRODUCTOS_PROCESOS.md`
> y `COMPARACION_C_vs_DOC.md`. Todos vienen en el bundle (`export_auditor/ensamblar.py`).

---

## 0. Rol y objetivo
Eres el **auditor independiente** (tercero). Ya existen los **oráculos (motor C)** en `40_validaciones/comparadores/`
y `entrega_finsus/` (Python, `decimal.Decimal`). Tu trabajo es **construir un SPA (tablero web) que ejecute cada
motor contra la BD, muestre el resultado con transparencia total, y un agente conversacional que lo explique**.

Principio rector (NO negociable): cada validación **devuelve las filas que violan la regla**. El SPA muestra el
**% de match** y, sobre todo, **los NO conformes** con su explicación. Verde ≠ auto-aprobado.

---

## 1. Qué construir (dos entregables)
1. **SPA (Single-Page App)** con **navegación de dos niveles**:
   - **Hoja inicial (home) = galería de cards**, una por cada caso/motor de validación. Cada card muestra el estado
     (✅/◐/🔒/⚪), el nombre, el % de match resumido y su categoría. **Click en una card → su pantalla individual.**
   - **Menú de hamburguesa (☰)** que lista los casos **agrupados por categoría** (Captación · Fiscal · Crédito ·
     Transaccional/Contable · Padrón); seleccionar uno navega directo a su pantalla. El menú permite filtrar la
     galería por categoría y saltar entre casos sin volver al home.
   - **Pantalla individual por caso** (la "card" a detalle, §3): fórmula, contra qué se valida, conteo, las **tres
     granularidades de cuadre** (§3.1), el scatterplot con foco en no-conformes, y la explicación.
   - **Botón "Ejecutar" (invoca nuestro backend)**: en cada pantalla (y opcionalmente uno global "ejecutar todo"),
     un botón dispara el motor del backend (los oráculos/comparadores). Estados visibles: **inactivo → "en
     ejecución" (spinner + progreso) → "terminé" (✔, con timestamp de la corrida)**. Mientras corre, deshabilita el
     botón y muestra el avance; al terminar, refresca la card con el resultado y habilita de nuevo. Ver §2 (contrato).
2. **Agente conversacional** — un chat que explica todo (fórmulas, procesos, por qué un no-conforme, qué desbloquea
   cada SOL), alimentado por `DOSSIER_MOTORES_ORACULO_C.md` + NORTE + INDICE + COMPARACION.

---

## 2. Arquitectura
```
  [ BD AurumCore (read-only) ]      [ feeds de logs pre-extraídos (CSV) ]
              │                                   │
              ▼                                   ▼
     backend/runner.py  ── ejecuta cada motor ──►  resultados/<motor>.json
              │                                   (métricas + puntos scatter + muestras no-conformes)
              ▼
     SPA (frontend)  ── lee los .json ──►  cards + scatterplots + chat
              │
              ▼
     agente conversacional (lee DOSSIER + NORTE + INDICE)
```
- **Backend `runner.py`**: por cada motor, corre la validación (reusando los oráculos existentes), y **escribe un
  JSON** con: `id`, `nombre`, `categoria`, `formula`, `valida_contra` (doc/config/…+fuente), `estado`, `n_comparadas`,
  `n_ok`, **`match`** (las tres granularidades, ver abajo; `pct` puede ser `null`), **`sesgo`**, `tolerancia`,
  **`cobertura`** (`"config" | "datos" | "sin_cruce"`), **`evidencia_config`** (texto, p.ej. "lc_reserve_ifrs 37/37"),
  **`ejecutable`** (bool) + **`motivo_no_ejecutable`**, `puntos` (para el scatter: `[{x, y_c, y_b, delta, ok,
  id_muestra}]`, **muestreado** si son muchos), `no_conformes` (top-N con su delta y motivo),
  `explicacion_no_conformes` (texto), y `ejecutado` (timestamp mtime de la corrida). Ver §3.2 para el despliegue
  cuando no hay `pct`.
  - **`match`** se produce con `comparadores/tolerancias.py` (`resumen_tolerancias(pares)`): devuelve las tres
    escalas `1e-8` / `1e-5` / `centavo` con `pct` y `n_ok`, más `sesgo` (prueba de signo). El SPA las muestra como
    en §3.1. Ver `MATRIZ_TOLERANCIAS.md` para la lectura del escalón entre granularidades.
- **Contrato de ejecución (botón "Ejecutar")**: el frontend llama un endpoint del backend (p.ej. `POST /run/<motor>`
  o `POST /run/all`). El backend responde **de inmediato** con `{job_id, estado:"en_ejecucion"}` y corre el
  comparador en segundo plano; el frontend hace **poll** (`GET /run/<job_id>`) o escucha SSE hasta
  `estado:"terminado"` (o `"error"`), y entonces recarga el `resultados/<motor>.json`. Estados del botón:
  `inactivo → en_ejecucion (spinner + % avance si el comparador lo emite) → terminado (✔ + timestamp)`. **Nunca**
  bloquear la UI; deshabilitar el botón mientras corre. El backend fuerza **read-only** en la BD.
- **Los logs los trae otro proceso**: el runner NO hace SSH en vivo. Lee los **feeds ya extraídos a CSV** por
  `log_extractor.py` / `barrido_average_balance.py` (en `_resultados/`, p.ej. `credito_provision_feed_*.csv`,
  `yield_feed_*.csv`). El SPA marca los motores que dependen de logs y su fecha de feed (los `🔒` no traen botón
  "Ejecutar" activo hasta que exista el feed / la corrida viva del 31-ago).
- **Frontend SPA**: lee los `resultados/<motor>.json` y renderiza. No necesita conexión directa a la BD.

---

## 3. Especificación de la "card" por motor
Cada motor es una tarjeta (resumida en el home; completa en su pantalla individual) con:
- **Encabezado**: nombre + badge de estado (✅ validado / ◐ parcial / 🔒 bloqueado / ⚪ sin cruce) + **categoría**.
- **Fórmula**: en bloque monoespaciado o KaTeX si está disponible (sin dependencias externas → inline). Ej. ordinario:
  `Interés = Capital × (tasa/100) × (días/360)`.
- **Valida contra**: chip con color por tipo — `doc` (azul, + página), `config` (verde, = config real de Aurum),
  `norma` (morado), `inferencia` (gris, ojo: por confirmar). Ejemplo IFRS 9: chip `config` "= lc_reserve_ifrs 37/37".
- **Conteo**: comparadas · match · no-conformes · sin dato.
- **Cuadre en tres granularidades** (§3.1).
- **Scatterplot** (ver §4).
- **No-conformes**: lista corta (top por |delta|) con `id_muestra`, C, B, delta, y **motivo** (etiquetado:
  `linaje` / `data-sourcing` / `bloqueo` / `defecto` / `redondeo`).
- **Botón "Ejecutar"** → invoca el backend (§2, estados en ejecución/terminé) · **Botón "explicar"** → abre el agente
  con el contexto de ese motor.

### 3.1 Cuadre en tres granularidades (obligatorio mostrarlas y explicarlas)
Cada motor de cálculo muestra **tres barras** de % de match, del bloque `match` del JSON (`tolerancias.py`):
- **1e-8** (8 decimales) — exactitud aritmética estricta · **1e-5** (5 decimales) — precisión intermedia ·
  **centavo** ($0.01) — tolerancia de negocio.
- Junto a las barras, un micro-texto con la **lectura del escalón**: p.ej. moratorio `81.1% → 95.7%` = "residuo
  sub-centavo = granularidad del snapshot, no defecto". Y una **bandera de sesgo** (verde "sin sesgo" / rojo "sesgo
  sistemático — severidad 1") del campo `sesgo`.
- Un **tooltip "¿qué significan?"** que explique las tres granularidades (texto en `MATRIZ_TOLERANCIAS.md`).
- Los motores de identidad/completitud (Contable, Motor B) muestran su tolerancia propia (`0.00` exacto / `A ≥ B`),
  no las tres barras — indícalo en la card.

### 3.2 Cuando NO hay porcentaje — no escondas cobertura buena (problema-espejo)
Este es el error que el tablero existe para evitar, pero **en la otra dirección**: así como nunca pinta de verde lo
que no corrió, **tampoco puede esconder validación real detrás de un guion**. Ocultar evidencia buena es tan
deshonesto como inventar la que no existe. Las etiquetas miden ejes distintos y **juntas** se leen como "aquí no hay
nada" — hay que separarlas:
- `parcial` = estado del **conocimiento** (mecánica confirmada, falta cerrar alcance) · `sin cruce` = **de dónde
  salió el número** (este tablero no lo corrió) · `—` = no hay % que mostrar · **botón apagado** = aún no se mapeó
  un caso ejecutable. **Ninguna dice "no validado"**, pero el conjunto lo sugería.

**Regla de despliegue cuando `pct` es nulo:**
1. Si `valida_contra = config` (el oráculo reproduce la **tabla de configuración del propio core**), la galería y la
   card **NO** muestran `—`: muestran la **evidencia de config**. Ej. IFRS 9:
   **"Validado contra la configuración real del core — `lc_reserve_ifrs` 37/37 · `lc_risk_stage` etapas exactas"**.
   El detalle explica **por qué no hay %** (una config no es una cohorte) y **por qué eso NO es falta de validación**
   — de hecho es **más fuerte que un %**, porque un % depende de qué cohorte elegiste y la config no.
2. Si de verdad **no hay cruce** (ni datos ni config), la card lo dice sin adornos: **"Eso no es un pase."**
3. **El botón apagado dice la verdad completa:** no es que el motor "no se pueda validar", es que **aún no se le
   construyó un caso ejecutable**. Texto sugerido: *"Sin caso ejecutable todavía — motor validado por {config/doc};
   ver detalle."* (nunca un botón muerto sin explicación).

**Campos de apoyo en el JSON** para esto: `pct` puede ser `null`; añade `cobertura` (`"config" | "datos" | "sin_cruce"`),
`evidencia_config` (texto, p.ej. "lc_reserve_ifrs 37/37"), y `ejecutable` (bool + `motivo_no_ejecutable`). La card
elige el texto según `cobertura`, no según si hay `pct`.

### Motores a incluir (del DOSSIER)
Plazo · Vista* · Saldo promedio* · ISR · ISR-vivo* · Crédito ordinario · Crédito moratorio · Crédito días ·
IVA · GAT inversión · IFRS 9 etapas+% · Amortización · CAT · Motor B · Contable · WSO2.
(* dependen de la corrida del 31-ago / logs → mostrar como 🔒 con la razón.)

---

## 4. El scatterplot (lo más importante — foco en no-conformes)
- **Eje X**: una magnitud del caso (p.ej. monto/capital/saldo, o índice). **Eje Y**: `delta = C − B` (o C vs B en
  dos series). **Meta visual**: los conformes se agrupan en `delta≈0`; los **no-conformes saltan** y se pintan en
  **rojo** (los conformes en verde tenue).
- **Interacción**: hover muestra `id_muestra`, C, B, delta, motivo; click abre la explicación en el agente.
- **Controles**: filtro "solo no-conformes", escala log (para CAT/GAT con outliers extremos), y un umbral de
  tolerancia ajustable (p.ej. 1e-8 / 0.01) que recolorea en vivo.
- **Sin librerías externas por CDN** (CSP): dibuja el scatter con SVG/Canvas propio, o incluye la librería inline.
- **Muestreo honesto**: si hay millones de puntos, muestrea, pero **incluye SIEMPRE todos los no-conformes** y
  **rotula cuántos se omitieron** (no ocultes cobertura).

---

## 5. Agente conversacional
- **Fuente de conocimiento**: `DOSSIER_MOTORES_ORACULO_C.md` (principal) + NORTE + INDICE + COMPARACION + las piezas K
  de `10_conocimiento/`. Cárgalas como contexto/base de recuperación.
- **Qué responde**: "¿cómo se calcula el moratorio?", "¿por qué el CAT no cuadra a volumen?", "¿qué desbloquea el
  Manual (SOL-015)?", "¿contra qué se validó el IFRS 9?", "explícame este punto rojo del scatter".
- **Estilo**: cita fórmula + fuente (doc/página o config) + resultado + no-conformes. Español de México, directo.
  **Nunca inventa**: si un dato no está en el DOSSIER/fuentes, lo dice y remite al SOL correspondiente.
- Si el entorno lo permite, conéctalo a un modelo; si no, un modo "explicación estática" que renderiza la sección
  del DOSSIER del motor seleccionado ya aporta el 80%.

---

## 6. Fuentes de datos y credenciales
- **BD read-only**: el auditor usa **sus propias credenciales** en `db_connections.yaml` (gitignored; formato en
  `db_connections.example.yaml`). SIEMPRE `SET default_transaction_read_only`/`set_session(readonly=True)`.
- **Feeds de logs**: CSV pre-extraídos (otro proceso los trae). El runner los lee de una carpeta configurable.
- **Nunca** credenciales ni PII al frontend. El JSON de resultados lleva **agregados + muestras anonimizadas**
  (ids truncados), no padrones completos.

---

## 7. Guardrails (heredados del arranque del auditor)
1. Read-only estricto en la BD. 2. `decimal.Decimal` en todo cálculo (los oráculos ya lo hacen). 3. Cada motor
reporta **las filas que violan la regla**; los no-conformes se explican, no se ocultan. 4. Distinguir
**defecto / linaje / data-sourcing / bloqueo / redondeo** en cada no-conforme. 5. Marcar lo `inferencia` como
por-confirmar (no como hecho). 6. No PII al front. 7. Verde ≠ aprobado; el dictamen lo emite el humano.

---

## 8. Stack sugerido (elige, prioriza simplicidad y autocontenido)
- **Backend**: Python (los oráculos ya son Python). Un `runner.py` que importa cada `oraculo_*` y escribe JSON.
  Reusa los patrones de `validate_plazo_origin.py`, `motor_b_diario.py`, `oraculo_credito.py` (cruces ya escritos).
- **Frontend**: un SPA autocontenido (HTML+JS único, sin dependencias por CDN) que hace fetch de los JSON. Scatter
  en Canvas/SVG propio. Si usas un framework, que compile a estático.
- **Alternativa rápida**: Streamlit/Dash si el auditor prefiere Python puro end-to-end (pero pierde "SPA" real;
  documenta el trade-off).

---

## 9. Entregables
1. `backend/runner.py` — ejecuta los N motores, escribe `resultados/<motor>.json`.
2. `spa/` — el tablero (cards + scatterplots + chat).
3. `resultados/` — los JSON (regenerables).
4. `README` — cómo correr (creds, feeds, `python runner.py`, abrir el SPA).
5. El agente conversacional cableado al DOSSIER.

## 10. Orden sugerido de construcción
1. `runner.py` para **1 motor sólido** (plazo o crédito ordinario) → JSON (con `match` de las 3 granularidades vía
   `tolerancias.py`) → card. Prueba end-to-end.
2. **Shell de navegación:** home = galería de cards + menú hamburguesa por categoría + ruteo a la pantalla individual.
3. **Botón "Ejecutar"** cableado al backend con los estados `en ejecución → terminé` (§2), primero en 1 motor.
4. Generaliza a los demás motores (tabla de config de motores → loop); cada card con sus 3 barras + bandera de sesgo.
5. Scatterplot con foco en no-conformes + controles (umbral de tolerancia recolorea en vivo).
6. Agente conversacional sobre el DOSSIER.
7. Marca los 🔒 (vista/saldo promedio/ISR-vivo) con su razón y la fecha de desbloqueo (31-ago); su botón "Ejecutar"
   queda inactivo hasta que exista el feed / la corrida viva.

Antes de construir cualquier **caso ejecutable nuevo**, lee la §11.

---

## 11. Guía para construir casos ejecutables (convenciones, sesgo y alcance)
Esta guía existe porque las mismas tres cosas se redescubren caso tras caso. Aplícalas **desde el inicio**; no son
opcionales, están confirmadas en el proyecto (ver punteros al final).

### 11.1 Independencia — de dónde salen los parámetros (lo más importante)
El oráculo (C) es **árbitro independiente**. Sus parámetros —%, tasa, base de días, tramos— salen de la **fuente
independiente** (norma / GTM / contrato / doc oficial), **NO de la tabla de configuración del core que estás
probando**.
- Ejemplo IFRS 9 E3: el `pct(días_mora)` (75/90/100) de C sale de las **Tablas del GTM**, no de `lc_reserve_ifrs`.
  Leer el % de la config del core y compararlo contra el mismo core probaría que **es consistente consigo mismo**, no
  que **aplica la norma**. Que además `lc_reserve_ifrs` coincida (37/37) es un **resultado** (fuerte, ver §3.2), **no
  el método.**
- Regla: si para construir el caso necesitas leer un parámetro del core, **detente** — ese parámetro debe venir de la
  fuente. Si la fuente no lo tiene, es `[PENDIENTE]`, no lo tomes del core.

### 11.2 Convenciones de cálculo confirmadas (heredarlas, no redescubrirlas)
- **Redondeo half-up por evento.** Finsus confirmó (24-ago) que el core redondea **half-up en cada evento**. Todo
  oráculo debe redondear igual (`ROUND_HALF_UP`) **antes** de comparar contra B. Los módulos existentes ya lo hacen;
  un caso nuevo **también** — es la causa #1 de sesgo espurio.
- **Base de días por producto.** 360 o 365 **según el esquema** — no asumir. Confírmala de los datos/esquema
  (p.ej. VISTA = 360·dt-mes; inversión plazo = 360; ISR = 365). Probar las convenciones y reportar cuál ajusta es
  válido (no-circular).
- **`decimal.Decimal` en todo cálculo monetario. Cero `float`.** El modo de redondeo es explícito, nunca default.

### 11.3 Playbook del sesgo — antes de gritar "severidad 1"
`tolerancias.py` corre una prueba de signo. Cuando marca **sesgo** (diferencias del mismo signo, sub-centavo),
**no lo reportes como defecto todavía** — pártelo en este orden (es lo que ya pasó 3 veces, y las 3 el sesgo era
del método, no de AurumCore):
1. **¿Aplicaste half-up por evento como el core?** Si tu C no redondea igual, ese es el sesgo. (En IFRS 9 E3 explicó
   la mitad: 5,133 → 2,381.)
2. **¿Es precisión de la base?** Si lees el insumo (`capital_venc`, `SPM`, capital) a N decimales y el core calculó
   con más, el residual sub-centavo es **granularidad del snapshot** — **patrón P-019** (mismo en moratorio y en
   VISTA-`dt`). Verifícalo: el % / la tasa **implícita** en las filas que fallan sale correcta (p.ej. 75.0000 /
   90.0001 / 100.0000) ⇒ la fórmula está bien, la diferencia es la base. **No es defecto de Aurum.**
3. **Solo si sobrevive a (1) y (2) y es material** → entonces sí es candidato a defecto del core; escálalo.

**Regla:** *un sesgo sub-centavo de un solo signo es, por defecto, tu redondeo o la precisión de la base — no un
defecto de Aurum — hasta descartar ambos.* La bandera roja **se muestra igual** (ocultarla sería peor, §3.2); lo que
cambia es la **lectura escrita** junto a ella: "sesgo del método (redondeo/base), no del core".

### 11.4 Declaración de alcance — escribe lo que dejas fuera
Cubre solo lo que la fuente sustenta. Lo que quede fuera **se escribe en el caso**, con el motivo:
- Ej. IFRS 9: solo **E3 consumo zona no marginada**; E1/E2 amortizando y la composición de `reserva_int` dependen de
  fórmulas **aún en el documento pendiente**; comercio/reestructurado necesitan las 9 tablas. Cubrirlos hoy exigiría
  **inventar la base** → no se hace (CLAUDE.md §3).
- El caso muestra el alcance cubierto **y** el declarado-fuera; el botón/badge no insinúan más cobertura de la real.

### 11.5 Punteros (dónde vive cada regla confirmada)
- Half-up y parámetros: `S-FIS-001`, `COMPARACION_C_vs_DOC.md`, los `oraculo_*.py`, `ESTADO_RESUMEN.md`.
- Precisión de base / snapshot / P-019: `COMPARACION_C_vs_DOC.md`, `DOSSIER_MOTORES_ORACULO_C.md`,
  `MATRIZ_TOLERANCIAS.md`, `tolerancias.py`, `K-DAT-002`.
- Tres granularidades y prueba de sesgo: `MATRIZ_TOLERANCIAS.md`, `comparadores/tolerancias.py`.

**Recuerda:** el valor del tablero está en los **no-conformes bien explicados**, no en los verdes. Ese es el
diferenciador del tercero independiente.
