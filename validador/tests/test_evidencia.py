# -*- coding: utf-8 -*-
"""Cadena probatoria — SIN BD.

La evidencia es lo que sostiene un hallazgo frente a un auditor. Se prueba que
es determinista, que graba la consulta exacta, que NUNCA graba credenciales, y
que un caso bloqueado tambien deja rastro.
"""

import json
from decimal import Decimal
from pathlib import Path

import polars as pl
import pytest

from engine import catalogo as cat
from engine import cobertura, evidencia, runner


def _manifiesto(caso_id="TEST-01", params=None, huella="abc123", global_="SIN-VIOLACIONES"):
    return evidencia.Manifiesto(
        caso_id=caso_id, titulo="Caso de prueba", motor="FIS", dominio="FIS",
        severidad=1, regla_ref=["K-FIS-002"], version_regla="S-FIS-001",
        estado_catalogo="VALIDADO", identidad="C == B", matriz_esperada="B == C",
        tolerancia={"tipo": "redondeo", "max_evento": "0.01", "prueba_sesgo": True},
        parametros=params or {"fecha_ini": "2026-07-01"},
        snapshot={"cores": {"aurum": {"host": "h", "dbname": "d", "user": "u"}}},
        consultas={"aurum": {"archivo": "x.sql", "statements": ["select 1"], "filas": [1]}},
        oraculo={"referencia": "oraculos/isr.py::fila_isr_retenido", "sha256": "deadbeef"},
        resultado={"veredicto": global_, "n_violaciones": 0},
        resultado_global=global_, hash=huella,
    )


# --- Determinismo -----------------------------------------------------------

def test_el_hash_no_depende_de_la_hora():
    """Misma entrada -> mismo hash. Si dependiera del reloj, cada corrida
    pareceria distinta aunque fuera identica (charter §1.1)."""
    args = ("ISR-01", {"a": 1}, {"aurum": ["select 1"]}, "sha", "0.01")
    assert evidencia.hash_corrida(*args) == evidencia.hash_corrida(*args)


def test_el_hash_cambia_si_cambian_los_parametros():
    base = ("ISR-01", {"anio": 2026}, {"aurum": ["select 1"]}, "sha", "0.01")
    otro = ("ISR-01", {"anio": 2025}, {"aurum": ["select 1"]}, "sha", "0.01")
    assert evidencia.hash_corrida(*base) != evidencia.hash_corrida(*otro)


def test_el_hash_cambia_si_cambia_la_consulta():
    base = ("ISR-01", {"a": 1}, {"aurum": ["select 1"]}, "sha", "0.01")
    otro = ("ISR-01", {"a": 1}, {"aurum": ["select 2"]}, "sha", "0.01")
    assert evidencia.hash_corrida(*base) != evidencia.hash_corrida(*otro)


def test_el_hash_cambia_si_cambia_el_oraculo():
    """Si el oraculo cambia, la evidencia anterior deja de aplicar."""
    base = ("ISR-01", {"a": 1}, {"aurum": ["select 1"]}, "sha_v1", "0.01")
    otro = ("ISR-01", {"a": 1}, {"aurum": ["select 1"]}, "sha_v2", "0.01")
    assert evidencia.hash_corrida(*base) != evidencia.hash_corrida(*otro)


def test_el_hash_cambia_si_cambia_la_tolerancia():
    base = ("ISR-01", {"a": 1}, {"aurum": ["select 1"]}, "sha", "0.01")
    otro = ("ISR-01", {"a": 1}, {"aurum": ["select 1"]}, "sha", "0.00")
    assert evidencia.hash_corrida(*base) != evidencia.hash_corrida(*otro)


# --- Contenido de la evidencia ----------------------------------------------

def test_escribe_violaciones_consultas_y_manifiesto(tmp_path):
    viol = pl.DataFrame({"k": ["1"], "motivo": ["|C-B| = 0.05 > tolerancia 0.01"]})
    universo = pl.DataFrame({"k": ["1", "2"], "celda": ["A=C!=B", "A=B=C"]})
    destino = evidencia.escribir(_manifiesto(), viol, universo, raiz=tmp_path)

    assert (destino / "violaciones.parquet").exists()
    assert (destino / "universo.parquet").exists()
    assert (destino / "manifiesto.json").exists()
    assert (destino / "consultas.sql").exists()
    assert (destino / "violaciones_muestra.csv").exists()

    # La consulta exacta queda en texto plano, auditable sin abrir el JSON.
    assert "select 1" in (destino / "consultas.sql").read_text(encoding="utf-8")


