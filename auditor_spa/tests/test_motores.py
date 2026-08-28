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


# --- Navegacion por categoria ----------------------------------------------

def test_todo_motor_cae_en_una_categoria_del_menu():
    for m in M.MOTORES:
        assert m.categoria in M.CATEGORIAS, f"{m.id} cae en '{m.categoria}', fuera del menu"


def test_las_categorias_cubren_los_dieciseis():
    agrupados = sum(len(v) for v in M.por_categoria().values())
    assert agrupados == len(M.MOTORES)


def test_la_categoria_es_vista_de_negocio_no_el_dominio_tecnico():
    """El auditor piensa en productos; el catalogo piensa en dominios."""
    assert M.POR_ID["PLAZO"].categoria == "Captacion" and M.POR_ID["PLAZO"].dominio == "DEV"
    assert M.POR_ID["IFRS9"].categoria == "Credito" and M.POR_ID["IFRS9"].dominio == "REG"


# --- Tres granularidades ----------------------------------------------------

def test_los_motores_de_identidad_no_fingen_tres_granularidades():
    """Contable y Motor B no comparan dos importes: un escalon de precision
    ahi no significaria nada y sugeriria un rigor que su regla no tiene."""
    for mid in ("CONTABLE", "MOTOR-B"):
        tp = M.POR_ID[mid].tolerancia_propia
        assert tp, f"{mid} deberia declarar tolerancia propia"
        assert tp[0] and tp[1], f"{mid}: la tolerancia propia debe decir la regla y el porque"
    for mid in ("PLAZO", "CRED-ORD", "ISR"):
        assert M.POR_ID[mid].tolerancia_propia is None


def test_el_resumen_de_tolerancias_da_las_tres_escalas():
    from decimal import Decimal as Dc
    from tolerancias import resumen_tolerancias
    r = resumen_tolerancias([(Dc("10.00"), Dc("10.00"))] * 10)
    assert [e["nombre"] for e in r["escalas"]] == ["1e-8", "1e-5", "centavo"]
    assert all(e["pct"] == "100.00" for e in r["escalas"])
    assert not r["sesgo"]["sesgo_detectado"]


def test_el_escalon_distingue_residuo_de_defecto():
    """Sub-centavo alternado: falla a 1e-8, cuadra al centavo, sin sesgo."""
    from decimal import Decimal as Dc
    from tolerancias import resumen_tolerancias
    pares = [(Dc("10.00") + (Dc("0.004") if i % 2 == 0 else Dc("-0.004")), Dc("10.00"))
             for i in range(200)]
    r = resumen_tolerancias(pares)
    e = {x["nombre"]: x["pct"] for x in r["escalas"]}
    assert e["1e-8"] == "0.00" and e["centavo"] == "100.00"
    assert not r["sesgo"]["sesgo_detectado"], "residuo alternado no es sesgo"


def test_el_sesgo_sistematico_se_marca_aunque_cuadre_al_centavo():
    """Verde al centavo CON sesgo no es aprobado: es severidad 1."""
    from decimal import Decimal as Dc
    from tolerancias import resumen_tolerancias
    r = resumen_tolerancias([(Dc("10.003"), Dc("10.00"))] * 200)
    e = {x["nombre"]: x["pct"] for x in r["escalas"]}
    assert e["centavo"] == "100.00"
    assert r["sesgo"]["sesgo_detectado"], "un residuo todo del mismo lado es sesgo"


# --- El boton "Ejecutar" no promete lo que no puede -------------------------

def test_ejecutable_refleja_el_catalogo_no_solo_la_existencia_del_caso():
    """Un caso puede existir y aun asi no correr hoy (consulta retirada).

    Regresion de un defecto real: la UI ofrecia 'Ejecutar' en MOTOR-B e ISR,
    cuyos casos existen pero no son ejecutables, y el backend los rechazaba.
    """
    import json
    idx = json.loads((RAIZ / "resultados" / "indice.json").read_text(encoding="utf-8"))
    for it in idx["motores"]:
        if it["ejecutable"]:
            assert R._caso_vigente(M.POR_ID[it["id"]]), \
                f"{it['id']} se ofrece ejecutable pero su caso no corre hoy"


def test_no_se_republica_evidencia_de_un_caso_retirado():
    """ISR-01 dejo evidencia de una consulta que ya se retiro: sus 27/27
    violaciones son defecto de la consulta, no del core. Republicarlas como
    'calculado aqui' seria acusar a AurumCore de un error propio."""
    isr = M.POR_ID["ISR"]
    assert not R._caso_vigente(isr)
    r = R.reconstruir_desde_evidencia(isr)
    assert r is None or r.get("origen_resultado") != "corrida_local"


def test_un_error_de_corrida_no_borra_una_corrida_buena():
    fuente = (RAIZ / "backend" / "runner.py").read_text(encoding="utf-8")
    assert "nuevo_sirve" in fuente
    assert "_caso_vigente(motor)" in fuente


# --- Contrato del servidor --------------------------------------------------

def test_el_servidor_rechaza_lo_que_no_puede_correr():
    fuente = (RAIZ / "backend" / "servidor.py").read_text(encoding="utf-8")
    for guarda in ("sin cruce", "caso no ejecutable", "bloqueado", "ya en ejecucion"):
        assert guarda in fuente, f"falta la guarda '{guarda}'"


def test_el_servidor_no_bloquea_la_ui():
    fuente = (RAIZ / "backend" / "servidor.py").read_text(encoding="utf-8")
    assert "threading.Thread" in fuente and "daemon=True" in fuente
    assert "202" in fuente, "el POST debe responder de inmediato con 202"


def test_un_solo_trabajo_por_motor():
    fuente = (RAIZ / "backend" / "servidor.py").read_text(encoding="utf-8")
    assert "_EN_CURSO" in fuente


def test_el_spa_tiene_navegacion_de_dos_niveles():
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    for pieza in ("hashchange", "id=\"menu\"", "galeria(", "detalle(", "por_categoria"):
        assert pieza in html, f"falta la pieza de navegacion: {pieza}"


def test_el_spa_explica_las_granularidades():
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "AYUDA_GRAN" in html
    for t in ("1e-8", "1e-5", "sesgo"):
        assert t in html
