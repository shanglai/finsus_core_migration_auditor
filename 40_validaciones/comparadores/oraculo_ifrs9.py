"""
ORACULO IFRS 9 — reservas de credito (motor C, independiente).
Fuente: doc oficial "Módulo IFRS 9 - Reglas de negocio" + "Mapa Guía IFRS 9" (D-IFR / D-REG).
decimal.Decimal, cero float.

ETAPAS (D-IFR p.21 Tabla 4):
  Etapa 1: 0-30 dias mora   (perdida esperada 12 meses)
  Etapa 2: 31-89 dias mora  (perdida esperada vida completa)
  Etapa 3: >=90 dias mora   (incumplimiento)

RESERVA % DIRECTO (Consumo / Microcredito / Vivienda) — D-IFR p.7-8, Tablas 1/2/3:
  Reserva = (Capital exigible + Intereses exigibles) * %   ; % por dias de mora y zona marginada.

RESERVA COMERCIAL (modelo EI x PI x SP) — D-IFR p.9-15:
  EI  = EI_capital + EI_intereses ; E1/E2: intereses exigibles al corte; E3: intereses hasta dia 89.
  SP  sin garantia E1/E2: Ent.Fed/Mpio/Fin=45%, PM/PF empresarial=55%; E3 por meses en E3 (Tabla 5).
  Reserva E1 o E3: EI*PI*SP.
  Reserva E2 (vida completa): (PI*SP*EI)/(r+PI) * [1 - ((1-PI)^n / (1+r)^n)] ; r=tasa anual (si 0 -> 0.00001%),
        n = max(dias_remanentes/365.25, 1). Reserva E2 final = Max(vida completa, PI*SP*EI).

NOTA: la tabla numerica de PI (probabilidad de incumplimiento) NO esta en el doc -> PI es parametro de entrada.
Zona marginada: 1=no marginada, 2=marginada (D-REG R454).
"""
from decimal import Decimal, ROUND_HALF_UP, getcontext
getcontext().prec = 50
D = lambda x: x if isinstance(x, Decimal) else Decimal(str(x))


def etapa(dias_mora):
    d = int(dias_mora)
    if d <= 30: return 1
    if d <= 89: return 2
    return 3


# --- Tablas de % de estimacion preventiva [no_marginada, marginada] por (tope_dias) ---
# Tabla 1 — Consumo (D-IFR p.18)
_T_CONSUMO = [(0, "1", "1"), (7, "4", "1"), (30, "15", "4"),
              (60, "30", "30"), (89, "50", "60"),
              (120, "75", "80"), (180, "90", "90"), (10**9, "100", "100")]
# Tabla 3 — Comercial microcredito (D-IFR p.20)
_T_MICRO = [(7, "1", "1"), (30, "5", "2.5"), (60, "20", "20"), (89, "40", "50"),
            (120, "70", "80"), (10**9, "100", "100")]
# Tabla 2 — Vivienda (D-IFR p.19) — sin distincion de zona marginada
_T_VIVIENDA = [(0, "0.35"), (30, "1.05"), (60, "2.45"), (89, "8.75"),
               (120, "17.50"), (150, "33.25"), (180, "34.30"), (1460, "70"), (10**9, "100")]
# Tabla 5 — SP sin garantia por meses en Etapa 3 [ent.fed/mpio/fin, PM/PF empresarial] (D-IFR p.22)
_T_SP_E3 = [(3, "45", "55"), (6, "55", "62"), (9, "62", "69"), (12, "66", "72"),
            (15, "72", "77"), (18, "75", "79"), (21, "78", "82"), (24, "81", "84"),
            (27, "88", "90"), (30, "91", "93"), (33, "94", "95"), (36, "96", "97"),
            (10**9, "100", "100")]


def _lookup(tabla, dias, col):
    for fila in tabla:
        if dias <= fila[0]:
            return Decimal(fila[col])
    return Decimal(fila[col])


def pct_consumo(dias_mora, marginada=False):
    """% de estimacion preventiva, cartera de consumo (Tabla 1)."""
    return _lookup(_T_CONSUMO, int(dias_mora), 2 if marginada else 1)


def pct_microcredito(dias_mora, marginada=False):
    """% de estimacion preventiva, comercial microcredito (Tabla 3)."""
    return _lookup(_T_MICRO, int(dias_mora), 2 if marginada else 1)


def pct_vivienda(dias_mora):
    """% de estimacion preventiva, vivienda (Tabla 2)."""
    return _lookup(_T_VIVIENDA, int(dias_mora), 1)


