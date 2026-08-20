# -*- coding: utf-8 -*-
"""ORACULO de RENDIMIENTOS (motor C) — vista, plazo fijo y saldo promedio.

Portado de 40_validaciones/comparadores/oraculo_rendimientos.py (autoprueba
3/3, plazo validado 775/775). Aritmetica identica; los redondeos se toman de
engine/redondeo.py y la base de dias es parametro obligatorio.

Sustento: K-DEV-002 v3 (vista, saldo promedio) · K-DEV-003 (plazo) ·
K-DEV-001 v2 (redondeo). Doc oficial "Pago de Rendimientos" (F-019) y
"Saldo Promedio" (F-022).

Independencia (charter §9.1): las formulas salen del doc oficial de la regla,
no de leer el motor de AurumCore.
"""

from __future__ import annotations

from decimal import Decimal, getcontext

from engine.redondeo import aplicar

getcontext().prec = 50

VERSION_REGLA = "K-DEV-002 v3 / K-DEV-003 v1"


def _dec(valor, nombre: str) -> Decimal:
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, float):
        raise TypeError(
            f"{nombre} llego como float ({valor!r}). Cero float en la ruta del "
            f"dinero (charter §1.3): pasar cadena o Decimal."
        )
    return Decimal(str(valor))


# --- 2.1.2 · Plazo fijo ------------------------------------------------------
def rendimiento_plazo(capital, tasa, dias_transcurridos, dias_anio) -> Decimal:
    """Rendimiento = RoundHalfEven2( Ceil10( Ceil10((Capital x Tasa)/100) / DiasAnio ) x Dias )

    K-DEV-003. Base de dias por producto (360 comercial / 365-366 natural):
    es PARAMETRO, no constante — en la muestra validada fueron 360 + dias
    reales de calendario, pero eso es un hecho de la muestra, no la regla.
    """
    c = _dec(capital, "capital")
    t = _dec(tasa, "tasa")
    d = _dec(dias_transcurridos, "dias_transcurridos")
    y = _dec(dias_anio, "dias_anio")
    paso1 = aplicar(c * t / Decimal("100"), "Ceil10")
    paso2 = aplicar(paso1 / y, "Ceil10")
    return aplicar(paso2 * d, "RoundHalfEven2")


# --- 2.1.1 · Vista / ahorro --------------------------------------------------
def rendimiento_vista(spm, tasa, dias_periodo, dias_anio) -> Decimal:
    """Rendimiento = Round2( Trunc20( Trunc20((SPM x Tasa)/100) / DiasAnio ) x Dias )

    SPM = saldo promedio mensual (ver saldo_promedio_rendimiento). K-DEV-002 v3.
    El cierre usa Round2 (half_up, "redondeo normal" del doc), a diferencia
    del plazo que usa RoundHalfEven2 — la diferencia es del doc, no un
    descuido: K-DEV-001 documenta que los redondeos difieren por producto.
    """
    s = _dec(spm, "spm")
    t = _dec(tasa, "tasa")
    d = _dec(dias_periodo, "dias_periodo")
    y = _dec(dias_anio, "dias_anio")
    paso1 = aplicar(s * t / Decimal("100"), "Trunc20")
    paso2 = aplicar(paso1 / y, "Trunc20")
    return aplicar(paso2 * d, "Round2")


# --- 2.1.3 · Saldo promedio --------------------------------------------------
def saldo_promedio_rendimiento(saldo_cuenta, difference_of_days, acumulado,
                               elapsed_days) -> Decimal:
    """SPM = (saldo x difference_of_days + acumulado) / elapsed_days

    K-DEV-002 v3 (formula Finsus F-022). `difference_of_days` es conteo
    EXCLUSIVO (dias con saldo sin cambio); `elapsed_days` es INCLUSIVO y es el
    divisor.

    NO se redondea aqui: el SPM es insumo de otro calculo y redondearlo antes
    de tiempo introduce error. Quien lo consuma decide su precision.

    [PENDIENTE · P-006] La correspondencia exacta entre esta formula y lo que
    el CORE registra sigue sin corroborarse contra los logs del core
    (traza `Calculating with average balance`). Mientras P-006 no cierre, el
    caso SALDO-PROM permanece BLOQUEADO en el catalogo — esta funcion existe,
    pero su resultado no se puede declarar veredicto.
    """
    s = _dec(saldo_cuenta, "saldo_cuenta")
    dif = _dec(difference_of_days, "difference_of_days")
    ac = _dec(acumulado, "acumulado")
    el = _dec(elapsed_days, "elapsed_days")
    if el == 0:
        raise ZeroDivisionError("elapsed_days = 0: el periodo no tiene dias, revisar la extraccion")
    return (s * dif + ac) / el


# --- Adaptadores para el motor -----------------------------------------------
def fila_rendimiento_plazo(fila: dict, params: dict) -> Decimal:
    return rendimiento_plazo(
        capital=fila["capital"],
        tasa=fila.get("tasa") or params["tasa"],
        dias_transcurridos=fila["dias_periodo"],
        dias_anio=params["dias_anio"],
    )


def fila_rendimiento_vista(fila: dict, params: dict) -> Decimal:
    return rendimiento_vista(
        spm=fila["saldo_promedio"],
        tasa=fila.get("tasa") or params["tasa"],
        dias_periodo=fila["dias_periodo"],
        dias_anio=params["dias_anio"],
    )


def fila_saldo_promedio(fila: dict, params: dict) -> Decimal:
    return saldo_promedio_rendimiento(
        saldo_cuenta=fila["saldo_cuenta"],
        difference_of_days=fila["difference_of_days"],
        acumulado=fila["acumulado"],
        elapsed_days=fila["elapsed_days"],
    )
