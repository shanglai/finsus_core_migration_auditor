"""Orquestador: extract -> warehouse -> oraculo -> compare -> evidencia.

Un caso BLOQUEADO tambien escribe evidencia. Es intencional: si un caso no se
pudo correr, esa es una observacion del auditor y tiene que quedar registrada
con su motivo y su fecha. Un caso sin rastro se confunde con un caso limpio.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

import polars as pl

from . import catalogo as cat
from . import compare, config, evidencia, extract, oracle_runner, warehouse
from .errores import ErrorValidador, ReglaFaltante


@dataclass
class Corrida:
    caso: cat.Caso
    parametros: dict[str, Any]
    resultado: compare.ResultadoComparacion | None = None
    manifiesto: evidencia.Manifiesto | None = None
    ruta_evidencia: str = ""
    estado: str = ""                 # resultado_global
    consultas: dict = field(default_factory=dict)
    advertencias: list[str] = field(default_factory=list)
    dry_run: bool = False

    def resumen_texto(self) -> str:
        lineas = [f"Caso {self.caso.id} — {self.caso.titulo}", f"  estado: {self.estado}"]
        if self.resultado:
            r = self.resultado
            lineas.append(f"  universo: {r.n_universo} filas · violaciones: {r.n_violaciones}")
            if r.matriz:
                celdas = " · ".join(f"{k}={v}" for k, v in r.matriz.items())
                lineas.append(f"  matriz A/B/C: {celdas}")
            if r.sesgo:
                lineas.append(
                    f"  sesgo: {'DETECTADO' if r.sesgo.sesgo_detectado else 'no detectado'} "
                    f"(p={r.sesgo.p_valor}, +{r.sesgo.n_positivas}/-{r.sesgo.n_negativas})"
                )
        for a in self.advertencias:
            lineas.append(f"  [aviso] {a}")
        if self.ruta_evidencia:
            lineas.append(f"  evidencia: {self.ruta_evidencia}")
        return "\n".join(lineas)


def resolver_parametros(caso: cat.Caso, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Defaults del catalogo + overrides del CLI. Falla si falta un requerido."""
    overrides = overrides or {}
    params = dict(caso.defaults())
    params.update({k: v for k, v in overrides.items() if v is not None})
    faltan = [p for p in caso.requeridos() if params.get(p) in (None, "", [])]
    if faltan:
        raise ErrorValidador(
            f"{caso.id}: faltan parametros requeridos {faltan}. "
            f"Pasarlos con --param nombre=valor (o --cohorte-archivo para listas)."
        )
    return params


def _cohortes_desde_params(params: dict[str, Any]) -> dict[str, dict]:
    """Traduce parametros de tipo cohorte a especificaciones de CTE."""
    cohortes: dict[str, dict] = {}
    if params.get("cohorte"):
        cohortes["cohorte_acc"] = {"columnas": ["account_number"], "valores": list(params["cohorte"])}
        cohortes["cohorte"] = {"columnas": ["accountholder_number"], "valores": list(params["cohorte"])}
    if params.get("cohorte_of"):
        cohortes["cohorte_of"] = {
            "columnas": ["id_sucursal", "id_role", "id_asociado"],
            "valores": list(params["cohorte_of"]),
        }
    return cohortes


def _snapshot(caso: cat.Caso, params: dict, conexiones: dict) -> dict:
    """Identificacion del corte. Sin credenciales."""
    cores = {}
    for core in caso.extraccion:
        try:
            cfg = config.config_core(core, conexiones)
            cores[core] = {
                "host": cfg.get("host"), "dbname": cfg.get("dbname"),
                "user": cfg.get("user"),
                "etiqueta": cfg.get("etiqueta_snapshot", ""),
            }
        except Exception as exc:  # noqa: BLE001
            cores[core] = {"error": str(exc)}
    return {
        "cores": cores,
        "fecha_ini": params.get("fecha_ini"),
        "fecha_fin": params.get("fecha_fin"),
        "fecha_corte": params.get("fecha_corte"),
        "n_cohorte": len(params.get("cohorte") or []),
    }


