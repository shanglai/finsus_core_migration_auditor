"""
ORACULO de CAT (Costo Anual Total) — motor C, credito.
Fuente: doc "Cálculos Motor de créditos" (D-CRE §8, Circular 21/2009 Banxico). decimal.Decimal.

REGLA:
- Pago para CAT = Capital + Interes ordinario + Comisiones sin IVA + Seguros sin IVA.
  EXCLUYE: IVA de intereses, IVA de comisiones/seguros, intereses MORATORIOS, penalizaciones, prepagos.
- Monto recibido = Monto del credito − Comisiones iniciales descontadas.
- CAT = tasa anual i que iguala VP(disposiciones) = VP(pagos):  Σ A_j/(1+i)^t_j = Σ B_k/(1+i)^s_k.

ONE CLICK (una sola amortizacion, base 360):
  CAT = [ (Pago unico sin IVA / Monto recibido)^(360/dias) − 1 ] × 100.

FRANCESA (multiperiodo): CAT = i que hace VP=0 del flujo (-recibido, pago_1, pago_2, ...), anualizada;
  se resuelve por biseccion sobre la tasa anual.

NOTA (igual que GAT): el CAT usa la tasa/interes REALES del cronograma (lc_loan_amortization), no el
`ordinary_interest_rate` nominal (que es techo). El `total_amount` de la tabla incluye IVA; para CAT se usa
capital+interes SIN IVA. La comision inicial hay que obtenerla (lc_account_commission / cargo de apertura).
"""
from decimal import Decimal, getcontext
getcontext().prec = 40
D = lambda x: x if isinstance(x, Decimal) else Decimal(str(x))


def cat_oneclick(monto_recibido, pago_sin_iva, dias, base=360):
    """CAT cerrado para credito de un solo pago. Devuelve % (Decimal)."""
    R = D(monto_recibido); P = D(pago_sin_iva)
    if R <= 0 or dias <= 0:
        raise ValueError("recibido>0 y dias>0")
    exp = D(base) / D(dias)
    return ((P / R) ** exp - Decimal(1)) * Decimal(100)


def _vp(tasa_anual_dec, recibido, pagos_dias):
    """VP neto del flujo (-recibido en t=0; +pago en su dia) a tasa anual (decimal), base 360."""
    v = -D(recibido)
    for pago, dia in pagos_dias:
        v += D(pago) / (Decimal(1) + D(tasa_anual_dec)) ** (D(dia) / Decimal(360))
    return v


def cat_frances(monto_recibido, pagos_dias, tol=Decimal("0.0000001"), it=200):
    """CAT multiperiodo por biseccion sobre la tasa anual. pagos_dias = [(pago_sin_iva, dias_desde_disposicion), ...].
    Devuelve % (Decimal)."""
    lo, hi = Decimal("-0.9999"), Decimal("1000")  # -99.99% .. 100000%
    flo = _vp(lo, monto_recibido, pagos_dias)
    fhi = _vp(hi, monto_recibido, pagos_dias)
    if flo * fhi > 0:
        # sin cambio de signo en el rango: devolver el extremo mas cercano a 0
        return (lo if abs(flo) < abs(fhi) else hi) * Decimal(100)
    for _ in range(it):
        mid = (lo + hi) / Decimal(2)
        fm = _vp(mid, monto_recibido, pagos_dias)
        if abs(fm) < tol:
            break
        if flo * fm < 0:
            hi = mid; fhi = fm
        else:
            lo = mid; flo = fm
    return mid * Decimal(100)


if __name__ == "__main__":
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    print("ORACULO CAT — autoprueba vs ejemplos del doc (D-CRE §8)\n")
    casos = []
    # One Click 90 dias (doc): recibido 96010, pago 105500, 90 dias -> 45.8%
    casos.append(("OneClick 90d (doc)", cat_oneclick(96010, 105500, 90), Decimal("45.8"), Decimal("0.3")))
    # One Click 1 dia (doc): recibido 960.10, pago 1000.611111..., 1 dia -> 289458538.2%
    casos.append(("OneClick 1d (doc)", cat_oneclick("960.10", "1000.61111111111111111", 1), Decimal("289458538.2"), Decimal("50")))
    # Francesa (doc): recibido 9601, 12 pagos de 935.94 (mensuales, dias≈30·k) -> CAT ~34.5%
    pagos = [(Decimal("935.94"), 30 * k) for k in range(1, 13)]
    casos.append(("Francesa 12x935.94 (doc)", cat_frances(9601, pagos), Decimal("34.5"), Decimal("1.5")))
    ok = 0
    for desc, got, exp, tolv in casos:
        m = abs(D(got) - exp) <= tolv
        ok += m
        print(f"  {desc:<26} = {float(got):>16.4f}%  esperado ~{str(exp):>12}  {'OK' if m else 'REVISAR'}")
    print(f"\n{ok}/{len(casos)} OK.")
