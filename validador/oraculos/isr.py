# -*- coding: utf-8 -*-
"""ORACULO ISR (motor C) — retencion al pago de rendimientos.

Portado de 40_validaciones/entrega_finsus/oraculo_isr.py (autoprueba 5/5),
con dos cambios y ninguno en la aritmetica:

  1. Los redondeos se toman de engine/redondeo.py (parametro explicito), en
     vez de estar fijos en el cuerpo de la funcion. S-FIS-001 §Precision dejo
     abierto si el cierre a 2 decimales era half_even o half_up; Finsus lo
     confirmo el 2026-08-24 (half-up, homogeneo, por evento). Se conserva como
     parametro para que la eleccion siga viajando en la evidencia.
  2. Los parametros normativos se resuelven POR ANIO DE CAUSACION. La UMA
     cambia cada 1-feb y la tasa se fija anual en la LIF; fijarlos en el
     codigo es exactamente el rezago que produjo C-001.

Sustento: S-FIS-001 · K-FIS-002 v3 · K-FIS-004 · K-DEV-001 v2
Independencia (charter §9.1): la formula sale de la norma y del doc oficial,
no de leer el codigo de AurumCore ni de OpenFin.

    Monto Exento  = UMA x multiplicador        (persona moral: 0)
    Base Gravable = max(0, Saldo Total Cliente - Monto Exento)
    Proporcion    = Trunc20(Saldo Cuenta / Saldo Total)      # <- saldo_total (C-002)
    Tasa Diaria   = Trunc20(Tasa / (100 x DiasAnio))
    ISR Diario    = Trunc5(Base Gravable x Tasa Diaria)
    ISR Retenido  = Round2(Trunc20(ISR Diario x Dias Periodo) x Proporcion)

C-002 RESUELTA (2026-08-19) a favor de dividir entre saldo_total_cliente, no
entre la base gravable. F-019 corrige a F-016.
"""

from __future__ import annotations

from decimal import Decimal, getcontext

from engine.redondeo import aplicar

getcontext().prec = 50

VERSION_REGLA = "S-FIS-001 / K-FIS-002 v3"

# --- Parametros normativos por ANIO DE CAUSACION -----------------------------
# UMA: INEGI, vigente desde el 1-feb de cada anio.
# Tasa: LIF Art. 24 del ejercicio (remite a LISR 54/135).
# Multiplicador: LISR Art. 93 fr. XX (5 x UMA, beneficio SOFIPO).
PARAMETROS_POR_ANIO: dict[int, dict[str, str]] = {
    2025: {"uma_anual": "41273.52", "tasa_anual": "0.5", "multiplicador_uma": "5", "dias_anio": "365"},
    2026: {"uma_anual": "42794.64", "tasa_anual": "0.9", "multiplicador_uma": "5", "dias_anio": "365"},
}

# Modos de redondeo de la regla (S-FIS-001 §Precision).
MODO_PROPORCION = "Trunc20"
MODO_TASA_DIARIA = "Trunc20"
MODO_ISR_DIARIO = "Trunc5"
MODO_DEVENGADO = "Trunc20"
MODO_FINAL_DEFAULT = "Round2"           # half-up: confirmado por Finsus 2026-08-24


def parametros_anio(anio: int) -> dict[str, str]:
    """Parametros normativos del anio de causacion.

    Falla si el anio no esta en la tabla en vez de caer a un default: correr
    con parametros de otro ejercicio es justo el defecto C-001.
    """
    if anio not in PARAMETROS_POR_ANIO:
        raise KeyError(
            f"No hay parametros normativos cargados para el anio {anio}. "
            f"Anios disponibles: {sorted(PARAMETROS_POR_ANIO)}. "
            f"Agregarlos exige actualizar K-FIS-004 con la LIF y la UMA del ejercicio."
        )
    return dict(PARAMETROS_POR_ANIO[anio])


def _dec(valor, nombre: str) -> Decimal:
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, float):
        raise TypeError(
            f"{nombre} llego como float ({valor!r}). Cero float en la ruta del "
            f"dinero (charter §1.3): pasar cadena o Decimal."
        )
    return Decimal(str(valor))


