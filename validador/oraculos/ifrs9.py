# -*- coding: utf-8 -*-
"""ORACULO IFRS 9 (motor C) — reserva de capital en etapa 3.

REUSA `40_validaciones/comparadores/oraculo_ifrs9.py` (autoprueba 14/14) en vez
de reescribir sus tablas: dos implementaciones de la misma regla son dos cosas
que pueden divergir. Aqui solo vive el adaptador fila -> Decimal.

Por que la independencia se sostiene: los porcentajes de C salen de las Tablas
1/2/3 del GTM-IFRS9, no de `lc_reserve_ifrs`. Leerlos de la configuracion del
core y compararlos contra el mismo core seria circular — probaria que el core
es consistente consigo mismo, no que aplica la norma. Que ademas coincidan
37/37 con `lc_reserve_ifrs` es un resultado, no el metodo.

    Etapa 3 = 90 dias o mas de mora
    Reserva de capital = capital vencido x % (por cartera, zona y dias de mora)

[ACLARADO 2026-08-24] El Core NO calcula PD: usa el % directo de CNBV
(DOF 04/jun/2012). El modelo EI x PI x SP que tambien trae el oraculo NO aplica
al motor de Aurum y no se usa aqui.

ALCANCE DELIBERADO: solo etapa 3, cartera de consumo, zona no marginada.
Lo que queda FUERA y por que:
  * E1/E2 amortizando — la base "capital / intereses exigibles" depende del
    spec, que sigue en el documento pendiente.
  * `reserva_int` — Finsus definio su composicion el 2026-08-24 (EPRC cubierta
    + expuesta + intereses vencidos, informativos en E3) pero sin formulas
    exactas.
  * comercio y reestructurado — llegan con las 9 tablas prometidas.
Cubrir esos hoy exigiria inventar la base, que es justo lo prohibido.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

_COMPARADORES = Path(__file__).resolve().parents[2] / "40_validaciones" / "comparadores"
if str(_COMPARADORES) not in sys.path:
    sys.path.insert(0, str(_COMPARADORES))

from oraculo_ifrs9 import etapa, pct_consumo, reserva_pct  # noqa: E402

from engine.redondeo import aplicar  # noqa: E402

VERSION_REGLA = "K-REG-001 / GTM-IFRS9 Tablas 1/2/3 (CNBV DOF 04-jun-2012)"

ETAPA_3 = 3


def reserva_capital_e3(capital_vencido, dias_mora, marginada: bool = False) -> Decimal:
    """Reserva de capital de un credito en etapa 3.

    `capital_vencido` se toma en valor absoluto: el staging lo guarda con signo
    negativo (es una contra-cuenta) y la reserva se expresa positiva en el
    activo. Comparar signos contrarios daria 100% de violaciones por una
    convencion de presentacion, no por un defecto.
    """
    cap = abs(_dec(capital_vencido))
    mora = int(dias_mora)
    if etapa(mora) != ETAPA_3:
        raise ValueError(
            f"{mora} dias de mora no es etapa 3: este oraculo solo cubre E3. "
            f"La base de E1/E2 amortizando depende del spec pendiente."
        )
    bruto = reserva_pct(cap, Decimal("0"), pct_consumo(mora, marginada))
    # `reserva_pct` devuelve el producto SIN redondear, a proposito: es un
    # insumo. El cierre a 2 decimales half-up lo confirmo Finsus el 2026-08-24
    # como homogeneo en todo el core y aplicado POR EVENTO. Omitirlo se noto en
    # la primera corrida: 5,133 diferencias sub-centavo, TODAS con C por debajo
    # de B, que la prueba de signo marco como sesgo. El sesgo era de no
    # redondear, no del core.
    return aplicar(bruto, "Round2")


def _dec(v) -> Decimal:
    if isinstance(v, Decimal):
        return v
    if isinstance(v, float):
        raise TypeError(f"float en la ruta del dinero: {v!r}")
    return Decimal(str(v))


def fila_reserva_e3(fila: dict, params: dict) -> Decimal:
    """Adaptador de IFRS9-E3."""
    return reserva_capital_e3(
        capital_vencido=fila["capital_venc"],
        dias_mora=fila["dias_mora"],
        marginada=str(fila.get("zona", "")).upper() == "MARGINAL",
    )
