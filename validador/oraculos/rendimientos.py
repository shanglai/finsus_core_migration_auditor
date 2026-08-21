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
def tasa_despejada(rend_periodo_1, capital, dias_periodo_1, dias_anio) -> Decimal:
    """Despeja la tasa anual del PRIMER periodo del plan de pagos.

        tasa = rend_1 x dias_anio / (capital x dias_1) x 100

    K-DEV-003 / V5: la tasa contratada no esta limpia en el modelo
    (`account_yield.interest_rate` = 0 para inversion), asi que se despeja y se
    verifica que reproduzca TODOS los demas periodos. Es prueba fuerte
    (775/775) pero NO sustituye leer la tasa de su tabla: si la tasa
    configurada estuviera mal, el despeje la absorbe y el caso pasaria. El
    hueco esta declarado en `supuestos:` de REND-PLAZO.

    El despeje se hace aqui, en Decimal, y no en el SQL: la aritmetica del
    servidor quedaria fuera de la ruta auditable del dinero.
    """
    r1 = _dec(rend_periodo_1, "rend_periodo_1")
    cap = _dec(capital, "capital")
    d1 = _dec(dias_periodo_1, "dias_periodo_1")
    y = _dec(dias_anio, "dias_anio")
    if cap == 0 or d1 == 0:
        raise ZeroDivisionError(
            "no se puede despejar la tasa: capital o dias del periodo 1 en cero"
        )
    return r1 * y / (cap * d1) * Decimal("100")


def fila_rendimiento_plazo(fila: dict, params: dict) -> Decimal:
    """Adaptador de REND-PLAZO.

    La tasa se toma, en este orden: la que traiga la fila, la que se pase por
    parametro, o la despejada del periodo 1. El orden importa: si algun dia
    aparece la tasa contratada en el modelo, este adaptador la prefiere sin
    tocar nada mas.
    """
    dias_anio = params["dias_anio"]
    tasa = fila.get("tasa") or params.get("tasa")
    if not tasa:
        tasa = tasa_despejada(
            fila["rend_periodo_1"], fila["capital"], fila["dias_periodo_1"], dias_anio
        )
    return rendimiento_plazo(
        capital=fila["capital"],
        tasa=tasa,
        dias_transcurridos=fila["dias_periodo"],
        dias_anio=dias_anio,
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
