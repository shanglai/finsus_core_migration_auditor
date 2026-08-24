# -*- coding: utf-8 -*-
"""Invariantes de honestidad del tablero — SIN BD.

Lo que se prueba no es que el tablero pinte bonito: es que NO PUEDA presentar
como verificado algo que no lo esta.
"""

import json
import re
from pathlib import Path

import pytest

import motores as M
import runner as R

RAIZ = Path(__file__).resolve().parent.parent


# --- La tabla de motores espeja el DOSSIER ---------------------------------

def test_hay_dieciseis_motores():
    assert len(M.MOTORES) == 16


@pytest.mark.parametrize("m", M.MOTORES, ids=lambda m: m.id)
def test_todo_motor_declara_contra_que_se_valida(m):
    """Sin fuente no hay validacion, hay opinion."""
    assert m.fuentes, f"{m.id} no declara ninguna fuente"
    for f in m.fuentes:
        assert f.tipo in M.TIPO_VALIDACION, f"{m.id}: tipo de fuente invalido {f.tipo}"
        assert f.cita.strip(), f"{m.id}: fuente sin cita"


@pytest.mark.parametrize("m", M.MOTORES, ids=lambda m: m.id)
def test_todo_motor_declara_formula_y_estado(m):
    assert m.formula.strip()
    assert m.estado in M.ESTADOS


@pytest.mark.parametrize("m", M.MOTORES, ids=lambda m: m.id)
def test_lo_bloqueado_dice_por_que(m):
    if m.estado == "bloqueado":
        assert m.bloqueo.strip(), f"{m.id} esta bloqueado y no explica que falta"


@pytest.mark.parametrize("m", M.MOTORES, ids=lambda m: m.id)
def test_la_clase_de_no_conforme_es_del_vocabulario(m):
    if m.clase_no_conforme:
        assert m.clase_no_conforme in M.CLASES_NO_CONFORME


def test_la_inferencia_se_marca_como_por_confirmar():
    """Una mecanica deducida NO se puede presentar como hecho documentado."""
    assert "POR CONFIRMAR" in M.TIPO_VALIDACION["inferencia"].upper()
    inferidos = [m.id for m in M.MOTORES if any(f.tipo == "inferencia" for f in m.fuentes)]
    assert inferidos, "se perdio el marcado de inferencia"


def test_config_es_la_validacion_mas_fuerte_y_esta_dicho():
    assert "mas fuerte" in M.TIPO_VALIDACION["config"]


# --- La distincion que sostiene el tablero ---------------------------------

def test_un_numero_del_dossier_nunca_se_marca_como_calculado_aqui():
    """Es el invariante central: citar no es calcular."""
    autos = {m.id: {"ok": True, "detalle": "x"} for m in M.MOTORES}
    for m in M.MOTORES:
        d = R.construir(m, autos, con_bd=False, params={})
        assert d["origen_resultado"] != "corrida_local", \
            f"{m.id} se marco como calculado localmente sin haber corrido"
        if m.dossier_pct:
            assert d["origen_resultado"] == "dossier"
            assert d["pct_mostrado"] == m.dossier_pct
        else:
            assert d["origen_resultado"] == "sin_cruce"
            assert d["pct_mostrado"] is None


def test_sin_cruce_no_muestra_porcentaje():
    autos = {m.id: {"ok": True, "detalle": "x"} for m in M.MOTORES}
    for m in M.MOTORES:
        d = R.construir(m, autos, con_bd=False, params={})
        if d["origen_resultado"] == "sin_cruce":
            assert d["pct_mostrado"] is None, f"{m.id}: sin cruce pero muestra un %"


# --- Autopruebas: la formula reproduce el ejemplo del documento -------------

def test_las_autopruebas_de_formula_pasan():
    res = R.correr_autopruebas()
    fallan = {k: v["detalle"] for k, v in res.items() if v["ok"] is False}
    assert not fallan, f"oraculos que no reproducen su ejemplo: {fallan}"


def test_cubren_a_todos_los_motores():
    res = R.correr_autopruebas()
    assert set(res) >= {m.id for m in M.MOTORES}


# --- Nada de PII al frontend ------------------------------------------------

def test_los_ids_de_muestra_van_truncados():
    fuente = (RAIZ / "backend" / "runner.py").read_text(encoding="utf-8")
    assert "[:24]" in fuente, "los identificadores de muestra deben truncarse"


def test_los_no_conformes_nunca_se_muestrean():
    """Muestrear no conformes seria ocultar hallazgos."""
    fuente = (RAIZ / "backend" / "runner.py").read_text(encoding="utf-8")
    assert "no_conf + conformes" in fuente
    assert "conformes_omitidos" in fuente


def test_las_salidas_no_se_versionan():
    gi = (RAIZ.parent / ".gitignore").read_text(encoding="utf-8")
    assert "auditor_spa/resultados/" in gi
    assert "auditor_spa/spa/datos.js" in gi


# --- El SPA es autocontenido ------------------------------------------------

def test_el_spa_no_carga_nada_por_cdn():
    """CSP y reproducibilidad: cero dependencias remotas."""
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    remotos = re.findall(r'(?:src|href)\s*=\s*["\'](https?:)?//[^"\']+', html)
    assert not remotos, f"el SPA carga recursos remotos: {remotos}"


def test_el_spa_avisa_que_verde_no_es_aprobado():
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "Verde no es aprobado" in html


def test_el_spa_distingue_los_tres_origenes():
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    for clave in ("corrida_local", "dossier", "sin_cruce"):
        assert clave in html


# --- El corpus del agente ---------------------------------------------------

def test_el_corpus_del_agente_se_construye():
    import dossier
    c = dossier.construir()
    assert len(c["secciones"]) > 50
    assert not c["documentos_faltantes"], f"faltan documentos: {c['documentos_faltantes']}"
    for s in c["secciones"][:20]:
        assert s["doc"] and s["titulo"] and s["busqueda"]


def test_toda_seccion_es_citable():
    """El agente cita documento y linea: sin eso no puede sostener nada."""
    import dossier
    for s in dossier.construir()["secciones"]:
        assert s["doc"] and isinstance(s["linea"], int)
