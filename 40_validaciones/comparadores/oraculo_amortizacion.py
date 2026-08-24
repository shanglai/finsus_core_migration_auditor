"""
ORACULO de AMORTIZACION (motor C) — tabla de amortizacion de credito.
Fuente: doc "Cálculos Motor de créditos" (D-CRE §8.6 Francesa) + verificacion empirica en BD
(aurumcore.lc_loan_amortization). decimal.Decimal, cero float.

MECANICA CONFIRMADA (contrato cd96ff4c y frescos, 2026-08-23):
- FRANCESA: cuota financiera (capital + interes) constante salvo ajuste del ultimo periodo.
- Interes del periodo = **Saldo insoluto × tasa_anual/100 / 360 × dias_periodo**  (Actual/360).
  (dias_periodo por calendario; hay quirk de convencion en el primer periodo — spec exacto pendiente.)
- Capital del periodo = cuota − interes ; saldo_remanente_n = saldo_{n-1} − capital_n ; saldo_final = 0.
- Cuota francesa base = Capital × [ i_periodo / (1 − (1 + i_periodo)^-n) ], i_periodo = tasa_anual/12/100 (mensual).

LINAJE (importante): en `lc_loan_amortization`, `capital_amount`/`interest_amount`/`total_amount` son el
CRONOGRAMA ORIGINAL; `capital_remaining_amount`/`provisioned_interest_amount`/`payment_to_capital_amount`
son estado VIVO (se actualizan con pagos) -> validar el cronograma solo en contratos sin pagos.

AMERICAN (dominante, 29,271): pago unico al vencimiento (One Click) -> interes via oraculo_credito.
"""
from decimal import Decimal, ROUND_HALF_UP, getcontext
getcontext().prec = 40
D = lambda x: x if isinstance(x, Decimal) else Decimal(str(x))


def cuota_francesa(capital, tasa_anual, n_periodos, meses_por_periodo=1):
    """Cuota (capital+interes) constante de una tabla francesa. i mensual = tasa/12."""
    i = D(tasa_anual) / Decimal(100) / Decimal(12) * Decimal(meses_por_periodo)
    n = int(n_periodos)
    if i == 0:
        return D(capital) / Decimal(n)
    factor = i / (Decimal(1) - (Decimal(1) + i) ** (-n))
    return D(capital) * factor


def interes_periodo(saldo_insoluto, tasa_anual, dias, base=360):
    """Interes del periodo, Actual/360 (sin redondear)."""
    return D(saldo_insoluto) * (D(tasa_anual) / Decimal(100)) / D(base) * D(dias)


def _r2(x):
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# --- Invariantes de la tabla (devuelven True/False; usar sobre el CRONOGRAMA ORIGINAL) ---
def inv_identidad_fila(cap, interes, tax, seguros, misc, total, tol="0.02"):
    """total = capital + interes + tax + seguros + misc."""
    return abs(D(total) - (D(cap) + D(interes) + D(tax) + D(seguros) + D(misc))) <= D(tol)


def inv_rollforward(loan_amount, filas, tol="0.02"):
    """filas = [(capital_amount, capital_remaining_amount), ...] en orden. saldo_n = saldo_{n-1}-cap_n; final=0."""
    prev = D(loan_amount)
    for cap, rem in filas:
        if abs((prev - D(cap)) - D(rem)) > D(tol):
            return False
        prev = D(rem)
    return abs(prev) <= D(tol)


def inv_suma_capital(loan_amount, capitales, tol="0.02"):
    return abs(sum(D(c) for c in capitales) - D(loan_amount)) <= D(tol)


if __name__ == "__main__":
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    print("ORACULO AMORTIZACION — autoprueba\n")
    casos = []
    # cuota francesa (anualidad estandar): 5000, 38%, 6 mensual -> 928.09.
    # NOTA: Aurum posta 929.15 (~0.1% mas): su cuota se ajusta por la convencion Actual/360 (dias reales),
    # no es la anualidad de periodos iguales. La anualidad estandar es la referencia; el ajuste por dias es
    # el residuo a caracterizar con el spec exacto.
    q = cuota_francesa(5000, 38, 6)
    casos.append(("cuota_francesa(5000,38%,6m) anualidad", _r2(q), Decimal("928.09")))
    # interes periodo 1 del mismo: saldo 5000, 38%, 30 dias -> 158.33
    casos.append(("interes(5000,38%,30d,360)", _r2(interes_periodo(5000, 38, 30)), Decimal("158.33")))
    # interes periodo 3: saldo 3433.95, 38%, 31 dias -> 112.37
    casos.append(("interes(3433.95,38%,31d,360)", _r2(interes_periodo("3433.95", 38, 31)), Decimal("112.37")))
    # invariantes
    casos.append(("inv_identidad(770.82+158.33=929.15)", inv_identidad_fila("770.82", "158.33", 0, 0, 0, "929.15"), True))
    casos.append(("inv_rollforward 5000->0", inv_rollforward(5000, [("770.82","4229.18"),("795.23","3433.95"),("816.78","2617.17"),("846.27","1770.90"),("871.20","899.70"),("899.70","0.00")]), True))
    casos.append(("inv_suma_capital=5000", inv_suma_capital(5000, ["770.82","795.23","816.78","846.27","871.20","899.70"]), True))
    ok = 0
    for desc, got, exp in casos:
        m = (got == exp) if isinstance(exp, bool) else (abs(D(got) - exp) <= Decimal("0.01"))
        ok += m
        print(f"  {desc:<42} = {str(got):>10}  esperado {str(exp):>8}  {'OK' if m else 'REVISAR'}")
    print(f"\n{ok}/{len(casos)} OK.")
