"""Base analitica propia del auditor (DuckDB, archivo local).

Por que existe: para no depender de los cores mas alla de la extraccion. Una
vez que los datos estan aqui, el cruce, el recalculo y la re-corrida no vuelven
a tocar produccion. Ademas deja el snapshot congelado: dos corridas del mismo
caso sobre el mismo warehouse comparan exactamente los mismos hechos.

Los montos se guardan como TEXTO (VARCHAR). Es deliberado: DuckDB haria
felizmente aritmetica de dobles sobre ellos, y la ruta del dinero va en
decimal.Decimal, en Python, en los oraculos.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import duckdb
import polars as pl

from . import config


class Warehouse:
    """Envoltura minima sobre DuckDB. Se usa como contexto."""

    def __init__(self, ruta: Path | None = None):
        self.ruta = ruta or config.ruta_warehouse()
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.con = duckdb.connect(str(self.ruta))

    def __enter__(self) -> "Warehouse":
        return self

    def __exit__(self, *exc) -> None:
        self.cerrar()

    def cerrar(self) -> None:
        try:
            self.con.close()
        except Exception:  # noqa: BLE001 — cerrar nunca debe tumbar una corrida
            pass

    # --- carga ------------------------------------------------------------
    def cargar(self, nombre: str, df: pl.DataFrame) -> int:
        """Reemplaza la tabla `nombre` con el contenido de `df`. Devuelve filas."""
        seguro = _nombre_seguro(nombre)
        self.con.register("_entrada", df.to_arrow())
        self.con.execute(f'CREATE OR REPLACE TABLE "{seguro}" AS SELECT * FROM _entrada')
        self.con.unregister("_entrada")
        return df.height

    def cargar_parquet(self, nombre: str, ruta: Path) -> int:
        seguro = _nombre_seguro(nombre)
        self.con.execute(
            f'CREATE OR REPLACE TABLE "{seguro}" AS '
            f"SELECT * FROM read_parquet('{ruta.as_posix()}')"
        )
        return int(self.con.execute(f'SELECT count(*) FROM "{seguro}"').fetchone()[0])

    # --- lectura ----------------------------------------------------------
    def consultar(self, sql: str) -> pl.DataFrame:
        return self.con.execute(sql).pl()

    def tabla(self, nombre: str) -> pl.DataFrame:
        return self.consultar(f'SELECT * FROM "{_nombre_seguro(nombre)}"')

    def tablas(self) -> list[str]:
        filas = self.con.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'main' ORDER BY table_name"
        ).fetchall()
        return [f[0] for f in filas]

    def existe(self, nombre: str) -> bool:
        return _nombre_seguro(nombre) in self.tablas()


def _nombre_seguro(nombre: str) -> str:
    """Normaliza un nombre de tabla: minusculas, sin acentos ni caracteres raros."""
    limpio = "".join(ch if (ch.isalnum() or ch == "_") else "_" for ch in nombre.lower())
    if not limpio or limpio[0].isdigit():
        limpio = "t_" + limpio
    return limpio


def nombre_tabla(caso_id: str, core: str, sufijo: str = "") -> str:
    partes = [caso_id, core] + ([sufijo] if sufijo else [])
    return _nombre_seguro("_".join(partes))


def guardar_parquet(df: pl.DataFrame, destino: Path) -> Path:
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(destino)
    return destino


def cargar_extracciones(wh: Warehouse, caso_id: str,
                        extracciones: Iterable[tuple[str, pl.DataFrame]]) -> dict[str, int]:
    """Carga (core, df) al warehouse bajo nombres estables por caso."""
    conteos: dict[str, int] = {}
    for core, df in extracciones:
        nombre = nombre_tabla(caso_id, core)
        conteos[nombre] = wh.cargar(nombre, df)
    return conteos
