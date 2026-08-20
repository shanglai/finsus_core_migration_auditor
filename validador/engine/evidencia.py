"""CAPA 3 — evidencia por corrida. Cadena probatoria, no bitacora.

Cada corrida escribe un directorio `reportes/<caso>_<fecha>_<hash>/` con:

    violaciones.parquet   las filas que violan la identidad (el producto)
    universo.parquet      todas las filas evaluadas, con su celda A/B/C
    manifiesto.json       caso, parametros, snapshot, version de la regla,
                          CONSULTA EXACTA, version del oraculo, resultado

El hash del directorio es determinista: sale de (caso, parametros, consultas,
sha256 del oraculo, tolerancia). Misma entrada -> mismo hash -> misma carpeta.
Eso hace que re-correr sea idempotente y que dos personas con los mismos
insumos produzcan la misma evidencia (charter §1.1).

La marca de tiempo se graba DENTRO del manifiesto pero NO entra al hash: si
entrara, cada corrida pareceria distinta aunque fuera identica.

Nunca se graban credenciales. Del core se guarda host/base/usuario, que es lo
que identifica el snapshot, y nada mas.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

from . import config

ESQUEMA_MANIFIESTO = 1


def _canonico(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


def hash_corrida(caso_id: str, params: dict, consultas: dict,
                 oraculo_sha: str, tolerancia: str) -> str:
    """Huella determinista de la corrida (no incluye la hora)."""
    material = _canonico({
        "caso": caso_id,
        "params": params,
        "consultas": consultas,
        "oraculo_sha256": oraculo_sha,
        "tolerancia": tolerancia,
        "esquema": ESQUEMA_MANIFIESTO,
    })
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]


@dataclass
class Manifiesto:
    caso_id: str
    titulo: str
    motor: str
    dominio: str
    severidad: int
    regla_ref: list[str]
    version_regla: str
    estado_catalogo: str
    identidad: str
    matriz_esperada: str
    tolerancia: dict
    parametros: dict
    snapshot: dict
    consultas: dict                  # core -> {"archivo":…, "statements":[…], "filas":[…]}
    oraculo: dict
    resultado: dict
    resultado_global: str            # SIN-VIOLACIONES | VIOLACIONES | SESGO | BLOQUEADO | ERROR | UNIVERSO-VACIO
    bloqueo: str = ""
    ejecutado_en: str = ""
    hash: str = ""
    advertencias: list[str] = field(default_factory=list)

    def como_dict(self) -> dict:
        d = {
            "esquema": ESQUEMA_MANIFIESTO,
            "caso": {
                "id": self.caso_id, "titulo": self.titulo, "motor": self.motor,
                "dominio": self.dominio, "severidad": self.severidad,
                "regla_ref": self.regla_ref, "version_regla": self.version_regla,
                "estado_catalogo": self.estado_catalogo,
                "identidad": self.identidad, "matriz_esperada": self.matriz_esperada,
            },
            "tolerancia": self.tolerancia,
            "parametros": self.parametros,
            "snapshot": self.snapshot,
            "consultas": self.consultas,
            "oraculo": self.oraculo,
            "resultado": self.resultado,
            "resultado_global": self.resultado_global,
            "bloqueo": self.bloqueo,
            "ejecutado_en": self.ejecutado_en,
            "hash": self.hash,
            "advertencias": self.advertencias,
        }
        return d


def nombre_directorio(caso_id: str, fecha: str, huella: str) -> str:
    return f"{caso_id}_{fecha}_{huella}"


def escribir(
    manifiesto: Manifiesto,
    violaciones: pl.DataFrame | None = None,
    universo: pl.DataFrame | None = None,
    raiz: Path | None = None,
) -> Path:
    """Escribe el directorio de evidencia y devuelve su ruta."""
    raiz = raiz or config.REPORTES
    ahora = datetime.now(timezone.utc)
    manifiesto.ejecutado_en = ahora.isoformat(timespec="seconds")
    fecha = ahora.strftime("%Y-%m-%d")

    destino = raiz / nombre_directorio(manifiesto.caso_id, fecha, manifiesto.hash)
    destino.mkdir(parents=True, exist_ok=True)

    if violaciones is not None:
        violaciones.write_parquet(destino / "violaciones.parquet")
        if violaciones.height:
            # Copia legible para quien audita sin herramientas: primeras 1000.
            violaciones.head(1000).write_csv(destino / "violaciones_muestra.csv")
    if universo is not None:
        universo.write_parquet(destino / "universo.parquet")

    (destino / "manifiesto.json").write_text(
        json.dumps(manifiesto.como_dict(), indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    # Las consultas exactas, tambien en texto plano: para auditarlas sin abrir JSON.
    lineas = [
        f"# Consultas ejecutadas — {manifiesto.caso_id} — {manifiesto.ejecutado_en}",
        f"# hash de corrida: {manifiesto.hash}",
        "",
    ]
    for core, info in (manifiesto.consultas or {}).items():
        lineas.append(f"-- ===== core: {core} · archivo: {info.get('archivo')} =====")
        for i, s in enumerate(info.get("statements") or [], 1):
            lineas.append(f"-- statement {i}")
            lineas.append(s.strip())
            lineas.append(";")
        lineas.append("")
    (destino / "consultas.sql").write_text("\n".join(lineas), encoding="utf-8")

    return destino


def leer_manifiestos(raiz: Path | None = None) -> list[dict]:
    """Lee todos los manifiestos escritos, mas reciente primero."""
    raiz = raiz or config.REPORTES
    if not raiz.exists():
        return []
    manifiestos = []
    for ruta in raiz.glob("*/manifiesto.json"):
        try:
            d = json.loads(ruta.read_text(encoding="utf-8"))
            d["_ruta"] = str(ruta.parent)
            manifiestos.append(d)
        except Exception as exc:  # noqa: BLE001
            manifiestos.append({
                "caso": {"id": ruta.parent.name.split("_")[0]},
                "resultado_global": "ERROR",
                "bloqueo": f"manifiesto ilegible: {exc}",
                "_ruta": str(ruta.parent),
                "ejecutado_en": "",
            })
    manifiestos.sort(key=lambda m: m.get("ejecutado_en", ""), reverse=True)
    return manifiestos


def ultimo_por_caso(raiz: Path | None = None) -> dict[str, dict]:
    """El manifiesto mas reciente de cada caso."""
    ultimos: dict[str, dict] = {}
    for m in leer_manifiestos(raiz):
        cid = (m.get("caso") or {}).get("id")
        if cid and cid not in ultimos:
            ultimos[cid] = m
    return ultimos
