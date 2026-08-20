# PROMPT CONSTRUCTOR — Validador Independiente del Motor C (auditor de AurumCore)

> **Cómo se usa este documento.** Es un **prompt de construcción**: se pega como primer mensaje en una
> sesión nueva de Claude Code (sobre este mismo repo) para que **construya la herramienta** que aquí se
> especifica. NO es el runtime del cálculo — el cálculo lo hace el **código determinista** que esta sesión
> generará. El LLM orquesta y explica; el veredicto lo da código reproducible.
>
> **Léelo junto con `CLAUDE.md`** (principio de veracidad, matriz de 3 motores, prohibiciones) y con
> **`40_validaciones/NORTE_VALIDACION.md`** (matriz maestra de qué se valida y dónde vive el dato).

---

## 0. Misión

Construir el **Validador Independiente** (en adelante, *VALIDADOR*): una herramienta que ejecuta, caso por
caso, las reglas de negocio/normativas **desde la fuente** (no desde el código de ningún core) y **devuelve
la verdad sobre AurumCore** — dónde cumple y dónde no. Tiene **doble propósito**:

1. **Pre-auditor nuestro (interno).** Lo corremos de forma adversaria **antes** de mostrar cualquier hallazgo
   a Finsus. Un hallazgo que no sobrevive su propio validador **no se reporta**.
2. **Producto final hacia Finsus.** Finsus (sus auditores/validadores: Alberto, Lluvia, INCO) lo corre con
   **sus propios accesos**, elige caso/motor y parámetros, y obtiene el mismo diagnóstico, reproducible y
   transparente (puede leer cada consulta).

**Regla de oro del diseño: NO all-pass.** El VALIDADOR existe para *encontrar* discrepancias, no para
firmarlas. Si un motor no se corrió, se marca **no-corrido**, jamás "OK". Ver §5.

---

## 1. Principios innegociables (heredados de `CLAUDE.md`)

1. **Determinismo.** Misma entrada → mismo resultado, siempre. Cero dependencia del LLM en la ruta de cálculo.
2. **Independencia (motor C).** El oráculo implementa la **norma/contrato**, nunca copia la lógica de openfin
   ni de AurumCore. Si para calcular hace falta mirar cómo lo hace un core → falta una **pieza de conocimiento**;
   se marca `[PENDIENTE]`, no se inventa.
3. **`decimal.Decimal` en todo cálculo monetario. Cero `float`.** Redondeo = **parámetro explícito** por caso
   (Trunc20/Trunc5/Ceil10/RoundHalfEven2/Round2 según la pieza K). Polars sirve para *mover y cruzar* datos
   (joins, set-diff, conteos), **no** para recalcular dinero.
4. **Violaciones como salida.** Cada caso devuelve **las filas que violan la identidad** (cero filas = pasa).
   Nunca un booleano ni un total "para comparar a ojo".
5. **Matriz de 3 motores A/B/C.** A = openfin (histórico, *no* es la verdad) · B = AurumCore (bajo prueba) ·
   C = oráculo. Se aplica la matriz de decisión de `CLAUDE.md §1` (=/≠ por motor → interpretación).
6. **Trazabilidad/evidencia.** Cada resultado guarda: caso, **parámetros**, **fecha de corte / snapshot**,
   **versión de la regla** (pieza K), **consulta exacta** usada, y las violaciones. Es la cadena probatoria.
7. **Tolerancias del charter (no negociables en caliente).** Identidades contables (familias B/C): **0.00**.
   Cálculo con redondeo (devengo): `≤ $0.01 por evento` **y ausencia de sesgo** (prueba de signo; sesgo ≠ 0
   estadístico = severidad 1 aunque cada diferencia sea de un centavo).
8. **Solo lectura** contra las bases. Ningún `INSERT/UPDATE/DDL`. Sesión con
   `SET default_transaction_read_only = on`.

---

## 2. Arquitectura a construir (3 capas)

