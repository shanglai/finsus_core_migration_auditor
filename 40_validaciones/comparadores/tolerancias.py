# -*- coding: utf-8 -*-
"""
tolerancias.py — Reporte estandar de % de cuadre por motor en TRES granularidades.

Sustento: CLAUDE.md 10 (tolerancia de devengo <= $0.01 por evento Y ausencia de sesgo).
El auditor (SPA/runner) usa este modulo para que CADA motor de calculo reporte, sobre su
universo de pares (C, B), el porcentaje de coincidencia a:

  - 1e-8  (8 decimales)  -> exactitud aritmetica estricta: mismo calculo, sin diferencia perceptible.
  - 1e-5  (5 decimales)  -> precision intermedia: absorbe ruido de acumulacion/orden de operaciones,
                            pero NO tolera un centavo. Separa "redondeo interno" de "diferencia real".
  - 0.01  (al centavo)   -> tolerancia de negocio: lo que importa al cliente y a la contabilidad.

Lectura diagnostica del ESCALON entre niveles (esto es lo que hay que EXPLICAR, no solo mostrar):
  - 100 / 100 / 100                 -> cuadre EXACTO (mismo motor bit a bit a 8 dec).
  - bajo a 1e-8, alto al centavo     -> el residuo sub-centavo es granularidad/redondeo del snapshot,
                                        NO defecto  (ej. moratorio: ~81% a 1e-8, ~96% al centavo).
  - bajo tambien al centavo          -> hay diferencia MATERIAL que investigar (defecto / linaje / dato).

Ademas, sobre el residuo que cae FUERA de 1e-8 se corre una PRUEBA DE SIGNO: si las diferencias
tienen sesgo (se cargan a un lado), es defecto sistematico aunque cada una sea sub-centavo; si el
signo es aleatorio, es ruido de snapshot. Un sesgo estadisticamente distinto de cero = severidad 1.

Cero float en el calculo de deltas (todo decimal.Decimal). El z de la prueba de signo es un
estadistico (no monetario) y se computa en float a proposito, aislado del calculo de importes.
"""
from decimal import Decimal, getcontext
import math

getcontext().prec = 40

# (nombre, umbral, descripcion) — el orden importa: la primera escala es la "estricta" (base del sesgo)
LADDER = [
    ("1e-8",    Decimal("0.00000001"), "exactitud aritmetica estricta (8 decimales)"),
    ("1e-5",    Decimal("0.00001"),    "precision intermedia (5 decimales)"),
    ("centavo", Decimal("0.01"),       "tolerancia de negocio (al centavo)"),
]


def _D(x):
    """Convierte a Decimal sin pasar por float (acepta str, int, Decimal)."""
    return x if isinstance(x, Decimal) else Decimal(str(x))


def _q2(pct):
    """Porcentaje a 2 decimales."""
    return pct.quantize(Decimal("0.01"))


def resumen_tolerancias(pares, escalas=LADDER):
    """
    pares: iterable de (c, b)  -> valor del oraculo C y del core B (Decimal o convertible).
    Devuelve un dict serializable con n, el % de cuadre por escala, y la prueba de sesgo.
    """
    deltas = []
    for c, b in pares:
        deltas.append(_D(c) - _D(b))
    n = len(deltas)

    escalas_out = []
    for nombre, umbral, desc in escalas:
        n_ok = sum(1 for d in deltas if abs(d) <= umbral)
        pct = (Decimal(n_ok) / Decimal(n) * 100) if n else Decimal(0)
        escalas_out.append({
            "nombre": nombre, "umbral": str(umbral),
            "n_ok": n_ok, "n": n, "pct": str(_q2(pct)), "desc": desc,
        })

    # ---- prueba de signo sobre el residuo fuera de la escala estricta (1e-8) ----
    umbral0 = escalas[0][1]
    fuera = [d for d in deltas if abs(d) > umbral0]
    n_pos = sum(1 for d in fuera if d > 0)
    n_neg = sum(1 for d in fuera if d < 0)
    nf = n_pos + n_neg
    # z ~ (n_pos - nf/2) / sqrt(nf/4)  (aprox normal del test de signo; float, estadistico no monetario)
    z = (n_pos - nf / 2) / math.sqrt(nf / 4) if nf > 0 else 0.0
    sesgo = abs(z) > 3.0  # |z|>3  ~  p<0.003
    max_abs = max((abs(d) for d in deltas), default=Decimal(0))

    return {
        "n": n,
        "escalas": escalas_out,
        "sesgo": {
            "n_fuera_1e8": nf, "n_pos": n_pos, "n_neg": n_neg,
            "z": round(z, 2), "sesgo_detectado": sesgo,
            "lectura": ("SESGO sistematico (residuo se carga a un lado) -> severidad 1"
                        if sesgo else "residuo con signo aleatorio -> ruido de snapshot, no defecto"),
        },
        "max_abs_delta": str(max_abs),
    }


