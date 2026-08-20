# -*- coding: utf-8 -*-
"""Invariantes del comparador — SIN BD.

Lo que se prueba aqui no es "el codigo corre": es que el comparador NO puede
devolver un pase por descuido. Las cinco celdas de la matriz, las filas
faltantes, el universo vacio y la ausencia de motor A.
"""

from decimal import Decimal

import polars as pl
import pytest

from engine import compare

LLAVES = ["cuenta"]
TOL = Decimal("0.01")


def _df(cuentas, valores, col):
    return pl.DataFrame({"cuenta": cuentas, col: [str(v) for v in valores]})


def _correr(a, b, c, tol=TOL):
    cuentas = [f"c{i}" for i in range(len(b))]
    df_a = _df(cuentas, a, "isr_of") if a is not None else None
    return compare.comparar_montos(
        caso_id="TEST", df_b=_df(cuentas, b, "isr_ac"), df_c=_df(cuentas, c, "isr_c"),
        llaves=LLAVES, col_b="isr_ac", col_c="isr_c", tolerancia=tol,
        df_a=df_a, col_a="isr_of" if a is not None else None,
    )


# --- Las cinco celdas -------------------------------------------------------

def test_celda_todos_coinciden():
    r = _correr(["10.00"], ["10.00"], ["10.00"])
    assert r.matriz == {compare.CELDA_OK: 1}
    assert r.n_violaciones == 0
    assert r.veredicto() == "SIN-VIOLACIONES"


def test_celda_ambos_cores_mal_es_severidad_maxima():
    """A=B!=C: los dos cores se apartan de la norma. Es el peor caso."""
    r = _correr(["10.00"], ["10.00"], ["12.00"])
    assert r.matriz == {compare.CELDA_DEFECTO_NEGOCIO: 1}
    assert r.n_violaciones == 1
    assert "AMBOS cores" in compare.INTERPRETACION[compare.CELDA_DEFECTO_NEGOCIO]


def test_celda_openfin_corregido():
    """A!=B=C: OpenFin tenia el defecto y AurumCore lo corrigio. No viola."""
    r = _correr(["12.00"], ["10.00"], ["10.00"])
    assert r.matriz == {compare.CELDA_OF_CORREGIDO: 1}
    assert r.n_violaciones == 0


def test_celda_defecto_de_aurum():
    """A=C!=B: AurumCore se aparta donde OpenFin no lo hacia."""
    r = _correr(["10.00"], ["12.00"], ["10.00"])
    assert r.matriz == {compare.CELDA_DEFECTO_AURUM: 1}
    assert r.n_violaciones == 1


def test_celda_regla_mal_especificada():
    """A!=B!=C: los tres distintos. La regla, no el motor."""
    r = _correr(["10.00"], ["12.00"], ["14.00"])
    assert r.matriz == {compare.CELDA_REGLA_MAL: 1}
    assert r.n_violaciones == 1


# --- Lo que no puede pasar por alto ----------------------------------------

def test_universo_vacio_no_es_un_pase():
    """Cero filas comparadas NUNCA se lee como 'paso'."""
    vacio = pl.DataFrame({"cuenta": [], "isr_ac": []}, schema={"cuenta": pl.Utf8, "isr_ac": pl.Utf8})
    vacio_c = pl.DataFrame({"cuenta": [], "isr_c": []}, schema={"cuenta": pl.Utf8, "isr_c": pl.Utf8})
    r = compare.comparar_montos("TEST", vacio, vacio_c, LLAVES, "isr_ac", "isr_c", TOL)
    assert r.universo_vacio
    assert r.veredicto() == "UNIVERSO-VACIO"
    assert r.veredicto() != "SIN-VIOLACIONES"
    assert any("NO es un pase" in n for n in r.notas)


def test_fila_faltante_en_aurum_es_violacion():
    """Si el core no tiene la fila, es violacion — no un renglon a ignorar."""
    df_b = pl.DataFrame({"cuenta": ["c1"], "isr_ac": ["10.00"]})
    df_c = pl.DataFrame({"cuenta": ["c1", "c2"], "isr_c": ["10.00", "5.00"]})
    r = compare.comparar_montos("TEST", df_b, df_c, LLAVES, "isr_ac", "isr_c", TOL)
    assert r.n_violaciones == 1
    assert r.matriz.get(compare.CELDA_SIN_B) == 1
    assert "faltante" in r.violaciones["motivo"][0]


