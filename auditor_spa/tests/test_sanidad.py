# -*- coding: utf-8 -*-
"""El tablero se audita a si mismo — NORTE_SANIDAD.md, brief §12.

Estas pruebas NO verifican que los invariantes existan (eso seria formato otra
vez). Verifican que ATRAPEN: cada una construye el engano y afirma que sale
como violacion. Un invariante que no atrapa su bug esta vacio, y un verde
sostenido por invariantes vacios es el mismo all-pass que el producto existe
para evitar.
"""

import json
from pathlib import Path

import pytest

import motores as M
import runner as R
import sanidad as S

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "resultados"


def claim(**kw):
    """Un claim conforme; cada prueba rompe UNA cosa."""
    base = {
        "motor": "X", "cobertura": "datos",
        "titular": {"escala": "centavo", "valor": "95.70"},
        "escalas": {"1e-8": "81.10", "1e-5": "[PEND]", "centavo": "95.70"},
        "evidencia_config": "", "ejecutable": False, "caso": False, "feed": True,
        "fuente": "MATRIZ_TOLERANCIAS.md", "n": "1,274", "sesgo": "no",
        "calculado_aqui": False, "estado": "validado",
    }
    base.update(kw)
    return base


def invs(claims, ref=None):
    return {v["invariante"] for v in S.revisar(claims, ref if ref is not None else {})}


# --- El estado real del tablero --------------------------------------------

def test_el_tablero_publicado_esta_sano():
    """§12.4: no se publica en NO SANO sin mostrar las violaciones.

    Si esto falla, el mensaje de pytest trae las violaciones: son la salida
    util, no un detalle del error.
    """
    r = S.reporte(RESULTADOS)
    assert r["status"] == "SANO", "\n".join(
        f"  [{v['invariante']}] {v['motor']}: {v['detalle']}" for v in r["violaciones"])


def test_cada_json_publicado_lleva_su_claim():
    """El esquema de claim viaja en el JSON, para que el mismo invariante corra
    de los dos lados (nuestro tablero y `comparadores/sanity_check.py`)."""
    for f in RESULTADOS.glob("*.json"):
        if f.stem in {"indice", "conocimiento"}:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        c = d.get("claim")
        assert c, f"{f.stem} no publica su claim"
        assert set(c) >= {"motor", "cobertura", "titular", "escalas", "ejecutable",
                          "fuente", "n", "sesgo"}, f"{f.stem}: claim incompleto"


def test_el_indice_publica_el_status_de_sanidad():
    idx = json.loads((RESULTADOS / "indice.json").read_text(encoding="utf-8"))
    assert idx["sanidad"]["status"] in {"SANO", "NO SANO"}
    assert idx["sanidad"]["falsabilidad"]["ok"] is True


# --- Falsabilidad: los invariantes atrapan los enganos que los motivaron ----

def test_falsabilidad_atrapa_los_dos_bugs_historicos():
    f = S.autoprueba_falsabilidad({})
    assert f["ok"], f["casos"]
    for c in f["casos"]:
        assert c["atrapado"], c["bug"]


def test_la_autoprueba_de_falsabilidad_puede_fallar():
    """La auto-prueba tiene que ser capaz de decir NO.

    Si `autoprueba_falsabilidad` devolviera siempre `ok`, seria decorativa. Se
    desactiva el invariante H5 y se comprueba que el bug del moratorio deja de
    atraparse.
    """
    original = S.revisar
    try:
        S.revisar = lambda claims, ref=None: [
            v for v in original(claims, ref) if v["invariante"] != "INV-H5"]
        f = S.autoprueba_falsabilidad({})
    finally:
        S.revisar = original
    assert f["ok"] is False
    mor = [c for c in f["casos"] if "CRED-MOR" in c["bug"]][0]
    assert mor["atrapado"] is False


# --- Familia H --------------------------------------------------------------

