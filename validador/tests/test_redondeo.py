# -*- coding: utf-8 -*-
"""Modos de redondeo — SIN BD.

El redondeo es parametro explicito por caso. Estos tests fijan la semantica de
cada modo declarado en el charter §1.3 y comprobada contra S-FIS-001 y los
oraculos ya autoprobados.
"""

from decimal import Decimal

import pytest

from engine.redondeo import MODOS, aplicar, cuantizador, es_modo_valido


def D(x):
    return Decimal(x)


def test_trunc_corta_hacia_cero_no_hacia_menos_infinito():
    """'Truncar' en materia fiscal es hacia cero, en los dos signos."""
    assert aplicar(D("1.999999"), "Trunc5") == D("1.99999")
    assert aplicar(D("-1.999999"), "Trunc5") == D("-1.99999")


def test_ceil10_va_hacia_arriba():
    assert aplicar(D("0.00000000001"), "Ceil10") == D("0.0000000001")


def test_round2_es_medio_arriba():
    assert aplicar(D("0.005"), "Round2") == D("0.01")
    assert aplicar(D("0.015"), "Round2") == D("0.02")


def test_roundhalfeven2_es_bancario():
    assert aplicar(D("0.005"), "RoundHalfEven2") == D("0.00")
    assert aplicar(D("0.015"), "RoundHalfEven2") == D("0.02")


def test_round2_y_halfeven2_difieren_en_el_medio_centavo():
    """La diferencia entre plazo y vista vive exactamente aqui (K-DEV-001)."""
    assert aplicar(D("0.005"), "Round2") != aplicar(D("0.005"), "RoundHalfEven2")


def test_trunc20_conserva_veinte_decimales():
    v = D("0.12345678901234567890123")
    assert aplicar(v, "Trunc20") == D("0.12345678901234567890")


def test_los_modos_del_charter_son_validos():
    for modo in MODOS:
        assert es_modo_valido(modo)
        assert isinstance(aplicar(D("1.23456789"), modo), Decimal)


def test_cuantizador_expone_el_exponente():
    assert cuantizador("Round2") == D("0.01")
    assert cuantizador("Ceil10") == D("1E-10")


def test_modo_desconocido_falla_en_vez_de_asumir():
    with pytest.raises(ValueError):
        aplicar(D("1.00"), "RedondeoNormal")


def test_float_se_rechaza():
    with pytest.raises(TypeError):
        aplicar(1.005, "Round2")
