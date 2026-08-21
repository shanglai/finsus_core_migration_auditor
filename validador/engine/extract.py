"""Extraccion BOUNDED y de SOLO LECTURA contra los cores.

Tres defensas, en este orden:

  1. SOLO LECTURA. Se rechaza cualquier SQL con verbos de escritura ANTES de
     conectar, la sesion abre con `default_transaction_read_only = on` y
     `readonly=True`, y la transaccion cierra con ROLLBACK siempre. La defensa
     de la aplicacion no sustituye a un rol de BD de solo lectura: son capas.

  2. ACOTADA. Se lee con cursor del servidor y se pide UNA fila mas que el
     limite. Si llega, se aborta con ExtraccionNoAcotada en vez de truncar.
     Truncar en silencio es peor que fallar: una muestra truncada se lee
     despues como universo completo.

  3. SIN FLOAT. psycopg2 entrega `numeric` como Decimal; aqui se convierte a
     CADENA antes de entrar a Polars, para que la ruta del dinero no pase
     nunca por punto flotante.

La cohorte se inyecta como CTE `VALUES` (no se crean tablas temporales: eso
seria escritura). Los identificadores de la cohorte se validan contra una
lista blanca antes de interpolarse.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Sequence

import polars as pl

from . import config
from .errores import DestinoSensible, ExtraccionNoAcotada, SolaLecturaViolada

# Verbos de escritura y DDL. Se busca como palabra completa, fuera de comentarios.
_VERBOS_PROHIBIDOS = (
    "insert", "update", "delete", "truncate", "drop", "create", "alter",
    "grant", "revoke", "merge", "copy", "vacuum", "reindex", "cluster",
    "refresh", "call", "do", "lock", "commit", "savepoint",
)
_RE_PROHIBIDOS = re.compile(r"\b(" + "|".join(_VERBOS_PROHIBIDOS) + r")\b", re.IGNORECASE)

# Identificadores admisibles en una cohorte (cuentas, ids). Lista blanca estricta.
_RE_ID_COHORTE = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")

# :param -> %(param)s, sin tocar los casts ::text
_RE_PARAM = re.compile(r"(?<!:):([a-z_][a-z0-9_]*)", re.IGNORECASE)


@dataclass
class Extraccion:
    """Resultado de correr un SQL: los datos y la consulta EXACTA que los produjo."""

    core: str
    archivo: str
    statements: list[str]           # texto final, tal cual se envio al servidor
    params: dict[str, Any]
    tablas: list[pl.DataFrame]
    filas: list[int]

    @property
    def principal(self) -> pl.DataFrame:
        """La primera tabla; es la que consumen los comparadores por convencion."""
        return self.tablas[0] if self.tablas else pl.DataFrame()


# ---------------------------------------------------------------------------
# Preparacion del SQL
# ---------------------------------------------------------------------------

def quitar_comentarios(texto: str) -> str:
    """Quita comentarios de linea antes de partir por ';'.

    Un ';' dentro de un comentario partiria el statement a la mitad.
    """
    return "\n".join(re.sub(r"--.*$", "", ln) for ln in texto.splitlines())


def asegurar_solo_lectura(sql: str, origen: str = "") -> None:
    """Rechaza el SQL si contiene verbos de escritura o DDL."""
    limpio = quitar_comentarios(sql)
    hallados = sorted({m.group(1).lower() for m in _RE_PROHIBIDOS.finditer(limpio)})
    if hallados:
        raise SolaLecturaViolada(
            f"{origen or 'SQL'}: verbos de escritura/DDL detectados {hallados}. "
            f"El VALIDADOR solo lee. Si el verbo aparece dentro de un literal, "
            f"reescribir la consulta: no se hacen excepciones."
        )


def _valores_cohorte(valores: Sequence[Any], columnas: int = 1) -> str:
    """Construye el cuerpo de un VALUES validando cada identificador."""
    if not valores:
        return "(NULL)" if columnas == 1 else "(" + ",".join(["NULL"] * columnas) + ")"
    partes = []
    for v in valores:
        if isinstance(v, (tuple, list)):
            elems = []
            for x in v:
                if isinstance(x, int):
                    elems.append(str(x))
                else:
                    s = str(x)
                    if not _RE_ID_COHORTE.match(s):
                        raise ValueError(f"Identificador de cohorte no admisible: {s!r}")
                    elems.append("'" + s.replace("'", "''") + "'")
            partes.append("(" + ",".join(elems) + ")")
        elif isinstance(v, int):
            partes.append(f"({v})")
        else:
            s = str(v)
            if not _RE_ID_COHORTE.match(s):
                raise ValueError(f"Identificador de cohorte no admisible: {s!r}")
            partes.append("('" + s.replace("'", "''") + "')")
    return ",".join(partes)


def cte_cohorte(cohortes: dict[str, dict]) -> str:
    """Arma el prefijo WITH con las cohortes que el SQL declare usar.

    `cohortes` = {nombre_cte: {"columnas": [...], "valores": [...]}}
    """
    if not cohortes:
        return ""
    piezas = []
    for nombre, spec in cohortes.items():
        cols = spec["columnas"]
        vals = _valores_cohorte(spec.get("valores") or [], columnas=len(cols))
        piezas.append(f"{nombre}({','.join(cols)}) as (values {vals})")
    return "with " + ",\n     ".join(piezas) + "\n"


def preparar(texto: str, cohortes: dict[str, dict] | None = None,
             origen: str = "") -> tuple[list[str], list[str]]:
    """Devuelve (statements listos, nombres de parametros usados).

    Inyecta el CTE de cohorte solo en los statements que la referencian, y
    traduce `:param` a `%(param)s` para psycopg2.
    """
    asegurar_solo_lectura(texto, origen)
    cohortes = cohortes or {}
    sin_com = quitar_comentarios(texto)
    stmts = [s.strip() for s in sin_com.split(";") if s.strip()]

    usados: set[str] = set()
    out: list[str] = []
    for s in stmts:
        necesarias = {n: spec for n, spec in cohortes.items() if re.search(rf"\b{n}\b", s)}
        if necesarias:
            prefijo = cte_cohorte(necesarias).rstrip()          # "with a(...) as (...), b(...) as (...)"
            if re.match(r"^\s*with\s", s, re.IGNORECASE):
                # El SQL ya trae sus propios CTE: se fusionan con una coma en vez
                # de anteponer un segundo WITH (que seria sintaxis invalida).
                resto = re.sub(r"^\s*with\s+", "", s, count=1, flags=re.IGNORECASE)
                s = prefijo + ",\n     " + resto
            else:
                s = prefijo + "\n" + s
        for m in _RE_PARAM.finditer(s):
            usados.add(m.group(1))
        s = _RE_PARAM.sub(r"%(\1)s", s)
        out.append(s)
    return out, sorted(usados)


# ---------------------------------------------------------------------------
# Ejecucion
# ---------------------------------------------------------------------------

def _normalizar(valor: Any) -> Any:
    """Decimal -> cadena exacta (sin float). Fechas -> ISO. Resto tal cual."""
    if isinstance(valor, Decimal):
        return str(valor)
    if isinstance(valor, float):
        # Si un core entrega double precision, lo dejamos ver como texto pero
        # marcado: el catalogo deberia castear a numeric/::text en el SQL.
        return repr(valor)
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    return valor


def conectar(cfg: dict[str, Any]):
    """Abre la conexion. Acepta DSN completo o parametros sueltos."""
    import psycopg2

    if cfg.get("dsn"):
        return psycopg2.connect(cfg["dsn"])
    kw = {k: cfg[k] for k in ("host", "port", "dbname", "user", "password", "sslmode")
          if k in cfg}
    return psycopg2.connect(**kw)


def probar_conexion(core: str, conexiones: dict | None = None) -> dict[str, Any]:
    """Prueba de vuelo previa: conecta en SOLO LECTURA y describe el destino.

    No corre ningun caso. Sirve para responder, antes de auditar nada:
    ¿a que base estoy pegado, con que usuario, y estoy realmente en solo
    lectura?

    Ademas INTENTA una escritura trivial y verifica que el servidor la
    rechace. Confiar en que la sesion es de solo lectura sin comprobarlo es
    justo el tipo de supuesto que este proyecto no acepta.

    Sobre el rol del servidor: se REPORTA `pg_is_in_recovery()`, que no es lo
    mismo que "es replica". Solo detecta standby por streaming; una replica
    t-1 restaurada desde respaldo responde `false` y sigue siendo replica. El
    rol se DECLARA en db_connections.yaml (`rol:`), no se infiere.
    """
    conexiones = conexiones if conexiones is not None else config.cargar_conexiones()
    cfg = config.config_core(core, conexiones)
    meta = config.metadatos_core(core, conexiones)
    info: dict[str, Any] = {"core": core, **meta}

    conn = conectar(cfg)
    try:
        conn.set_session(readonly=True, autocommit=False)
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only = on")
            cur.execute(
                "SELECT current_database(), current_user, version(), "
                "pg_is_in_recovery(), current_setting('transaction_read_only'), now()"
            )
            db, usuario, version, en_recuperacion, solo_lectura, ahora = cur.fetchone()
            info.update({
                "base": db, "usuario": usuario,
                "servidor": version.split(",")[0],
                # Observado, no interpretado: `false` NO significa "no es replica".
                "en_recuperacion": bool(en_recuperacion),
                "solo_lectura": solo_lectura == "on",
                "hora_servidor": ahora.isoformat(),
            })

        # Comprobacion activa: la escritura debe fallar.
        try:
            with conn.cursor() as cur:
                cur.execute("CREATE TEMP TABLE _validador_prueba_escritura (x int)")
            info["escritura_bloqueada"] = False
        except Exception as exc:  # noqa: BLE001 — que falle es el resultado deseado
            info["escritura_bloqueada"] = True
            info["error_escritura"] = type(exc).__name__
        finally:
            conn.rollback()
    finally:
        conn.rollback()
        conn.close()
    return info


def ejecutar(
    core: str,
    statements: Sequence[str],
    params: dict[str, Any],
    archivo: str = "",
    max_filas: int | None = None,
    conexiones: dict | None = None,
    statement_timeout_ms: int | None = None,
    permitir_sensible: bool = False,
) -> Extraccion:
    """Corre los statements contra `core` en SOLO LECTURA y devuelve DataFrames."""
    conexiones = conexiones if conexiones is not None else config.cargar_conexiones()

    if config.es_sensible(core, conexiones) and not permitir_sensible:
        raise DestinoSensible(
            f"El destino {core!r} esta marcado `sensible: true` en "
            f"db_connections.yaml y no aguanta una extraccion de auditoria. "
            f"No se conecto. Si de verdad hace falta, correr con "
            f"--permitir-sensible y con una cohorte minima."
        )

    cfg = config.config_core(core, conexiones)
    limite = max_filas or config.limite_filas(conexiones)
    timeout = statement_timeout_ms or int(cfg.get("statement_timeout_ms", 300_000))

    for s in statements:
        asegurar_solo_lectura(s, archivo)

    conn = conectar(cfg)
    tablas: list[pl.DataFrame] = []
    conteos: list[int] = []
    try:
        conn.set_session(readonly=True, autocommit=False)
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only = on")
            cur.execute(f"SET statement_timeout = {int(timeout)}")

        for i, stmt in enumerate(statements, 1):
            # Cursor del servidor: no trae todo a memoria antes de contar.
            nombre = f"validador_{i}"
            with conn.cursor(name=nombre) as cur:
                cur.itersize = 10_000
                cur.execute(stmt, params)
                filas = cur.fetchmany(limite + 1)
                cols = [d[0] for d in cur.description] if cur.description else []
            if len(filas) > limite:
                raise ExtraccionNoAcotada(
                    f"{archivo or core} statement {i}: la consulta devolvio mas de "
                    f"{limite:,} filas. NO se trunca la muestra en silencio — acotar "
                    f"la cohorte o la ventana de fechas y volver a correr. "
                    f"(Una muestra truncada se lee despues como universo completo.)"
                )
            datos = [[_normalizar(v) for v in fila] for fila in filas]
            df = pl.DataFrame(datos, schema=cols, orient="row") if cols else pl.DataFrame()
            tablas.append(df)
            conteos.append(df.height)
    finally:
        conn.rollback()
        conn.close()

    return Extraccion(core=core, archivo=archivo, statements=list(statements),
                      params=dict(params), tablas=tablas, filas=conteos)


def extraer_archivo(
    core: str,
    ruta_sql: str | Path,
    params: dict[str, Any],
    cohortes: dict[str, dict] | None = None,
    max_filas: int | None = None,
    conexiones: dict | None = None,
    dry_run: bool = False,
    permitir_sensible: bool = False,
) -> Extraccion:
    """Prepara y (salvo dry-run) ejecuta un SQL del catalogo."""
    ruta = config.resolver_ruta(str(ruta_sql))
    texto = ruta.read_text(encoding="utf-8")
    stmts, usados = preparar(texto, cohortes, origen=str(ruta_sql))

    faltantes = [p for p in usados if p not in params]
    if faltantes:
        raise KeyError(
            f"{ruta_sql}: la consulta usa parametros no provistos: {faltantes}. "
            f"Declararlos en el YAML del caso o pasarlos con --param."
        )
    efectivos = {p: params[p] for p in usados}

    if dry_run:
        return Extraccion(core=core, archivo=str(ruta_sql), statements=stmts,
                          params=efectivos, tablas=[], filas=[])

    return ejecutar(core, stmts, efectivos, archivo=str(ruta_sql),
                    max_filas=max_filas, conexiones=conexiones,
                    permitir_sensible=permitir_sensible)
