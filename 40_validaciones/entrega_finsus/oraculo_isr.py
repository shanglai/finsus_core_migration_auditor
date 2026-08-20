# -*- coding: utf-8 -*-
"""
ORÁCULO ISR (independiente) — para validación por Finsus.

Implementa la regla de retención de ISR sobre rendimientos EXACTAMENTE como el documento
oficial "AurumCore - Cálculo de Pago de Rendimientos" (v actualizada, proporción ÷ saldo total),
y como la norma vigente 2026 (LIF Art. 24 tasa 0.90%; LISR Art. 93 fr. XX exención 5×UMA;
UMA 2026 = 42,794.64). Sin `float` en la ruta monetaria (todo `decimal.Decimal`).

USO:
  1) Autoprueba (sin BD): reproduce casos conocidos → `python oraculo_isr.py`
  2) Con tus datos: importa `isr_retenido(...)` y pásale saldo_total, saldo_cuenta, días.

No conecta a ninguna base. Es el "árbitro" de cálculo; se compara contra lo que postea el core.
"""
import sys
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, getcontext
getcontext().prec = 50
try:
    sys.stdout.reconfigure(encoding="utf-8")   # consolas Windows (cp1252)
except Exception:
    pass

# --- Parámetros normativos 2026 (verificados contra la norma; P-010) ---------
UMA_ANUAL_2026   = Decimal("42794.64")     # INEGI, DOF 9-ene-2026, vigente 1-feb-2026
FACTOR_UMA_EXENTO = Decimal("5")           # LISR Art. 93 fr. XX
TASA_ISR_ANUAL   = Decimal("0.9")          # % — LIF 2026 Art. 24 (subió de 0.50%)
DIAS_ANIO        = Decimal("365")          # tax.days.year

def trunc(x: Decimal, n: int) -> Decimal:
    """Trunca (no redondea) a n decimales."""
    return x.quantize(Decimal(1).scaleb(-n), rounding=ROUND_DOWN)

def round2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

def isr_retenido(saldo_total_cliente, saldo_cuenta, dias_periodo,
                 uma=UMA_ANUAL_2026, factor=FACTOR_UMA_EXENTO,
                 tasa_anual=TASA_ISR_ANUAL, dias_anio=DIAS_ANIO, persona_moral=False):
    """
    ISR retenido de UNA cuenta/inversión al pago de rendimientos.
    Fórmula (doc oficial AurumCore + norma):
        Monto Exento  = UMA × factor            (persona moral: 0)
        Base Gravable = max(0, Saldo Total − Monto Exento)
        Proporción    = Trunc20(Saldo Cuenta / Saldo Total)      # ÷ SALDO TOTAL
        ISR Diario    = Trunc5(Base Gravable × Trunc20(Tasa / (100 × DíasAño)))
        ISR Retenido  = Round2(Trunc20(ISR Diario × Días Periodo) × Proporción)
    """
    ST = Decimal(str(saldo_total_cliente)); SC = Decimal(str(saldo_cuenta)); D = Decimal(str(dias_periodo))
    monto_exento  = Decimal("0") if persona_moral else uma * factor
    base_gravable = max(Decimal("0"), ST - monto_exento)
    if base_gravable == 0 or ST == 0:
        return Decimal("0.00")
    proporcion  = trunc(SC / ST, 20)
    tasa_diaria = trunc(tasa_anual / (Decimal("100") * dias_anio), 20)
    isr_diario  = trunc(base_gravable * tasa_diaria, 5)
    isr         = round2(trunc(isr_diario * D, 20) * proporcion)
    return isr

# ------------------------------- AUTOPRUEBA ----------------------------------
def _autoprueba():
    print("ORÁCULO ISR — autoprueba (sin BD). Parámetros 2026: UMA=42,794.64 · 5×UMA=213,973.20 · tasa=0.90% · 365 días\n")
    casos = [
        # (descripción, saldo_total, saldo_cuenta, días, esperado_del_core)
        ("Caso de oro inv.1 (cliente con vista+plazo)", "311136.07", "50182.96", 120, "46.37"),
        ("Caso de oro inv.2",                            "311136.07", "89175.01",   7, "4.81"),
        ("Caso de oro inv.3",                            "311136.07",   "202.57",  30, "0.05"),
        ("Cliente 1 inversión 300k, 361 días (BD real)", "300000.00","300000.00", 361, "765.75"),
        ("Ejemplo del doc (30k de 513,973), 31 días",    "513973.20", "30000.00",  31, "13.38"),
    ]
    ok = 0
    print(f"{'caso':<48}{'C (oráculo)':>13}{'core':>9}{'dif':>8}")
    for desc, st, sc, d, esperado in casos:
        c = isr_retenido(st, sc, d); e = Decimal(esperado); dif = c - e
        marca = "OK" if abs(dif) <= Decimal("0.01") else "REVISAR"
        print(f"{desc:<48}{str(c):>13}{esperado:>9}{str(dif):>8}  {marca}")
        if abs(dif) <= Decimal("0.01"): ok += 1
    print(f"\n{ok}/{len(casos)} dentro de +/-0.01. (El ejemplo del doc usa /saldo_total corregido = 13.38, no 22.93.)")
    print("Persona moral (exencion 0):", isr_retenido("300000","300000",361, persona_moral=True), "-> base gravable = saldo total.")

if __name__ == "__main__":
    _autoprueba()
