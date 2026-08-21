"""
Experimento: validar el oraculo de plazo fijo por cohorte de ORIGIN (migrado vs live).
Metodo (identico al 775/775 de V5): por cuenta, capital=iv_initial_amount, dias=due_date-start_date;
la tasa se despeja del periodo 1 y se verifica que el oraculo (Ceil10/Ceil10/RoundHalfEven2, base 360)
reproduce interest_amount en TODOS los periodos. Devuelve # periodos que NO cuadran (cero = pasa).

Dos experimentos separados y registrados:
  A) origin='FINSUS' (MIGRADO, ingestado de OpenFin) -> confirma C = calculo ingestado (=A)
  B) origin IS NULL  (LIVE, generado por AurumCore)  -> confirma C = motor vivo (=B)

SOLO LECTURA.  Uso: python validate_plazo_origin.py
"""
import sys, argparse, yaml, psycopg2, time
from decimal import Decimal, getcontext
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from oraculo_rendimientos import rendimiento_plazo
sys.stdout.reconfigure(encoding="utf-8")
getcontext().prec = 40

RAIZ = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load(open(RAIZ / "db_connections.yaml", encoding="utf-8"))
BASE = 360


def conn():
    C = CFG["aurum"]; kw = {k: C[k] for k in ("host","port","dbname","user","password","sslmode") if k in C}
    for a in range(3):
        try:
            c = psycopg2.connect(**kw); c.set_session(readonly=True); return c
        except Exception:
            time.sleep(4)
    raise RuntimeError("no conecta")


def _procesa_cuenta(per, ok_viol, ejemplos):
    """per = lista (pnum, dias, rend, cap) de una cuenta. Deriva tasa del periodo 1, verifica el resto."""
    per.sort()
    cap = per[0][3]; d1, rend1 = per[0][1], per[0][2]
    if cap == 0 or d1 == 0:
        return
    tasa = rend1 * Decimal(BASE) / (cap * Decimal(d1)) * Decimal(100)
    ok_viol[2] += 1  # cuentas
    for (pnum, dias, rend, _c) in per:
        ok_viol[3] += 1  # periodos
        calc = rendimiento_plazo(cap, tasa, dias, BASE)
        if abs(calc - rend) <= Decimal("0.01"):
            ok_viol[0] += 1
        else:
            ok_viol[1] += 1
            if len(ejemplos) < 5:
                ejemplos.append((pnum, str(rend), str(calc)))


def experimento(cur, nombre, filtro_origin, limite=None):
    """Escalable: una sola query (cohorte CTE + periodos), streaming por cuenta. limite=None => TODO."""
    lim = f"limit {int(limite)}" if limite else ""
    cur.execute(f"""
      with coh as (
        select account_id from aurumcore.iv_payment_plan
        where {filtro_origin} and interest_paid=true and interest_amount>0
        group by account_id having count(*) >= 2 {lim})
      select p.account_id, p.payment_number, (p.due_date - p.start_date) dias,
             p.interest_amount, a.iv_initial_amount capital
      from aurumcore.iv_payment_plan p
      join coh on coh.account_id = p.account_id
      join aurumcore.account a on a.account_id = p.account_id
      where {filtro_origin} and p.interest_paid=true and p.interest_amount>0
        and (p.due_date - p.start_date) > 0 and a.iv_initial_amount > 0
      order by p.account_id, p.payment_number""")
    ok_viol = [0, 0, 0, 0]  # ok, viol, cuentas, periodos
    ejemplos = []
    cur_aid = None; per = []
    while True:
        filas = cur.fetchmany(20000)
        if not filas:
            break
        for aid, pnum, dias, rend, cap in filas:
            if aid != cur_aid:
                if per:
                    _procesa_cuenta(per, ok_viol, ejemplos)
                cur_aid = aid; per = []
            per.append((pnum, int(dias), Decimal(str(rend)), Decimal(str(cap))))
    if per:
        _procesa_cuenta(per, ok_viol, ejemplos)
    ok, viol, ctas, total = ok_viol
    print(f"\n[{nombre}]  cuentas={ctas:,}  periodos={total:,}  cuadran={ok:,}  NO_cuadran={viol:,}")
    if total:
        print(f"    match = {ok/total*100:.2f}%")
    for e in ejemplos:
        print(f"    viola: p{e[0]}  aurum={e[1]}  oraculo={e[2]}")
    return total, ok, viol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=300, help="cuentas por cohorte (0 = TODAS = escala completa)")
    ap.add_argument("--solo", choices=["migrado", "live", "ambos"], default="ambos")
    a = ap.parse_args()
    lim = None if a.limite == 0 else a.limite
    cn = conn(); cur = cn.cursor(); cur.execute("SET statement_timeout='600s'")
    print("=== Validacion de plazo por ORIGIN (oraculo C, base 360) ===")
    print(f"Metodo: tasa despejada del periodo 1; el oraculo reproduce TODOS los periodos (V5). limite={a.limite or 'TODAS'}")
    if a.solo in ("migrado", "ambos"):
        experimento(cur, "A · MIGRADO (origin=FINSUS = ingestado de OpenFin)", "origin='FINSUS'", lim)
    if a.solo in ("live", "ambos"):
        experimento(cur, "B · Aurum-engine (origin IS NULL = shadow+live)", "origin is null", lim)
    cn.close()


if __name__ == "__main__":
    main()
