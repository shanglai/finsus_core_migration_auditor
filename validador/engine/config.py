"""Rutas y conexiones del VALIDADOR."""

from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from .errores import ConexionNoConfigurada

RAIZ = Path(__file__).resolve().parent.parent          # validador/
RAIZ_REPO = RAIZ.parent                                # raiz del repositorio

CATALOGO = RAIZ / "catalogo"
EXTRACCION = RAIZ / "extraccion"
ORACULOS = RAIZ / "oraculos"
REPORTES = RAIZ / "reportes"
DATOS = RAIZ / "datos"

ARCHIVO_CONEXIONES = RAIZ / "db_connections.yaml"
ARCHIVO_CONEXIONES_EJEMPLO = RAIZ / "db_connections.example.yaml"

# Cotas por defecto si db_connections.yaml no las declara.
MAX_FILAS_DEFAULT = 500_000
MAX_COHORTE_DEFAULT = 50_000


def resolver_ruta(rel: str) -> Path:
    """Resuelve una ruta declarada en un YAML del catalogo.

    Las rutas se declaran RELATIVAS A LA RAIZ DEL REPO, no a validador/. Es
    deliberado: los SQL ya validados viven en 40_validaciones/extraccion/ y
    40_validaciones/entrega_finsus/, y el VALIDADOR los apunta ahi en vez de
    copiarlos. Dos copias de una consulta significan que nadie sabe cual se
    corrio — inaceptable en cadena probatoria.
    """
    p = Path(rel)
    if p.is_absolute():
        return p
    candidato = RAIZ_REPO / p
    if candidato.exists():
        return candidato
    return RAIZ / p          # respaldo: relativa a validador/


def cargar_conexiones(ruta: Path | None = None) -> dict[str, Any]:
    """Lee db_connections.yaml. No falla si no existe: los modos --dry-run,
    --explicar y --cobertura deben funcionar sin credenciales."""
    ruta = ruta or ARCHIVO_CONEXIONES
    if not ruta.exists():
        return {}
    with ruta.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def config_core(nombre: str, conexiones: dict[str, Any] | None = None) -> dict[str, Any]:
    """Devuelve la config de conexion de un core (`aurum` / `openfin`).

    Resuelve la contrasena desde `password_env` si esta declarada. Nunca
    imprime ni guarda la contrasena: el manifiesto de evidencia solo graba
    host/dbname/usuario.
    """
    conexiones = conexiones if conexiones is not None else cargar_conexiones()
    cores = (conexiones or {}).get("cores") or {}
    if nombre not in cores:
        raise ConexionNoConfigurada(
            f"No hay conexion configurada para el core {nombre!r}. "
            f"Copiar {ARCHIVO_CONEXIONES_EJEMPLO.name} a {ARCHIVO_CONEXIONES.name} "
            f"y llenar credenciales de SOLO LECTURA."
        )
    cfg = dict(cores[nombre])
    env = cfg.pop("password_env", None)
    if env and not cfg.get("password"):
        valor = os.environ.get(env)
        if not valor:
            raise ConexionNoConfigurada(
                f"El core {nombre!r} declara password_env={env!r} pero la variable "
                f"de ambiente no esta definida."
            )
        cfg["password"] = valor
    return cfg


def limite_filas(conexiones: dict[str, Any] | None = None) -> int:
    conexiones = conexiones if conexiones is not None else cargar_conexiones()
    return int(((conexiones or {}).get("extraccion") or {}).get("max_filas", MAX_FILAS_DEFAULT))


def limite_cohorte(conexiones: dict[str, Any] | None = None) -> int:
    conexiones = conexiones if conexiones is not None else cargar_conexiones()
    return int(((conexiones or {}).get("extraccion") or {}).get("max_cohorte", MAX_COHORTE_DEFAULT))


def ruta_warehouse(conexiones: dict[str, Any] | None = None) -> Path:
    conexiones = conexiones if conexiones is not None else cargar_conexiones()
    rel = ((conexiones or {}).get("warehouse") or {}).get("ruta", "datos/validador.duckdb")
    ruta = Path(rel)
    return ruta if ruta.is_absolute() else RAIZ / ruta


def a_decimal(valor: Any, campo: str = "") -> Decimal:
    """Convierte a Decimal exigiendo que el origen NO sea float.

    Un float que llega hasta aqui es un defecto de la ruta del dinero, no un
    detalle de tipado: se rechaza en vez de convertirse.
    """
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, float):
        raise TypeError(
            f"Valor float en campo monetario {campo or '<sin nombre>'}: {valor!r}. "
            "Declararlo como cadena en el YAML (p.ej. \"0.01\") — cero float "
            "en la ruta del dinero (charter §1.3)."
        )
    if isinstance(valor, (int, str)):
        return Decimal(str(valor))
    raise TypeError(f"No se puede convertir a Decimal el campo {campo!r}: {valor!r}")
