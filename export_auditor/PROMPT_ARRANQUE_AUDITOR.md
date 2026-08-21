# PROMPT DE ARRANQUE — Auditor / Validador Independiente (pegar como primer mensaje)

> Pega este mensaje completo en una sesión nueva de Claude Code, en el repo del auditor, con la carpeta
> `export_auditor/bundle/` (o el nombre que le hayas dado) ya copiada en el proyecto. Este prompt te dice
> QUÉ construir, con qué **guardrails** y **directrices**, usando el **NORTE** como fuente de verdad.

---

## 0. Qué vas a construir
El **Validador Independiente del motor C** (auditor de AurumCore): una herramienta **determinista** que ejecuta,
caso por caso, las reglas de negocio/normativas **desde la fuente** (no desde el código de ningún core) y
**devuelve la verdad sobre AurumCore** — dónde cumple y dónde no. Doble uso: (1) **pre-auditor** interno; (2)
**entregable a Finsus** para que sus auditores lo corran con sus accesos.

## 1. Empieza leyendo estos archivos del paquete (en este orden)
1. **`PROMPT_CONSTRUCTOR_VALIDADOR.md`** — el brief de construcción (arquitectura de 3 capas, catálogo, plan por fases).
2. **`NORTE_VALIDACION.md`** — **FUENTE ÚNICA**: panorama + **catálogo de casos** (qué se valida, tablas, filtros,
   estado). El auditor **espeja** estas filas; no mantiene un catálogo paralelo.
3. **`REFERENCIA_TABLAS_POR_CASO.md`** — por cada caso: base, tablas, columnas, filtros, llaves, oráculo, script.
4. **`PROMPT_SYNC_AUDITOR.md`** — cómo se propaga cada novedad (fuente única + export).
5. **`SOLICITUDES_FINSUS.md`** — lo que está bloqueado por insumos de Finsus (no lo inventes; márcalo pendiente).
6. Oráculos (`oraculo_isr.py`, `oraculo_rendimientos.py`), comparadores (`motor_b_diario.py`, `contable_bc.py`,
   `cuentahabientes_wso2.py`, `validate_plazo_origin.py`, `isr_live_nativo.py`, `fase1_isr_*`), SQL (`V1..V5`,
   `consultas_validacion.sql`, `wso2_cuentahabientes.sql`), planes y `10_conocimiento/` (las reglas / piezas K).

---

## 2. GUARDRAILS (reglas duras — no negociables)
1. **Veracidad. NUNCA inventes.** Toda afirmación lleva estado: `[CONFIRMADO]` (con cita a fuente),
   `[INFERIDO]`, `[SUPUESTO]`, `[PENDIENTE]`, `[CONTRADICCION]`. Sin cita no puede ser CONFIRMADO. No cites
   artículos normativos sin verificarlos. No resuelvas contradicciones por tu cuenta: escálalas.
2. **Solo lectura** a las bases. Cero `INSERT/UPDATE/DDL`. Abre la sesión con
   `SET default_transaction_read_only = on` y `statement_timeout`.
3. **`decimal.Decimal` en TODO cálculo monetario. Cero `float`.** El modo de redondeo es parámetro explícito
   (Trunc20/Trunc5/Ceil10/RoundHalfEven2/Round2 según la pieza K). Polars/DuckDB para mover y cruzar datos; el
   dinero se recalcula con Decimal.
4. **Oráculo independiente (motor C).** Implementa la **norma/contrato**, NUNCA copia la lógica de openfin ni de
   AurumCore. Si para calcular necesitas mirar cómo lo hace un core → falta una pieza de conocimiento → márcala
   `[PENDIENTE]`, no la inventes.
5. **Violaciones como salida.** Cada caso devuelve **las filas que violan la identidad** (cero filas = pasa).
   Nunca un booleano ni un total "a ojo".
