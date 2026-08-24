"""
ORACULO de GAT (Ganancia Anual Total) — motor C, independiente.
Fuente: doc oficial "GTM-Cálculo de GAT (Cuentas e Inversiones)" (D-GAT). decimal.Decimal, cero float.

Dos metodologias (doc p.2-7):

CUENTAS (vista/ahorro, tipo ACCOUNT) — pagos mensuales, m = DiasAno/DiasPeriodo:
  m      = DiasAno / DiasPeriodo            (ej. 360/30 = 12)
  paso1  = Round10( tasa% / 100 )
  paso2  = Round10( 1 + paso1/m )
  paso3  = Round10( paso2 ^ m )
  GAT Nominal% = Round8( paso3 - 1 ) * 100
  GAT Real%    = Round2( ( Round10( Round10(paso3) / (1 + Round10(infl_dec)) ) - 1 ) * 100 )
  Ej doc: tasa 10%, 360, 30, infl 4.18% -> Nominal 10.471307, Real 6.04.

INVERSIONES (plazo fijo, tipo INVESTMENT_ACCOUNT) — base = total de dias de la inversion:
  m      = Round10( DiasAno / DiasInversion )      (ej. 360/90 = 4)
  paso1  = Round10( (Inicial + Intereses) / Inicial )
  paso2  = Round10( paso1 ^ m )
  paso3  = Round16( paso2 - 1 )
  GAT Nominal% = paso3 * 100
  GAT Real%    = Round2( ( Round10( (1 + Round10(GATnom%/100)) / (1 + Round10(infl%/100)) ) - 1 ) * 100 )
  Ej doc: 1000 + 200 a 90 dias, 360, infl 4.18% -> Nominal 107.36, Real 99.04.

RoundN = redondeo a N decimales, HALF_UP (redondeo normal; el doc no especifica modo -> se asume
half-up estandar de Banxico). Los ejemplos del doc validan con half-up.
DiasAno, DiasInversion y la inflacion son parametros (esquema/misceláneo del producto y Banxico).
Validacion oficial: calculadora GAT de Banxico. En BD: account.nominal_cgat / account.real_cgat.
"""
from decimal import Decimal, ROUND_HALF_UP, getcontext
getcontext().prec = 60

D = lambda x: x if isinstance(x, Decimal) else Decimal(str(x))


def _r(x, n):
    """Redondeo a n decimales HALF_UP."""
    return D(x).quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP)


def gat_cuenta(tasa_pct, dias_anio, dias_periodo, inflacion_pct):
    """GAT nominal y real para cuenta a la vista/ahorro (tipo ACCOUNT). Devuelve (nominal%, real%)."""
    m = D(dias_anio) / D(dias_periodo)
    paso1 = _r(D(tasa_pct) / Decimal(100), 10)
    paso2 = _r(Decimal(1) + paso1 / m, 10)
    paso3 = _r(paso2 ** m, 10)
    nominal = _r(paso3 - Decimal(1), 8) * Decimal(100)
    infl_dec = _r(D(inflacion_pct) / Decimal(100), 10)
    paso4 = _r(_r(paso3, 10) / (Decimal(1) + infl_dec), 10)
    real = _r((paso4 - Decimal(1)) * Decimal(100), 2)
    return nominal, real


def gat_inversion(inicial, intereses, dias_anio, dias_inversion, inflacion_pct):
    """GAT nominal y real para inversion de plazo fijo (tipo INVESTMENT_ACCOUNT). Devuelve (nominal%, real%)."""
    m = _r(D(dias_anio) / D(dias_inversion), 10)
    paso1 = _r((D(inicial) + D(intereses)) / D(inicial), 10)
    paso2 = _r(paso1 ** m, 10)
    paso3 = _r(paso2 - Decimal(1), 16)
    nominal = paso3 * Decimal(100)
    infl_dec = _r(D(inflacion_pct) / Decimal(100), 10)
    paso2r = _r((Decimal(1) + _r(nominal / Decimal(100), 10)) / (Decimal(1) + infl_dec), 10)
    real = _r((paso2r - Decimal(1)) * Decimal(100), 2)
    return nominal, real


if __name__ == "__main__":
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    print("ORACULO GAT — autoprueba vs ejemplos del doc oficial D-GAT\n")
    casos = []
    n, r = gat_cuenta(10, 360, 30, Decimal("4.18"))
    casos.append(("Cuenta 10% base360 m=12 infl4.18%", n, r, "10.471307", "6.04"))
    n, r = gat_inversion(1000, 200, 360, 90, Decimal("4.18"))
    casos.append(("Inversion 1000+200 90d base360 infl4.18%", n, r, "107.36", "99.04"))
    ok = 0
    print(f"{'caso':<44}{'nom C':>13}{'nom doc':>10}{'real C':>9}{'real doc':>10}")
    for desc, nom, real, enom, ereal in casos:
        mn = abs(nom - Decimal(enom)) <= Decimal("0.0001")
        mr = abs(real - Decimal(ereal)) <= Decimal("0.01")
        ok += mn and mr
        print(f"{desc:<44}{str(nom):>13}{enom:>10}{str(real):>9}{ereal:>10}  {'OK' if mn and mr else 'REVISAR'}")
    print(f"\n{ok}/{len(casos)} casos OK.")