```
validador/
├── db_connections.yaml         # credenciales (gitignored; formato en .example)
├── cli.py                      # interfaz: seleccionar caso/motor + parámetros (menú + flags)
├── catalogo/                   # CAPA 1 — QUÉ se valida (config declarativa, 1 archivo por caso)
│   ├── _schema.md              # plantilla de un caso (ver §4)
│   ├── ISR-01.yaml  ...        # un YAML por caso: regla, pieza K, tablas, extracción, oráculo, tolerancia
│   └── manifest.yaml           # índice + estado de cobertura de todos los casos
├── engine/                     # CAPA 2 — motor determinista de ejecución
│   ├── extract.py              # extracción BOUNDED por core (psycopg2, cohortes/ventanas) -> parquet
│   ├── warehouse.py            # carga a DuckDB (base analítica propia)
│   ├── compare.py              # cruce A/B/C con Polars; aplica identidad; devuelve VIOLACIONES
│   ├── oracle_runner.py        # invoca el oráculo (Decimal) del caso
│   └── runner.py               # orquesta: extract -> warehouse -> oráculo -> compare -> evidencia
├── oraculos/                   # motor C — funciones Decimal (REUTILIZAR las existentes, ver §6)
│   ├── isr.py                  # <- entrega_finsus/oraculo_isr.py
│   ├── rendimientos.py         # <- comparadores/oraculo_rendimientos.py (plazo/vista/saldo prom)
│   └── ...                     # nuevos por caso
├── extraccion/                 # SQL parametrizado por core (:param), BOUNDED
│   ├── aurum/*.sql
│   └── openfin/*.sql
├── reportes/                   # CAPA 3 — evidencia por corrida
│   ├── <caso>_<fecha>_<hash>/  # violaciones.parquet + manifiesto.json (params, snapshot, regla, query)
│   └── cobertura.md            # qué se corrió, qué no, qué está bloqueado (se regenera)
└── tests/                      # autopruebas de los oráculos (sin BD) + invariantes de regresión
```

**Flujo de un caso** (determinista):
1. `cli.py` selecciona el caso y pide/parametriza (fecha, cohorte, producto, tolerancia…).
2. `extract.py` corre el SQL **bounded** de cada core → `parquet` (nunca volcar tablas de 65 GB; usar cohorte
   como CTE `VALUES`, ventana de fechas, límites).
3. `warehouse.py` carga los parquet a **DuckDB** (archivo local = base analítica propia del auditor).
4. `oracle_runner.py` calcula **C** con `Decimal` para cada fila del universo del caso.
5. `compare.py` cruza A/B/C con **Polars**, evalúa la **identidad** del caso, y emite **violaciones.parquet**
   + resumen por matriz de decisión (=/≠). Corre la **prueba de sesgo** si el caso es de devengo.
6. Se escribe la **evidencia** (manifiesto con params/snapshot/regla/query) y se actualiza `cobertura.md`.

---

## 3. Interfaz (lo que Finsus opera)

- **Selección de caso/motor:** `python cli.py --caso ISR-01` o menú interactivo que lista el `manifest.yaml`
  agrupado por motor/dominio, con su estado.
- **Parámetros:** cada caso declara sus parámetros (fecha de corte, cohorte de cuentas, producto, base de días,
  UMA/tasa por año de causación, tolerancia). El CLI los pide con defaults del catálogo y permite override.
- **Apartados por caso (auto-generados desde el YAML):** (a) **descripción** de la regla y su fuente; (b)
  **tablas/vistas y llaves** por core; (c) **consultas** que se ejecutarán (mostradas antes de correr, para
  auditar); (d) **parámetros** elegibles; (e) **salida** esperada (qué significa cero filas).
- **Salida:** las **violaciones** (tabla), el veredicto por matriz A/B/C, y el path a la evidencia. Un `--dry-run`
  muestra las consultas y el plan sin tocar la BD.

---

## 4. El CATÁLOGO de casos (plantilla + siembra)

Cada caso es un archivo declarativo en `catalogo/`. **Plantilla obligatoria** (`_schema.md`):

```yaml
id: ISR-01
titulo: Retención de ISR al pago = regla normativa
motor: FIS
dominio: FIS
regla_ref: [K-FIS-002, K-FIS-004, S-FIS-001]     # piezas de conocimiento que la sustentan
severidad: 1                                      # 1 bloquea go-live · 2 bloquea ciclo · 3 documentar
tolerancia: {tipo: redondeo, max_evento: 0.01, prueba_sesgo: true}
parametros:
  - {nombre: cohorte, tipo: lista_cuentas, requerido: true}
  - {nombre: uma_anual, tipo: decimal, default: 42794.64, nota: "por año de causación"}
  - {nombre: tasa_ret, tipo: decimal, default: 0.90}
extraccion:
  aurum: extraccion/aurum/isr_al_pago.sql          # :cohorte
  openfin: extraccion/openfin/isr_diario.sql        # :cohorte  (para el motor A/comparación)
oraculo: oraculos/isr.py::isr_retenido               # C, Decimal
identidad: "C(fila) == B(isr_posteado)  ±tolerancia"  # lo que se afirma; viola quien no la cumple
matriz_esperada: "A≠B posible (modelo); B==C obligatorio"
estado: VALIDADO                                     # VALIDADO | PARCIAL | PENDIENTE | BLOQUEADO
cobertura_nota: "set desviación 3,236/3,236 = MODELO; B==C ±0.01"
```