def linea_matriz(motor, res):
    """Renglon de tabla markdown: motor | 1e-8 | 1e-5 | centavo | n | sesgo."""
    e = {x["nombre"]: x["pct"] for x in res["escalas"]}
    s = "si" if res["sesgo"]["sesgo_detectado"] else "no"
    return (f"| {motor} | {e.get('1e-8','-')}% | {e.get('1e-5','-')}% | "
            f"{e.get('centavo','-')}% | {res['n']:,} | {s} |")


def imprimir(motor, res):
    """Salida de consola legible por el auditor."""
    print(f"[{motor}]  n={res['n']:,}")
    for x in res["escalas"]:
        print(f"    {x['nombre']:>7} (<= {x['umbral']}):  {x['pct']}%  ({x['n_ok']:,}/{x['n']:,})  — {x['desc']}")
    sg = res["sesgo"]
    print(f"    sesgo: {sg['lectura']}  (fuera 1e-8={sg['n_fuera_1e8']:,}, +{sg['n_pos']:,}/-{sg['n_neg']:,}, z={sg['z']})")
    print(f"    |delta| max = {res['max_abs_delta']}")


# --------------------------------------------------------------------------------------
# Autoprueba (sin BD): valida el propio helper con universos sinteticos de comportamiento conocido.
# --------------------------------------------------------------------------------------
def _autoprueba():
    D = Decimal
    ok = 0
    total = 0

    # Caso 1: cuadre EXACTO -> 100/100/100, sin sesgo.
    pares = [(D("10.00"), D("10.00"))] * 1000
    r = resumen_tolerancias(pares)
    e = {x["nombre"]: x["pct"] for x in r["escalas"]}
    total += 1
    if e["1e-8"] == "100.00" and e["centavo"] == "100.00" and not r["sesgo"]["sesgo_detectado"]:
        ok += 1
    else:
        print("FALLA caso 1", e, r["sesgo"])

    # Caso 2: residuo sub-centavo ALTERNADO (sin sesgo) -> bajo a 1e-8, 100% al centavo, sesgo=no.
    pares = []
    for i in range(1000):
        d = D("0.0005") if i % 2 == 0 else D("-0.0005")  # +/- 5 milesimas, se cancela
        pares.append((D("10.00") + d, D("10.00")))
    r = resumen_tolerancias(pares)
    e = {x["nombre"]: x["pct"] for x in r["escalas"]}
    total += 1
    # fuera de 1e-8 y de 1e-5 (0.0005 > 1e-5), pero <= centavo
    if e["1e-8"] == "0.00" and e["centavo"] == "100.00" and not r["sesgo"]["sesgo_detectado"]:
        ok += 1
    else:
        print("FALLA caso 2", e, r["sesgo"])

    # Caso 3: residuo sub-centavo SESGADO (siempre +) -> sesgo=si (severidad 1).
    pares = [(D("10.00") + D("0.003"), D("10.00"))] * 1000  # todos positivos, sub-centavo
    r = resumen_tolerancias(pares)
    e = {x["nombre"]: x["pct"] for x in r["escalas"]}
    total += 1
    if e["centavo"] == "100.00" and r["sesgo"]["sesgo_detectado"]:
        ok += 1
    else:
        print("FALLA caso 3", e, r["sesgo"])

    # Caso 4: mezcla realista -> 96.8% a 1e-8 exacto, resto sub-centavo aleatorio.
    pares = [(D("100.00"), D("100.00"))] * 968
    for i in range(32):
        d = D("0.004") if i % 2 == 0 else D("-0.004")
        pares.append((D("100.00") + d, D("100.00")))
    r = resumen_tolerancias(pares)
    e = {x["nombre"]: x["pct"] for x in r["escalas"]}
    total += 1
    if e["1e-8"] == "96.80" and e["centavo"] == "100.00":
        ok += 1
    else:
        print("FALLA caso 4", e)

    print(f"\nAUTOPRUEBA tolerancias: {ok}/{total} OK")
    if ok == total:
        print("\nEjemplo de salida por motor:")
        imprimir("demo-moratorio", r)


if __name__ == "__main__":
    _autoprueba()
