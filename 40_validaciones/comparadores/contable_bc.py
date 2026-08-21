"""
CONTABLE-BC — Validaciones contables sobre AurumCore (familias B y C del charter 10).

Tercero independiente. SOLO LECTURA. Devuelve las filas que VIOLAN la identidad (cero = pasa).
Tolerancia contable = 0.00 (sin excepcion).

Modelo (AurumCore no guarda poliza/balanza como tabla; el asiento vive en transaction_detail):
  - transaction_detail: source_accounting_account (debita), target_accounting_account (acredita),
    debit_amount (NEGATIVO), credit_amount (POSITIVO). Cada fila = 1 asiento balanceado.
  - cat_accounting_account: plan de cuentas (accounting_id, account_type, account_nature).

Familias implementadas aqui:
  B1 — Doble partida diaria: Sum(debit)+Sum(credit) = 0 por dia (tol 0.00).
  B2 — Naturaleza / rollforward por cuenta contable: neto por cuenta y dia.
  C  — (pendiente) amarre auxiliar<->balanza por producto/dia.

Uso:  python contable_bc.py [--desde YYYY-MM-DD] [--dias N]
"""
import sys, argparse, yaml, psycopg2, time
from decimal import Decimal
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load(open(RAIZ / "db_connections.yaml", encoding="utf-8"))
RES = RAIZ / "40_validaciones" / "_resultados"; RES.mkdir(exist_ok=True)


def conn():
    C = CFG["aurum"]; kw = {k: C[k] for k in ("host","port","dbname","user","password","sslmode") if k in C}
    for a in range(3):
        try:
            c = psycopg2.connect(**kw); c.set_session(readonly=True); return c
        except Exception as e:
            print("retry", a, str(e).splitlines()[0][:50]); time.sleep(4)
    raise RuntimeError("no conecta aurum")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="2026-08-10")
    ap.add_argument("--dias", type=int, default=7)
    a = ap.parse_args()
    cn = conn(); cur = cn.cursor(); cur.execute("SET statement_timeout='240s'")

    print("=== CONTABLE-BC · AurumCore (familias B/C, tol 0.00) ===\n")

    # --- B1: doble partida diaria (violaciones = dias con descuadre != 0) ---
    cur.execute("""
      select created::date dia, count(*) asientos,
             round(sum(debit_amount),2) sum_debit, round(sum(credit_amount),2) sum_credit,
             round(sum(coalesce(debit_amount,0)+coalesce(credit_amount,0)),2) descuadre
      from aurumcore.transaction_detail
      where created::date >= %s and created::date < (%s::date + %s * interval '1 day')
      group by 1 order by 1
    """, (a.desde, a.desde, a.dias))
    rows = cur.fetchall()
    print("B1 — Doble partida diaria (descuadre = Sum(debit)+Sum(credit); debe ser 0.00):")
    print(f"  {'dia':<12} {'asientos':>9} {'Sum debit':>16} {'Sum credit':>16} {'descuadre':>12}")
    viol_b1 = 0
    for dia, n, sd, sc, desc in rows:
        flag = "" if desc == Decimal("0.00") else "  <-- VIOLA"
        if desc != Decimal("0.00"): viol_b1 += 1
        print(f"  {str(dia):<12} {n:>9,} {sd:>16,.2f} {sc:>16,.2f} {desc:>12,.2f}{flag}")
    print(f"  => dias que violan doble partida: {viol_b1} de {len(rows)}")

    # --- B2: rollforward/naturaleza — cuentas con mayor movimiento neto en el ultimo dia ---
    ult = rows[-1][0] if rows else a.desde
    cur.execute("""
      with mov as (
        select target_accounting_account acc, sum(credit_amount) cr, 0 db from aurumcore.transaction_detail
          where created::date=%s and target_accounting_account is not null group by 1
        union all
        select source_accounting_account acc, 0 cr, sum(debit_amount) db from aurumcore.transaction_detail
          where created::date=%s and source_accounting_account is not null group by 1)
      select m.acc, ca.account_type tipo, ca.account_nature nat,
             round(sum(m.cr)+sum(m.db),2) neto
      from mov m left join aurumcore.cat_accounting_account ca on ca.accounting_id=m.acc
      group by 1,2,3 order by abs(sum(m.cr)+sum(m.db)) desc limit 12
    """, (ult, ult))
    print(f"\nB2 — Movimiento neto por cuenta contable ({ult}) con su naturaleza (top 12):")
    print(f"  {'cuenta':<16} {'tipo':<8} {'nat':<9} {'neto':>16}")
    for acc, tipo, nat, neto in cur.fetchall():
        print(f"  {str(acc):<16} {str(tipo):<8} {str(nat):<9} {neto:>16,.2f}")

    # --- Cobertura: filas sin cuenta contable (no deberian existir) ---
    cur.execute("""select count(*) from aurumcore.transaction_detail
      where created::date >= %s and created::date < (%s::date + %s * interval '1 day')
        and (source_accounting_account is null or target_accounting_account is null)""",
      (a.desde, a.desde, a.dias))
    sin_cta = cur.fetchone()[0]
    print(f"\n[COBERTURA] asientos sin cuenta contable (src o tgt nulo): {sin_cta:,}")

    # --- B3/B4 al grano CUENTA (UUID), via DuckDB (extraer dia -> chains locales, sin timeouts) ---
    cerrar_b3_b4(cur, ult)

    print("\nNOTA: B1 es el invariante contable duro (tol 0.00). B3/B4 al grano cuenta via DuckDB (abajo).")
    print("      Pendiente: amarre auxiliar<->balanza (familia C). Ver PLAN_CONTABLE_BC.md.")
    cn.close()


