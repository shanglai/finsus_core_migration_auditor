"""Modos de redondeo — parametro EXPLICITO por caso, nunca un default global.

El charter (§1.3) enumera los modos usados por las piezas K:
    Trunc20 · Trunc5 · Ceil10 · RoundHalfEven2 · Round2

Lectura CONFIRMADA contra S-FIS-001 §Precision y contra los oraculos ya
autoprobados (40_validaciones/entrega_finsus/oraculo_isr.py,
40_validaciones/comparadores/oraculo_rendimientos.py): el sufijo numerico es
el NUMERO DE DECIMALES y el prefijo es la direccion del corte.

    Trunc20         truncar (hacia cero) a 20 decimales   -> precision interna
    Trunc5          truncar a 5 decimales                 -> paso intermedio
    Ceil10          techo a 10 decimales
    RoundHalfEven2  redondeo bancario a 2 decimales       -> importe final
    Round2          medio-arriba a 2 decimales            -> importe final

[PENDIENTE menor · S-FIS-001] Para el ISR, F-016 no desambigua si el cierre a
2 decimales es half_even o half_up. El oraculo lo recibe como PARAMETRO
(`modo_final`) en vez de fijarlo: asi la ambiguedad queda visible en el
manifiesto de evidencia de cada corrida, no escondida en el codigo.

Ningun oraculo aplica un redondeo por su cuenta: lo recibe como parametro
obligatorio y lo aplica una sola vez, en el punto que la regla indique.
"""

from __future__ import annotations

import re
from decimal import ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

__all__ = ["MODOS", "aplicar", "es_modo_valido", "cuantizador"]

# nombre -> (rounding de decimal, decimales)
_PREFIJOS = {
    "Trunc": ROUND_FLOOR,          # se corrige a ROUND_UP si el valor es negativo
    "Ceil": ROUND_CEILING,
    "Floor": ROUND_FLOOR,
    "RoundHalfEven": ROUND_HALF_EVEN,
    "Round": ROUND_HALF_UP,
}

# Modos declarados por el charter. Se aceptan otros con la misma gramatica,
# pero estos son los que el catalogo puede citar sin nota adicional.
MODOS = ("Trunc20", "Trunc5", "Ceil10", "RoundHalfEven2", "Round2")

_PATRON = re.compile(r"^(Trunc|Ceil|Floor|RoundHalfEven|Round)(\d{1,3})$")


def _partir(modo: str) -> tuple[str, int]:
    m = _PATRON.match(modo or "")
    if not m:
        raise ValueError(
            f"Modo de redondeo desconocido: {modo!r}. "
            f"Gramatica: <Trunc|Ceil|Floor|RoundHalfEven|Round><decimales>. "
            f"Declarados en el charter: {', '.join(MODOS)}"
        )
    return m.group(1), int(m.group(2))


def es_modo_valido(modo: str) -> bool:
    return bool(_PATRON.match(modo or ""))


def cuantizador(modo: str) -> Decimal:
    """Devuelve el Decimal exponente usado para quantize (p.ej. 0.01)."""
    _, decimales = _partir(modo)
    return Decimal(1).scaleb(-decimales)


def aplicar(valor: Decimal, modo: str) -> Decimal:
    """Aplica `modo` a `valor`. Exige Decimal: un float aqui es un defecto.

    Trunc siempre trunca HACIA CERO (no hacia -infinito), que es lo que
    significa "truncar" en materia fiscal y contable.
    """
    if not isinstance(valor, Decimal):
        raise TypeError(
            f"redondeo.aplicar exige decimal.Decimal, recibio {type(valor).__name__}. "
            "Cero float en la ruta del dinero (charter §1.3)."
        )
    prefijo, decimales = _partir(modo)
    exp = Decimal(1).scaleb(-decimales)

    if prefijo == "Trunc":
        # hacia cero: FLOOR para positivos, CEILING para negativos
        rounding = ROUND_CEILING if valor < 0 else ROUND_FLOOR
    else:
        rounding = _PREFIJOS[prefijo]

    return valor.quantize(exp, rounding=rounding)
