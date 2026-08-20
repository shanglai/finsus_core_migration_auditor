# -*- coding: utf-8 -*-
"""
Decantamiento acumulativo de inversiones (motor C, OFFLINE sobre F-013). **NO toca ninguna BD.**
Filtra variable por variable (cliente+inversión → fecha → monto → tasa → rendimiento → ISR):
una inversión sobrevive sólo si A(OpenFin) y B(Aurum) coinciden en TODAS las previas.
Salida: la cascada de conteos + desglose de casuísticas. Diagrama: decantamiento_inversiones.svg
Nota: las fechas de OpenFin (xlsx) vienen como serial de Excel (epoch 1899-12-30).
"""
import datetime, polars as pl

BASE = "20_fuentes/datos/analisis_arboles_20260803/Inversiones/03 08 2026 23_59_59 "
AC = BASE + "AurumCore/Histórico/inversiones_aurumcore_20260803.csv"
OF_ISR = BASE + "Openfin/inversiones_openfin_con_ISR.xlsx"
EXCEL_EPOCH = datetime.date(1899, 12, 30)

def load():
    a = pl.read_csv(AC, infer_schema_length=3000).rename(lambda c: c.strip().lstrip("﻿"))
    o = pl.read_excel(OF_ISR).rename(lambda c: c.strip().lstrip("﻿"))
    a = a.with_columns(
        pl.col("fecha_apertura").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("ap"),
        pl.col("fecha_cierre").str.slice(0, 10).str.to_date("%Y-%m-%d").alias("ci"),
    )
    o = o.with_columns(
        (pl.lit(EXCEL_EPOCH) + pl.duration(days=pl.col("fecha_apertura"))).alias("ap_of"),
        (pl.lit(EXCEL_EPOCH) + pl.duration(days=pl.col("fecha_cierre"))).alias("ci_of"),
    ).rename({"rendimiento_pagado": "rend_of", "isr_retenido": "isr_of",
              "monto_apertura": "monto_of", "tasa": "tasa_of"})
    return a.join(o, left_on="id_inversion_openfin", right_on="id_cuenta", how="inner")

def decantar(j):
    s1 = j.filter((pl.col("ap") == pl.col("ap_of")) & (pl.col("ci") == pl.col("ci_of")))
    s2 = s1.filter((pl.col("monto_apertura") - pl.col("monto_of")).abs() <= 0.005)
    s3 = s2.filter((pl.col("tasa") - pl.col("tasa_of")).abs() <= 0.0005)
    s4 = s3.filter((pl.col("rendimiento_pagado") - pl.col("rend_of")).abs() == 0)
    s5 = s4.filter((pl.col("isr_retenido") - pl.col("isr_of")).abs() == 0)
    return {"pareadas": j.height, "+fecha": s1.height, "+monto": s2.height,
            "+tasa": s3.height, "+rendimiento": s4.height, "+ISR": s5.height}

if __name__ == "__main__":
    pasos = decantar(load())
    prev = None
    for k, v in pasos.items():
        cae = "" if prev is None else f"  (cae {prev - v})"
        print(f"{k:14s}: {v:6d}{cae}"); prev = v