def _evidencia_bloqueada(caso: cat.Caso, params: dict, motivo: str,
                         consultas: dict, snapshot: dict, estado: str = "BLOQUEADO") -> Corrida:
    """Escribe evidencia de un caso que NO se pudo correr. No es un pase."""
    huella = evidencia.hash_corrida(caso.id, params, consultas, "", str(caso.tolerancia.max_evento))
    man = evidencia.Manifiesto(
        caso_id=caso.id, titulo=caso.titulo, motor=caso.motor, dominio=caso.dominio,
        severidad=caso.severidad, regla_ref=list(caso.regla_ref),
        version_regla="[no ejecutado]", estado_catalogo=caso.estado,
        identidad=caso.identidad, matriz_esperada=caso.matriz_esperada,
        tolerancia={"tipo": caso.tolerancia.tipo,
                    "max_evento": str(caso.tolerancia.max_evento),
                    "prueba_sesgo": caso.tolerancia.prueba_sesgo},
        parametros=params, snapshot=snapshot, consultas=consultas, oraculo={},
        resultado={
            "veredicto": estado,
            "motivo": motivo,
            "advertencia": "NO-CORRIDO no significa que pase. Este caso no aporta cobertura.",
        },
        resultado_global=estado, bloqueo=motivo, hash=huella,
    )
    ruta = evidencia.escribir(man)
    return Corrida(caso=caso, parametros=params, manifiesto=man,
                   ruta_evidencia=str(ruta), estado=estado, consultas=consultas,
                   advertencias=[motivo])