def test_h1_un_porcentaje_sin_escala_es_violacion():
    assert "INV-H1" in invs([claim(titular={"escala": None, "valor": "96.62"})])


def test_h1_no_lo_se_explicito_tambien_es_violacion_si_hay_cifra():
    """"sin escala declarada" es honesto, pero sigue siendo un hueco: se
    reporta para que alguien lo cierre, no se acepta como estado final."""
    assert "INV-H1" in invs([claim(
        titular={"escala": "sin escala declarada", "valor": "96.62"})])


def test_h2_la_escala_pertenece_a_la_cobertura():
    """La forma general del defecto de CAT: un cruce a volumen leido como
    precision aritmetica."""
    assert "INV-H2" in invs([claim(
        motor="CAT", cobertura="volumen",
        titular={"escala": "1e-8", "valor": "11.60"},
        escalas={"1e-8": "[PEND]", "1e-5": "[PEND]", "centavo": "[PEND]",
                 "volumen": "11.60"})])


def test_h2_una_identidad_de_completitud_no_tiene_granularidad():
    assert "INV-H2" in invs([claim(
        motor="CONTABLE", cobertura="completitud",
        titular={"escala": "centavo", "valor": "100.00"},
        escalas={})])


def test_h2_el_titular_debe_ser_el_valor_de_su_escala():
    assert "INV-H2" in invs([claim(
        titular={"escala": "centavo", "valor": "99.90"})])   # escalas dice 95.70


def test_h3_atrapa_el_fallback_fabricado_de_cat():
    v = S.revisar([claim(motor="CAT", cobertura="volumen",
                         titular={"escala": "1e-8", "valor": "11.60"},
                         escalas={"1e-8": "[PEND]", "1e-5": "[PEND]",
                                  "centavo": "[PEND]", "volumen": "11.60"})], {})
    assert any(x["invariante"] == "INV-H3" for x in v)


def test_h4_un_numero_sin_procedencia_es_violacion():
    assert "INV-H4" in invs([claim(fuente=None)])


def test_h5_el_titular_estricto_ocultando_el_centavo():
    """El bug del moratorio: 81.10% de titular con 95.70% al centavo disponible
    hace concluir que el motor falla 1 de cada 5 veces."""
    assert "INV-H5" in invs([claim(titular={"escala": "1e-8", "valor": "81.10"})])


def test_h5_no_se_dispara_cuando_el_titular_ya_es_el_centavo():
    assert "INV-H5" not in invs([claim()])


# --- Familia E (el problema-espejo) ----------------------------------------

def test_e1_calculado_aqui_exige_corrida_con_datos():
    assert "INV-E1" in invs([claim(calculado_aqui=True, n=None)])
    assert "INV-E1" in invs([claim(calculado_aqui=True, n=0)])
    assert "INV-E1" not in invs([claim(calculado_aqui=True, n=302)])


def test_e2_sin_cruce_no_muestra_porcentaje():
    assert "INV-E2" in invs([claim(
        cobertura="sin_cruce", titular={"escala": "centavo", "valor": "95.70"})])


def test_e3_config_sin_evidencia_es_esconder_cobertura_buena():
    """El problema-espejo: `cobertura=config` es la validacion MAS fuerte, y
    mostrarla como un guion la esconde."""
    assert "INV-E3" in invs([claim(
        cobertura="config", titular={"escala": None, "valor": None},
        escalas={}, evidencia_config="")])
    assert "INV-E3" not in invs([claim(
        cobertura="config", titular={"escala": None, "valor": None},
        escalas={}, evidencia_config="lc_reserve_ifrs 37/37")])


def test_e4_boton_activo_exige_caso_y_insumo():
    assert "INV-E4" in invs([claim(ejecutable=True, caso=False, feed=True)])
    assert "INV-E4" in invs([claim(ejecutable=True, caso=True, feed=False)])
    assert "INV-E4" not in invs([claim(ejecutable=True, caso=True, feed=True)])


