# -*- coding: utf-8 -*-
"""Las cinco defensas anti-all-pass, como invariantes ejecutables (§5).

Si alguien afloja una de estas, la bateria se rompe. Esa es toda la idea: el
valor del producto no es que corra, es que NO PUEDA firmar en falso.
"""

import inspect
from decimal import Decimal

import pytest

from engine import catalogo as cat
from engine import cobertura, compare, extract
from engine.errores import ExtraccionNoAcotada, ReglaFaltante, SolaLecturaViolada
from engine import oracle_runner


# --- Defensa 1 · violaciones como salida ------------------------------------

def test_ningun_comparador_devuelve_booleano():
    """Un booleano invita a leerlo como semaforo. La salida es el set de filas."""
    for nombre in ("comparar_montos", "comparar_existencia", "comparar_doble_partida"):
        fn = getattr(compare, nombre)
        # El modulo usa `from __future__ import annotations`: la anotacion es cadena.
        assert inspect.signature(fn).return_annotation == "ResultadoComparacion", \
            f"{nombre} no devuelve el conjunto de violaciones"


def test_resultado_expone_las_filas_no_un_total():
    r = compare.comparar_montos(
        "T",
        __import__("polars").DataFrame({"k": ["1"], "b": ["1.00"]}),
        __import__("polars").DataFrame({"k": ["1"], "c": ["2.00"]}),
        ["k"], "b", "c", Decimal("0.01"),
    )
    assert hasattr(r, "violaciones")
    assert r.violaciones.height == 1
    assert "motivo" in r.violaciones.columns, "cada violacion dice por que lo es"


# --- Defensa 2 · matriz A/B/C ------------------------------------------------

def test_las_cinco_celdas_estan_interpretadas():
    for celda in (compare.CELDA_OK, compare.CELDA_DEFECTO_NEGOCIO,
                  compare.CELDA_OF_CORREGIDO, compare.CELDA_DEFECTO_AURUM,
                  compare.CELDA_REGLA_MAL):
        assert celda in compare.INTERPRETACION
        assert compare.INTERPRETACION[celda].strip()


def test_no_hay_semaforo_agregado():
    """El veredicto nunca colapsa la matriz a un color: se reporta la celda."""
    r = compare.comparar_montos(
        "T",
        __import__("polars").DataFrame({"k": ["1"], "b": ["1.00"]}),
        __import__("polars").DataFrame({"k": ["1"], "c": ["2.00"]}),
        ["k"], "b", "c", Decimal("0.01"),
    )
    resumen = r.resumen()
    assert isinstance(resumen["matriz"], dict), "la matriz se reporta por celda, no agregada"
    assert "celda_dominante" in resumen


# --- Defensa 3 · manifiesto de cobertura ------------------------------------

def test_cobertura_lista_todos_los_casos_no_solo_los_corridos():
    texto = cobertura.generar()
    casos = cat.cargar_todos()
    for cid in casos:
        assert cid in texto, f"{cid} no aparece en cobertura.md"


def test_cobertura_dice_explicitamente_que_no_corrido_no_es_paso():
    texto = cobertura.generar()
    assert "NO-CORRIDO NO ES PASO" in texto.upper()
    assert cobertura.SIN_CORRIDA.startswith("NO-CORRIDO")


def test_un_caso_sin_corrida_nunca_se_lee_como_ok():
    """Ningun estado de lectura de un caso no ejecutado contiene 'cero violaciones'."""
    for clave, lectura in cobertura.LECTURA.items():
        if clave in ("BLOQUEADO", "ERROR", "DRY-RUN"):
            assert lectura.startswith("NO-CORRIDO")
            assert "cero violaciones" not in lectura


def test_universo_vacio_no_se_lee_como_limpio():
    assert "no prueba nada" in cobertura.LECTURA["UNIVERSO-VACIO"]


# --- Defensa 4 · prueba de sesgo obligatoria en devengo ---------------------

def test_todo_caso_de_redondeo_exige_prueba_de_sesgo():
    for cid, c in cat.cargar_todos().items():
        if c.tolerancia.tipo == "redondeo":
            assert c.tolerancia.prueba_sesgo, f"{cid}: devengo sin prueba de sesgo"


def test_toda_identidad_contable_tiene_tolerancia_cero():
    for cid, c in cat.cargar_todos().items():
        if c.tolerancia.tipo == "contable":
            assert c.tolerancia.max_evento == Decimal("0"), f"{cid}: contable con holgura"


