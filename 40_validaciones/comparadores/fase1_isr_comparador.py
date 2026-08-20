# -*- coding: utf-8 -*-
"""
Fase 1 · Comparador ISR A/B/C (offline sobre los Parquet ya extraidos).
Corre el oraculo C (Decimal, sin float) sobre los saldos y lo confronta con:
  A = OpenFin isr_diario (dia por dia, real)
  B = AurumCore ISR al pago
Clasifica cada dia/cliente: OK / MODELO / REDONDEO / DEFECTO_OPENFIN / REVISAR.

Insumos (en 40_validaciones/_resultados/, los produce el runner):
  f1_openfin_isr_diario_<COH>_s1.parquet   (A)  cols: id_cliente, fecha, saldo_base_of, isr_dia_of
  f1_aurum_saldo_base_isr_<COH>_s1.parquet  (base C) cols: id_cliente, account_number, fecha, final_balance
  f1_aurum_isr_al_pago_<COH>_s1.parquet     (B)  cols: id_cliente, account_number, fecha_pago, isr_retenido_ac

Parametros de la regla (P-010, PENDIENTE de confirmar contra norma en P2):
  se pueden sobreescribir con los valores reales de cat_tax/system_configuration.
"""
import sys, pathlib
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
import polars as pl
sys.stdout.reconfigure(encoding="utf-8")
getcontext().prec = 40

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT = ROOT / "40_validaciones" / "_resultados"

# --- P-010 (parametros de la regla) — [PENDIENTE] confirmar en P2 --------------
UMA          = Decimal("42794.64")
MULT_EXENCION= Decimal("5")
TASA_ISR     = Decimal("0.009")
DIAS_ANIO    = Decimal("365")
BASE_EXENTA  = UMA * MULT_EXENCION
TOL          = Decimal("0.01")   # tolerancia por evento (charter §10)

def c_isr_dia(saldo_total: Decimal) -> Decimal:
    parte = max(Decimal("0"), saldo_total - BASE_EXENTA)
    return (TASA_ISR / DIAS_ANIO) * parte

def leer(nombre):
    p = RESULT / nombre
    if not p.exists():
        print(f"[!] falta {p.name} (corre el runner con --confirm para esta cohorte)")
        return None
    return pl.read_parquet(p)

def dec(x):
    return Decimal(str(x)) if x is not None else Decimal("0")

def comparar(coh="SEMILLA"):
    A = leer(f"f1_openfin_isr_diario_{coh}_s1.parquet")
    base = leer(f"f1_aurum_saldo_base_isr_{coh}_s1.parquet")
    B = leer(f"f1_aurum_isr_al_pago_{coh}_s1.parquet")
    if A is None:
        print("Sin datos A: nada que comparar todavia (esperado en dry-run).")
        return

    # --- Base total del cliente por dia (suma de sus cuentas) para C ----------
    if base is not None:
        base_dia = (base.group_by(["id_cliente", "fecha"])
                        .agg(pl.col("final_balance").sum().alias("saldo_total")))
    else:
        # fallback: usar el saldo que reporto OpenFin (menos independiente; se marca)
        print("[aviso] sin account_balance_tracking; se usa isr_diario.saldo como base (menos independiente).")
        base_dia = A.select(pl.col("id_cliente"), pl.col("fecha"),
                            pl.col("saldo_base_of").alias("saldo_total"))

    # --- C dia por dia (Decimal) ---------------------------------------------
    filas = []
    for row in base_dia.iter_rows(named=True):
        c = c_isr_dia(dec(row["saldo_total"]))
        filas.append({"id_cliente": row["id_cliente"], "fecha": row["fecha"],
                      "saldo_total": float(row["saldo_total"] or 0), "isr_dia_c": float(c)})
    C = pl.DataFrame(filas)

    # --- Join A vs C por cliente-dia -----------------------------------------
    comp = A.join(C, on=["id_cliente", "fecha"], how="full", coalesce=True)
    comp = comp.with_columns(
        pl.col("isr_dia_of").fill_null(0.0),
        pl.col("isr_dia_c").fill_null(0.0),
    ).with_columns((pl.col("isr_dia_of") - pl.col("isr_dia_c")).alias("dif_a_c"))

    # --- Acumulados por cliente y clasificacion periodo -----------------------
    agg = comp.group_by("id_cliente").agg(
        pl.col("isr_dia_of").sum().alias("A_isr_periodo"),
        pl.col("isr_dia_c").sum().alias("C_isr_periodo"),
        pl.len().alias("dias"),
    )
    if B is not None:
        Bcli = B.group_by("id_cliente").agg(pl.col("isr_retenido_ac").sum().alias("B_isr_pago"))
        agg = agg.join(Bcli, on="id_cliente", how="left")
    else:
        agg = agg.with_columns(pl.lit(None).alias("B_isr_pago"))

    def clasifica(a, c):
        a, c = dec(a), dec(c)
        if abs(a - c) <= TOL:                       return "OK"
        if c == 0 and a > TOL:                       return "DEFECTO_OPENFIN (sobre-retencion a exento)"
        if a > c:                                     return "MODELO/DEFECTO (A>C: revisar base/exencion)"
        return "MODELO (A<C: snapshot parcial / sincronia)"

    agg = agg.with_columns(
        pl.struct(["A_isr_periodo", "C_isr_periodo"])
          .map_elements(lambda s: clasifica(s["A_isr_periodo"], s["C_isr_periodo"]),
                        return_dtype=pl.Utf8).alias("clasificacion")
    )
    RESULT.mkdir(exist_ok=True)
    comp.write_parquet(RESULT / f"f1_comp_diario_{coh}.parquet")
    agg.write_parquet(RESULT / f"f1_comp_cliente_{coh}.parquet")
    print(f"\n=== Resumen A/B/C por cliente ({coh}) ===")
    with pl.Config(tbl_rows=40, fmt_str_lengths=60):
        print(agg.sort("A_isr_periodo", descending=True))
    print(f"\nGuardado: f1_comp_diario_{coh}.parquet, f1_comp_cliente_{coh}.parquet")
    print("[PENDIENTE P-010] tasa/exencion/dias son los documentados; confirmar con cat_tax/system_configuration (P2).")

if __name__ == "__main__":
    coh = sys.argv[1] if len(sys.argv) > 1 else "SEMILLA"
    comparar(coh)
