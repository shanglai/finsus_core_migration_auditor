# -*- coding: utf-8 -*-
"""CASOS-TRAMPA — se prueba el VALIDADOR, no el core (charter §5, ultimo parrafo).

Se siembran discrepancias CONOCIDAS y se verifica que la herramienta las
detecte. Si el tooling deja pasar una de estas, el tooling esta mal — y
cualquier "cero violaciones" que produzca no vale nada.

Trampas sembradas:
  C-001  rezago de UMA: el core tiene configurado 5 x UMA 2025 (206,367.60)
         mientras la norma del ejercicio 2026 exige 213,973.20.
  C-002  denominador de la proporcion del ISR: /saldo_total, no /base_gravable.
  sesgo  diferencias de un centavo, todas del mismo lado: cada evento cumple la
         tolerancia y el agregado esta mal.
"""

from decimal import Decimal

import polars as pl

from engine import compare
from engine.sesgo import prueba_de_signo
from oraculos import parametros_isr
from oraculos.isr import isr_retenido_por_anio

TOL_CENTAVO = Decimal("0.01")


# --- Trampa C-001: rezago de UMA -------------------------------------------

def test_trampa_c001_el_validador_detecta_el_rezago_de_uma():
    """La exencion configurada en el core es la de 2025; la norma 2026 es otra.

    ISR-03 tiene que exhibirlo como violacion. Cero violaciones aqui
    significaria que el comparador esta ciego al parametro que mas caro sale.
    """
    configurado_por_el_core = "206367.60"          # 5 x UMA 2025 (C-001)
    esperado_por_la_norma = parametros_isr.valor_normativo("exencion", 2026)

    assert esperado_por_la_norma == Decimal("213973.20")

    df_b = pl.DataFrame({
        "parametro": ["yield.tax.exempt.amount"],
        "fuente": ["system_configuration"],
        "valor_configurado": [configurado_por_el_core],
    })
    df_c = pl.DataFrame({
        "parametro": ["yield.tax.exempt.amount"],
        "fuente": ["system_configuration"],
        "valor_normativo": [str(esperado_por_la_norma)],
    })
    r = compare.comparar_montos(
        "ISR-03", df_b, df_c, ["parametro", "fuente"],
        col_b="valor_configurado", col_c="valor_normativo",
        tolerancia=Decimal("0.00"),
    )
    assert r.n_violaciones == 1, "el VALIDADOR NO detecto el rezago de UMA (C-001)"
    assert r.veredicto() == "VIOLACIONES"
    assert r.violaciones["dif_c_menos_b"][0] == "7605.60"


def test_trampa_c001_el_oraculo_da_resultados_distintos_por_anio():
    """Correr con el ejercicio equivocado cambia el ISR de forma material."""
    con_2026 = isr_retenido_por_anio("300000", "300000", 361, anio=2026)
    con_2025 = isr_retenido_por_anio("300000", "300000", 361, anio=2025)
    assert con_2026 != con_2025
    # El caso de oro (1-10-370, B=765.75) solo lo reproduce el ejercicio correcto.
    assert abs(con_2026 - Decimal("765.75")) <= TOL_CENTAVO
    assert abs(con_2025 - Decimal("765.75")) > TOL_CENTAVO


def test_trampa_parametro_fiscal_desconocido_no_se_aprueba():
    """Un parametro fiscal que nadie sabe interpretar es un hallazgo, no un pase."""
    assert parametros_isr.normalizar_nombre("parametro.que.nadie.mapeo") is None


# --- Trampa C-002: denominador de la proporcion ----------------------------

def test_trampa_c002_denominador_equivocado_seria_detectado():
    """Si el oraculo dividiera entre la base gravable, el caso de oro reventaria."""
    correcto = isr_retenido_por_anio("311136.07", "50182.96", 120, anio=2026)
    # Simulacion del error: proporcion sobre la parte expuesta, no sobre el total.
    base_gravable = Decimal("311136.07") - Decimal("213973.20")
    equivocado = correcto * (Decimal("311136.07") / base_gravable)
    r = compare.comparar_montos(
        "ISR-01",
        pl.DataFrame({"k": ["1"], "b": [str(correcto)]}),
        pl.DataFrame({"k": ["1"], "c": [str(equivocado.quantize(Decimal('0.01')))]}),
        ["k"], col_b="b", col_c="c", tolerancia=TOL_CENTAVO,
    )
    assert r.n_violaciones == 1, "un denominador equivocado pasaria sin ser visto"


# --- Trampa del sesgo: cada evento cumple, el agregado no -------------------

def test_trampa_sesgo_sistematico_de_un_centavo():
    """400 diferencias de +0.01: todas dentro de tolerancia, todas del mismo lado.

    Sin prueba de signo esto es un 'cero violaciones' impecable y un agregado
    mal por $4.00. La prueba tiene que marcarlo severidad 1.
    """
    n = 400
    df_b = pl.DataFrame({"k": [str(i) for i in range(n)], "b": ["10.00"] * n})
    df_c = pl.DataFrame({"k": [str(i) for i in range(n)], "c": ["10.01"] * n})
    r = compare.comparar_montos("TEST", df_b, df_c, ["k"], "b", "c",
                                tolerancia=TOL_CENTAVO, prueba_sesgo=True)

    assert r.n_violaciones == 0, "cada evento respeta la tolerancia (esa es la trampa)"
    assert r.sesgo is not None and r.sesgo.sesgo_detectado, "el sesgo paso desapercibido"
    assert r.sesgo.severidad == 1
    assert r.veredicto() == "SESGO", "un caso con sesgo NO puede reportarse como limpio"
    assert r.sesgo.extremos["suma"] == "4.00"


def test_ruido_simetrico_no_se_marca_como_sesgo():
    """La prueba no puede ser un detector de humo: ruido balanceado pasa."""
    difs = [Decimal("0.01"), Decimal("-0.01")] * 200
    res = prueba_de_signo(difs)
    assert not res.sesgo_detectado
    assert res.n_positivas == res.n_negativas


def test_sesgo_leve_en_muestra_grande_se_detecta():
    """55/45 en 2,000 eventos es sesgo, aunque a ojo parezca ruido."""
    difs = [Decimal("0.01")] * 1100 + [Decimal("-0.01")] * 900
    res = prueba_de_signo(difs)
    assert res.sesgo_detectado
    assert res.metodo == "binomial_exacta"


def test_prueba_de_signo_es_determinista():
    """Misma entrada, mismo p-valor. Siempre."""
    difs = [Decimal("0.01")] * 30 + [Decimal("-0.01")] * 10
    a = prueba_de_signo(difs)
    b = prueba_de_signo(list(difs))
    assert a.p_valor == b.p_valor and a.sesgo_detectado == b.sesgo_detectado
