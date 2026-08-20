# -*- coding: utf-8 -*-
"""Integridad del catalogo — SIN BD.

El catalogo es la fuente de verdad de QUE se valida. Si se degrada, el
validador valida otra cosa que la que dice validar.
"""

import re
from decimal import Decimal

import pytest
import yaml

from engine import catalogo as cat
from engine import config
from engine.errores import CatalogoInvalido

CASOS = cat.cargar_todos()


def test_hay_casos_cargados():
    assert len(CASOS) >= 13


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_cada_caso_cita_su_sustento(cid):
    """Toda afirmacion con su fuente (§9). Un caso sin pieza K no es auditable."""
    assert CASOS[cid].regla_ref, f"{cid} no cita ninguna pieza de conocimiento"


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_cada_caso_declara_su_identidad_y_su_matriz(cid):
    c = CASOS[cid]
    assert c.identidad.strip(), f"{cid} no declara que afirma"
    assert c.matriz_esperada.strip(), f"{cid} no declara que celda espera"


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_los_ids_no_llevan_acentos_ni_enie(cid):
    """Identificadores sin acentos ni ñ (§9)."""
    assert re.match(r"^[A-Z0-9\-]+$", cid)


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_las_rutas_de_extraccion_existen_o_dicen_pendiente(cid):
    for core, ruta in CASOS[cid].extraccion.items():
        if str(ruta).upper() == cat.PENDIENTE:
            continue
        assert config.resolver_ruta(ruta).exists(), f"{cid}/{core}: ruta rota {ruta}"


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_el_oraculo_declarado_se_puede_cargar(cid):
    from engine import oracle_runner
    c = CASOS[cid]
    if c.oraculo_pendiente:
        return
    fn, ruta, version = oracle_runner.cargar_oraculo(c.oraculo)
    assert callable(fn)
    assert version and "sin VERSION_REGLA" not in version, \
        f"{cid}: el modulo del oraculo no declara VERSION_REGLA"


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_los_montos_del_yaml_son_cadenas_no_floats(cid):
    """Un 0.01 sin comillas en YAML es un float y contamina la ruta del dinero."""
    crudo = yaml.safe_load(CASOS[cid].ruta.read_text(encoding="utf-8"))
    assert isinstance(crudo["tolerancia"]["max_evento"], str)
    for p in crudo.get("parametros") or []:
        if p.get("tipo") == "decimal" and p.get("default") is not None:
            assert isinstance(p["default"], str), \
                f"{cid}: parametro {p['nombre']} tiene default float"


@pytest.mark.parametrize("cid", sorted(CASOS))
def test_un_caso_no_ejecutable_declara_bloqueo_o_pendientes(cid):
    c = CASOS[cid]
    if c.ejecutable:
        return
    assert c.bloqueo or c.oraculo_pendiente or c.sql_pendientes, \
        f"{cid} no se puede correr y no explica que falta"


def test_el_cargador_rechaza_un_validado_sin_insumos(tmp_path):
    """Invariante duro: no se puede firmar como validado lo que no corre."""
    yaml_malo = tmp_path / "MALO-01.yaml"
    yaml_malo.write_text("""
id: MALO-01
titulo: Caso que se declara validado sin tener con que correr
motor: FIS
dominio: FIS
regla_ref: [K-FIS-002]
severidad: 1
tolerancia: {tipo: contable, max_evento: "0.00", prueba_sesgo: false}
extraccion: {aurum: PENDIENTE}
oraculo: PENDIENTE
comparacion: {tipo: igualdad_montos, llaves: [k], columna_b: b, columna_c: c}
identidad: "C == B"
matriz_esperada: "B == C"
estado: VALIDADO
""", encoding="utf-8")
    with pytest.raises(CatalogoInvalido, match="VALIDADO"):
        cat.cargar_caso(yaml_malo)


def test_el_cargador_rechaza_un_monto_float(tmp_path):
    yaml_malo = tmp_path / "MALO-02.yaml"
    yaml_malo.write_text("""
id: MALO-02
titulo: Tolerancia declarada como float
motor: FIS
dominio: FIS
regla_ref: [K-FIS-002]
severidad: 1
tolerancia: {tipo: redondeo, max_evento: 0.01, prueba_sesgo: true}
extraccion: {aurum: PENDIENTE}
oraculo: PENDIENTE
comparacion: {tipo: igualdad_montos, llaves: [k], columna_b: b, columna_c: c}
identidad: "C == B"
matriz_esperada: "B == C"
estado: PENDIENTE
""", encoding="utf-8")
    with pytest.raises(CatalogoInvalido, match="CADENA"):
        cat.cargar_caso(yaml_malo)


def test_el_cargador_rechaza_devengo_sin_prueba_de_sesgo(tmp_path):
    yaml_malo = tmp_path / "MALO-03.yaml"
    yaml_malo.write_text("""
id: MALO-03
titulo: Devengo con tolerancia de centavo y sin prueba de signo
motor: DEV
dominio: DEV
regla_ref: [K-DEV-001]
severidad: 1
tolerancia: {tipo: redondeo, max_evento: "0.01", prueba_sesgo: false}
extraccion: {aurum: PENDIENTE}
oraculo: PENDIENTE
comparacion: {tipo: igualdad_montos, llaves: [k], columna_b: b, columna_c: c}
identidad: "C == B"
matriz_esperada: "B == C"
estado: PENDIENTE
""", encoding="utf-8")
    with pytest.raises(CatalogoInvalido, match="prueba_sesgo"):
        cat.cargar_caso(yaml_malo)


def test_el_cargador_rechaza_contable_con_holgura(tmp_path):
    yaml_malo = tmp_path / "MALO-04.yaml"
    yaml_malo.write_text("""
id: MALO-04
titulo: Identidad contable con tolerancia de un centavo
motor: CTB
dominio: CTB
regla_ref: [K-CTB-001]
severidad: 1
tolerancia: {tipo: contable, max_evento: "0.01", prueba_sesgo: false}
extraccion: {aurum: PENDIENTE}
oraculo: PENDIENTE
comparacion: {tipo: igualdad_montos, llaves: [k], columna_b: b, columna_c: c}
identidad: "cargos == abonos"
matriz_esperada: "exacto"
estado: PENDIENTE
""", encoding="utf-8")
    with pytest.raises(CatalogoInvalido, match="0.00"):
        cat.cargar_caso(yaml_malo)


def test_severidad_1_no_se_diluye():
    """Los casos que bloquean go-live siguen marcados como tales."""
    sev1 = {cid for cid, c in CASOS.items() if c.severidad == 1}
    assert {"ISR-01", "ISR-03", "REND-PLAZO", "SALDO-PROM", "CONTABLE-BC"} <= sev1
