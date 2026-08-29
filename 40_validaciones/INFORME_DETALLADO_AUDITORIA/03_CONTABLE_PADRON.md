# Informe Detallado — Transaccional / Contable / Padrón

> Ficha por punto: Alcance · Periodo · Universo y representatividad · Metodología + rationale · Santo y seña ·
> Conciliación. Solo lectura. Estos motores son de **identidad/completitud** (tolerancia 0.00 / A≥B), no de las tres
> granularidades. Corte 2026-08-26.

---

## V-20 · Motor B diario — completitud A vs B (transaccional)
- **Alcance — sí:** que **no falte** ninguna operación de openfin (A) en AurumCore (B), por día. **No:** cruce
  instancia-a-instancia (falta el crosswalk tipo-numérico OF↔AU; SOL-004); es cruce de **volumen** por clase/tipo.
- **Periodo:** **6 días, 2026-08-10 → 2026-08-18.** Ejecutado 2026-08-23 13:10.
- **Universo y representatividad:** **censo por día** — todas las ops de esos 6 días (21K–29K/día). Ampliable a más días.
- **Metodología + rationale:** se filtró `transaction.origin IS NULL` = generado por AurumCore (live), excluyendo lo
  ingestado, para comparar **solo lo que Aurum calculó**. Varios días seguidos para ver estabilidad.
- **Santo y seña:** A = openfin `public.<tabla>` normalizado por clase/tipo; B = `aurumcore.transaction_detail` ⋈
  `transaction` (`td.created::date=fecha AND t.origin IS NULL`). Motor `comparadores/motor_b_diario.py` (`--fecha`).
- **Conciliación:** **OF ≥ AU siempre** (delta +0.1% a +2.1%) → **0 faltantes** en B. Ej.: 08-14 OF 29,029 vs AU 29,004.
  `MOTOR_B_multidia_2026-08.txt`.

## V-21 · Contable — doble partida diaria
- **Alcance — sí:** que cada día Σ(débitos)+Σ(créditos) = **0.00** (tolerancia exacta, sin excepción). **No:** amarre
  auxiliar↔balanza por producto (familia C, pendiente); el mapeo `tipo_movimiento → cuenta` (gap de doc, D2).
- **Periodo:** **7 días, 2026-08-10 → 2026-08-16.** Ejecutado 2026-08-20 14:53.
- **Universo y representatividad:** **censo por día** — todos los asientos (17K–220K/día).
- **Santo y seña:** `aurumcore` pólizas del día (débitos/créditos por asiento); grano cuenta UUID vía DuckDB. Motor
  `comparadores/contable_bc.py` (`--desde`, `--dias`).
- **Conciliación:** **descuadre $0.00 en 7/7 días.** Montos diarios $84M–$1,301M. Alerta abierta (balanza D ~1-2%,
  producto 2001 −34%, `daily_account_balances` stale) → SOL de mapeo contable. `CONTABLE_BC_2026-08-20.txt`.

## V-22 · Contable — detalle transaccional (día completo)
- **Alcance:** insumo de amarre — todos los movimientos con saldos antes/después.
- **Universo y representatividad:** **96,235 movimientos = censo del día 08-14** (`transaction_detail`).
- **Santo y seña:** `_td_2026-08-14.csv` (`transaction_detail_id`, `created`, `source/target_address`,
  `source/target_prior/after_balance`, `debit/credit_amount`).

## V-23 · Cuentahabientes WSO2 ↔ padrón Aurum
- **Alcance — sí:** cobertura **bidireccional** identidad ↔ padrón. **No:** la semántica del ciclo de vida de identidad
  (por confirmar, P-017).
- **Periodo:** corte 2026-08-20. Ejecutado 2026-08-20 13:58.
- **Universo y representatividad:** **censo bidireccional** — todo el padrón vs todo WSO2. Resultados: Aurum→WSO2
  **20 huérfanos**; WSO2→Aurum **181,850** teléfonos no en Aurum; altas incompletas **295**; teléfono duplicado **1**.
- **Metodología + rationale:** `accountholder_number not like '201-%'` para aislar clientes (201=fondeadora, K-MIG-004).
- **Santo y seña:** `aurumcore.accountholder` vs WSO2 (`wso2_cuentahabientes.sql`); motor
  `comparadores/cuentahabientes_wso2.py`; sets de violación `cuentahab_*.csv`/`.parquet`.
- **Conciliación:** asimetría de retención esperada por ciclo de vida (P-017), por confirmar con Finsus.

---

## Nota transversal (para la auditoría)
- **Representatividad:** los censos (por día / por alcance) cubren **el 100% de su alcance**; los subconjuntos declaran
  su n, su total y su rationale (performance o validez del dato). **Ninguno es un muestreo estadístico con
  extrapolación** — la herramienta corre el universo completo con visto bueno (F-031 @00:30, SPEAKER_09).
- **Qué NO se valida** por punto está escrito en cada ficha (responde a F-031 @00:49: ver "qué se está tomando").
- Los denominadores de universo total quedaron **verificados en BD (2026-08-28)** — ver `00_INDICE.md` §3. No cambian
  ninguna conclusión; solo precisan el % (p.ej. V-01 pasó de "100% de lo live" a **~39.6%** por metodología, declarado).
