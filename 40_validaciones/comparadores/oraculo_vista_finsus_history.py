# -*- coding: utf-8 -*-
"""
oraculo_vista_finsus_history.py — Cruce VIVO de rendimiento VISTA (motor C vs B).

Convierte VISTA de "citado" a "calculado aqui": calcula el interes de vista con el oraculo
independiente y lo compara contra lo que AurumCore POSTEO en el ciclo mensual.

Fuentes (esquema aurumcore, SOLO LECTURA):
  - B (posteado por Aurum): aurumcore.yield_dto  (iv_payment_plan_id IS NULL = VISTA),
       process_date = cierre del ciclo, yield_amount = interes devengado del mes.
  - Insumos de C: aurumcore.finsus_account_history (foto diaria por cuenta) en el record_date
       del cierre: average_balance_amount = SPM, interest_rate = tasa.
  - base de dias: aurumcore.account_yield.days_in_year (360 o 365 segun esquema).

Formula (doc D-REN, via oraculo_rendimientos.rendimiento_vista):
  C = Round2( Trunc20( Trunc20((SPM x Tasa)/100) / base ) x DiasPeriodo )

Como la base (360/365) y DiasPeriodo (30/31) dependen del esquema, el script prueba las
convenciones naturales y reporta cual ajusta (no-circular) y el % de cuadre a 1e-8 / 1e-5 / centavo.

decimal.Decimal, cero float. Uso:
  python oraculo_vista_finsus_history.py --cierre 2026-07-31 --limite 20000
  python oraculo_vista_finsus_history.py --cierre 2026-07-31 --limite 0   # universo completo
"""
import argparse, sys, yaml, psycopg2
from decimal import Decimal
sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
from oraculo_rendimientos import rendimiento_vista
from tolerancias import resumen_tolerancias, imprimir

CONVENCIONES = [(360, 31), (365, 31), (360, 30), (365, 30)]  # (base, DiasPeriodo)


def conn():
    a = yaml.safe_load(open("db_connections.yaml"))["aurum"]
    c = psycopg2.connect(host=a["host"], port=a.get("port", 5432), dbname=a["dbname"],
                         user=a["user"], password=a["password"], connect_timeout=10)
    c.set_session(readonly=True)
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cierre", default="2026-07-31", help="record_date del cierre del ciclo (SPM en finsus_account_history)")
    ap.add_argument("--pago", default="2026-08-01", help="process_date del pago mensual en yield_dto (B posteada)")
    ap.add_argument("--limite", type=int, default=0, help="cuentas a muestrear (0 = TODAS)")
    ap.add_argument("--dt-por-cuenta", action="store_true",
                    help="usa el dt real por cuenta (dias con saldo en el mes) en vez de dt fijo; base 360")
    a = ap.parse_args()
    lim = "" if a.limite == 0 else f"limit {int(a.limite)}"

    c = conn(); cur = c.cursor(); cur.execute("set statement_timeout=290000")
    print(f"=== VISTA vivo · SPM {a.cierre} vs pago {a.pago} · {'UNIVERSO' if a.limite==0 else a.limite}"
          f"{' · dt-por-cuenta' if a.dt_por_cuenta else ''} ===")
    if a.dt_por_cuenta:
        q = f"""
          with pay as (
            select y.account_id, y.yield_amount b, h.average_balance_amount spm, h.interest_rate tasa
            from aurumcore.yield_dto y
            join aurumcore.finsus_account_history h
              on h.account_id = y.account_id and h.record_date = date '{a.cierre}'
            where y.iv_payment_plan_id is null and y.process_date = date '{a.pago}'
              and y.yield_amount > 0 and h.average_balance_amount > 0 {lim}),
          dt as (
            select account_id, count(distinct record_date) dt
            from aurumcore.finsus_account_history
            where record_date between date_trunc('month', date '{a.cierre}') and date '{a.cierre}'
              and average_balance_amount > 0 and account_id in (select account_id from pay)
            group by account_id)
          select p.account_id, p.b, p.spm, p.tasa, coalesce(d.dt, 31) dt
          from pay p left join dt d on d.account_id = p.account_id
        """
    else:
        q = f"""
          select y.account_id, y.yield_amount, h.average_balance_amount, h.interest_rate
          from aurumcore.yield_dto y
          join aurumcore.finsus_account_history h
            on h.account_id = y.account_id and h.record_date = date '{a.cierre}'
          where y.iv_payment_plan_id is null
            and y.process_date = date '{a.pago}'
            and y.yield_amount > 0
            and h.average_balance_amount > 0
          {lim}
        """
    cur.execute(q)
    filas = cur.fetchall()
    print(f"pares (B posteado ∧ SPM en historia): {len(filas):,}")
    if not filas:
        print("sin pares — revisar cierre/cobertura."); return

    if a.dt_por_cuenta:
        pares = [(rendimiento_vista(Decimal(str(spm)), Decimal(str(tasa)), int(dt), 360), Decimal(str(b)))
                 for acc, b, spm, tasa, dt in filas]
        imprimir(f"vista-{a.cierre}-dtcuenta (base 360)", resumen_tolerancias(pares))
        fuera = [(acc, cval, Decimal(str(b))) for (cval, _), (acc, b, *_r) in zip(pares, filas)
                 if abs(cval - Decimal(str(b))) > Decimal("0.01")]
        print(f"\nno-conformes al centavo: {len(fuera):,} de {len(filas):,} (residual = granularidad del SPM de cierre)")
        return

    # C para cada convencion; nos quedamos con la mejor por cuenta (la que mas cuadra al centavo)
    mejor_pares = []       # (C_mejor, B) usando la convencion que mas cuadra globalmente
    universo_por_conv = {}
    for base, dt in CONVENCIONES:
        pares = []
        for acc, b, spm, tasa in filas:
            cval = rendimiento_vista(Decimal(str(spm)), Decimal(str(tasa)), dt, base)
            pares.append((cval, Decimal(str(b))))
        res = resumen_tolerancias(pares)
        pct_cent = next(x["pct"] for x in res["escalas"] if x["nombre"] == "centavo")
        universo_por_conv[(base, dt)] = (res, pct_cent)

    # elegir la convencion global con mayor % al centavo
    (best_base, best_dt), (best_res, best_pct) = max(universo_por_conv.items(), key=lambda kv: Decimal(kv[1][1]))
    print(f"\n-- % de cuadre por convencion (base, DiasPeriodo) --")
    for (base, dt), (res, pc) in universo_por_conv.items():
        e = {x['nombre']: x['pct'] for x in res['escalas']}
        marca = "  <== mejor" if (base, dt) == (best_base, best_dt) else ""
        print(f"   base {base} · dt {dt}:  1e-8={e['1e-8']}%  1e-5={e['1e-5']}%  centavo={e['centavo']}%{marca}")

    print(f"\n-- Detalle de la mejor convencion (base {best_base}, dt {best_dt}) --")
    imprimir(f"vista-{a.cierre}", best_res)

    # muestra de no-conformes (para el tablero)
    pares_best = [(rendimiento_vista(Decimal(str(spm)), Decimal(str(tasa)), best_dt, best_base), Decimal(str(b)), acc)
                  for acc, b, spm, tasa in filas]
    fuera = [(acc, cval, b, (cval - b)) for cval, b, acc in pares_best if abs(cval - b) > Decimal("0.01")]
    print(f"\nno-conformes al centavo: {len(fuera):,} de {len(filas):,}")
    for acc, cval, b, d in fuera[:6]:
        print(f"   {acc[:12]}  C={cval}  B={b}  delta={d}")


if __name__ == "__main__":
    main()
