"""Prueba de signo — defensa anti-all-pass #4 (charter §5.4, §1.7).

Una tolerancia de $0.01 por evento NO basta. Si TODAS las diferencias caen
del mismo lado, el motor tiene un sesgo sistematico: cada evento cumple la
tolerancia y el agregado esta mal. Ese caso es severidad 1 aunque ninguna
diferencia individual pase de un centavo.

La prueba: bajo la hipotesis nula "el redondeo no favorece a nadie", el signo
de cada diferencia es una moneda justa. Se cuenta cuantas son positivas y
cuantas negativas (los ceros se descartan, es la prueba de signo estandar) y
se calcula la probabilidad exacta de ver un desbalance asi de extremo.

Determinismo: para n <= UMBRAL_EXACTO se usa la binomial EXACTA con enteros
(fracciones, sin punto flotante). Por arriba se usa la aproximacion normal
con math.erfc, que es determinista y suficiente a esos tamanos. El umbral
queda grabado en el resultado para que quien audite sepa cual se uso.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction

UMBRAL_EXACTO = 2000


@dataclass
class ResultadoSesgo:
    n_total: int
    n_positivas: int
    n_negativas: int
    n_ceros: int
    n_efectiva: int              # positivas + negativas (base de la prueba)
    p_valor: str                 # cadena para no arrastrar float a la evidencia
    alfa: str
    metodo: str                  # "binomial_exacta" | "normal_erfc"
    sesgo_detectado: bool
    severidad: int | None = None
    nota: str = ""
    extremos: dict = field(default_factory=dict)

    def como_dict(self) -> dict:
        return {
            "n_total": self.n_total,
            "n_positivas": self.n_positivas,
            "n_negativas": self.n_negativas,
            "n_ceros": self.n_ceros,
            "n_efectiva": self.n_efectiva,
            "p_valor": self.p_valor,
            "alfa": self.alfa,
            "metodo": self.metodo,
            "sesgo_detectado": self.sesgo_detectado,
            "severidad": self.severidad,
            "nota": self.nota,
            "extremos": self.extremos,
        }


def _p_valor_exacto(k: int, n: int) -> Fraction:
    """P(X <= k) + P(X >= n-k) con X ~ Bin(n, 1/2), en aritmetica exacta."""
    if n == 0:
        return Fraction(1)
    cola = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1))
    p = Fraction(2 * cola, 2 ** n)
    return min(p, Fraction(1))


def _p_valor_normal(k: int, n: int) -> float:
    """Aproximacion normal con correccion de continuidad. Determinista."""
    if n == 0:
        return 1.0
    media = n / 2.0
    desv = math.sqrt(n) / 2.0
    z = (abs(k - media) - 0.5) / desv
    if z <= 0:
        return 1.0
    return min(1.0, math.erfc(z / math.sqrt(2.0)))


def prueba_de_signo(diferencias, alfa: str = "0.01") -> ResultadoSesgo:
    """Corre la prueba de signo sobre las diferencias C - B.

    `diferencias` es un iterable de Decimal. Los ceros se descartan de la
    prueba pero se reportan: un universo mayoritariamente cero con un puñado
    de diferencias todas del mismo signo sigue siendo sesgo.
    """
    difs = [d if isinstance(d, Decimal) else Decimal(str(d)) for d in diferencias]
    n_total = len(difs)
    pos = sum(1 for d in difs if d > 0)
    neg = sum(1 for d in difs if d < 0)
    ceros = n_total - pos - neg
    n_ef = pos + neg
    alfa_frac = Fraction(Decimal(alfa))

    if n_ef == 0:
        return ResultadoSesgo(
            n_total=n_total, n_positivas=0, n_negativas=0, n_ceros=ceros,
            n_efectiva=0, p_valor="1", alfa=alfa, metodo="sin_diferencias",
            sesgo_detectado=False,
            nota="Todas las diferencias son exactamente cero: no hay sesgo que probar.",
        )

    k = min(pos, neg)
    if n_ef <= UMBRAL_EXACTO:
        p = _p_valor_exacto(k, n_ef)
        metodo = "binomial_exacta"
        detectado = p < alfa_frac
        p_txt = f"{float(p):.6g}" if p > 0 else "0"
    else:
        pf = _p_valor_normal(k, n_ef)
        metodo = "normal_erfc"
        detectado = pf < float(alfa_frac)
        p_txt = f"{pf:.6g}"

    lado = "positivo (C > B)" if pos > neg else "negativo (C < B)"
    nota = (
        f"Sesgo {lado}: {max(pos, neg)} de {n_ef} diferencias no nulas caen del mismo lado. "
        f"Severidad 1 (charter §1.7): el agregado esta mal aunque cada evento respete la tolerancia."
        if detectado else
        f"Sin sesgo detectable al alfa={alfa} ({pos} positivas / {neg} negativas)."
    )

    difs_no_cero = [d for d in difs if d != 0]
    extremos = {
        "min": str(min(difs)) if difs else None,
        "max": str(max(difs)) if difs else None,
        "suma": str(sum(difs, Decimal("0"))),
        "suma_absoluta": str(sum((abs(d) for d in difs_no_cero), Decimal("0"))),
    }

    return ResultadoSesgo(
        n_total=n_total, n_positivas=pos, n_negativas=neg, n_ceros=ceros,
        n_efectiva=n_ef, p_valor=p_txt, alfa=alfa, metodo=metodo,
        sesgo_detectado=detectado, severidad=1 if detectado else None,
        nota=nota, extremos=extremos,
    )