def isr_retenido(
    saldo_total_cliente,
    saldo_cuenta,
    dias_periodo,
    uma_anual,
    tasa_anual,
    multiplicador_uma="5",
    dias_anio="365",
    persona_moral: bool = False,
    modo_final: str = MODO_FINAL_DEFAULT,
) -> Decimal:
    """ISR retenido de UNA cuenta/inversion al pago de rendimientos.

    Todos los parametros normativos son OBLIGATORIOS y explicitos (no hay
    defaults de UMA ni de tasa): el anio de causacion lo decide quien corre,
    y queda grabado en la evidencia.
    """
    st = _dec(saldo_total_cliente, "saldo_total_cliente")
    sc = _dec(saldo_cuenta, "saldo_cuenta")
    dias = _dec(dias_periodo, "dias_periodo")
    uma = _dec(uma_anual, "uma_anual")
    mult = _dec(multiplicador_uma, "multiplicador_uma")
    tasa = _dec(tasa_anual, "tasa_anual")
    base_dias = _dec(dias_anio, "dias_anio")

    monto_exento = Decimal("0") if persona_moral else uma * mult
    base_gravable = max(Decimal("0"), st - monto_exento)
    if base_gravable == 0 or st == 0:
        return Decimal("0.00")

    proporcion = aplicar(sc / st, MODO_PROPORCION)
    tasa_diaria = aplicar(tasa / (Decimal("100") * base_dias), MODO_TASA_DIARIA)
    isr_diario = aplicar(base_gravable * tasa_diaria, MODO_ISR_DIARIO)
    devengado = aplicar(isr_diario * dias, MODO_DEVENGADO)
    return aplicar(devengado * proporcion, modo_final)


def isr_retenido_por_anio(saldo_total_cliente, saldo_cuenta, dias_periodo,
                          anio: int, persona_moral: bool = False,
                          modo_final: str = MODO_FINAL_DEFAULT) -> Decimal:
    """Atajo: resuelve los parametros del anio de causacion y calcula."""
    p = parametros_anio(anio)
    return isr_retenido(
        saldo_total_cliente, saldo_cuenta, dias_periodo,
        uma_anual=p["uma_anual"], tasa_anual=p["tasa_anual"],
        multiplicador_uma=p["multiplicador_uma"], dias_anio=p["dias_anio"],
        persona_moral=persona_moral, modo_final=modo_final,
    )


def isr_devengo_diario(saldo_total_cliente, uma_anual, tasa_anual,
                       multiplicador_uma="5", dias_anio="365",
                       persona_moral: bool = False,
                       modo_final: str = "Round2") -> Decimal:
    """ISR DEVENGADO de un dia sobre el saldo total del cliente (caso ISR-02).

    Es OTRA cosa que la retencion al pago: aqui se provisiona dia a dia sobre
    el saldo, sin prorrateo por cuenta y sin dias de periodo.

        isr_dia = Round2( (tasa/100 / dias_anio) x max(0, saldo_total - exencion) )

    K-FIS-003 v2. Esta funcion existe para probar la afirmacion de que el
    descuadre OpenFin vs AurumCore es de MODELO (provision-devengo contra
    retencion-al-pago) y NO un defecto de calculo: si el devengo diario de
    OpenFin reproduce esta formula, el descuadre queda explicado.
    """
    st = _dec(saldo_total_cliente, "saldo_total_cliente")
    uma = _dec(uma_anual, "uma_anual")
    mult = _dec(multiplicador_uma, "multiplicador_uma")
    tasa = _dec(tasa_anual, "tasa_anual")
    base_dias = _dec(dias_anio, "dias_anio")

    exencion = Decimal("0") if persona_moral else uma * mult
    parte_expuesta = max(Decimal("0"), st - exencion)
    if parte_expuesta == 0:
        return Decimal("0.00")
    return aplicar((tasa / Decimal("100") / base_dias) * parte_expuesta, modo_final)


# --- Adaptador para el motor: fila (dict) -> Decimal -------------------------
def fila_isr_retenido(fila: dict, params: dict) -> Decimal:
    """Firma que consume engine/oracle_runner.py.

    `fila` trae las columnas del universo del caso; `params` los parametros
    resueltos del catalogo + CLI.
    """
    return isr_retenido(
        saldo_total_cliente=fila["saldo_total_cliente"],
        saldo_cuenta=fila["saldo_cuenta"],
        dias_periodo=fila["dias_periodo"],
        uma_anual=params["uma_anual"],
        tasa_anual=params["tasa_anual"],
        multiplicador_uma=params.get("multiplicador_uma", "5"),
        dias_anio=params.get("dias_anio", "365"),
        persona_moral=bool(fila.get("persona_moral", False)),
        modo_final=params.get("modo_final", MODO_FINAL_DEFAULT),
    )


def fila_isr_devengo_diario(fila: dict, params: dict) -> Decimal:
    """Adaptador del caso ISR-02 (devengo diario, motor A = OpenFin)."""
    return isr_devengo_diario(
        saldo_total_cliente=fila["saldo_base"],
        uma_anual=params["uma_anual"],
        tasa_anual=params["tasa_anual"],
        multiplicador_uma=params.get("multiplicador_uma", "5"),
        dias_anio=params.get("dias_anio", "365"),
        persona_moral=bool(fila.get("persona_moral", False)),
        modo_final=params.get("modo_final", "Round2"),
    )
