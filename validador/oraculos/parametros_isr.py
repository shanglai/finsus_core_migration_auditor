# -*- coding: utf-8 -*-
"""ORACULO de PARAMETROS FISCALES (motor C) — la norma como valor esperado.

Caso ISR-03. Aqui el "calculo" es una lectura de la norma: para cada parametro
que el core tiene configurado, el oraculo dice cuanto DEBERIA valer segun la
LIF / LISR / UMA del anio de causacion, y el comparador exhibe la diferencia.

Este es el caso-trampa vivo del charter §5 (ultimo parrafo). C-001 documenta
que AurumCore tiene configurado `yield.tax.exempt.amount = 206,367.60` (5 x UMA
2025) mientras APLICA 213,973.20 (5 x UMA 2026). El VALIDADOR tiene que
exhibir ese rezago. Si esta corrida sale limpia, el tooling esta mal — no el
core.

Sustento: K-FIS-004 (sustento normativo), S-FIS-001 §Parametros, P-010 (cerrada),
C-001 (contradiccion abierta).
"""

from __future__ import annotations

from decimal import Decimal

from oraculos.isr import PARAMETROS_POR_ANIO, parametros_anio

VERSION_REGLA = "K-FIS-004 / S-FIS-001 §Parametros (P-010 cerrada)"

# Nombre del parametro en el core -> como se deriva de la norma.
# Se cubre tanto `system_configuration.name` como las columnas de `cat_tax`.
CATALOGO_NORMATIVO: dict[str, str] = {
    "yield.tax.exempt.amount": "exencion",       # 5 x UMA del anio
    "tax.exempt.amount": "exencion",
    "exempt.amount": "exencion",
    "tax.days.year": "dias_anio",                # 365
    "cat_tax.isr": "tasa_isr_fraccion",          # 0.009 (fraccion, no porcentaje)
    "account_tax.isr": "tasa_isr_fraccion",
    "isr": "tasa_isr_fraccion",
    "uma": "uma_anual",
    "uma.anual": "uma_anual",
}

FUENTE_NORMATIVA = {
    "exencion": "LISR Art. 93 fr. XX — 5 x UMA anual (beneficio SOFIPO)",
    "dias_anio": "Prorrateo anual de la tasa (S-FIS-001; tax.days.year)",
    "tasa_isr_fraccion": "LIF Art. 24 del ejercicio (remite a LISR 54/135)",
    "uma_anual": "UMA anual INEGI, vigente desde el 1-feb",
}


def valor_normativo(concepto: str, anio: int) -> Decimal:
    """Valor que la norma exige para `concepto` en el anio de causacion."""
    p = parametros_anio(anio)
    if concepto == "exencion":
        return Decimal(p["uma_anual"]) * Decimal(p["multiplicador_uma"])
    if concepto == "dias_anio":
        return Decimal(p["dias_anio"])
    if concepto == "tasa_isr_fraccion":
        return Decimal(p["tasa_anual"]) / Decimal("100")
    if concepto == "uma_anual":
        return Decimal(p["uma_anual"])
    raise KeyError(
        f"Concepto normativo desconocido: {concepto!r}. "
        f"Agregarlo exige actualizar K-FIS-004, no adivinar aqui."
    )


def normalizar_nombre(nombre: str) -> str | None:
    """Mapea el nombre del parametro del core a un concepto normativo."""
    n = (nombre or "").strip().lower()
    if n in CATALOGO_NORMATIVO:
        return CATALOGO_NORMATIVO[n]
    # coincidencia por sufijo: los cores prefijan por modulo
    for clave, concepto in CATALOGO_NORMATIVO.items():
        if n.endswith(clave):
            return concepto
    return None


def fila_parametro_normativo(fila: dict, params: dict) -> Decimal:
    """Valor esperado por la norma para el parametro que trae la fila.

    Si el parametro del core no esta en el catalogo normativo, NO se devuelve
    un valor: se levanta el error y la fila queda como violacion "sin C". Un
    parametro fiscal que nadie sabe interpretar es un hallazgo, no un renglon
    a ignorar.
    """
    nombre = fila.get("parametro") or fila.get("name") or ""
    concepto = normalizar_nombre(nombre)
    if concepto is None:
        raise KeyError(
            f"Parametro fiscal {nombre!r} sin correspondencia normativa en "
            f"K-FIS-004. Revisar si es un parametro nuevo del core."
        )
    anio = int(fila.get("anio_causacion") or params["anio_causacion"])
    return valor_normativo(concepto, anio)


def tabla_esperada(anio: int) -> list[dict]:
    """Tabla de referencia legible (la que va al reporte para Finsus)."""
    p = parametros_anio(anio)
    return [
        {"concepto": "uma_anual", "valor": p["uma_anual"], "fuente": FUENTE_NORMATIVA["uma_anual"]},
        {"concepto": "exencion", "valor": str(valor_normativo("exencion", anio)),
         "fuente": FUENTE_NORMATIVA["exencion"]},
        {"concepto": "tasa_isr_fraccion", "valor": str(valor_normativo("tasa_isr_fraccion", anio)),
         "fuente": FUENTE_NORMATIVA["tasa_isr_fraccion"]},
        {"concepto": "dias_anio", "valor": p["dias_anio"], "fuente": FUENTE_NORMATIVA["dias_anio"]},
    ]


ANIOS_DISPONIBLES = sorted(PARAMETROS_POR_ANIO)