**Siembra inicial del catálogo** (construir estos casos primero; el estado refleja lo ya avanzado):

| id | motor | regla | fuente | reutiliza | estado |
|----|-------|-------|--------|-----------|--------|
| **ISR-01** | FIS | ISR retención al pago = regla | K-FIS-002/004, S-FIS-001 | `oraculo_isr.py` (5/5), `V1_isr_al_pago_aurum.sql` | VALIDADO |
| **ISR-02** | FIS | Descuadre OF↔AC = MODELO (devengo vs pago) | K-FIS-003 | `V2_isr_devengo_openfin.sql`, `fase1_isr_desviacion.py` (3,236/3,236) | VALIDADO |
| **ISR-03** | FIS | Parámetros ISR vs norma | K-FIS-004 | tabla P-010 | VALIDADO |
| **REND-PLAZO** | DEV | Rendimiento plazo fijo al centavo | K-DEV-003 | `oraculo_rendimientos.py::rendimiento_plazo`, `V5` | VALIDADO (775/775) · **escalar muestra** |
| **REND-VISTA** | DEV | Interés/capitalización cuenta vista | K-DEV-002 v3 | `oraculo_rendimientos.py::rendimiento_vista` | PARCIAL · corrida viva **31-ago** (P-015) |
| **SALDO-PROM** | DEV | Saldo promedio `(saldo_ant+Σdía)/n` | K-DEV-002 v3 | `::saldo_promedio_rendimiento` | BLOQUEADO · logs del core (P-006) |
| **DIARIO-B** | MOV | Transaccional diaria OF↔AC (2:1/1:1) | K-MOV-001 v2 | `motor_b_diario.py` (−1.7%) | CORRIENDO · falta match instancia (P-016) |
| **GAPB-IDNC** | REG | Suspensión devengo / IDNC (≥90d, reserva 100%) | K-REG-001 v2 | `V3_gapB_idnc.sql`, ejemplo `123-1515-1837` | PARCIAL · cuadre en datos |
| **GAPC-PROSOFIPO** | REG | Cuota Prosofipo (motor faltante) | K-REG-002 v3 | `V4_gapC_prosofipo.sql` | HALLAZGO · cuota por fuera |
| **WRITEOFFS** | CTB/COL | Quitas/condonaciones/castigos = póliza por evento | F-023 §1 | — (nuevo) | PENDIENTE |
| **CRED-IO** | COL | Interés ordinario/moratorio de crédito | (falta pieza, P-006) | — | PENDIENTE |
| **CONTABLE-BC** | CTB | Doble partida + amarre auxiliar↔balanza (tol 0.00) | K-CTB-001 | `consultas_validacion.sql` | PENDIENTE |
| **COMPLETITUD** | MOV | "¿Se come todas?" (existencia OF↔AC por cohorte) | K-PRC-001, K-MIG-002 | árbol día cero | PARCIAL |

> El catálogo es **la fuente de verdad de QUÉ se valida**. Agregar un requisito = agregar un YAML (§7). Debe
> quedar sincronizado con `NORTE_VALIDACION.md` (misma nomenclatura y estado).

---

## 5. Integridad de auditoría — cómo se hace estructural el "NO all-pass"

El builder DEBE implementar estas cinco defensas (son el corazón del valor del producto):

1. **Violaciones-como-salida.** Ningún caso devuelve "pasó"; devuelve el *set* de filas que violan la identidad.
   "Cero violaciones" es un resultado, no un default.
2. **Matriz A/B/C.** Siempre se computa C independiente. `A=B=C`=OK; `A=B≠C`=defecto histórico de negocio
   (ambos cores mal, severidad máxima); `A≠B=C`=defecto de OF ya corregido; `A=C≠B`=defecto de AurumCore;
   `A≠B≠C`=regla mal especificada. Se reporta la celda, no un semáforo agregado.
3. **Manifiesto de cobertura.** `reportes/cobertura.md` lista **todos** los casos del catálogo con su último
   estado real: `corrido / no-corrido / bloqueado`, con fecha y parámetros. **No-corrido ≠ pasó.** Un caso sin
   correr NO puede pintarse verde en ningún tablero.
4. **Prueba de sesgo obligatoria en devengo.** Para casos con tolerancia de redondeo, correr **prueba de signo**
   sobre la distribución de diferencias C−B. Sesgo estadísticamente ≠ 0 = **severidad 1**, aunque cada diferencia
   sea de un centavo (charter §10).
