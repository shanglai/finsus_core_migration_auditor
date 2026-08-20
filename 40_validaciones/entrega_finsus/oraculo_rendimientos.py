# -*- coding: utf-8 -*-
"""
ORÁCULO de RENDIMIENTOS (independiente) — puntos 2.1.1 (vista), 2.1.2 (plazo), 2.1.3 (saldo promedio).
Implementa las fórmulas EXACTAS del doc oficial "Pago de Rendimientos" (F-019) y "Saldo Promedio".
Sin float; todo decimal.Decimal. Redondeos distintos por producto (así está en el doc).
"""
import sys
from decimal import Decimal, ROUND_DOWN, ROUND_CEILING, ROUND_HALF_EVEN, ROUND_HALF_UP, getcontext
getcontext().prec = 50
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

def trunc(x, n):  return Decimal(str(x)).quantize(Decimal(1).scaleb(-n), rounding=ROUND_DOWN)
def ceil10(x):    return Decimal(str(x)).quantize(Decimal("1e-10"), rounding=ROUND_CEILING)   # a 10 dec hacia arriba
def r2_even(x):   return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
def r2_up(x):     return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def rendimiento_plazo(capital, tasa, dias_transcurridos, dias_anio):
    """2.1.2 · Rendimiento = RoundHalfEven2( Ceil10( Ceil10((Capital×Tasa)/100) / DíasAño ) × DíasTranscurridos )"""
    C = Decimal(str(capital)); T = Decimal(str(tasa)); D = Decimal(str(dias_transcurridos)); Y = Decimal(str(dias_anio))
    paso1 = ceil10(C * T / Decimal("100"))
    paso2 = ceil10(paso1 / Y)
    return r2_even(paso2 * D)

def rendimiento_vista(spm, tasa, dias_periodo, dias_anio):
    """2.1.1 · Rendimiento = Round2( Trunc20( Trunc20((SPM×Tasa)/100) / DíasAño ) × DíasPeriodo )
       (SPM = saldo promedio mensual; 'redondeo normal' -> half_up, ver nota)"""
    S = Decimal(str(spm)); T = Decimal(str(tasa)); D = Decimal(str(dias_periodo)); Y = Decimal(str(dias_anio))
    paso1 = trunc(S * T / Decimal("100"), 20)
    paso2 = trunc(paso1 / Y, 20)
    return r2_up(paso2 * D)

def saldo_promedio_rendimiento(saldo_cuenta, difference_of_days, acumulado, elapsed_days):
    """2.1.3 · SPM = (saldo × difference_of_days + acumulado) / elapsed_days
       difference_of_days: conteo EXCLUSIVO (días con saldo sin cambio) · elapsed_days: conteo INCLUSIVO (divisor)."""
    S = Decimal(str(saldo_cuenta)); dif = Decimal(str(difference_of_days))
    ac = Decimal(str(acumulado)); el = Decimal(str(elapsed_days))
    return (S * dif + ac) / el

def _autoprueba():
    print("ORÁCULO RENDIMIENTOS — autoprueba (sin BD). Fórmulas del doc oficial.\n")
    casos = []
    # 2.1.2 plazo: doc ej. capital 1000, tasa 5%, 360 días, 100 días -> 13.89
    casos.append(("Plazo (doc): 1000 @5% base360 x100d", rendimiento_plazo(1000,5,100,360), "13.89"))
    # 2.1.1 vista: doc ej. SPM 5000, 7%, 360, 31 días -> 30.14
    casos.append(("Vista (doc): SPM 5000 @7% base360 x31d", rendimiento_vista(5000,7,31,360), "30.14"))
    # 2.1.3 saldo promedio: doc ej. saldo 30000, diff 8, acum 20000, elapsed 9 -> 28888.88...
    spm = saldo_promedio_rendimiento(30000,8,20000,9)
    casos.append(("Saldo promedio (doc): (30000x8+20000)/9", spm.quantize(Decimal('0.01')), "28888.89"))
    ok=0
    print(f"{'caso':<44}{'C (oráculo)':>14}{'doc':>12}{'dif':>10}")
    for desc,c,e in casos:
        e=Decimal(e); dif=c-e; marca="OK" if abs(dif)<=Decimal("0.01") else "REVISAR"
        print(f"{desc:<44}{str(c):>14}{str(e):>12}{str(dif):>10}  {marca}"); ok+= abs(dif)<=Decimal("0.01")
    print(f"\n{ok}/{len(casos)} dentro de +/-0.01.")

if __name__ == "__main__":
    _autoprueba()