def correr_caso(
    caso: cat.Caso,
    overrides: dict[str, Any] | None = None,
    dry_run: bool = False,
    conexiones: dict | None = None,
    max_filas: int | None = None,
    escribir_evidencia: bool = True,
    permitir_sensible: bool = False,
) -> Corrida:
    """Corre un caso de punta a punta."""
    conexiones = conexiones if conexiones is not None else config.cargar_conexiones()
    params = resolver_parametros(caso, overrides)
    snapshot = _snapshot(caso, params, conexiones)
    cohortes = _cohortes_desde_params(params)
    # Los supuestos del caso viajan con la evidencia: una decision de modelado
    # que no queda escrita se lee despues como hecho verificado.
    advertencias: list[str] = [f"[SUPUESTO] {s}" for s in caso.supuestos]

    # --- Preparacion de consultas (siempre, incluso en dry-run) --------------
    consultas: dict[str, dict] = {}
    for core, ruta_sql in caso.extraccion.items():
        if str(ruta_sql).strip().upper() == cat.PENDIENTE:
            consultas[core] = {"archivo": cat.PENDIENTE, "statements": [], "filas": []}
            continue
        try:
            ext = extract.extraer_archivo(core, ruta_sql, params, cohortes,
                                          max_filas=max_filas, conexiones=conexiones,
                                          dry_run=True)
            consultas[core] = {"archivo": ruta_sql, "statements": ext.statements,
                               "params": {k: _mostrable(v) for k, v in ext.params.items()},
                               "filas": []}
        except Exception as exc:  # noqa: BLE001
            consultas[core] = {"archivo": ruta_sql, "error": str(exc),
                               "statements": [], "filas": []}
            advertencias.append(f"{core}: {exc}")

    # --- Guardas: lo que no se puede correr se marca, no se aprueba ---------
    if not caso.ejecutable:
        motivo = caso.motivo_no_ejecutable()
        if dry_run or not escribir_evidencia:
            return Corrida(caso=caso, parametros=params, estado="BLOQUEADO",
                           consultas=consultas, advertencias=[motivo], dry_run=dry_run)
        c = _evidencia_bloqueada(caso, params, motivo, consultas, snapshot)
        c.advertencias.extend(advertencias)
        return c

    if dry_run:
        return Corrida(caso=caso, parametros=params, estado="DRY-RUN",
                       consultas=consultas, advertencias=advertencias, dry_run=True)

    # --- Extraccion real -----------------------------------------------------
    try:
        extracciones: dict[str, extract.Extraccion] = {}
        for core, ruta_sql in caso.extraccion.items():
            if str(ruta_sql).strip().upper() == cat.PENDIENTE:
                advertencias.append(
                    f"Motor {core} sin consulta (PENDIENTE): la matriz corre sin el. "
                    f"Su ausencia NO se interpreta como coincidencia."
                )
                continue
            ext = extract.extraer_archivo(core, ruta_sql, params, cohortes,
                                          max_filas=max_filas, conexiones=conexiones,
                                          permitir_sensible=permitir_sensible)
            extracciones[core] = ext
            consultas[core]["filas"] = ext.filas

        # --- Warehouse -------------------------------------------------------
        with warehouse.Warehouse() as wh:
            for core, ext in extracciones.items():
                for i, df in enumerate(ext.tablas, 1):
                    sufijo = "" if i == 1 else f"s{i}"
                    wh.cargar(warehouse.nombre_tabla(caso.id, core, sufijo), df)

            universo = pl.DataFrame()
            conjuntos = None
            if caso.comparacion.tipo == "suma_cero":
                universo = _construir_universo(caso, wh, extracciones)
            elif caso.comparacion.tipo == "existencia":
                conjuntos = _construir_conjuntos(caso, wh, extracciones)
            else:
                universo = _construir_universo(caso, wh, extracciones)

        # --- Oraculo (motor C) ----------------------------------------------
        # En un caso de existencia el motor C es la identidad de conjuntos
        # ("el set-diff debe ser vacio en ambos sentidos"): no hay monto que
        # recalcular, asi que no hay oraculo que invocar.
        salida_c = None
        if caso.comparacion.tipo not in ("existencia", "suma_cero"):
            salida_c = oracle_runner.correr(
                caso.oraculo, universo, caso.comparacion.llaves, params
            )
            if salida_c.n_fallidas:
                advertencias.append(
                    f"El oraculo no pudo calcular {salida_c.n_fallidas} de "
                    f"{universo.height} filas: {list(salida_c.errores)[:3]}. "
                    f"Esas filas cuentan como violacion 'sin C', no se descartan."
                )

        # --- Comparacion -----------------------------------------------------
        resultado = _comparar(caso, universo, salida_c, extracciones, advertencias,
                              conjuntos=conjuntos)

    except Exception as exc:  # noqa: BLE001
        # CUALQUIER fallo — no solo los nuestros. Una caida de red, un timeout
        # o una columna que no existe tienen que terminar en EVIDENCIA con
        # resultado ERROR, no en un traceback: un caso que revienta y no deja
        # rastro se confunde despues con un caso que nunca se intento, y eso
        # es exactamente el all-pass que este disenno persigue evitar.
        detalle = f"{type(exc).__name__}: {exc}"
        c = _evidencia_bloqueada(caso, params, detalle, consultas, snapshot, estado="ERROR")
        c.advertencias.extend(advertencias)
        return c

    # --- Evidencia -----------------------------------------------------------
    huella = evidencia.hash_corrida(
        caso.id, params,
        {k: v.get("statements") for k, v in consultas.items()},
        salida_c.sha256 if salida_c else "", str(caso.tolerancia.max_evento),
    )
    info_oraculo = (
        {"referencia": caso.oraculo, "modulo": salida_c.modulo,
         "sha256": salida_c.sha256, "version_regla": salida_c.version_regla,
         "filas_calculadas": salida_c.n_calculadas,
         "filas_fallidas": salida_c.n_fallidas, "errores": salida_c.errores}
        if salida_c else
        {"referencia": "n/a",
         "version_regla": ("identidad de conjuntos (set-diff)"
                           if caso.comparacion.tipo == "existencia"
                           else "identidad de suma (las columnas se cancelan)"),
         "nota": ("El motor C es la identidad misma, no un monto recalculado: "
                  "no hay oraculo que invocar.")}
    )
    man = evidencia.Manifiesto(
        caso_id=caso.id, titulo=caso.titulo, motor=caso.motor, dominio=caso.dominio,
        severidad=caso.severidad, regla_ref=list(caso.regla_ref),
        version_regla=info_oraculo.get("version_regla", ""), estado_catalogo=caso.estado,
        identidad=caso.identidad, matriz_esperada=caso.matriz_esperada,
        tolerancia={"tipo": caso.tolerancia.tipo,
                    "max_evento": str(caso.tolerancia.max_evento),
                    "prueba_sesgo": caso.tolerancia.prueba_sesgo,
                    "alfa_sesgo": caso.tolerancia.alfa_sesgo},
        parametros={k: _mostrable(v) for k, v in params.items()},
        snapshot=snapshot, consultas=consultas,
        oraculo=info_oraculo,
        resultado=resultado.resumen(), resultado_global=resultado.veredicto(),
        hash=huella, advertencias=advertencias,
    )

    ruta = ""
    if escribir_evidencia:
        ruta = str(evidencia.escribir(man, resultado.violaciones, resultado.universo))

    return Corrida(caso=caso, parametros=params, resultado=resultado, manifiesto=man,
                   ruta_evidencia=ruta, estado=resultado.veredicto(),
                   consultas=consultas, advertencias=advertencias)


def _mostrable(valor: Any) -> Any:
    """Recorta listas largas para que el manifiesto sea legible (guarda el conteo)."""
    if isinstance(valor, (list, tuple)) and len(valor) > 25:
        return {"n": len(valor), "muestra": list(valor)[:25], "nota": "lista recortada en el manifiesto"}
    return valor


