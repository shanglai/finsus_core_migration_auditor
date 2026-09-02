# -*- coding: utf-8 -*-
"""La cohorte carga su propia procedencia.

Sale de la pregunta de la auditoria del 2026-08-28 sobre las 300 cuentas de
V-02: "la metodologia con la que determinaron cuantos y POR QUE". Sin metodo
declarado, un porcentaje no se extrapola. Un archivo de cohorte que es solo una
lista de numeros pierde esa informacion en cuanto sale de la carpeta.
"""

import subprocess
import sys
from pathlib import Path

import pytest

import cohorte

RAIZ = Path(__file__).resolve().parent.parent


class _Args:
    producto = "2301"
    desde = "2026-09-01"
    hasta = "2026-09-02"
    delimitador = "live"
    criterio = "censo"
    semilla = None
    n = 0


def _cab(**kw):
    a = _Args()
    for k, v in kw.items():
        setattr(a, k, v)
    return "\n".join(cohorte.cabecera(a, kw.pop("_disp", 12480), kw.pop("_tom", 300),
                                      "2026-09-02T00:00:00+00:00"))


def test_la_cabecera_declara_como_se_eligio():
    t = _cab(criterio="aleatorio", semilla=42)
    for campo in ("criterio", "disponibles", "tomadas", "representa", "semilla"):
        assert campo in t, f"la cohorte no declara {campo}"
    assert "2.40%" in t, "no expresa que fraccion del universo representa"


def test_la_muestra_determinista_se_marca_como_no_extrapolable():
    """Es el error facil: tomar las primeras N y tratarlas como aleatorias."""
    t = _cab(criterio="determinista", n=300)
    assert "NO es aleatoria" in t
    assert "NO para extrapolar" in t


def test_un_censo_recortado_deja_de_ser_censo_y_lo_dice():
    t = _cab(criterio="censo", _disp=12480, _tom=300)
    assert "Deja de ser censo" in t, (
        "un censo cortado por la cota se sigue llamando censo, que es una "
        "sobre-afirmacion de cobertura")


def test_el_censo_completo_no_se_marca():
    t = _cab(criterio="censo", _disp=300, _tom=300)
    assert "Deja de ser censo" not in t


def test_la_cabecera_declara_el_delimitador_y_que_no_se_mezclan():
    assert "no se mezclan" in _cab(delimitador="live")
    assert "FINSUS" in _cab(delimitador="migrado")


def test_el_lector_de_cli_ignora_la_cabecera():
    """Si cli.py no filtrara los '#', la procedencia entraria como cuentas."""
    from cli import parsear_params
    tmp = RAIZ / "tests" / "_cohorte_tmp.txt"
    tmp.write_text(_cab(criterio="aleatorio", semilla=1) + "\n100-2301-1\n100-2301-2\n",
                   encoding="utf-8")
    try:
        p = parsear_params([], str(tmp), None)
        assert p["cohorte"] == ["100-2301-1", "100-2301-2"]
    finally:
        tmp.unlink(missing_ok=True)


@pytest.mark.parametrize("argv,falta", [
    (["--desde", "2026-09-01", "--hasta", "2026-09-02", "--criterio", "aleatorio",
      "--n", "300"], "semilla"),
    (["--desde", "2026-09-01", "--hasta", "2026-09-02", "--criterio", "determinista"], "--n"),
])
def test_los_guardarrailes_bloquean_antes_de_tocar_la_base(argv, falta):
    """Ninguno de los dos errores debe llegar a conectarse: se rechazan antes."""
    r = subprocess.run([sys.executable, "cohorte.py", *argv], cwd=RAIZ,
                       capture_output=True, text=True, timeout=60)
    assert r.returncode != 0
    assert falta in (r.stdout + r.stderr)
