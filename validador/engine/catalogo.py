"""CAPA 1 — el catalogo es la fuente de verdad de QUE se valida.

Un caso = un YAML declarativo en catalogo/. Este modulo lo carga, lo valida
contra el esquema de catalogo/_schema.md y lo expone como objeto. Ninguna
regla vive en el codigo del motor: el motor solo ejecuta lo que el catalogo
declara.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from . import config
from .errores import CatalogoInvalido
from .redondeo import es_modo_valido

# Marcador unico para lo que no se puede ejecutar porque falta el insumo.
# El runner lo respeta y BLOQUEA el caso — nunca lo aprueba.
PENDIENTE = "PENDIENTE"

ESTADOS = ("VALIDADO", "PARCIAL", "PENDIENTE", "BLOQUEADO", "HALLAZGO")
MOTORES = ("FIS", "DEV", "MOV", "REG", "CTB", "COL", "PRC", "MIG")
TIPOS_COMPARACION = ("igualdad_montos", "existencia", "doble_partida", "suma_cero")
TIPOS_TOLERANCIA = ("contable", "redondeo")

# Ids en mayusculas, con o sin guion: ISR-01, GAPB-IDNC, COMPLETITUD.
# Sin acentos ni ñ (charter §9).
_RE_ID = re.compile(r"^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*$")
_RE_ORACULO = re.compile(r"^oraculos/[a-z0-9_]+\.py::[a-z0-9_]+$")


@dataclass(frozen=True)
class Parametro:
    nombre: str
    tipo: str
    requerido: bool = False
    default: Any = None
    nota: str = ""


@dataclass(frozen=True)
class Tolerancia:
    tipo: str                       # contable | redondeo
    max_evento: Decimal             # 0.00 para identidades contables
    prueba_sesgo: bool = False
    alfa_sesgo: str = "0.01"        # nivel de la prueba de signo

    @property
    def es_cero(self) -> bool:
        return self.max_evento == Decimal("0")


@dataclass(frozen=True)
class Comparacion:
    tipo: str
    llaves: tuple[str, ...]
    columna_a: str | None = None
    columna_b: str | None = None
    columna_c: str | None = None
    columnas: tuple[str, ...] = ()      # para suma_cero
    # De que core sale cada motor. Por omision B = aurum (el core bajo prueba) y
    # A = openfin (el historico). ISR-02 es la excepcion: ahi el motor bajo
    # prueba es OpenFin, y se declara explicitamente.
    fuente_a: str = "openfin"
    fuente_b: str = "aurum"


@dataclass(frozen=True)
class Caso:
    id: str
    titulo: str
    motor: str
    dominio: str
    regla_ref: tuple[str, ...]
    severidad: int
    tolerancia: Tolerancia
    parametros: tuple[Parametro, ...]
    extraccion: dict[str, str]      # core -> ruta sql | PENDIENTE
    oraculo: str                    # "oraculos/x.py::fn" | PENDIENTE
    comparacion: Comparacion
    identidad: str
    matriz_esperada: str
    estado: str
    universo: dict = field(default_factory=dict, compare=False)
    cobertura_nota: str = ""
    bloqueo: str = ""
    estado_origen: str = ""         # lo que el documento fuente afirmaba
    norte_ref: str = ""             # fila del NORTE que este caso espeja (fuente unica)
    solicitudes: tuple[str, ...] = ()   # SOL-* que lo desbloquean
    supuestos: tuple[str, ...] = ()
    ruta: Path | None = field(default=None, compare=False)

    # --- capacidad de ejecucion -------------------------------------------
    @property
    def oraculo_pendiente(self) -> bool:
        return self.oraculo.strip().upper() == PENDIENTE

    @property
    def sql_pendientes(self) -> list[str]:
        return [c for c, v in self.extraccion.items() if str(v).strip().upper() == PENDIENTE]

    def _sql_listo(self, core: str) -> bool:
        return str(self.extraccion.get(core, PENDIENTE)).strip().upper() != PENDIENTE

    @property
    def ejecutable(self) -> bool:
        """Hay con que correr el caso.

        Hay dos familias que NO llevan oraculo, porque la identidad es la
        comparacion misma y no hay monto que recalcular:
          - EXISTENCIA: el set-diff entre los dos cores (exige ambas consultas).
          - SUMA_CERO : las columnas se cancelan (exige la del core bajo prueba).
        Las demas exigen oraculo + la consulta del core bajo prueba.
        """
        if self.comparacion.tipo == "existencia":
            return self._sql_listo(self.comparacion.fuente_a) and \
                   self._sql_listo(self.comparacion.fuente_b)
        if self.comparacion.tipo == "suma_cero":
            return self._sql_listo(self.comparacion.fuente_b)
        if self.oraculo_pendiente:
            return False
        return self._sql_listo(self.comparacion.fuente_b)

    def motivo_no_ejecutable(self) -> str:
        faltantes = []
        if self.oraculo_pendiente and self.comparacion.tipo not in ("existencia", "suma_cero"):
            faltantes.append("oraculo PENDIENTE (falta pieza de conocimiento)")
        for core in self.sql_pendientes:
            faltantes.append(f"SQL de {core} PENDIENTE")
        if self.bloqueo:
            faltantes.append(self.bloqueo)
        return "; ".join(faltantes) or "sin motivo declarado"

    def defaults(self) -> dict[str, Any]:
        return {p.nombre: p.default for p in self.parametros if p.default is not None}

    def requeridos(self) -> list[str]:
        return [p.nombre for p in self.parametros if p.requerido]


# ---------------------------------------------------------------------------
# Validacion de esquema
# ---------------------------------------------------------------------------

def _exigir(cond: bool, mensaje: str, ruta: Path) -> None:
    if not cond:
        raise CatalogoInvalido(f"{ruta.name}: {mensaje}")


def _monetario(valor: Any, campo: str, ruta: Path) -> Decimal:
    _exigir(
        isinstance(valor, str),
        f"{campo} debe ser CADENA para evitar float (usar \"0.01\", no 0.01); "
        f"se recibio {type(valor).__name__}",
        ruta,
    )
    try:
        return Decimal(valor)
    except Exception as exc:  # noqa: BLE001
        raise CatalogoInvalido(f"{ruta.name}: {campo} no es un decimal valido: {valor!r}") from exc


def cargar_caso(ruta: Path) -> Caso:
    """Carga y valida un YAML de caso."""
    with ruta.open("r", encoding="utf-8") as fh:
        d = yaml.safe_load(fh) or {}

    for campo in ("id", "titulo", "motor", "dominio", "regla_ref", "severidad",
                  "tolerancia", "extraccion", "oraculo", "comparacion",
                  "identidad", "matriz_esperada", "estado"):
        _exigir(campo in d, f"falta el campo obligatorio {campo!r}", ruta)

    _exigir(bool(_RE_ID.match(str(d["id"]))), f"id invalido: {d['id']!r} (formato ABC-01)", ruta)
    _exigir(d["motor"] in MOTORES, f"motor invalido: {d['motor']!r} (validos {MOTORES})", ruta)
    _exigir(d["estado"] in ESTADOS, f"estado invalido: {d['estado']!r} (validos {ESTADOS})", ruta)
    _exigir(d["severidad"] in (1, 2, 3), f"severidad invalida: {d['severidad']!r}", ruta)
    _exigir(isinstance(d["regla_ref"], list) and d["regla_ref"],
            "regla_ref debe ser una lista no vacia de piezas K/S/F/P", ruta)

    tol = d["tolerancia"] or {}
    _exigir(tol.get("tipo") in TIPOS_TOLERANCIA,
            f"tolerancia.tipo invalido: {tol.get('tipo')!r} (validos {TIPOS_TOLERANCIA})", ruta)
    max_evento = _monetario(tol.get("max_evento"), "tolerancia.max_evento", ruta)
    _exigir(max_evento >= 0, "tolerancia.max_evento no puede ser negativa", ruta)
    if tol["tipo"] == "contable":
        _exigir(max_evento == Decimal("0"),
                "una identidad contable exige tolerancia 0.00 (charter §1.7)", ruta)
    if tol["tipo"] == "redondeo":
        _exigir(bool(tol.get("prueba_sesgo")),
                "todo caso con tolerancia de redondeo exige prueba_sesgo: true (charter §5.4)", ruta)
    tolerancia = Tolerancia(
        tipo=tol["tipo"],
        max_evento=max_evento,
        prueba_sesgo=bool(tol.get("prueba_sesgo", False)),
        alfa_sesgo=str(tol.get("alfa_sesgo", "0.01")),
    )

    params: list[Parametro] = []
    for p in d.get("parametros") or []:
        _exigir("nombre" in p and "tipo" in p, "cada parametro exige nombre y tipo", ruta)
        if p.get("tipo") == "decimal" and p.get("default") is not None:
            _monetario(p["default"], f"parametros.{p['nombre']}.default", ruta)
        params.append(Parametro(
            nombre=p["nombre"], tipo=p["tipo"],
            requerido=bool(p.get("requerido", False)),
            default=p.get("default"), nota=p.get("nota", ""),
        ))

    extraccion = {k: str(v) for k, v in (d["extraccion"] or {}).items()}
    _exigir(bool(extraccion), "extraccion debe declarar al menos el core aurum", ruta)
    for core, val in extraccion.items():
        if val.strip().upper() != PENDIENTE:
            _exigir(config.resolver_ruta(val).exists(),
                    f"extraccion.{core} apunta a un SQL inexistente: {val}", ruta)

    oraculo = str(d["oraculo"]).strip()
    if oraculo.upper() != PENDIENTE:
        _exigir(bool(_RE_ORACULO.match(oraculo)),
                f"oraculo invalido: {oraculo!r} (formato oraculos/mod.py::funcion)", ruta)

    comp = d["comparacion"] or {}
    _exigir(comp.get("tipo") in TIPOS_COMPARACION,
            f"comparacion.tipo invalido: {comp.get('tipo')!r} (validos {TIPOS_COMPARACION})", ruta)
    _exigir(isinstance(comp.get("llaves"), list) and comp["llaves"],
            "comparacion.llaves debe ser una lista no vacia", ruta)
    if comp["tipo"] == "suma_cero":
        _exigir(isinstance(comp.get("columnas"), list) and len(comp["columnas"]) >= 2,
                "comparacion.columnas debe listar al menos dos columnas para suma_cero", ruta)
    if comp["tipo"] == "igualdad_montos":
        for col in ("columna_b", "columna_c"):
            _exigir(bool(comp.get(col)),
                    f"comparacion.{col} es obligatoria para tipo igualdad_montos", ruta)
    comparacion = Comparacion(
        tipo=comp["tipo"],
        llaves=tuple(comp["llaves"]),
        columna_a=comp.get("columna_a"),
        columna_b=comp.get("columna_b"),
        columna_c=comp.get("columna_c"),
        columnas=tuple(comp.get("columnas") or []),
        fuente_a=comp.get("fuente_a", "openfin"),
        fuente_b=comp.get("fuente_b", "aurum"),
    )

    if d.get("redondeo") is not None:
        _exigir(es_modo_valido(str(d["redondeo"])),
                f"redondeo invalido: {d['redondeo']!r}", ruta)

    caso = Caso(
        id=d["id"], titulo=d["titulo"], motor=d["motor"], dominio=d["dominio"],
        regla_ref=tuple(d["regla_ref"]), severidad=int(d["severidad"]),
        tolerancia=tolerancia, parametros=tuple(params), extraccion=extraccion,
        oraculo=oraculo, comparacion=comparacion, identidad=d["identidad"],
        matriz_esperada=d["matriz_esperada"], estado=d["estado"],
        universo=d.get("universo") or {},
        cobertura_nota=d.get("cobertura_nota", ""), bloqueo=d.get("bloqueo", ""),
        estado_origen=d.get("estado_origen", ""),
        norte_ref=d.get("norte_ref", ""),
        solicitudes=tuple(d.get("solicitudes") or []),
        supuestos=tuple(d.get("supuestos") or []), ruta=ruta,
    )

    # Invariante anti-all-pass: un caso no puede declararse VALIDADO si no es
    # ejecutable. "Validado" sin oraculo ni SQL es una firma en falso.
    _exigir(
        not (caso.estado == "VALIDADO" and not caso.ejecutable),
        f"estado VALIDADO pero el caso no es ejecutable ({caso.motivo_no_ejecutable()}). "
        f"Un caso sin insumos se marca PENDIENTE o BLOQUEADO, nunca VALIDADO.",
        ruta,
    )
    return caso


def cargar_todos(directorio: Path | None = None) -> dict[str, Caso]:
    """Carga todos los casos del catalogo, indexados por id."""
    directorio = directorio or config.CATALOGO
    casos: dict[str, Caso] = {}
    for ruta in sorted(directorio.glob("*.yaml")):
        if ruta.name == "manifest.yaml":
            continue
        caso = cargar_caso(ruta)
        if caso.id in casos:
            raise CatalogoInvalido(f"id duplicado en el catalogo: {caso.id}")
        casos[caso.id] = caso
    return casos


def cargar_manifest(directorio: Path | None = None) -> dict[str, Any]:
    directorio = directorio or config.CATALOGO
    ruta = directorio / "manifest.yaml"
    if not ruta.exists():
        raise CatalogoInvalido("falta catalogo/manifest.yaml")
    with ruta.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def verificar_sincronia(directorio: Path | None = None) -> list[str]:
    """El manifest y los YAML deben coincidir (§7.4). Devuelve discrepancias."""
    casos = cargar_todos(directorio)
    manifest = cargar_manifest(directorio)
    en_manifest = {c["id"]: c for c in (manifest.get("casos") or [])}
    problemas: list[str] = []
    for cid in sorted(set(casos) - set(en_manifest)):
        problemas.append(f"{cid}: existe el YAML pero no esta en manifest.yaml")
    for cid in sorted(set(en_manifest) - set(casos)):
        problemas.append(f"{cid}: esta en manifest.yaml pero no existe el YAML")
    for cid in sorted(set(casos) & set(en_manifest)):
        if casos[cid].estado != en_manifest[cid].get("estado"):
            problemas.append(
                f"{cid}: estado desincronizado "
                f"(YAML={casos[cid].estado}, manifest={en_manifest[cid].get('estado')})"
            )
    return problemas