def _construir_universo(caso: cat.Caso, wh: warehouse.Warehouse,
                        extracciones: dict) -> pl.DataFrame:
    """El universo del caso: lo que el oraculo va a recalcular.

    Se declara en el YAML. Si el caso trae `universo.sql`, se evalua en DuckDB
    sobre las tablas ya cargadas; si trae `universo.fuente`, se toma la tabla
    de ese core tal cual.
    """
    spec = caso.universo or {}
    if spec.get("sql"):
        return wh.consultar(spec["sql"])
    fuente = spec.get("fuente", "aurum")
    nombre = warehouse.nombre_tabla(caso.id, fuente)
    if not wh.existe(nombre):
        raise ErrorValidador(
            f"{caso.id}: no hay tabla {nombre} para construir el universo. "
            f"Declarar `universo.sql` en el YAML del caso."
        )
    return wh.tabla(nombre)


def _construir_conjuntos(caso: cat.Caso, wh: warehouse.Warehouse,
                         extracciones: dict) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Los dos conjuntos a cruzar en un caso de existencia.

    Casi nunca los dos cores exponen la llave de correlacion con el mismo
    nombre ni el mismo formato: OpenFin la lleva partida en columnas y
    AurumCore concatenada en `account_number`. El YAML declara `universo.sql_a`
    y `universo.sql_b` para NORMALIZARLA en DuckDB antes del set-diff.

    Sin esa normalizacion el set-diff saldria enorme por un problema de llave
    y no de datos — un falso hallazgo, que en una auditoria cuesta tanta
    credibilidad como un falso pase.
    """
    spec = caso.universo or {}
    c = caso.comparacion

    def _lado(sql_key: str, core: str) -> pl.DataFrame:
        if spec.get(sql_key):
            return wh.consultar(spec[sql_key])
        if core in extracciones:
            return extracciones[core].principal
        return pl.DataFrame()

    return _lado("sql_a", c.fuente_a), _lado("sql_b", c.fuente_b)


def _comparar(caso: cat.Caso, universo: pl.DataFrame,
              salida_c: oracle_runner.SalidaOraculo | None,
              extracciones: dict, advertencias: list[str],
              conjuntos: tuple[pl.DataFrame, pl.DataFrame] | None = None
              ) -> compare.ResultadoComparacion:
    c = caso.comparacion
    llaves = list(c.llaves)

    if c.tipo == "existencia":
        df_a, df_b = conjuntos if conjuntos else (pl.DataFrame(), pl.DataFrame())
        return compare.comparar_existencia(caso.id, df_a, df_b, llaves)

    if c.tipo == "suma_cero":
        return compare.comparar_suma_cero(
            caso.id, universo, llaves, c.columnas, caso.tolerancia.max_evento
        )

    if c.tipo == "doble_partida":
        df = extracciones[c.fuente_b].principal
        return compare.comparar_doble_partida(
            caso.id, df, llaves, c.columna_a or "cargo", c.columna_b or "abono"
        )

    # igualdad_montos
    if c.columna_b in universo.columns:
        df_b = universo.select(llaves + [c.columna_b])
    elif c.fuente_b in extracciones:
        df_b = extracciones[c.fuente_b].principal.select(llaves + [c.columna_b])
    else:
        raise ErrorValidador(
            f"{caso.id}: no hay de donde tomar el motor B ({c.columna_b!r} desde "
            f"{c.fuente_b!r}). Declararlo en universo.sql o en extraccion."
        )
    df_c = salida_c.df.rename({"c_oraculo": c.columna_c}) \
        if "c_oraculo" in salida_c.df.columns else salida_c.df

    df_a = None
    if c.columna_a and c.fuente_a in extracciones:
        candidato = extracciones[c.fuente_a].principal
        if c.columna_a in candidato.columns:
            df_a = candidato
        else:
            advertencias.append(
                f"El motor A no trae la columna {c.columna_a!r}: la matriz corre sin A."
            )

    return compare.comparar_montos(
        caso_id=caso.id, df_b=df_b, df_c=df_c, llaves=llaves,
        col_b=c.columna_b, col_c=c.columna_c,
        tolerancia=caso.tolerancia.max_evento,
        df_a=df_a, col_a=c.columna_a,
        prueba_sesgo=caso.tolerancia.prueba_sesgo,
        alfa_sesgo=caso.tolerancia.alfa_sesgo,
    )
