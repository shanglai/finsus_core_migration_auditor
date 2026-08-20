# -*- coding: utf-8 -*-
"""
FASE 0 — Recálculo independiente (motor C) del rendimiento de inversiones.
100% OFFLINE sobre los archivos de F-013 (árbol día cero). **NO se conecta a ninguna base de datos.**
Stack: polars (datos) + decimal (dinero, sin float). Sustento: K-DEV-003, K-DEV-001.

Regla (K-DEV-003): rendimiento = capital × (tasa_anual/100) × dias/360, redondeo HALF_EVEN a 2.
Nota: `rendimiento_pagado` en F-013 es el del ÚLTIMO periodo mensual; las inversiones multiperiodo
(dias>32) requieren `iv_payment_plan` (extracto Fase 1) para recalcularse por periodo.

Resultados con datos de clientes se escriben a 40_validaciones/_resultados/ (gitignored).
"""
import polars as pl
from decimal import Decimal, ROUND_HALF_EVEN

BASE = "20_fuentes/datos/analisis_arboles_20260803/Inversiones/03 08 2026 23_59_59 "
AC = BASE + "AurumCore/Histórico/inversiones_aurumcore_20260803.csv"
OF = BASE + "Openfin/Histórico/inversiones_openfin_20260803.csv"

def rendimiento_c(monto, tasa_anual, dias) -> Decimal:
    r = Decimal(str(monto)) * (Decimal(str(tasa_anual)) / Decimal(100)) * Decimal(int(dias)) / Decimal(360)
    return r.quantize(Decimal("0.01"), ROUND_HALF_EVEN)

def main():
    a = pl.read_csv(AC, infer_schema_length=3000).rename(lambda c: c.strip().lstrip("﻿"))
    o = pl.read_csv(OF, infer_schema_length=3000).rename(lambda c: c.strip().lstrip("﻿"))
    a = a.with_columns(
        pl.col("fecha_apertura").str.slice(0, 10).str.to_date().alias("ap"),
        pl.col("fecha_cierre").str.slice(0, 10).str.to_date().alias("ci"),
    ).with_columns((pl.col("ci") - pl.col("ap")).dt.total_days().alias("dias"))
    j = a.join(
        o.select(["id_cuenta", "rendimiento_pagado"]).rename({"rendimiento_pagado": "rend_of"}),
        left_on="id_inversion_openfin", right_on="id_cuenta", how="left",
    ).with_columns((pl.col("rendimiento_pagado") - pl.col("rend_of")).alias("diff_ab"))
    return j

if __name__ == "__main__":
    j = main()
    print("pareadas:", j.filter(pl.col("rend_of").is_not_null()).height, "/", j.height)
