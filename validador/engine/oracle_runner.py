"""Invoca el oraculo (motor C) fila por fila, en Decimal.

Contrato de un oraculo de caso: una funcion `f(fila: dict, params: dict) -> Decimal`
declarada en el YAML como `oraculos/modulo.py::funcion`.

Dos reglas:

  * Si el oraculo no puede calcular una fila (le falta un insumo), NO se
    inventa un valor ni se descarta la fila: se devuelve C = None con el
    motivo. compare.py la marcara como violacion de tipo "sin C". Descartarla
    seria maquillar cobertura.

  * El resultado sale como CADENA (str(Decimal)) para que ningun paso
    posterior lo degrade a float.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Sequence

import polars as pl

from . import config
from .errores import ReglaFaltante


@dataclass
class SalidaOraculo:
    df: pl.DataFrame                 # llaves + c_oraculo (Utf8) + error_oraculo
    modulo: str
    funcion: str
    sha256: str
    version_regla: str
    n_calculadas: int
    n_fallidas: int
    errores: dict[str, int]          # mensaje -> conteo


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def cargar_oraculo(referencia: str) -> tuple[Callable, Path, str]:
    """Resuelve 'oraculos/isr.py::fila_isr_retenido' a un callable.

    Devuelve (funcion, ruta del archivo, version de la regla declarada).
    """
    if referencia.strip().upper() == "PENDIENTE":
        raise ReglaFaltante(
            "El caso no tiene oraculo: falta la pieza de conocimiento que sustenta "
            "la regla. No se inventa el calculo — el caso queda BLOQUEADO."
        )
    if "::" not in referencia:
        raise ValueError(f"Referencia de oraculo invalida: {referencia!r}")

    ruta_rel, nombre_fn = referencia.split("::", 1)
    ruta = config.RAIZ / ruta_rel
    if not ruta.exists():
        raise ReglaFaltante(f"No existe el modulo de oraculo: {ruta}")

    # Import por ruta, asegurando que `engine` y `oraculos` sean importables.
    if str(config.RAIZ) not in sys.path:
        sys.path.insert(0, str(config.RAIZ))
    mod_nombre = "oraculos." + ruta.stem
    if mod_nombre in sys.modules:
        modulo = sys.modules[mod_nombre]
    else:
        spec = importlib.util.spec_from_file_location(mod_nombre, ruta)
        modulo = importlib.util.module_from_spec(spec)
        sys.modules[mod_nombre] = modulo
        spec.loader.exec_module(modulo)

    if not hasattr(modulo, nombre_fn):
        raise ReglaFaltante(f"{ruta.name} no define la funcion {nombre_fn!r}")
    version = getattr(modulo, "VERSION_REGLA", "[sin VERSION_REGLA declarada]")
    return getattr(modulo, nombre_fn), ruta, version


def correr(
    referencia: str,
    universo: pl.DataFrame,
    llaves: Sequence[str],
    params: dict[str, Any],
    columna_salida: str = "c_oraculo",
) -> SalidaOraculo:
    """Aplica el oraculo a cada fila del universo del caso."""
    funcion, ruta, version = cargar_oraculo(referencia)
    llaves = list(llaves)

    faltan = [k for k in llaves if k not in universo.columns]
    if faltan:
        raise KeyError(f"El universo del oraculo no trae las llaves {faltan}")

    valores: list[str | None] = []
    errores_fila: list[str | None] = []
    errores: dict[str, int] = {}
    ok = 0

    for fila in universo.iter_rows(named=True):
        try:
            resultado = funcion(fila, params)
            if not isinstance(resultado, Decimal):
                raise TypeError(
                    f"el oraculo devolvio {type(resultado).__name__}, se exige Decimal"
                )
            valores.append(str(resultado))
            errores_fila.append(None)
            ok += 1
        except Exception as exc:  # noqa: BLE001 — se registra, no se oculta
            msg = f"{type(exc).__name__}: {exc}"
            valores.append(None)
            errores_fila.append(msg)
            errores[msg] = errores.get(msg, 0) + 1

    df = universo.select(llaves).with_columns([
        pl.Series(columna_salida, valores, dtype=pl.Utf8),
        pl.Series("error_oraculo", errores_fila, dtype=pl.Utf8),
    ])

    return SalidaOraculo(
        df=df, modulo=str(ruta.relative_to(config.RAIZ)), funcion=referencia.split("::")[1],
        sha256=_sha256(ruta), version_regla=version,
        n_calculadas=ok, n_fallidas=len(valores) - ok, errores=errores,
    )