5. **Regresión permanente.** Cada hallazgo confirmado se convierte en un **invariante nuevo** que queda en la
   batería (`tests/` + un caso o sub-check). La red de regresión sólo crece.

Además: **casos-trampa**. Sembrar al menos un caso con discrepancia *conocida* (p.ej. el rezago de UMA de feb,
C-001) para verificar que el VALIDADOR **la detecta** — si el tooling la deja pasar, el tooling está mal.

---

## 6. Activos existentes a REUTILIZAR (no reinventar)

- **Oráculos (Decimal, autoprobados):**
  `40_validaciones/entrega_finsus/oraculo_isr.py` (ISR, 5/5) · `40_validaciones/comparadores/oraculo_rendimientos.py`
  (plazo/vista/saldo promedio, 3/3). Portar a `validador/oraculos/` tal cual, con sus autopruebas.
- **Comparadores:** `comparadores/fase1_isr_desviacion.py` (set 3,236/3,236 MODELO) · `comparadores/motor_b_diario.py`
  (diario OF↔AC, DuckDB/Polars-ready) · `comparadores/fase1_isr_runner.py` (extractor read-only con cohorte-CTE).
- **SQL:** `entrega_finsus/V1..V5.sql` + `entrega_finsus/consultas_validacion.sql` (catálogo integral §0→§6) +
  `extraccion/*.sql` (aurum_/openfin_). Son la base de `validador/extraccion/`.
- **Conocimiento (las reglas):** `10_conocimiento/**` — cada caso cita su(s) pieza(s) K en `regla_ref`. Cuando
  una pieza sube de versión, marcar el caso "revisión requerida" (como en `30_oraculo/TRAZABILIDAD.md`).
- **Localizadores de BD:** `NORTE_VALIDACION.md §2` (producto real por `product_type_key`, flujos por
  `transaction_type`/referencia, llaves OF↔AC, migrado-vs-generado, réplica-no-T1) y
  `extraccion/REFERENCIA_queries_diario_finsus.md` (escenarios de Finsus, **referencia no verdad**).

---

## 7. Cómo se actualiza (cada vez que generemos un insight nuevo)

1. **Nuevo requisito/regla** → nueva pieza K en `10_conocimiento/` (si no existe) → **nuevo YAML** en
   `catalogo/` con su `regla_ref`, extracción, oráculo, identidad, tolerancia → alta en `manifest.yaml`.
2. **Regla que cambia** → subir versión de la pieza K → marcar los casos que la citan como "revisión requerida"
   → ajustar oráculo/identidad → re-correr → actualizar cobertura.
3. **Hallazgo confirmado** → convertirlo en **invariante de regresión** permanente.
4. Mantener `NORTE_VALIDACION.md`, `manifest.yaml` y `cobertura.md` **sincronizados** (misma nomenclatura/estado).

---

## 8. Plan de construcción (orden para la sesión que lo construya)

1. **Andamiaje:** estructura de `validador/`, `db_connections.example.yaml`, `cli.py` (menú + `--dry-run`),
   `warehouse.py` (DuckDB), utilidades de evidencia y `cobertura.md`.
2. **Portar oráculos** (`isr.py`, `rendimientos.py`) con sus autopruebas en `tests/` (deben dar 5/5 y 3/3 sin BD).
3. **Motor de ejecución** (`extract`/`compare`/`runner`) con el patrón bounded + matriz A/B/C + violaciones-como-salida.
4. **Casos ya validados primero** (ISR-01/02/03, REND-PLAZO) para probar el pipeline end-to-end contra BD.
5. **Casos en curso** (DIARIO-B, REND-VISTA, SALDO-PROM, GAPB-IDNC) con sus estados/bloqueos honestos.
6. **Defensas anti-all-pass** (§5): manifiesto de cobertura, prueba de sesgo, caso-trampa, regresión.
7. **Empaque para Finsus:** README de operación, `db_connections.example.yaml`, y verificación de que TODO es
   solo lectura y reproducible con sus accesos. Nota de seguridad: nunca credenciales en claro en el repo.

## 9. Restricciones duras (repetir al builder)

- **Solo lectura.** `decimal.Decimal` en dinero, **cero float**. Extracción **bounded** (jamás volcar tablas
  masivas). **No** copiar la lógica de ningún core en el oráculo. **No** all-pass: lo no-corrido se marca, no se
  aprueba. Toda afirmación con su fuente (pieza K/norma) y su evidencia (params/snapshot/query). Español de
  México, identificadores sin acentos ni ñ.
```
