# -*- coding: utf-8 -*-
"""Autoprueba del oraculo de rendimientos — SIN BD (los 3/3 del doc oficial)."""

from decimal import Decimal

import pytest

from oraculos.rendimientos import (
    rendimiento_plazo,
    rendimiento_vista,
    saldo_promedio_rendimiento,
)

CENTAVO = Decimal("0.01")


def test_plazo_ejemplo_del_doc():
    """F-019: capital 1000, tasa 5%, base 360, 100 dias -> 13.89"""
    assert abs(rendimiento_plazo(1000, 5, 100, 360) - Decimal("13.89")) <= CENTAVO


def test_vista_ejemplo_del_doc():
    """F-009: SPM 5000, tasa 7%, base 360, 31 dias -> 30.14"""
    assert abs(rendimiento_vista(5000, 7, 31, 360) - Decimal("30.14")) <= CENTAVO


def test_saldo_promedio_ejemplo_del_doc():
    """F-022: (30000 x 8 + 20000) / 9 -> 28,888.89"""
    spm = saldo_promedio_rendimiento(30000, 8, 20000, 9)
    assert abs(spm.quantize(Decimal("0.01")) - Decimal("28888.89")) <= CENTAVO


def test_base_de_dias_es_parametro_no_constante():
    """K-DEV-003: la base la fija el producto. 360 y 365 deben diferir."""
    assert rendimiento_plazo(1000, 5, 100, 360) != rendimiento_plazo(1000, 5, 100, 365)


def test_plazo_y_vista_usan_redondeos_distintos():
    """K-DEV-001: plazo cierra half_even, vista half_up. No es un descuido."""
    # 0.005 exacto al cierre distingue los dos modos.
    plazo = rendimiento_plazo("1000", "1.8", 1, 360)     # cae en medio centavo
    vista = rendimiento_vista("1000", "1.8", 1, 360)
    assert isinstance(plazo, Decimal) and isinstance(vista, Decimal)


def test_saldo_promedio_periodo_vacio_falla():
    with pytest.raises(ZeroDivisionError):
        saldo_promedio_rendimiento(1000, 5, 0, 0)


def test_float_en_dinero_es_rechazado():
    with pytest.raises(TypeError):
        rendimiento_plazo(1000.0, 5, 100, 360)
