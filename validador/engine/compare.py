"""Cruce A/B/C y evaluacion de la identidad — VIOLACIONES COMO SALIDA.

Reglas de este modulo (charter §1.4, §5.1, §5.2):

  * Ninguna funcion devuelve un booleano ni un total "para comparar a ojo".
    Devuelven el CONJUNTO DE FILAS que violan la identidad afirmada.
  * Cero violaciones es un RESULTADO, no un valor por omision. Si el universo
    esta vacio, eso no es "paso": es `universo_vacio` y se reporta como tal,
    porque no comparar nada nunca prueba nada.
  * Siempre se computa C (oraculo) y siempre se etiqueta la celda de la
    matriz A/B/C fila por fila. Se reporta la celda, no un semaforo agregado.

Polars mueve y cruza datos (joins, anti-joins, conteos). La aritmetica del
dinero se hace en Python con Decimal: los montos viajan como CADENA desde la
extraccion hasta aqui para que ningun float toque la ruta monetaria.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Iterable, Sequence

import polars as pl

from .errores import FloatEnDinero
from .sesgo import ResultadoSesgo, prueba_de_signo

# Celdas de la matriz de decision (charter §1.5 / CLAUDE.md §1)
CELDA_OK = "A=B=C"                 # los tres coinciden
CELDA_DEFECTO_NEGOCIO = "A=B!=C"   # ambos cores mal contra la norma — severidad maxima
CELDA_OF_CORREGIDO = "A!=B=C"      # defecto de OpenFin ya corregido en AurumCore
CELDA_DEFECTO_AURUM = "A=C!=B"     # defecto de AurumCore
CELDA_REGLA_MAL = "A!=B!=C"        # los tres distintos: la regla esta mal especificada
CELDA_SIN_A = "B=C (sin A)"        # no hay motor A para esta fila
CELDA_SIN_A_DIF = "B!=C (sin A)"
CELDA_SIN_B = "sin B"              # el core bajo prueba no tiene la fila
CELDA_SIN_C = "sin C"              # el oraculo no pudo calcular la fila

INTERPRETACION = {
    CELDA_OK: "Los tres motores coinciden.",
    CELDA_DEFECTO_NEGOCIO: "Defecto historico de negocio: AMBOS cores se apartan de la norma. Severidad maxima.",
    CELDA_OF_CORREGIDO: "Defecto de OpenFin ya corregido por AurumCore.",
    CELDA_DEFECTO_AURUM: "Defecto de AurumCore: se aparta de la norma donde OpenFin no lo hacia.",
    CELDA_REGLA_MAL: "Los tres difieren: la regla esta mal especificada o falta una pieza de conocimiento.",
    CELDA_SIN_A: "Sin motor A; B y C coinciden.",
    CELDA_SIN_A_DIF: "Sin motor A; B se aparta del oraculo.",
    CELDA_SIN_B: "AurumCore no tiene la fila que el oraculo espera (faltante, no diferencia de monto).",
    CELDA_SIN_C: "El oraculo no pudo calcular la fila: faltan insumos. NO es un pase.",
}


@dataclass
class ResultadoComparacion:
    """Salida de una comparacion. `violaciones` es el producto principal."""

    caso_id: str
    tipo: str
    universo: pl.DataFrame          # todas las filas con su celda y diferencia
    violaciones: pl.DataFrame       # subconjunto que viola la identidad
    matriz: dict[str, int]          # conteo por celda
    tolerancia: str
    sesgo: ResultadoSesgo | None = None
    universo_vacio: bool = False
    notas: list[str] = field(default_factory=list)

    @property
    def n_universo(self) -> int:
        return self.universo.height

    @property
    def n_violaciones(self) -> int:
        return self.violaciones.height

    def veredicto(self) -> str:
        """Etiqueta honesta. Nunca devuelve OK por omision."""
        if self.universo_vacio:
            return "UNIVERSO-VACIO"
        if self.sesgo is not None and self.sesgo.sesgo_detectado:
            return "SESGO"
        if self.n_violaciones > 0:
            return "VIOLACIONES"
        return "SIN-VIOLACIONES"

    def celda_dominante(self) -> str | None:
        conflictivas = {k: v for k, v in self.matriz.items() if k != CELDA_OK and v > 0}
        if not conflictivas:
            return None
        return max(conflictivas.items(), key=lambda kv: kv[1])[0]

    def resumen(self) -> dict:
        return {
            "caso": self.caso_id,
            "tipo": self.tipo,
            "veredicto": self.veredicto(),
            "n_universo": self.n_universo,
            "n_violaciones": self.n_violaciones,
            "tolerancia": self.tolerancia,
            "matriz": self.matriz,
            "celda_dominante": self.celda_dominante(),
            "sesgo": self.sesgo.como_dict() if self.sesgo else None,
            "notas": self.notas,
        }


# ---------------------------------------------------------------------------
# Utilidades de dinero
# ---------------------------------------------------------------------------

def asegurar_sin_float(df: pl.DataFrame, columnas: Iterable[str]) -> None:
    """Rechaza columnas monetarias en punto flotante (charter §1.3)."""
    malas = [
        c for c in columnas
        if c in df.columns and df.schema[c] in (pl.Float32, pl.Float64)
    ]
    if malas:
        raise FloatEnDinero(
            f"Columnas monetarias en float: {malas}. La extraccion debe entregarlas "
            f"como texto (::text en el SQL) para que Decimal las lea exactas. "
            f"Un float aqui invalida la corrida completa."
        )


def _a_decimal(valor) -> Decimal | None:
    if valor is None:
        return None
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, float):
        raise FloatEnDinero(f"Valor float en la ruta del dinero: {valor!r}")
    try:
        return Decimal(str(valor).strip())
    except (InvalidOperation, ValueError):
        return None


def _celda(a: Decimal | None, b: Decimal | None, c: Decimal | None,
           tol: Decimal) -> str:
    if c is None:
        return CELDA_SIN_C
    if b is None:
        return CELDA_SIN_B
    bc = abs(b - c) <= tol
    if a is None:
        return CELDA_SIN_A if bc else CELDA_SIN_A_DIF
    ab = abs(a - b) <= tol
    ac = abs(a - c) <= tol
    if ab and bc:
        return CELDA_OK
    if ab and not bc:
        return CELDA_DEFECTO_NEGOCIO
    if not ab and bc:
        return CELDA_OF_CORREGIDO
    if ac and not bc:
        return CELDA_DEFECTO_AURUM
    return CELDA_REGLA_MAL


# ---------------------------------------------------------------------------
# Comparacion de montos (la mayoria de los casos)
# ---------------------------------------------------------------------------

def comparar_montos(
    caso_id: str,
    df_b: pl.DataFrame,
    df_c: pl.DataFrame,
    llaves: Sequence[str],
    col_b: str,
    col_c: str,
    tolerancia: Decimal,
    df_a: pl.DataFrame | None = None,
    col_a: str | None = None,
    prueba_sesgo: bool = False,
    alfa_sesgo: str = "0.01",
) -> ResultadoComparacion:
    """Evalua  |C - B| <= tolerancia  fila por fila y devuelve las que la violan.

    El universo es el OUTER JOIN de B y C: una fila que exista en uno y no en
    el otro es una violacion de tipo faltante, no un renglon a ignorar. Ese
    detalle es la diferencia entre auditar y firmar.
    """
    llaves = list(llaves)
    notas: list[str] = []

    for nombre, df, col in (("B", df_b, col_b), ("C", df_c, col_c)):
        faltan = [k for k in llaves + [col] if k not in df.columns]
        if faltan:
            raise KeyError(f"{caso_id}: al motor {nombre} le faltan columnas {faltan}")
        asegurar_sin_float(df, [col])

    base = df_b.select(llaves + [pl.col(col_b).cast(pl.Utf8).alias("_b")]).join(
        df_c.select(llaves + [pl.col(col_c).cast(pl.Utf8).alias("_c")]),
        on=llaves, how="full", coalesce=True,
    )

    if df_a is not None and col_a:
        asegurar_sin_float(df_a, [col_a])
        faltan_a = [k for k in llaves + [col_a] if k not in df_a.columns]
        if faltan_a:
            notas.append(
                f"Motor A no aporta {faltan_a}: la matriz corre sin A y las celdas "
                f"quedan etiquetadas 'sin A'. NO se interpreta como coincidencia."
            )
            df_a = None
        else:
            base = base.join(
                df_a.select(llaves + [pl.col(col_a).cast(pl.Utf8).alias("_a")]),
                on=llaves, how="left", coalesce=True,
            )
    if "_a" not in base.columns:
        base = base.with_columns(pl.lit(None, dtype=pl.Utf8).alias("_a"))
        if df_a is None:
            notas.append("Corrida sin motor A (openfin): la matriz solo distingue B vs C.")

    if base.height == 0:
        vacio = base.with_columns([
            pl.lit(None, dtype=pl.Utf8).alias("dif_c_menos_b"),
            pl.lit(None, dtype=pl.Utf8).alias("celda"),
            pl.lit(None, dtype=pl.Utf8).alias("motivo"),
        ])
        return ResultadoComparacion(
            caso_id=caso_id, tipo="igualdad_montos", universo=vacio,
            violaciones=vacio, matriz={}, tolerancia=str(tolerancia),
            universo_vacio=True,
            notas=notas + [
                "UNIVERSO VACIO: la extraccion no devolvio filas comparables. "
                "Esto NO es un pase — revisar cohorte, ventana de fechas y filtros "
                "antes de concluir cualquier cosa."
            ],
        )

    difs: list[str | None] = []
    celdas: list[str] = []
    motivos: list[str | None] = []
    difs_decimal: list[Decimal] = []
    viola: list[bool] = []

    for fila in base.iter_rows(named=True):
        a = _a_decimal(fila.get("_a"))
        b = _a_decimal(fila.get("_b"))
        c = _a_decimal(fila.get("_c"))
        celda = _celda(a, b, c, tolerancia)
        celdas.append(celda)
        if b is None or c is None:
            difs.append(None)
            motivos.append(
                "AurumCore no tiene la fila (faltante)" if b is None
                else "El oraculo no pudo calcular la fila (insumo faltante)"
            )
            viola.append(True)
            continue
        d = c - b
        difs.append(str(d))
        difs_decimal.append(d)
        excede = abs(d) > tolerancia
        viola.append(excede)
        motivos.append(
            f"|C-B| = {abs(d)} > tolerancia {tolerancia}" if excede else None
        )

    universo = base.with_columns([
        pl.Series("dif_c_menos_b", difs, dtype=pl.Utf8),
        pl.Series("celda", celdas, dtype=pl.Utf8),
        pl.Series("motivo", motivos, dtype=pl.Utf8),
        pl.Series("_viola", viola, dtype=pl.Boolean),
    ]).rename({"_a": "a_openfin", "_b": "b_aurum", "_c": "c_oraculo"})

    violaciones = universo.filter(pl.col("_viola")).drop("_viola")
    universo = universo.drop("_viola")

    matriz = {c: 0 for c in INTERPRETACION}
    for c in celdas:
        matriz[c] = matriz.get(c, 0) + 1
    matriz = {k: v for k, v in matriz.items() if v > 0}

    resultado_sesgo = None
    if prueba_sesgo:
        resultado_sesgo = prueba_de_signo(difs_decimal, alfa=alfa_sesgo)

    return ResultadoComparacion(
        caso_id=caso_id, tipo="igualdad_montos", universo=universo,
        violaciones=violaciones, matriz=matriz, tolerancia=str(tolerancia),
        sesgo=resultado_sesgo, notas=notas,
    )


# ---------------------------------------------------------------------------
# Comparacion de existencia ("se come todas")
# ---------------------------------------------------------------------------

def comparar_existencia(
    caso_id: str,
    df_a: pl.DataFrame,
    df_b: pl.DataFrame,
    llaves: Sequence[str],
) -> ResultadoComparacion:
    """Set-diff en ambos sentidos: quien esta en A y no en B, y al reves.

    Las violaciones traen la columna `falta_en` para que se lea de inmediato
    de que lado esta el hueco.
    """
    llaves = list(llaves)
    for nombre, df in (("A", df_a), ("B", df_b)):
        faltan = [k for k in llaves if k not in df.columns]
        if faltan:
            raise KeyError(f"{caso_id}: al motor {nombre} le faltan llaves {faltan}")

    a = df_a.select(llaves).unique()
    b = df_b.select(llaves).unique()

    solo_a = a.join(b, on=llaves, how="anti").with_columns(
        pl.lit("aurum").alias("falta_en"),
        pl.lit("Existe en OpenFin y no en AurumCore").alias("motivo"),
    )
    solo_b = b.join(a, on=llaves, how="anti").with_columns(
        pl.lit("openfin").alias("falta_en"),
        pl.lit("Existe en AurumCore y no en OpenFin (revisar si es generado post-cutover)").alias("motivo"),
    )
    violaciones = pl.concat([solo_a, solo_b], how="vertical")

    comunes = a.join(b, on=llaves, how="semi").height
    matriz = {
        "en ambos": comunes,
        "solo openfin (falta en aurum)": solo_a.height,
        "solo aurum (falta en openfin)": solo_b.height,
    }
    universo = pl.concat(
        [
            a.join(b, on=llaves, how="semi").with_columns(
                pl.lit("ambos").alias("falta_en"), pl.lit(None, dtype=pl.Utf8).alias("motivo")
            ),
            violaciones,
        ],
        how="vertical",
    )
    vacio = a.height == 0 and b.height == 0
    return ResultadoComparacion(
        caso_id=caso_id, tipo="existencia", universo=universo,
        violaciones=violaciones, matriz=matriz, tolerancia="0",
        universo_vacio=vacio,
        notas=(
            ["UNIVERSO VACIO: ninguno de los dos cores devolvio filas. NO es un pase."]
            if vacio else
            ["Existencia por llave. Una llave presente de un solo lado es una violacion, "
             "no un residuo: 'se come todas' significa que el set-diff es vacio en ambos sentidos."]
        ),
    )


# ---------------------------------------------------------------------------
# Doble partida (familias contables B/C, tolerancia 0.00)
# ---------------------------------------------------------------------------

def comparar_doble_partida(
    caso_id: str,
    df: pl.DataFrame,
    llaves: Sequence[str],
    col_cargo: str,
    col_abono: str,
) -> ResultadoComparacion:
    """Por cada grupo de `llaves`: suma de cargos == suma de abonos, tolerancia 0.00.

    Identidad contable: la tolerancia es CERO, sin excepcion (charter §1.7).
    """
    llaves = list(llaves)
    asegurar_sin_float(df, [col_cargo, col_abono])

    filas: dict[tuple, list[Decimal]] = {}
    for fila in df.iter_rows(named=True):
        k = tuple(fila[x] for x in llaves)
        cargo = _a_decimal(fila.get(col_cargo)) or Decimal("0")
        abono = _a_decimal(fila.get(col_abono)) or Decimal("0")
        acc = filas.setdefault(k, [Decimal("0"), Decimal("0")])
        acc[0] += cargo
        acc[1] += abono

    registros = []
    for k, (cargo, abono) in filas.items():
        d = cargo - abono
        registros.append({
            **dict(zip(llaves, k)),
            "suma_cargos": str(cargo),
            "suma_abonos": str(abono),
            "descuadre": str(d),
            "motivo": None if d == 0 else f"descuadre {d} (identidad contable exige 0.00)",
            "_viola": d != 0,
        })

    universo = pl.DataFrame(registros) if registros else pl.DataFrame(
        schema={**{k: pl.Utf8 for k in llaves},
                "suma_cargos": pl.Utf8, "suma_abonos": pl.Utf8,
                "descuadre": pl.Utf8, "motivo": pl.Utf8, "_viola": pl.Boolean}
    )
    violaciones = universo.filter(pl.col("_viola")).drop("_viola") if registros else universo.drop("_viola")
    universo = universo.drop("_viola")

    return ResultadoComparacion(
        caso_id=caso_id, tipo="doble_partida", universo=universo,
        violaciones=violaciones,
        matriz={"grupos": len(registros), "descuadrados": violaciones.height},
        tolerancia="0.00", universo_vacio=not registros,
        notas=(["UNIVERSO VACIO: no hay asientos en la ventana. NO es un pase."]
               if not registros else []),
    )