def test_fila_sin_oraculo_es_violacion_no_pase():
    """Si el oraculo no pudo calcular, la fila NO se descarta: cuenta como violacion."""
    df_b = pl.DataFrame({"cuenta": ["c1"], "isr_ac": ["10.00"]})
    df_c = pl.DataFrame({"cuenta": ["c1"], "isr_c": [None]}, schema={"cuenta": pl.Utf8, "isr_c": pl.Utf8})
    r = compare.comparar_montos("TEST", df_b, df_c, LLAVES, "isr_ac", "isr_c", TOL)
    assert r.n_violaciones == 1
    assert r.matriz.get(compare.CELDA_SIN_C) == 1


def test_sin_motor_a_no_se_lee_como_coincidencia():
    """Ausencia de A se ETIQUETA, nunca se cuenta como A=B=C."""
    r = _correr(None, ["10.00"], ["10.00"])
    assert compare.CELDA_OK not in r.matriz
    assert r.matriz == {compare.CELDA_SIN_A: 1}
    assert any("sin motor A" in n for n in r.notas)


def test_tolerancia_se_respeta_al_centavo():
    r = _correr(None, ["10.00"], ["10.01"])
    assert r.n_violaciones == 0
    r = _correr(None, ["10.00"], ["10.02"])
    assert r.n_violaciones == 1


def test_float_en_columna_de_dinero_aborta():
    """Un float en la ruta del dinero invalida la corrida, no se convierte."""
    df_b = pl.DataFrame({"cuenta": ["c1"], "isr_ac": [10.0]})
    df_c = pl.DataFrame({"cuenta": ["c1"], "isr_c": ["10.00"]})
    with pytest.raises(compare.FloatEnDinero):
        compare.comparar_montos("TEST", df_b, df_c, LLAVES, "isr_ac", "isr_c", TOL)


def test_decimales_grandes_no_pierden_precision():
    """El cruce va por cadena: 20 decimales sobreviven intactos."""
    a = "0.00000000000000000001"
    r = _correr(None, ["0.00000000000000000000"], [a], tol=Decimal("0"))
    assert r.n_violaciones == 1
    # La diferencia se guarda como cadena; Decimal la imprime en notacion
    # cientifica, pero el VALOR es exacto — que es lo que importa.
    assert Decimal(r.violaciones["dif_c_menos_b"][0]) == Decimal(a)


# --- Existencia -------------------------------------------------------------

def test_existencia_reporta_los_dos_sentidos():
    df_a = pl.DataFrame({"id": ["1", "2", "3"]})
    df_b = pl.DataFrame({"id": ["2", "3", "4"]})
    r = compare.comparar_existencia("TEST", df_a, df_b, ["id"])
    assert r.n_violaciones == 2
    faltan = set(zip(r.violaciones["id"].to_list(), r.violaciones["falta_en"].to_list()))
    assert ("1", "aurum") in faltan
    assert ("4", "openfin") in faltan


def test_existencia_vacia_no_es_pase():
    vacio = pl.DataFrame({"id": []}, schema={"id": pl.Utf8})
    r = compare.comparar_existencia("TEST", vacio, vacio, ["id"])
    assert r.veredicto() == "UNIVERSO-VACIO"


# --- Doble partida ----------------------------------------------------------

def test_doble_partida_tolerancia_cero():
    df = pl.DataFrame({
        "poliza": ["p1", "p1", "p2", "p2"],
        "cargo": ["100.00", "0.00", "100.00", "0.00"],
        "abono": ["0.00", "100.00", "0.00", "99.99"],
    })
    r = compare.comparar_doble_partida("TEST", df, ["poliza"], "cargo", "abono")
    assert r.n_violaciones == 1
    assert r.violaciones["poliza"][0] == "p2"
    assert r.violaciones["descuadre"][0] == "0.01"
    assert r.tolerancia == "0.00"
