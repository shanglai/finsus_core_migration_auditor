# -*- coding: utf-8 -*-
"""Autoprueba del oraculo de ISR — SIN BD.

Reproduce los 5 casos de oro de S-FIS-001 (los mismos de la autoprueba 5/5 de
40_validaciones/entrega_finsus/oraculo_isr.py). Si esta bateria se rompe, el
motor C dejo de reproducir la regla y NINGUN veredicto del dominio FIS es
valido hasta arreglarla.
"""

from decimal import Decimal

import pytest

from oraculos.isr import (
    PARAMETROS_POR_ANIO,
    isr_retenido,
    isr_retenido_por_anio,
    parametros_anio,
)

CENTAVO = Decimal("0.01")

# (descripcion, saldo_total, saldo_cuenta, dias, esperado_del_core)
CASOS_ORO_2026 = [
    ("caso de oro inv.1 — 100-10-233102", "311136.07", "50182.96", 120, "46.37"),
    ("caso de oro inv.2 — 100-10-233102", "311136.07", "89175.01", 7, "4.81"),
    ("caso de oro inv.3 — 100-10-233102", "311136.07", "202.57", 30, "0.05"),
    ("BD real 1-10-370 — 300k a 361 dias", "300000.00", "300000.00", 361, "765.75"),
    ("ejemplo del doc — 30k de 513,973.20", "513973.20", "30000.00", 31, "13.38"),
]


@pytest.mark.parametrize("desc,total,cuenta,dias,esperado", CASOS_ORO_2026)
def test_casos_de_oro_2026(desc, total, cuenta, dias, esperado):
    c = isr_retenido_por_anio(total, cuenta, dias, anio=2026)
    assert abs(c - Decimal(esperado)) <= CENTAVO, f"{desc}: C={c} vs core={esperado}"


def test_persona_moral_sin_exencion():
    """LISR Art. 54: personas morales sin exencion -> base = saldo total."""
    con = isr_retenido_por_anio("300000", "300000", 361, anio=2026, persona_moral=True)
    sin = isr_retenido_por_anio("300000", "300000", 361, anio=2026, persona_moral=False)
    assert con > sin


def test_saldo_bajo_exencion_no_retiene():
    """Saldo total <= 5 x UMA: no hay base gravable, no se retiene."""
    assert isr_retenido_por_anio("100000", "100000", 365, anio=2026) == Decimal("0.00")


def test_cero_dias_no_retiene():
    assert isr_retenido_por_anio("300000", "300000", 0, anio=2026) == Decimal("0.00")


def test_saldo_total_cero_no_divide_entre_cero():
    assert isr_retenido_por_anio("0", "0", 30, anio=2026) == Decimal("0.00")


def test_denominador_es_saldo_total_no_base_gravable():
    """C-002 RESUELTA a favor de /saldo_total.

    Si alguien 'corrigiera' el oraculo a /base_gravable, el caso 1-10-370
    daria ~2,670 en vez de 765.76. Este test es el candado.
    """
    c = isr_retenido_por_anio("311136.07", "50182.96", 120, anio=2026)
    assert abs(c - Decimal("46.37")) <= CENTAVO
    assert c < Decimal("100"), "el denominador parece ser la base gravable, no el saldo total"


def test_float_en_dinero_es_rechazado():
    """Cero float en la ruta del dinero: no se convierte, se rechaza."""
    with pytest.raises(TypeError):
        isr_retenido(300000.0, "300000", 361, uma_anual="42794.64", tasa_anual="0.9")


def test_anio_desconocido_falla_en_vez_de_asumir():
    """Correr con parametros de otro ejercicio es el defecto C-001. Debe fallar."""
    with pytest.raises(KeyError):
        parametros_anio(2027)


def test_parametros_normativos_declarados():
    """Los parametros del catalogo normativo son los de K-FIS-004 / P-010."""
    assert PARAMETROS_POR_ANIO[2026]["uma_anual"] == "42794.64"
    assert PARAMETROS_POR_ANIO[2026]["tasa_anual"] == "0.9"
    assert PARAMETROS_POR_ANIO[2025]["uma_anual"] == "41273.52"
    # exencion = 5 x UMA
    exencion_2026 = Decimal(PARAMETROS_POR_ANIO[2026]["uma_anual"]) * Decimal("5")
    assert exencion_2026 == Decimal("213973.20")
    exencion_2025 = Decimal(PARAMETROS_POR_ANIO[2025]["uma_anual"]) * Decimal("5")
    assert exencion_2025 == Decimal("206367.60")
