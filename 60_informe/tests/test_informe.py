# -*- coding: utf-8 -*-
"""Invariantes del informe detallado.

La regla que estas pruebas protegen sale de la sesion del 2026-08-28: la
auditoria pidio saber CUANTO REPRESENTA lo probado respecto del universo, y la
forma facil de "cumplir" seria escribir un porcentaje que nadie puede
reproducir. Aqui no se verifica que el campo ESTE, se verifica que sea
DERIVABLE: o hay denominador medido, o hay la consulta exacta que lo mide.

Es el mismo criterio de `NORTE_SANIDAD.md`: el fallback de lo que no se puede
derivar es un "no lo se" con instrucciones de cierre, nunca un valor por
defecto.
"""

import re
from pathlib import Path

import pytest

import puntos as P
import generar as G

RAIZ = Path(__file__).resolve().parent.parent


# --- La regla dura ----------------------------------------------------------

def test_ningun_punto_declara_n_sin_denominador_o_consulta():
    """Un `n` sin denominador y sin forma de medirlo es un hueco permanente."""
    faltan = []
    for p in P.PUNTOS:
        if p.denominador.pendiente and not p.denominador.consulta.strip():
            faltan.append(f"{p.id}: denominador [PEND] y sin consulta que lo cierre")
    assert not faltan, "\n  " + "\n  ".join(faltan)


def test_la_representatividad_nunca_se_inventa():
    """Si el denominador esta pendiente, el porcentaje TIENE que salir [PEND].

    Rellenarlo con una estimacion seria exactamente lo que la auditoria pidio
    que no se hiciera: un numero que suena a respuesta y no lo es.
    """
    for p in P.PUNTOS:
        if p.denominador.pendiente:
            assert p.representatividad == P.PEND, (
                f"{p.id} publica representatividad {p.representatividad} con el "
                f"denominador pendiente")


def test_la_representatividad_declarada_cuadra_con_sus_cifras():
    for p in P.PUNTOS:
        if p.denominador.pendiente or p.n_comparado == P.PEND:
            continue
        n = float(p.n_comparado.replace(",", ""))
        t = float(p.denominador.total.replace(",", ""))
        esperado = f"{n / t * 100:.2f}%"
        assert p.representatividad == esperado, f"{p.id}: {p.representatividad} != {esperado}"


# --- Alcance: lo que NO se valida es obligatorio -----------------------------

def test_todo_punto_declara_lo_que_NO_valida():
    """Un alcance sin fuera-de-alcance se lee con mas cobertura de la que tiene.

    Es la peticion de [00:49:04]: "que estamos validando y que no estamos
    validando".
    """
    for p in P.PUNTOS:
        assert p.que_NO_se_valida, f"{p.id} no declara que queda fuera de su alcance"


def test_todo_punto_declara_su_racional_de_subconjunto():
    """[00:32:35] "la metodologia con la que determinaron cuantos y POR QUE"."""
    for p in P.PUNTOS:
        assert len(p.racional_subconjunto) > 80, (
            f"{p.id} no explica por que ese subconjunto (racional demasiado corto "
            f"para ser una explicacion)")


def test_todo_punto_bloqueado_dice_que_le_hace_falta_y_cuando():
    """[00:52:11] "vamos a poder ver que es lo que le hace falta a esa prueba"."""
    for p in P.PUNTOS:
        if not p.bloqueo:
            continue
        assert p.insumo_requerido, f"{p.id} esta bloqueado y no declara el insumo requerido"
        txt = p.insumo_requerido.upper()
        assert "QUE:" in txt and "CUANDO:" in txt, (
            f"{p.id} declara el insumo pero no separa QUE se necesita de CUANDO")


# --- Santo y sena: reproducible ---------------------------------------------

def test_todo_punto_declara_tablas_filtros_y_llave():
    for p in P.PUNTOS:
        assert p.tablas, f"{p.id} sin tablas declaradas"
        assert p.filtros, f"{p.id} sin los predicados que definen su universo"
        assert p.llave, f"{p.id} sin llave de comparacion"


def test_el_sql_declarado_existe_en_el_repo():
    """Un santo y sena que apunta a un archivo inexistente no reproduce nada."""
    for p in P.PUNTOS:
        if not p.sql:
            continue
        assert (RAIZ.parent / p.sql).exists(), f"{p.id} declara un SQL que no existe: {p.sql}"


def test_los_casos_declarados_existen_en_el_catalogo():
    import sys
    v = RAIZ.parent / "validador"
    if not (v / "catalogo").exists():
        pytest.skip("catalogo no disponible")
    sys.path.insert(0, str(v))
    from engine import catalogo
    casos = catalogo.cargar_todos()
    for p in P.PUNTOS:
        if p.caso_validador:
            assert p.caso_validador in casos, (
                f"{p.id} declara el caso {p.caso_validador}, que no esta en el catalogo")


# --- El generador no puede tapar un hueco -----------------------------------

def test_el_generador_publica_la_consulta_de_los_denominadores_pendientes():
    for p in P.PUNTOS:
        if not p.denominador.pendiente:
            continue
        md = G.ficha(p)
        assert "PENDIENTE" in md, f"{p.id}: la ficha no marca el denominador como pendiente"
        assert p.denominador.consulta.split("\n")[0][:30] in md, (
            f"{p.id}: la ficha no publica la consulta que cierra el hueco")


def test_las_brechas_listan_todos_los_pendientes():
    md = G.brechas()
    for p in P.PUNTOS:
        if p.denominador.pendiente:
            assert p.id in md, f"{p.id} tiene denominador pendiente y no sale en las brechas"


def test_el_indice_no_reporta_mas_cobertura_de_la_real():
    md = G.indice()
    declarados = sum(1 for p in P.PUNTOS if not p.denominador.pendiente)
    assert f"**{declarados} de {len(P.PUNTOS)}**" in md, (
        "el indice no dice cuantos denominadores estan realmente declarados")


def test_las_fichas_se_generan_todas():
    for p in P.PUNTOS:
        md = G.ficha(p)
        assert md.startswith(f"# {p.id} ·")
        for seccion in ("## 1. Alcance", "## 2. Periodo",
                        "## 3. Universo y representatividad",
                        "## 4. Racional del subconjunto",
                        "## 5. Santo y sena", "## 6. Resultado",
                        "Lo que este punto NO concluye"):
            assert seccion in md, f"{p.id} sin la seccion {seccion}"


def test_no_hay_ids_repetidos():
    ids = [p.id for p in P.PUNTOS]
    assert len(ids) == len(set(ids)), f"ids repetidos: {ids}"