6. **NO all-pass.** Cobertura explícita: **lo no-corrido se marca no-corrido, JAMÁS "OK"**. Prueba de sesgo en
   devengo (sesgo ≠ 0 = severidad 1 aunque cada diferencia sea de un centavo). Siembra un **caso-trampa** (una
   discrepancia conocida) para verificar que el tooling la detecta.
7. **Matriz de 3 motores A/B/C.** A = openfin (histórico, no es la verdad) · B = AurumCore (bajo prueba) ·
   C = oráculo. Reporta la celda de la matriz, no un semáforo agregado.
8. **Tolerancias.** Identidades contables: **0.00, sin excepción**. Cálculo con redondeo: `≤ $0.01 por evento`
   **y ausencia de sesgo**.
9. **Seguridad.** NUNCA credenciales en claro en el repo (`db_connections.yaml` gitignored; usa
   `db_connections.example.yaml`). Sin PII a git. Sin resultados (`_resultados/`, `*.parquet`, CSV de datos) al repo.
10. **Extracción bounded.** Cohortes/ventanas de fecha. NUNCA vuelques tablas masivas (`iv_payment_plan` 36.7M,
    `isr_diario` 171.8M, `detalle_auxiliar` 65 GB).

---

## 3. DIRECTRICES METODOLÓGICAS (lo aprendido — aplícalo)
- **Delimitador "Aurum nativo/vivo".** `transaction.origin` tiene **semántica mixta** (unos valores = fuente de
  **migración** como `FINSUS_INVESTMENT`; otros = **canal/producto vivo** como `DIMO`); y `origin IS NULL` aparece
  desde antes del cutover (periodo **shadow**). Regla:
  - Para validar el **CÁLCULO** de un motor (¿Aurum computa bien?): usa **lo generado por Aurum** = `origin is null`
    donde la tabla no tenga tags de canal (p.ej. `iv_payment_plan` solo tiene FINSUS/null → limpio; ISR-retención
    100% null → limpio). El periodo shadow es el **mismo motor**, así que es válido comparar.
  - Para **completitud/transaccional** (¿le llegó todo post-primario?): usa **`created >= cutover (2026-08-02/03)`**.
  - **Confirmar la taxonomía de `origin` con Finsus** (SOL-004) antes de tratarlo como definitivo.
- **AurumCore persiste el AUXILIAR, no los agregados derivados** (balanza/mayor, tasas contratadas, saldo base
  punto-en-tiempo). Por eso varias validaciones de **cálculo vivo** requieren los **logs del CORE (SOL-003)**;
  márcalas BLOQUEADAS, no las fuerces con aproximaciones que se presenten como validación.
- **Cada hallazgo confirmado → invariante de regresión permanente** (la batería solo crece).
- **Reutiliza los oráculos/comparadores del paquete** (no reinventes). Cuando una pieza K sube de versión, marca
  sus dependientes "revisión requerida".

---

## 4. Orden de construcción (fases)
1. Andamiaje: estructura `validador/`, `db_connections.example.yaml`, CLI (menú + `--dry-run`), DuckDB, evidencia,
   `cobertura.md`.
2. Portar oráculos (`isr.py`, `rendimientos.py`) con autopruebas (deben dar 5/5 y 3/3 **sin BD**).
3. Motor de ejecución (extract bounded → warehouse DuckDB → oráculo Decimal → compare Polars → violaciones) + matriz A/B/C.
4. Casos ya validados primero (ISR-01/02/03, REND-PLAZO) end-to-end contra BD; luego los en curso con su estado honesto.
5. Defensas anti-all-pass (§2.6): manifiesto de cobertura, prueba de sesgo, caso-trampa, regresión.
6. Empaque para Finsus (README, `db_connections.example.yaml`, todo solo lectura y reproducible).

## 5. Regla de oro
El objetivo es un **diagnóstico confiable** de AurumCore — **la verdad, no un "todo pasa"**. Un caso sin correr
no es verde. Una aproximación no es una validación. Un hallazgo que apunta a defecto del core **no se suaviza**.