# --- Familia C: la referencia se PARSEA, no se hardcodea --------------------

def test_la_matriz_de_referencia_se_lee_de_verdad():
    """INV-C1 comparando contra un dict vacio "pasaria" siempre.

    Un invariante que no tiene con que comparar no prueba nada, asi que se
    exige que el parser saque cifras reales de MATRIZ_TOLERANCIAS.md.
    """
    ref = S.leer_matriz()
    cifras = [(m, e, v) for m, f in ref.items()
              for e, v in f.items() if e in S.GRANULARIDADES and v]
    assert len(cifras) >= 5, f"la matriz se leyo casi vacia: {cifras}"
    assert ref["CRED-MOR"]["1e-8"] == "81.10"
    assert ref["CRED-MOR"]["centavo"] == "95.70"
    assert ref["PLAZO"]["centavo"] == "100.00"


def test_c1_una_cifra_distinta_de_la_matriz_es_violacion():
    ref = S.leer_matriz()
    assert "INV-C1" in invs([claim(
        motor="CRED-MOR", titular={"escala": "centavo", "valor": "89.00"},
        escalas={"1e-8": "81.10", "1e-5": "[PEND]", "centavo": "89.00"})], ref)


def test_c1_no_reclama_lo_que_corrimos_nosotros():
    """Una corrida propia mas reciente no "discrepa" de la matriz: la supera."""
    ref = S.leer_matriz()
    assert "INV-C1" not in invs([claim(
        motor="VISTA", calculado_aqui=True, n=20000,
        titular={"escala": "centavo", "valor": "96.62"},
        escalas={"1e-8": "96.37", "1e-5": "96.37", "centavo": "96.62"})], ref)


def test_c2_un_sesgo_que_no_cuadra_con_la_fuente():
    ref = S.leer_matriz()
    assert "INV-C2" in invs([claim(motor="CRED-MOR", sesgo="si")], ref)


def test_c2_no_confunde_la_nota_al_pie_con_otro_valor():
    """La matriz escribe `no¹` cuando el "no" lleva aclaracion. Es el mismo
    valor; leerlo como distinto seria un falso positivo, y un invariante que
    grita de mas se acaba apagando."""
    ref = S.leer_matriz()
    assert ref["CRED-ORD"]["sesgo"] == "no"


# --- Familia T --------------------------------------------------------------

def test_t1_una_cifra_sin_cita_debe_degradar():
    assert "INV-T1" in invs([claim(fuente="")])


def test_t2_una_granularidad_omitida_no_es_lo_mismo_que_pend():
    """Omitir un nivel lo vuelve indistinguible de "no aplica". Se marca."""
    assert "INV-T2" in invs([claim(escalas={"1e-8": "81.10", "centavo": "95.70"})])
    assert "INV-T2" not in invs([claim()])


# --- El cajon de avisos no puede usarse como escondite ----------------------

def test_avisos_upstream_solo_admite_lo_que_el_tablero_muestra_mas_nuevo():
    ref = S.leer_matriz()
    # Nuestra corrida supera un [PEND] de la matriz -> aviso, no violacion.
    nuestro = claim(motor="VISTA", calculado_aqui=True, n=20000,
                    titular={"escala": "centavo", "valor": "96.62"},
                    escalas={"1e-8": "96.37", "1e-5": "96.37", "centavo": "96.62"})
    assert S.avisos_upstream([nuestro], ref)
    # Una cifra CITADA que contradice a la matriz NO entra al cajon: es INV-C1.
    citado = claim(motor="CRED-MOR", titular={"escala": "centavo", "valor": "89.00"},
                   escalas={"1e-8": "81.10", "1e-5": "[PEND]", "centavo": "89.00"})
    assert S.avisos_upstream([citado], ref) == []
    assert "INV-C1" in invs([citado], ref)


# --- La escala de una corrida propia se DERIVA y se VERIFICA ----------------