def reserva_pct(capital_exigible, interes_exigible, pct):
    """Reserva = (capital exigible + intereses exigibles) * (%/100). Devuelve Decimal."""
    return (D(capital_exigible) + D(interes_exigible)) * (D(pct) / Decimal(100))


# --- Modelo comercial EI x PI x SP ---
def ei(capital_insoluto, intereses_exigibles):
    """Exposicion al Incumplimiento = capital insoluto + intereses exigibles (E3: intereses solo hasta dia 89,
    el que llama debe pasar ya recortados los intereses)."""
    return D(capital_insoluto) + D(intereses_exigibles)


def sp_sin_garantia(stage, tipo="empresarial", meses_en_e3=0):
    """SP sin garantia. tipo: 'financiera' (ent.fed/mpio/entidad fin, 45%) | 'empresarial' (PM/PF, 55%).
    E1/E2 = base; E3 ajusta por meses en E3 (Tabla 5)."""
    col = 1 if tipo == "financiera" else 2
    if stage in (1, 2):
        return Decimal("45") if tipo == "financiera" else Decimal("55")
    return _lookup(_T_SP_E3, int(meses_en_e3), col)


def reserva_comercial(ei_val, pi, sp, stage, tasa_anual=Decimal("0"), dias_remanentes=None):
    """Reserva comercial. pi y sp en fraccion (0.05) o %? -> aqui en FRACCION (0.05 = 5%).
    E1/E3: EI*PI*SP. E2: Max(vida_completa, EI*PI*SP)."""
    EI = D(ei_val); PI = D(pi); SP = D(sp)
    simple = EI * PI * SP
    if stage in (1, 3):
        return simple
    # Etapa 2 — vida completa
    r = D(tasa_anual)
    if r == 0:
        r = Decimal("0.0000001")  # 0.00001%
    n = max((D(dias_remanentes) / Decimal("365.25")) if dias_remanentes is not None else Decimal(1), Decimal(1))
    vida = (PI * SP * EI) / (r + PI) * (Decimal(1) - ((Decimal(1) - PI) ** n) / ((Decimal(1) + r) ** n))
    return max(vida, simple)


def _r2(x):
    return D(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


if __name__ == "__main__":
    import sys
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    print("ORACULO IFRS 9 — autoprueba estructural (tablas del doc D-IFR)\n")
    casos = []
    # etapas
    casos.append(("etapa(15)", etapa(15), 1)); casos.append(("etapa(45)", etapa(45), 2)); casos.append(("etapa(120)", etapa(120), 3))
    # % consumo
    casos.append(("pct_consumo(45)=E2 31-60 =30", pct_consumo(45), Decimal("30")))
    casos.append(("pct_consumo(5)=E1 1-7 =4", pct_consumo(5), Decimal("4")))
    casos.append(("pct_consumo(5,marg)=1", pct_consumo(5, True), Decimal("1")))
    casos.append(("pct_consumo(200)=E3 >=181 =100", pct_consumo(200), Decimal("100")))
    # % microcredito
    casos.append(("pct_micro(70)=E2 61-89 =40", pct_microcredito(70), Decimal("40")))
    casos.append(("pct_micro(70,marg)=50", pct_microcredito(70, True), Decimal("50")))
    # % vivienda
    casos.append(("pct_vivienda(100)=E3 90-120 =17.50", pct_vivienda(100), Decimal("17.50")))
    # reserva % : consumo 1000 cap + 100 int, 45 dias -> 30% -> 330
    casos.append(("reserva_consumo(1000,100,45d)=330", _r2(reserva_pct(1000, 100, pct_consumo(45))), Decimal("330.00")))
    # SP
    casos.append(("sp_sin_gar(E1,empr)=55", sp_sin_garantia(1), Decimal("55")))
    casos.append(("sp_sin_gar(E3,empr,7m)=69", sp_sin_garantia(3, "empresarial", 7), Decimal("69")))
    # reserva comercial E1: EI 10000, PI 0.05, SP 0.55 -> 275
    casos.append(("reserva_com(E1,EI10000,PI.05,SP.55)=275", _r2(reserva_comercial(10000, Decimal("0.05"), Decimal("0.55"), 1)), Decimal("275.00")))
    ok = 0
    for desc, got, exp in casos:
        m = (got == exp) if not isinstance(exp, Decimal) else (abs(D(got) - exp) <= Decimal("0.01"))
        ok += m
        print(f"  {desc:<45} = {str(got):>10}  esperado {str(exp):>8}  {'OK' if m else 'REVISAR'}")
    print(f"\n{ok}/{len(casos)} OK.")
