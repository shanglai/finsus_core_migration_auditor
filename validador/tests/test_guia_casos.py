# -*- coding: utf-8 -*-
"""§11 del brief, como invariantes EJECUTABLES — no como documentacion.

El propio brief se queja de que estas tres cosas "se redescubren caso tras
caso". Un documento que nadie relee se rompe en silencio; una prueba que falla
al agregar un caso nuevo, no. Cada regla de
`validador/guia/CONSTRUIR_UN_CASO.md` tiene aqui su verificacion.
"""

import re
from decimal import Decimal
from pathlib import Path

import pytest

from engine import catalogo as cat
from engine import config

CASOS = cat.cargar_todos()
GUIA = config.RAIZ / "guia" / "CONSTRUIR_UN_CASO.md"
ORACULOS = sorted((config.RAIZ / "oraculos").glob("*.py"))


# --- §11.1 Independencia ----------------------------------------------------

def test_la_guia_existe_y_cubre_las_cuatro_reglas():
    txt = GUIA.read_text(encoding="utf-8")
    for tema in ("Independencia", "convenciones", "Playbook del sesgo", "alcance"):
        assert tema.lower() in txt.lower(), f"la guia no cubre {tema}"


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_leer_un_parametro_del_core_se_declara(cid):
    """§11.1: un parametro tomado del core es una dependencia, y se declara.

    No se prohibe —hay hechos del contrato que solo viven ahi— pero tiene que
    estar escrito en `supuestos:` para que quien lea el resultado sepa que
    prueba se perdio.
    """
    c = CASOS[cid]
    if not c.ejecutable:
        return
    sospechosas = ("interest_rate", "system_configuration", "cat_tax",
                   "lc_reserve_ifrs", "account_yield")
    for core, ruta in c.extraccion.items():
        if str(ruta).upper() == cat.PENDIENTE:
            continue
        sql = config.resolver_ruta(ruta).read_text(encoding="utf-8").lower()
        usadas = [s for s in sospechosas if s in sql]
        if not usadas:
            continue
        texto = " ".join(c.supuestos).lower() + " " + c.identidad.lower() + \
                " " + c.matriz_esperada.lower() + " " + (c.cobertura_nota or "").lower()
        assert texto.strip(), f"{cid} lee {usadas} del core y no declara nada"
        assert any(p in texto for p in ("independen", "circular", "del core", "de la config",
                                        "configurad", "tasa", "no sustituye", "parametro")), \
            (f"{cid} lee {usadas} del core y sus supuestos no lo declaran. "
             f"§11.1: si el parametro viene del core, hay que decir que prueba se pierde.")


# --- §11.2 Convenciones confirmadas ----------------------------------------

def test_ningun_oraculo_usa_float():
    for p in ORACULOS:
        txt = p.read_text(encoding="utf-8")
        assert "float(" not in txt.replace("isinstance(valor, float)", "") \
                                  .replace("isinstance(v, float)", ""), \
            f"{p.name}: float en la ruta del dinero (§11.2)"


def test_los_oraculos_declaran_su_modo_de_redondeo():
    """El modo es explicito, nunca el default de la biblioteca."""
    for p in ORACULOS:
        txt = p.read_text(encoding="utf-8")
        if "quantize" in txt:
            assert "rounding=" in txt, f"{p.name}: quantize sin modo explicito"


def test_el_redondeo_del_proyecto_es_half_up():
    """Finsus confirmo half-up homogeneo por evento (2026-08-24)."""
    from engine.redondeo import aplicar
    assert aplicar(Decimal("0.005"), "Round2") == Decimal("0.01")
    from oraculos import isr
    assert isr.MODO_FINAL_DEFAULT == "Round2", \
        "el cierre del ISR debe ser half-up: Finsus lo confirmo"


def test_la_base_de_dias_es_parametro_no_constante():
    """§11.2: 360 o 365 segun el esquema — no asumir."""
    for cid, c in CASOS.items():
        if not c.ejecutable:
            continue
        nombres = {p.nombre for p in c.parametros}
        if "dias_anio" in nombres:
            p = next(x for x in c.parametros if x.nombre == "dias_anio")
            assert p.nota, f"{cid}: dias_anio sin nota que diga de donde sale la base"


# --- §11.3 Playbook del sesgo ----------------------------------------------

def test_todo_caso_con_sesgo_declara_como_leerlo():
    """Una bandera roja sin lectura se interpreta como defecto del core.

    §11.3: un sesgo sub-centavo de un solo signo es, por omision, del metodo.
    El caso tiene que decirlo donde se lee el resultado.
    """
    for cid, c in CASOS.items():
        if not (c.tolerancia.prueba_sesgo and c.ejecutable):
            continue
        texto = (c.matriz_esperada + " " + " ".join(c.supuestos) + " " +
                 (c.cobertura_nota or "")).lower()
        assert any(p in texto for p in ("sesgo", "signo")), \
            (f"{cid} corre prueba de sesgo y no explica como leer la bandera. "
             f"§11.3: hay que distinguir sesgo del metodo del sesgo del core.")


def test_la_guia_fija_el_orden_del_playbook():
    txt = GUIA.read_text(encoding="utf-8")
    i_red = txt.lower().index("redondeaste half-up")
    i_base = txt.lower().index("precisión de la base")
    i_def = txt.lower().index("candidato a defecto")
    assert i_red < i_base < i_def, \
        "el playbook debe ir redondeo -> base -> defecto, en ese orden"


# --- §11.4 Declaracion de alcance ------------------------------------------

@pytest.mark.parametrize("cid", sorted(CASOS))
def test_todo_caso_declara_su_alcance(cid):
    """Lo que queda fuera se escribe, con su motivo."""
    c = CASOS[cid]
    tiene = bool(c.bloqueo) or bool(c.supuestos) or bool(c.cobertura_nota)
    assert tiene, (f"{cid} no declara alcance: ni bloqueo, ni supuestos, ni nota de "
                   f"cobertura. §11.4 pide escribir lo que se deja fuera.")


def test_los_casos_ejecutables_declaran_supuestos():
    """Un caso que corre contra datos SIEMPRE tiene decisiones de modelado."""
    for cid, c in CASOS.items():
        if c.ejecutable:
            assert c.supuestos, (f"{cid} es ejecutable y no declara ni un supuesto. "
                                 f"Correr contra datos siempre exige decidir algo.")