# --- Defensa 5 · lo que no se puede correr se marca, no se aprueba ----------

def test_oraculo_pendiente_levanta_error_no_devuelve_cero():
    with pytest.raises(ReglaFaltante):
        oracle_runner.cargar_oraculo("PENDIENTE")


def test_estado_validado_exige_caso_ejecutable():
    """El cargador rechaza un VALIDADO sin insumos. Aqui se comprueba el efecto."""
    for cid, c in cat.cargar_todos().items():
        if c.estado == "VALIDADO":
            assert c.ejecutable, f"{cid} se declara VALIDADO sin con que correrlo"


def test_casos_no_ejecutables_declaran_su_motivo():
    for cid, c in cat.cargar_todos().items():
        if not c.ejecutable:
            motivo = c.motivo_no_ejecutable()
            assert motivo and motivo != "sin motivo declarado", \
                f"{cid} no se puede correr y no dice por que"


# --- Solo lectura y extraccion acotada --------------------------------------

@pytest.mark.parametrize("sql", [
    "insert into t values (1)",
    "SELECT 1; DROP TABLE x",
    "update aurumcore.account set saldo = 0",
    "create temp table cohorte as select 1",
    "truncate isr_diario",
])
def test_verbos_de_escritura_se_rechazan(sql):
    with pytest.raises(SolaLecturaViolada):
        extract.asegurar_solo_lectura(sql, "prueba")


def test_un_verbo_en_comentario_no_bloquea_una_consulta_legitima():
    sql = "-- no se hace ningun insert aqui\nselect 1"
    extract.asegurar_solo_lectura(sql, "prueba")


def test_todos_los_sql_del_catalogo_son_de_solo_lectura():
    """Invariante permanente: ninguna consulta del catalogo escribe."""
    from engine import config
    for cid, c in cat.cargar_todos().items():
        for core, ruta in c.extraccion.items():
            if str(ruta).upper() == cat.PENDIENTE:
                continue
            texto = config.resolver_ruta(ruta).read_text(encoding="utf-8")
            extract.asegurar_solo_lectura(texto, f"{cid}/{core}")


def test_cohorte_rechaza_identificadores_no_admisibles():
    """La cohorte se interpola: lista blanca estricta, sin excepciones."""
    with pytest.raises(ValueError):
        extract._valores_cohorte(["100-2301-1'; drop table x --"])


def test_extraccion_no_acotada_es_un_error_no_una_truncada():
    assert issubclass(ExtraccionNoAcotada, Exception)
    doc = extract.ejecutar.__doc__ or ""
    fuente = inspect.getsource(extract.ejecutar)
    assert "limite + 1" in fuente, "debe pedirse una fila mas que el limite para detectar el exceso"
    assert "ExtraccionNoAcotada" in fuente


# --- Sincronia de indices (§7.4) --------------------------------------------

def test_catalogo_y_manifest_sincronizados():
    problemas = cat.verificar_sincronia()
    assert not problemas, "catalogo/manifest desincronizados:\n  " + "\n  ".join(problemas)


# --- Fuente unica: el catalogo espeja el NORTE, no compite con el -----------

def test_todo_caso_declara_la_fila_del_norte_que_espeja():
    """Decision C: el NORTE es la fuente unica; esto es su espejo ejecutable.

    Un caso sin `norte_ref` es un catalogo paralelo empezando a nacer, que es
    justo lo que PROMPT_SYNC_AUDITOR.md prohibe.
    """
    for cid, c in cat.cargar_todos().items():
        assert c.norte_ref.strip(), f"{cid} no declara que fila del NORTE espeja"


def test_todo_caso_bloqueado_dice_que_insumo_lo_desbloquea():
    """Un bloqueo sin salida es una queja; con SOL-* es una peticion accionable."""
    for cid, c in cat.cargar_todos().items():
        if c.estado in ("BLOQUEADO", "PENDIENTE") or not c.ejecutable:
            tiene_via = bool(c.solicitudes) or bool(c.bloqueo) or bool(c.sql_pendientes)
            assert tiene_via, f"{cid} esta detenido y no dice que lo desbloquea"


def test_las_familias_sin_oraculo_no_lo_exigen():
    """existencia y suma_cero son identidades, no recalculos de monto."""
    for cid, c in cat.cargar_todos().items():
        if c.comparacion.tipo in ("existencia", "suma_cero") and c.ejecutable:
            assert "oraculo PENDIENTE" not in c.motivo_no_ejecutable()