def test_la_escala_de_una_corrida_no_sale_del_dossier():
    """La regresion que destapo este chequeo.

    `pct_escala` se derivaba solo de `dossier_match`, asi que un motor CORRIDO
    AQUI sin fila en la matriz publicaba su porcentaje pelon (IFRS9 mostraba
    "100.00%" sin decir que era al centavo, teniendo 88.10% a 1e-8).
    """
    for mid in ("VISTA", "PLAZO", "IFRS9", "CONTABLE"):
        d = json.loads((RESULTADOS / f"{mid}.json").read_text(encoding="utf-8"))
        if d["origen_resultado"] != "corrida_local":
            continue
        assert d["pct_escala"] not in S.NO_SE, f"{mid} publica su % sin escala"


def test_escala_de_corrida_se_verifica_contra_el_match():
    """No basta con nombrar la tolerancia: el nivel tiene que reportar ESE
    numero. Si no coincide, la salida es el "no lo se", no una etiqueta puesta
    para cumplir."""
    motor = M.POR_ID["PLAZO"]
    bueno = {"pct_match": "100.00", "tolerancia": "0.01", "n_ok": 302,
             "match": {"escalas": [{"nombre": "centavo", "pct": "100.00", "n_ok": 302}]}}
    assert R.escala_de_corrida(motor, bueno) == "centavo"

    # El nivel no explica las mismas filas conformes que el titular.
    mentiroso = {"pct_match": "97.00", "tolerancia": "0.01", "n_ok": 293,
                 "match": {"escalas": [{"nombre": "centavo", "pct": "100.00", "n_ok": 302}]}}
    assert R.escala_de_corrida(motor, mentiroso) == "sin escala declarada"

    # Sin el conteo no hay con que verificar; no se supone la escala.
    sin_conteo = {"pct_match": "100.00", "tolerancia": "0.01",
                  "match": {"escalas": [{"nombre": "centavo", "pct": "100.00"}]}}
    assert R.escala_de_corrida(motor, sin_conteo) == "sin escala declarada"

    sin_match = {"pct_match": "100.00", "tolerancia": "0.01", "match": None}
    assert R.escala_de_corrida(motor, sin_match) == "sin escala declarada"


def test_una_identidad_declara_completitud_no_una_granularidad():
    motor = M.POR_ID["CONTABLE"]
    assert R.escala_de_corrida(motor, {"pct_match": "100.00", "tolerancia": "0.00",
                                       "match": None}) == "completitud"


def test_la_cobertura_distingue_volumen_y_completitud():
    assert M.POR_ID["CAT"].cobertura(True, "volumen") == "volumen"
    assert M.POR_ID["CONTABLE"].cobertura(True, "completitud") == "completitud"
    assert M.POR_ID["PLAZO"].cobertura(True, "centavo") == "datos"
    assert M.POR_ID["ISR"].cobertura(False) == "config"


# --- El SPA muestra el status, no lo esconde -------------------------------

def test_el_spa_pinta_el_badge_de_sanidad_en_el_home():
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "panelSanidad()" in html
    assert "NO SANO" in html
    # El detalle por invariante tiene que ser alcanzable desde la UI.
    assert "s.invariantes" in html
    assert "falsabilidad" in html


def test_el_spa_refresca_la_sanidad_despues_de_una_corrida():
    """Un verde calculado antes de la corrida es un verde caducado."""
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "/api/sanidad" in html


# --- Los dos lados se auditan con la misma vara (NORTE_SANIDAD §7) ----------

