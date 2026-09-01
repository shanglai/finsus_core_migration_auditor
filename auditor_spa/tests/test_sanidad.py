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
    # Corte 2026-09-01. El 1e-8 del moratorio SE MUEVE con el corte porque
    # `capital_venc` es un campo vivo; el centavo es el estable. Fijar aqui el
    # valor viejo convertiria la prueba en un ancla al pasado.
    assert ref["CRED-MOR"]["1e-8"] == "94.66"
    assert ref["CRED-MOR"]["centavo"] == "95.38"
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
    # La matriz declara sesgo "si" para el moratorio al corte 01-sep; citar "no"
    # es la discrepancia que INV-C2 tiene que atrapar.
    assert "INV-C2" in invs([claim(motor="CRED-MOR", sesgo="no")], ref)


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
    # Al corte 01-sep la matriz ya trae VISTA con cifras, asi que ese aviso se
    # cerro. Se construye el caso con un motor que SI sigue [PEND] para que la
    # prueba siga probando el mecanismo y no el estado del dia.
    pendiente = next((m for m, f in ref.items()
                      if all(f.get(e) is None for e in S.GRANULARIDADES)), None)
    assert pendiente, "ya no hay ningun motor [PEND] en la matriz; revisar la prueba"
    nuestro = claim(motor=pendiente, calculado_aqui=True, n=20000,
                    titular={"escala": "centavo", "valor": "96.62"},
                    escalas={"1e-8": "96.37", "1e-5": "96.37", "centavo": "96.62"})
    assert S.avisos_upstream([nuestro], ref)
    # Una cifra CITADA que contradice a la matriz NO entra al cajon: es INV-C1.
    citado = claim(motor="CRED-MOR", titular={"escala": "centavo", "valor": "89.00"},
                   escalas={"1e-8": "94.66", "1e-5": "[PEND]", "centavo": "89.00"})
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

    # AUD-005: su `MATRIZ_REF` esta HARDCODEADA con las cifras pre-2026-09-01
    # (96.80 / 81.10 / 95.70 / 99.00) mientras `MATRIZ_TOLERANCIAS.md` ya trae
    # las del corte 01-sep. Su INV-C1 compara una copia contra otra copia, asi
    # que hoy marca discrepancias que no existen. Esta prueba NO se relaja: se
    # acota a esa clase conocida, de modo que cualquier violacion de OTRO tipo
    # sigue rompiendo.
    ref_matriz = S.leer_matriz()
    esperadas = []
    for inv, m, det in V:
        viejo_ok = (inv == "INV-C1"
                    and any(str(v) in det for v in ("96.80", "81.10", "95.70", "99.00"))
                    and m in ref_matriz)
        if not viejo_ok:
            esperadas.append((inv, m, det))
    assert esperadas == [], "\n".join(f"  [{i}] {m}: {d}" for i, m, d in esperadas)
    assert V, ("su MATRIZ_REF ya se actualizo: quitar la excepcion de AUD-005 y "
               "volver a exigir cero violaciones")


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


# --- El glosario del bundle manda (sync 2026-08-31) ------------------------

GLOSARIO = RAIZ.parent / "40_validaciones" / "GLOSARIO_ESTADOS_TABLERO.md"


def test_las_etiquetas_del_tablero_son_las_del_glosario():
    """El brief del sync pide alinear las etiquetas EXACTAMENTE al glosario.

    Dos diccionarios se separan en cuanto alguien edita uno. Esta prueba falla
    si el tablero define un estado, una cobertura o una escala que el glosario
    del bundle no reconoce.
    """
    if not GLOSARIO.exists():
        pytest.skip("el glosario no esta en este bundle")
    txt = GLOSARIO.read_text(encoding="utf-8").lower()
    for e in M.ESTADOS:
        assert e.replace("_", " ") in txt, f"el estado '{e}' no existe en el glosario"
    for c in ("datos", "volumen", "config", "completitud"):
        assert c in txt, f"la cobertura '{c}' no existe en el glosario"
    for g in ("1e-8", "1e-5", "centavo"):
        assert g in txt, f"la escala '{g}' no existe en el glosario"


def test_el_glosario_se_renderiza_desde_el_bundle_no_desde_una_copia():
    """Si el tablero mantuviera su propia copia de las definiciones, se
    separaria del bundle sin que nadie lo note."""
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "GLOSARIO_ESTADOS_TABLERO.md" in html, (
        "el SPA no cita el documento fuente del glosario")
    assert "s.doc==='GLOSARIO'" in html, (
        "el SPA no renderiza el glosario desde el corpus; parece tener una copia")
    con = json.loads((RESULTADOS / "conocimiento.json").read_text(encoding="utf-8"))
    docs = {s["doc"] for s in con["secciones"]}
    assert "GLOSARIO" in docs, "el glosario no entro al corpus del agente"


def test_aud004_declara_la_hora_de_la_medicion():
    """El cierre acordado de AUD-004(a) NO es alinear la cifra: es declarar la
    hora de cada medicion."""
    a = M.POR_ID["CAT"].alcance
    assert "31,866" in a.nota and "31,867" in a.nota, "CAT no contrasta las dos cifras"
    assert "14:29" in a.nota, "CAT no declara la HORA de su medicion"