def test_el_manifiesto_no_graba_credenciales(tmp_path):
    destino = evidencia.escribir(_manifiesto(), raiz=tmp_path)
    texto = (destino / "manifiesto.json").read_text(encoding="utf-8").lower()
    for prohibido in ("password", "contrasena", "secret", "sslkey"):
        assert prohibido not in texto


def test_el_manifiesto_conserva_regla_parametros_y_snapshot(tmp_path):
    destino = evidencia.escribir(_manifiesto(), raiz=tmp_path)
    d = json.loads((destino / "manifiesto.json").read_text(encoding="utf-8"))
    assert d["caso"]["regla_ref"] == ["K-FIS-002"]
    assert d["caso"]["version_regla"] == "S-FIS-001"
    assert d["parametros"]["fecha_ini"] == "2026-07-01"
    assert d["snapshot"]["cores"]["aurum"]["dbname"] == "d"
    assert d["oraculo"]["sha256"] == "deadbeef"
    assert d["tolerancia"]["max_evento"] == "0.01"


def test_reescribir_la_misma_corrida_es_idempotente(tmp_path):
    a = evidencia.escribir(_manifiesto(), raiz=tmp_path)
    b = evidencia.escribir(_manifiesto(), raiz=tmp_path)
    assert a == b
    assert len(list(tmp_path.iterdir())) == 1


# --- Un caso bloqueado tambien deja rastro ----------------------------------

def test_un_caso_bloqueado_escribe_evidencia_y_nunca_dice_ok(tmp_path, monkeypatch):
    """Un caso sin rastro se confunde despues con un caso limpio."""
    monkeypatch.setattr(evidencia.config, "REPORTES", tmp_path)
    caso = cat.cargar_todos()["SALDO-PROM"]
    assert not caso.ejecutable

    corrida = runner.correr_caso(
        caso,
        overrides={"cohorte": ["100-2006-1"], "fecha_ini": "2026-07-01",
                   "fecha_fin": "2026-08-01"},
        dry_run=False,
    )
    assert corrida.estado == "BLOQUEADO"
    d = json.loads((Path(corrida.ruta_evidencia) / "manifiesto.json")
                   .read_text(encoding="utf-8"))
    assert d["resultado_global"] == "BLOQUEADO"
    assert d["bloqueo"]
    assert "NO-CORRIDO no significa que pase" in d["resultado"]["advertencia"]
    assert d["resultado"]["veredicto"] != "SIN-VIOLACIONES"


def test_cobertura_lee_el_bloqueo_como_no_corrido(tmp_path, monkeypatch):
    monkeypatch.setattr(evidencia.config, "REPORTES", tmp_path)
    caso = cat.cargar_todos()["SALDO-PROM"]
    runner.correr_caso(caso, overrides={"cohorte": ["100-2006-1"],
                                        "fecha_ini": "2026-07-01",
                                        "fecha_fin": "2026-08-01"}, dry_run=False)
    texto = cobertura.generar(raiz_reportes=tmp_path)
    fila = [l for l in texto.splitlines() if "**SALDO-PROM**" in l][0]
    assert "NO-CORRIDO" in fila


def test_faltan_parametros_requeridos_falla_antes_de_conectar():
    caso = cat.cargar_todos()["ISR-01"]
    with pytest.raises(Exception, match="requeridos"):
        runner.resolver_parametros(caso, {})


def test_los_defaults_del_catalogo_llegan_a_los_parametros():
    caso = cat.cargar_todos()["ISR-01"]
    p = runner.resolver_parametros(caso, {"cohorte": ["100-2301-1"],
                                          "fecha_ini": "2026-07-01",
                                          "fecha_fin": "2026-08-01"})
    assert p["uma_anual"] == "42794.64"
    assert p["tasa_anual"] == "0.9"
    assert Decimal(p["uma_anual"]) * Decimal("5") == Decimal("213973.20")