def test_los_claims_pasan_el_sanity_check_de_finsus():
    """El JSON del tablero conforma al esquema de claim del repo de validacion
    y pasa SUS invariantes, no solo los de esta casa.

    Esto no es redundancia: correrlo destapo que el INV-H4 de alla es mas
    estricto que el de aqui —exige procedencia en TODO claim, no solo en los
    que traen cifra— y que siete motores sin porcentaje no declaraban la suya
    teniendola. Dos implementaciones del mismo invariante se corrigen entre si;
    una sola se cree.
    """
    ruta = RAIZ.parent / "40_validaciones" / "comparadores"
    if not (ruta / "sanity_check.py").exists():
        pytest.skip("sanity_check.py no esta en este bundle")
    import sys
    if str(ruta) not in sys.path:
        sys.path.insert(0, str(ruta))
    import sanity_check as F

    claims = [{**c, "titular": (c["titular"]["escala"], c["titular"]["valor"])}
              for c in S.cargar_claims(RESULTADOS)]
    V = F.chk(claims)
    assert V == [], "\n".join(f"  [{i}] {m}: {d}" for i, m, d in V)


def test_h4_exige_procedencia_aunque_no_haya_cifra():
    """Un motor sin porcentaje igual afirma algo, y esa afirmacion cita."""
    assert "INV-H4" in invs([claim(
        cobertura="sin_cruce", titular={"escala": None, "valor": None},
        escalas={}, fuente=None)])


def test_un_motor_sin_porcentaje_declara_su_fuente():
    """Regresion del hallazgo anterior: `fuente` vacia se leia como "de aqui no
    se sabe nada" en motores que si estan contrastados contra config/norma/doc."""
    for mid in ("ISR", "GAT", "WSO2", "SALDO-PROM", "MOTOR-B", "CRED-DIAS", "ISR-VIVO"):
        c = S.claim_de(json.loads((RESULTADOS / f"{mid}.json").read_text(encoding="utf-8")))
        assert c["fuente"], f"{mid} no declara procedencia"


# --- La prosa tambien puede fabricar --------------------------------------

def test_la_lectura_del_escalon_declarada_gana_a_la_plantilla():
    """El tablero no puede afirmar un diagnostico que no verifico.

    La plantilla dice "escalon ancho = residuo sub-centavo, no defecto". Para
    CAT eso es FALSO: el escalon es angosto porque `lc_loan_contract.cat` guarda
    dos decimales, no porque haya residuo que absorber. Un invariante sobre las
    cifras no atrapa esto porque el engano vive en la prosa.
    """
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "m.lectura_escalon" in html, "el SPA ignora la lectura declarada por el motor"
    # La plantilla generica no puede AFIRMAR el diagnostico.
    assert "hay que verificarla" in html, (
        "la lectura generica del escalon sigue afirmando el diagnostico en vez "
        "de marcarlo como la lectura habitual por verificar")


def test_cat_declara_por_que_su_escalon_no_es_el_habitual():
    cat = M.POR_ID["CAT"]
    assert cat.lectura_escalon, "CAT no declara la lectura de su escalon"
    assert "DOS DECIMALES" in cat.lectura_escalon
    d = json.loads((RESULTADOS / "CAT.json").read_text(encoding="utf-8"))
    assert d["lectura_escalon"] == cat.lectura_escalon


def test_cat_se_calcula_aqui_sobre_el_estrato_per_contrato():
    """CAT dejo de citar 11.60% a volumen: ahora es un cuadre calculado."""
    d = json.loads((RESULTADOS / "CAT.json").read_text(encoding="utf-8"))
    assert d["origen_resultado"] == "corrida_local"
    assert d["cobertura"] == "datos"
    assert d["pct_escala"] == "centavo"
    assert d["caso_validador"] == "CAT-01"
    cr = d["cruce"]
    # El universo es el estrato, no los 31,866 contratos.
    assert 4000 < cr["n_comparadas"] < 5000, (
        f"el universo de CAT-01 deberia ser el estrato per-contrato, no {cr['n_comparadas']}")
    # Las barras se miden sobre el universo entero, no solo sobre los pares.
    for e in cr["match"]["escalas"]:
        assert e["n"] == cr["n_comparadas"], (
            "una fila que el oraculo no pudo calcular quedaria fuera del "
            "denominador y subiria el porcentaje por no haberla medido")