def test_vista_declara_cual_es_la_cifra_de_referencia():
    """AUD-004(b): la referencia vigente es el censo de julio; lo de agosto es
    preview. Mostrar las dos sin decir cual manda invita a elegir la que
    convenga."""
    a = M.POR_ID["VISTA"].alcance
    assert "REFERENCIA" in a.nota.upper()
    assert "PREVIEW" in a.nota.upper() or "preview" in a.tipo
    assert "94.76" in a.nota and "96.62" in a.nota


# --- Cierre de version, corte 2026-09-01 -----------------------------------

def test_ninguna_cifra_nueva_reemplaza_una_firme_sin_declararlo():
    """Regla de oro del PLAN: un resultado nuevo no reemplaza uno en firme sin
    declarar QUE sustituye y POR QUE. Si `corte` esta, tienen que estar los tres."""
    for m in M.MOTORES:
        d = m.dossier_match or {}
        if not d.get("corte"):
            continue
        assert d.get("firme_anterior"), (
            f"{m.id} declara corte {d['corte']} y no dice a que cifra sustituye")
        assert d.get("porque_cambio"), (
            f"{m.id} sustituye una cifra en firme y no explica por que")


def test_una_corrida_propia_superada_no_se_borra_ni_se_publica_de_titular():
    """VISTA: el preview de 20,000 filas quedo superado por el censo de agosto.

    Los dos errores posibles son simetricos: publicarlo como titular contradice
    el corte declarado; borrarlo pierde cobertura en silencio.
    """
    d = json.loads((RESULTADOS / "VISTA.json").read_text(encoding="utf-8"))
    assert d["origen_resultado"] == "dossier", "el preview sigue de titular"
    assert d["pct_mostrado"] == "97.65", f"titular inesperado: {d['pct_mostrado']}"
    cr = d.get("cruce") or {}
    assert cr.get("superada") is True, "la corrida no esta marcada como superada"
    assert cr.get("superada_por"), "no dice que la supera"
    assert cr.get("pct_match") == "96.62", "se perdio el preview en vez de conservarlo"


def test_la_corrida_superada_no_manda_las_barras():
    """Si las barras vinieran del preview, la card se contradiria a si misma."""
    c = S.claim_de(json.loads((RESULTADOS / "VISTA.json").read_text(encoding="utf-8")))
    assert c["escalas"].get("centavo") == "97.65"
    assert c["calculado_aqui"] is False


def test_todas_las_cards_declaran_el_umbral_de_bloqueo():
    """F-032: $0.99 MXN es la vara con la que el grupo auditoria lee los numeros."""
    idx = json.loads((RESULTADOS / "indice.json").read_text(encoding="utf-8"))
    u = idx["cobertura"]["umbral_bloqueo"]
    assert u["monto"] == "0.99" and u["moneda"] == "MXN"
    assert "F-032" in u["fuente"]
    html = (RAIZ / "spa" / "index.html").read_text(encoding="utf-8")
    assert "bloqueUmbral()" in html, "el detalle no muestra el umbral"
    assert "bloqueante &gt; $0.99" in html, "la galeria no muestra el umbral"


def test_estar_bajo_el_umbral_no_se_presenta_como_todo_pasa():
    """Su criterio pide DOS cosas: por debajo de $0.99 Y explicado. Publicar solo
    la primera seria el all-pass con otra vara."""
    idx = json.loads((RESULTADOS / "indice.json").read_text(encoding="utf-8"))
    lectura = idx["cobertura"]["umbral_bloqueo"]["lectura"].lower()
    assert "explicado" in lectura, (
        "la lectura del umbral no dice que el residuo tiene que estar explicado")


def test_cada_criterio_de_f032_apunta_a_donde_se_atiende():
    """El prompt de cierre lo pide explicito: mapeo observacion -> donde se atiende."""
    idx = json.loads((RESULTADOS / "indice.json").read_text(encoding="utf-8"))
    crits = idx["cobertura"]["criterios_f032"]
    assert len(crits) >= 13
    ids = {m.id for m in M.MOTORES}
    for c in crits:
        assert c["nota"], f"{c['id']} sin explicacion"
        assert c["motores"] or c["doc"], f"{c['id']} no apunta a nada"
        for mid in c["motores"]:
            assert mid in ids, f"{c['id']} apunta al motor inexistente {mid}"


def test_el_tablero_no_declara_cubierto_lo_que_depende_de_terceros():
    """A3 (reproducibilidad) NO lo controla este tablero: depende del acceso del
    grupo auditoria. Marcarlo 'cubierto' seria apropiarse de un pendiente ajeno."""
    idx = json.loads((RESULTADOS / "indice.json").read_text(encoding="utf-8"))
    a3 = [c for c in idx["cobertura"]["criterios_f032"] if c["id"] == "A3"][0]
    assert a3["estado"] == "depende-de-terceros"
