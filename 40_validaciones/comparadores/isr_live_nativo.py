"""
ISR-LIVE-NATIVO — validacion del ISR retenido por AurumCore EN VIVO vs oraculo C.

NUEVA validacion, separada de la anterior (set de desviacion / MODELO). Aqui probamos el
**motor vivo** de Aurum: retenciones de ISR generadas post-cutover, contra la regla (oraculo C).

Delimitador de "Aurum vivo": **created >= CUTOVER** (NO `origin is null`, que tiene semantica mixta;
se reporta el desglose por origin para transparencia — ver P-013 / SOLICITUDES_FINSUS SOL-004).

Firma del asiento de ISR (verificada): transaction_type='INTERNAL TRANSFER', channel='Generic',
contrapartida producto 0000; isr = credit_amount; referencia = 'Pago de rendimientos-<inversion>'.

Oraculo: isr_retenido(saldo_total_cliente, saldo_cuenta_inversion, dias_periodo).
Caveat v1: saldo_total se toma de los saldos ACTUALES (aprox. del saldo base al momento) -> el
residual incluye deriva de saldo, no solo defecto. Cohorte acotada.

SOLO LECTURA.  Uso: python isr_live_nativo.py [--cutover 2026-08-03] [--limite 3000]
"""
import sys, argparse, yaml, psycopg2, time
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "entrega_finsus"))
from oraculo_isr import isr_retenido
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load(open(RAIZ / "db_connections.yaml", encoding="utf-8"))
RES = RAIZ / "40_validaciones" / "_resultados"; RES.mkdir(exist_ok=True)
UMA = Decimal("42794.64"); TASA = Decimal("0.90")


def conn():
    C = CFG["aurum"]; kw = {k: C[k] for k in ("host","port","dbname","user","password","sslmode") if k in C}
    for a in range(3):
        try:
            c = psycopg2.connect(**kw); c.set_session(readonly=True); return c
        except Exception:
            time.sleep(4)
    raise RuntimeError("no conecta")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutover", default="2026-08-03")
    ap.add_argument("--limite", type=int, default=3000)
    a = ap.parse_args()
    cn = conn(); cur = cn.cursor(); cur.execute("SET statement_timeout='240s'")

    print("=== ISR-LIVE-NATIVO · retencion viva de Aurum vs oraculo C ===")
    print(f"Delimitador: created >= {a.cutover} (Aurum vivo). Cohorte <= {a.limite} retenciones.\n")

    # Desglose por origin (transparencia) sobre el universo de retenciones vivas
    cur.execute("""
      select t.origin, count(*) n, round(sum(td.credit_amount),2) isr
      from aurumcore.transaction_detail td join aurumcore.transaction t on t.transaction_id=td.transaction_id
      join aurumcore.account pe on pe.account_id=t.payee_account_id
      where td.transaction_type='INTERNAL TRANSFER' and td.transaction_channel='Generic'
        and split_part(pe.account_number,'-',2)='0000' and td.created::date >= %s
      group by 1 order by n desc""", (a.cutover,))
    print("Universo de retenciones ISR vivas — desglose por origin:")
    for org, n, isr in cur.fetchall():
        print(f"   origin={str(org):<22} n={n:>8,}  isr=${isr:,.2f}")

    # Extraccion: retencion + inversion (de la referencia) + capital + dias + saldo_total del cliente
    cur.execute("""
      with sal as (  -- saldo_total actual por cliente (solo cuentas ACTIVAS: balance<>0)
        select accountholder_id,
          sum(case when split_part(account_number,'-',2)='2301' and coalesce(balance_amount,0)<>0 then coalesce(iv_initial_amount,0) else 0 end)
        + sum(case when split_part(account_number,'-',2) ~ '^20' then coalesce(average_balance_amount,0) else 0 end) saldo_total
        from aurumcore.account group by accountholder_id)
      select pa.accountholder_id,
             td.credit_amount as isr_ac,
             substring(td.alfanumeric_reference from '\\d{3}-\\d{4}-\\d+') as inv,
             td.created::date fecha, sal.saldo_total
      from aurumcore.transaction_detail td
      join aurumcore.transaction t on t.transaction_id=td.transaction_id
      join aurumcore.account pa on pa.account_id=t.payer_account_id
      join aurumcore.account pe on pe.account_id=t.payee_account_id
      join sal on sal.accountholder_id=pa.accountholder_id
      where td.transaction_type='INTERNAL TRANSFER' and td.transaction_channel='Generic'
        and split_part(pe.account_number,'-',2)='0000' and td.created::date >= %s
        and td.credit_amount > 0
      limit %s""", (a.cutover, a.limite))
    ret = cur.fetchall()
    print(f"\nRetenciones en cohorte: {len(ret):,}")

    # capital (iv_initial_amount) y dias del periodo por inversion
    invs = tuple({r[2] for r in ret if r[2]})
    cur.execute("""
      select a.account_number, a.iv_initial_amount,
             (select (p.due_date - p.start_date) from aurumcore.iv_payment_plan p
               where p.account_number=a.account_number and p.interest_amount>0
               order by p.payment_number desc limit 1) dias
      from aurumcore.account a where a.account_number = any(%s)""", (list(invs),))
    inv_info = {an: (Decimal(str(cap or 0)), int(d) if d else None) for an, cap, d in cur.fetchall()}

    ok = viol = sin_datos = 0
    ejem = []
    for aid, isr_ac, inv, fecha, saldo_total in ret:
        info = inv_info.get(inv)
        if not info or info[1] is None or info[0] == 0 or not saldo_total or saldo_total <= 0:
            sin_datos += 1; continue
        cap, dias = info
        st = Decimal(str(saldo_total))
        calc = isr_retenido(st, cap, dias)  # defaults = params 2026 (UMA 42,794.64, tasa 0.90%, 5xUMA, 365)
        if abs(calc - Decimal(str(isr_ac))) <= Decimal("0.01"):
            ok += 1
        else:
            viol += 1
            if len(ejem) < 5:
                ejem.append((inv, str(isr_ac), str(calc), str(dias), f"{st:.0f}"))
    val = ok + viol
    print(f"\nComparadas: {val:,}  (sin datos suficientes: {sin_datos:,})")
    if val:
        print(f"  CUADRAN (±0.01): {ok:,}  ({ok/val*100:.2f}%)   NO cuadran: {viol:,}")
    for e in ejem:
        print(f"   viola inv {e[0]}: aurum={e[1]} oraculo={e[2]} dias={e[3]} saldo_total={e[4]}")
    print("\nNOTA v1: saldo_total = saldos ACTUALES (aprox); el residual incluye deriva de saldo, no solo")
    print("         defecto. Para exacto se requiere el saldo base al momento (logs del CORE, SOL-003).")
    cn.close()


if __name__ == "__main__":
    main()