def cerrar_b3_b4(cur, fecha):
    import duckdb
    csv = (RES / f"_td_{fecha}.csv").as_posix()
    print(f"\n--- B3/B4 (grano cuenta UUID) via DuckDB · dia {fecha} ---")
    print("  extrayendo transaction_detail del dia a CSV local...")
    sql = f"""copy (select transaction_detail_id, created, source_address, target_address,
        source_prior_balance, source_after_balance, target_prior_balance, target_after_balance,
        debit_amount, credit_amount
      from aurumcore.transaction_detail where created::date='{fecha}') to stdout with csv header"""
    with open(csv, "w", encoding="utf-8", newline="") as f:
        cur.copy_expert(sql, f)

    d = duckdb.connect()
    # Stream unificado de movimientos por cuenta (UUID): cada cuenta como target(credito) y como source(debito)
    d.execute(f"""create table mov as
      select target_address acc, created, transaction_detail_id id,
             target_prior_balance pbal, target_after_balance abal, credit_amount amount
        from read_csv_auto('{csv}', header=true) where target_address is not null
      union all
      select source_address acc, created, transaction_detail_id id,
             source_prior_balance pbal, source_after_balance abal, debit_amount amount
        from read_csv_auto('{csv}', header=true) where source_address is not null""")
    d.execute("""create table mv as
      select *, lag(abal) over (partition by acc order by created, id) prev_aft,
             count(*) over (partition by acc) mov_cuenta
      from mov""")

    tot = d.execute("select count(*) from mv").fetchone()[0]
    # B3: el movimiento cambia el saldo por exactamente el monto posteado
    b3_viol = d.execute("select count(*) from mv where round(abal-pbal,2) <> round(amount,2)").fetchone()[0]
    # B4: continuidad (prior[i] = after[i-1]) sobre la misma cuenta
    b4_tot = d.execute("select count(*) from mv where prev_aft is not null").fetchone()[0]
    b4_viol = d.execute("select count(*) from mv where prev_aft is not null and round(pbal,2)<>round(prev_aft,2)").fetchone()[0]
    # Concentracion de violaciones B4 (¿pool operativo?)
    conc = d.execute("""select acc, count(*) v from mv where prev_aft is not null and round(pbal,2)<>round(prev_aft,2)
                        group by 1 order by v desc limit 5""").fetchall()
    cuentas_pool = d.execute("select count(*) from (select acc from mv group by acc having count(*)>500)").fetchone()[0]

    # Excluir cuentas POOL (>500 mov = operativas/clearing; snapshot no atomico por concurrencia)
    b3_cli = d.execute("select count(*) from mv where mov_cuenta<=500 and round(abal-pbal,2)<>round(amount,2)").fetchone()[0]
    b4_cli = d.execute("select count(*) from mv where mov_cuenta<=500 and prev_aft is not null and round(pbal,2)<>round(prev_aft,2)").fetchone()[0]
    tot_cli = d.execute("select count(*) from mv where mov_cuenta<=500").fetchone()[0]

    print(f"  movimientos (piernas) del dia: {tot:,}   cuentas pool (>500 mov): {cuentas_pool}")
    print(f"  -- CRUDO (incluye pool) --")
    print(f"  B3 · (after-prior) <> monto ......... {b3_viol:>8,} de {tot:,}")
    print(f"  B4 · continuidad rota ............... {b4_viol:>8,} de {b4_tot:,}")
    print(f"  -- CUENTAS CLIENTE (excl. {cuentas_pool} pools) = el invariante real --")
    # ¿Las rupturas B4 cliente son empates de timestamp (orden ambiguo) o gaps reales?
    d.execute("""create table mvt as
      select *, lag(created) over (partition by acc order by created, id) prev_created
      from mv where mov_cuenta<=500""")
    b4_empate = d.execute("""select count(*) from mvt where prev_aft is not null
       and round(pbal,2)<>round(prev_aft,2) and created=prev_created""").fetchone()[0]
    b4_real = b4_cli - b4_empate
    print(f"  B3 cliente .......................... {b3_cli:>8,} de {tot_cli:,}")
    print(f"  B4 cliente .......................... {b4_cli:>8,}  (empates de timestamp: {b4_empate:,} · gaps reales: {b4_real:,})")
    if conc:
        print("      (rupturas B4 crudas concentradas en pools:)")
        for acc, v in conc:
            print(f"        {acc[:24]}  rupturas={v}")
    d.close()


if __name__ == "__main__":
    main()
