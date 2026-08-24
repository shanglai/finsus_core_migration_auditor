"""
Oraculo de credito (motor C) — interes ordinario, moratorio e IVA.
Fuente: doc "Calculos Motor de creditos" (F-029, aurum_docs). decimal.Decimal, cero float.

Reglas (F-029):
- Interes ORDINARIO: base = Saldo Insoluto del Capital. Provision diaria un dia despues del inicio
  del periodo. interes_dia = SaldoInsoluto * (tasa/100) / DiasAnio.
- Interes MORATORIO: base = Capital Vencido No Pagado (porcion de capital de la cuota exigible no
  pagada). Desde el dia posterior al vencimiento. moratorio_dia = CapitalVenc * (tasaMor/100) / DiasAnio.
- DiasAnio: calendario Comercial = 360, Natural = 365/366.
- Precision: calculo intermedio a alta precision (~15 dec); redondeo FINAL a 2 decimales (Half Up).
- IVA sobre interes: interes * (tasaIVA/100), 16 dec, redondeo 2 (Half Up). $0 si no grava.
- Ajuste a fin de periodo: al vencimiento se cuadra la suma de provisiones diarias al monto pactado
  en la tabla de amortizacion (no se modela aqui a nivel formula; se valida contra el cargo del periodo).

NOTA: la tasa contratada, el saldo insoluto por dia y los dias de mora vienen de la BD
(lc_loan_contract, lc_loan_amortization, lc_finantial_data_stage). Este modulo es solo la formula.
"""
from decimal import Decimal, ROUND_HALF_UP, getcontext
getcontext().prec = 40

D = lambda x: x if isinstance(x, Decimal) else Decimal(str(x))


def dias_anio(calendar_type):
    """Comercial=360; Natural=365/366. Mapeo de codigos de Finsus (aurumcore.lc_loan_contract.calendar_type):
    `1` = Comercial = 360 [CONFIRMADO empirico 2026-08-23: match exacto io = monto*tasa*dias/360].
    Otros/natural -> 365 (366 bisiesto se pasa explicito por quien llame)."""
    c = str(calendar_type).strip().lower()
    if c in ("comercial", "commercial", "360", "0", "1"):
        return Decimal(360)
    return Decimal(365)


def _round2(x):
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def interes_ordinario_dia(saldo_insoluto, tasa_anual, base=360):
    """Provision diaria de interes ordinario (sin redondear, alta precision)."""
    return D(saldo_insoluto) * (D(tasa_anual) / Decimal(100)) / D(base)


def interes_ordinario_periodo(saldo_insoluto, tasa_anual, dias, base=360):
    """Interes ordinario de un periodo de `dias` (redondeo final 2 dec Half Up)."""
    return _round2(interes_ordinario_dia(saldo_insoluto, tasa_anual, base) * D(dias))


def interes_moratorio_dia(capital_vencido, tasa_mor_anual, base=360):
    """Provision diaria de interes moratorio SIN redondear (alta precision).
    Simetrico a interes_ordinario_dia. Usar para cruzar contra el feed de provision diaria
    del CORE (`credits-closing-trans`, col monto = valor sin redondear). Comparar con _round2
    contra el feed rompe el match a 1e-8 (el feed NO esta redondeado)."""
    return D(capital_vencido) * (D(tasa_mor_anual) / Decimal(100)) / D(base)


def interes_moratorio_periodo(capital_vencido, tasa_mor_anual, dias_mora, base=360):
    """Interes moratorio de un periodo de `dias_mora` (redondeo final 2 dec, para el cargo)."""
    return _round2(interes_moratorio_dia(capital_vencido, tasa_mor_anual, base) * D(dias_mora))


def iva_interes(interes, tasa_iva):
    """IVA sobre el interes (ordinario o moratorio). $0 si tasa_iva<=0."""
    if D(tasa_iva) <= 0:
        return Decimal("0.00")
    return _round2(D(interes) * (D(tasa_iva) / Decimal(100)))


if __name__ == "__main__":
    # Autoprueba estructural (valores ilustrativos; los oficiales van en los ejemplos del doc F-029).
    # Credito de 10,000 al 36% anual, base 360, 30 dias:
    io = interes_ordinario_periodo(10000, 36, 30, 360)     # 10000*0.36/360*30 = 300.00
    print("interes ordinario 30d:", io, "(esperado 300.00)")
    im = interes_moratorio_periodo(2000, 60, 10, 360)      # 2000*0.60/360*10 = 33.333.. -> 33.33
    print("interes moratorio 10d:", im, "(esperado 33.33)")
    print("IVA 16% sobre 300:", iva_interes(io, 16), "(esperado 48.00)")