# --- INV-E5: el alcance se declara (delta del export 2026-08-28) -----------

def _claim_con_alcance(**kw):
    a = {"universo": "1,339,023", "representatividad": "~39.6%", "no": ["mono-pago"]}
    a.update(kw.pop("alcance", {}) or {})
    return claim(alcance=a, **kw)


def test_e5_un_porcentaje_sin_alcance_es_violacion():
    """El caso que lo motivo: PLAZO publicaba 100% y se leia como 'todo lo live',
    cuando el cohorte es el 39.6% de los periodos live-pagados."""
    assert "INV-E5" in invs([claim(alcance=None)])


def test_e5_alcance_sin_universo_o_sin_representatividad():
    assert "INV-E5" in invs([_claim_con_alcance(alcance={"universo": ""})])
    assert "INV-E5" in invs([_claim_con_alcance(alcance={"representatividad": ""})])


def test_e5_la_representatividad_no_se_inventa_sobre_un_universo_pendiente():
    """Mismo criterio que INV-H3: si no se sabe el universo, no hay porcentaje."""
    assert "INV-E5" in invs([_claim_con_alcance(
        alcance={"universo": "[PEND]", "representatividad": "39.60%"})])
    # Declararlo pendiente en ambos SI pasa: es el "no lo se" explicito.
    assert "INV-E5" not in invs([_claim_con_alcance(
        alcance={"universo": "[PEND]", "representatividad": "[PEND]"})])


def test_e5_un_alcance_sin_fuera_de_alcance_es_violacion():
    assert "INV-E5" in invs([_claim_con_alcance(alcance={"no": []})])


def test_e5_no_se_dispara_con_un_alcance_completo():
    assert "INV-E5" not in invs([_claim_con_alcance()])


# --- El alcance viaja del catalogo al tablero ------------------------------

def test_los_dieciseis_motores_declaran_su_alcance():
    for m in M.MOTORES:
        assert m.alcance, f"{m.id} no declara alcance"
        assert m.alcance.no, f"{m.id} no declara que queda FUERA de su alcance"
        assert m.alcance.ref.startswith("40_validaciones/INFORME_DETALLADO_AUDITORIA"), (
            f"{m.id} no cita la ficha del informe detallado")


def test_plazo_ya_no_afirma_cobertura_completa_de_lo_live():
    """La correccion que trajo el export: 530,195 NO es el 100% de lo live."""
    a = M.POR_ID["PLAZO"].alcance
    assert "39.6" in a.representatividad, (
        f"PLAZO sigue sin declarar su representatividad real: {a.representatividad}")
    assert "1,339,023" in a.universo
    # La distincion vive donde el lector la necesita: en el "que NO se valida".
    texto = (a.rationale + " " + " ".join(a.no)).upper()
    assert "METODOLOGIA" in texto and "MUESTREO" in texto, (
        "PLAZO no explica que las cuentas de un solo pago quedan fuera por metodo, "
        "no por muestreo")


def test_vista_advierte_que_su_cifra_no_es_comparable_con_la_citada():
    """INV-C3: el tablero calcula agosto sobre una cota; el informe cita julio
    como censo. Ni se contradicen ni se promedian — hay que decirlo."""
    a = M.POR_ID["VISTA"].alcance
    assert a.nota, "VISTA no advierte el contraste de ciclo"
    assert "JULIO" in a.nota.upper() and "AGOSTO" in a.nota.upper()
    assert "94.76" in a.nota, "VISTA no cita la cifra del informe contra la que contrasta"


def test_el_alcance_llega_al_json_y_al_spa():
    d = json.loads((RESULTADOS / "PLAZO.json").read_text(encoding="utf-8"))
    assert d["alcance"]["representatividad"]
    assert d["alcance"]["no"]
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "bloqueAlcance" in html, "el SPA no pinta el alcance"
    assert "NO se valida" in html, "el SPA no muestra que queda fuera"
    assert "Representatividad" in html
