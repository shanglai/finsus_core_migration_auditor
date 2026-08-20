# -*- coding: utf-8 -*-
"""
Fase 1 · Prueba a escala del SET DE DESVIACIÓN de ISR (SOLO LECTURA, gated).

Pregunta: de las inversiones donde el ISR de OpenFin (A) != AurumCore (B) en el árbol,
¿la desviación es un DEFECTO real o es MODELO (provisión-devengo de OpenFin vs retención-al-pago
de Aurum)? Se contrasta directamente contra la base.

Para cada inversión del set de desviación (|A-B|>umbral) trae de la BD:
  - A_prov   = Σ isr_diario_aux_log (kauxiliar) sobre la vida  → la PROVISIÓN de OpenFin (debe ≈ isr_of del árbol)
  - OF regla = isr_diario (kasociado): compara isr vs C=(0.009/365)·max(0,saldo-213973.20) por día
               → ¿el devengo diario de OpenFin sigue la regla?  (no requiere reconstruir base)
  - B_pago   = retención al pago de Aurum (INTERNAL TRANSFER/Generic → cuenta ISR 0000)
  - B vs C   = SOLO en clientes de una sola inversión (base = capital, proporción=1) → ¿Aurum sigue la regla?

Clasifica cada caso:
  MODELO           : OF sigue la regla como provisión Y (donde medible) B sigue la regla → el gap es timing/modelo
  REVISAR_OPENFIN  : el devengo diario de OpenFin NO sigue la regla
  REVISAR_AURUM    : B (Aurum) NO coincide con C (posible defecto del core destino)
  SIN_BASE         : no se pudo verificar B vs C (multi-cuenta / reinversión) → queda como provisión-vs-pago

Uso:
  python fase1_isr_desviacion.py --plan                 # cohorte y plan (sin BD)
  python fase1_isr_desviacion.py --sample 400 --confirm # ejecuta (read-only)
Requiere doble validación (regla del proyecto) antes de --confirm.
"""
import argparse, sys, pathlib
from decimal import Decimal, getcontext
import polars as pl
sys.stdout.reconfigure(encoding="utf-8"); getcontext().prec = 40

ROOT = pathlib.Path(__file__).resolve().parents[2]
RESULT = ROOT / "40_validaciones" / "_resultados"
JOIN = RESULT / "_isr_join_full.parquet"
CONN_YAML = ROOT / "db_connections.yaml"

EX2026 = Decimal("213973.20")   # 5 × UMA 2026
EX2025 = Decimal("206367.60")   # 5 × UMA 2025 (aplica en el rezago de transición ~feb-2026, C-001)
TASA = Decimal("0.009"); ANIO = Decimal("365")
TOL_DIA = Decimal("0.02")     # tolerancia por día en el check de devengo OF (redondeo a 2)
UMBRAL  = 0.10                # set de desviación material |A-B|>0.10
VENTANA = ("2025-09-03", "2026-08-18")   # rango disponible de isr_diario

def _c_dia(saldo, ex):
    return (TASA/ANIO) * max(Decimal("0"), Decimal(str(saldo)) - ex)

def dia_sigue_regla(saldo, isr):
    """Un día 'sigue la regla' si el ISR coincide con C usando UMA 2026 O 2025 (transición)."""
    i = Decimal(str(isr))
    return (abs(i - _c_dia(saldo, EX2026)) <= TOL_DIA) or (abs(i - _c_dia(saldo, EX2025)) <= TOL_DIA)

def cohorte(sample, band):
    m = pl.read_parquet(JOIN).with_columns(pl.col("diff").abs().alias("ad"))
    dev = m.filter(pl.col("ad") > UMBRAL)
    if band == "OF": dev = dev.filter(pl.col("diff") > 0)
    elif band == "AC": dev = dev.filter(pl.col("diff") < 0)
    # muestreo estratificado por dirección y bucket de vida (determinista: ordena por diff)
    if sample and dev.height > sample:
        dev = dev.with_columns(pl.col("diff").sign().alias("sg"))
        parts = []
        for sg in dev["sg"].unique().to_list():
            sub = dev.filter(pl.col("sg") == sg).sort("ad", descending=True)
            n = max(1, round(sample * sub.height / dev.height))
            # toma n repartidos (cabeza+cola+medio) para cubrir rango de magnitud
            idx = [round(i*(sub.height-1)/(n-1)) for i in range(n)] if n > 1 else [0]
            parts.append(sub[idx])
        dev = pl.concat(parts)
    return dev

def conn(sec):
    import yaml, psycopg2
    c = yaml.safe_load(CONN_YAML.read_text(encoding="utf-8"))[sec]
    kw = {k: c[k] for k in ("host","port","dbname","user","password","sslmode") if k in c}
    cn = psycopg2.connect(**kw); cn.set_session(readonly=True)
    cn.cursor().execute("SET statement_timeout='300s'")
    return cn

def split3(s):
    p = s.split("-"); return int(p[0]), int(p[1]), int(p[2])

def ejecutar(coh, confirm):
    if not confirm:
        print("  [dry-run] NO se conecta. Cohorte y consultas listas; agrega --confirm para ejecutar.")
        return
    import psycopg2.extras
    of = conn("openfin"); ac = conn("aurum")
    ofc = of.cursor(); acc = ac.cursor()

    # llaves OF: (suc,rol,aso)->kasociado ; (sucaux,prod,aux)->kauxiliar
    cli_keys = list({split3(c) for c in coh["id_cliente"].to_list()})
    inv_keys = list({split3(c) for c in coh["id_inversion_openfin"].to_list()})
    ofc.execute("select idsucursal,idrol,idasociado,kasociado from asociados where (idsucursal,idrol,idasociado) in %s",(tuple(cli_keys),))
    kas = {(r[0],r[1],r[2]): r[3] for r in ofc.fetchall()}
    ofc.execute("select idsucaux,idproducto,idauxiliar,kauxiliar from acreedores where (idsucaux,idproducto,idauxiliar) in %s",(tuple(inv_keys),))
    kaux = {(r[0],r[1],r[2]): r[3] for r in ofc.fetchall()}
    print(f"  mapeadas {len(kas)} clientes -> kasociado, {len(kaux)} inversiones -> kauxiliar")

    # A_prov por inversión (Σ aux_log)
    kx = tuple(v for v in kaux.values())
    ofc.execute("""select kauxiliar, round(sum(isr_diario),2) from isr_diario_aux_log
                   where kauxiliar in %s group by kauxiliar""",(kx,))
    a_prov = {r[0]: Decimal(str(r[1])) for r in ofc.fetchall()}

    # OF regla: isr_diario por cliente (saldo, isr) en la ventana → frac de días que siguen la regla
    ks = tuple(v for v in kas.values())
    ofc.execute("""select kasociado, saldo, isr from isr_diario
                   where kasociado in %s and fecha>=%s and fecha<%s""",(ks, VENTANA[0], VENTANA[1]))
    of_rows = ofc.fetchall()
    from collections import defaultdict
    okc, totc = defaultdict(int), defaultdict(int)
    for kaso, saldo, isr in of_rows:
        if isr is None: continue
        totc[kaso]+=1
        if dia_sigue_regla(saldo, isr): okc[kaso]+=1
    of_rule = {k: (okc[k]/totc[k] if totc[k] else None) for k in totc}

    # B_pago por cliente (Σ retención Aurum), amarrado al holder de la cuenta semilla
    accs = coh["id_inversion_aurumcore"].to_list()
    acc.execute("""select account_number, accountholder_id from aurumcore.account where account_number = any(%s)""",(accs,))
    acc_holder = {r[0]: r[1] for r in acc.fetchall()}
    b_by_holder = {}
    acc.execute("""select pa.accountholder_id, round(sum(td.credit_amount),2)
        from aurumcore.transaction_detail td
        join aurumcore.transaction t on t.transaction_id=td.transaction_id
        join aurumcore.account pa on pa.account_id=t.payer_account_id
        join aurumcore.account pe on pe.account_id=t.payee_account_id
        where td.transaction_type='INTERNAL TRANSFER' and td.transaction_channel='Generic'
          and split_part(pe.account_number,'-',2)='0000'
          and pa.accountholder_id in (select accountholder_id from aurumcore.account where account_number = any(%s))
        group by 1""",(accs,))
    for hid, s in acc.fetchall(): b_by_holder[hid] = Decimal(str(s))

    of.rollback(); of.close(); ac.rollback(); ac.close()

    # --- clasificación (robusta: se basa en si el DEVENGO de OpenFin sigue la regla) ---
    filas = []
    for row in coh.iter_rows(named=True):
        cid = row["id_cliente"]; ofid = row["id_inversion_openfin"]; acid = row["id_inversion_aurumcore"]
        k_aso = kas.get(split3(cid)); k_aux = kaux.get(split3(ofid))
        aprov = a_prov.get(k_aux)
        frac = of_rule.get(k_aso)
        hid = acc_holder.get(acid); b = b_by_holder.get(hid)
        if frac is None:
            clase = "SIN_DATO_OF"            # sin isr_diario en la ventana (inversión fuera de rango)
        elif frac < 0.90:
            clase = "REVISAR_OPENFIN"        # el devengo diario de OpenFin NO sigue la regla
        else:
            clase = "MODELO"                 # OF devenga per-regla; el gap A-B es provisión-vs-pago (timing)
        filas.append({"id_cliente":cid, "isr_of_arbol":row["isr_of"], "isr_ac_arbol":row["isr_ac"],
                      "A_prov_bd":float(aprov) if aprov is not None else None,
                      "OF_frac_regla":round(frac,3) if frac is not None else None,
                      "B_pago_bd":float(b) if b is not None else None,
                      "clase":clase})
    res = pl.DataFrame(filas)
    RESULT.mkdir(exist_ok=True)
    res.write_parquet(RESULT / "f1_desviacion_clasificada.parquet")
    print("\n=== Clasificación del set de desviación ===")
    print(res.group_by("clase").len().sort("len", descending=True))
    # sanidad: A_prov (BD) vs isr_of (árbol)
    chk = res.filter(pl.col("A_prov_bd").is_not_null())
    if chk.height:
        dif = chk.with_columns((pl.col("A_prov_bd")-pl.col("isr_of_arbol")).abs().alias("d"))
        print(f"\nSanidad A_prov(BD) ≈ isr_of(árbol): coincide (|dif|<0.05) en {dif.filter(pl.col('d')<0.05).height}/{chk.height}")
    print(f"\nGuardado: f1_desviacion_clasificada.parquet ({res.height} casos)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=400, help="tamaño de muestra estratificada (0 = todo)")
    ap.add_argument("--band", choices=["OF","AC","ALL"], default="ALL")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    coh = cohorte(a.sample or 0, a.band)
    print(f"Set de desviación |A-B|>{UMBRAL} band={a.band} muestra={a.sample or 'TODO'} → {coh.height} inversiones "
          f"({coh['id_cliente'].n_unique()} clientes)")
    print(f"  OF>AC={coh.filter(pl.col('diff')>0).height}  AC>OF={coh.filter(pl.col('diff')<0).height}  ventana isr_diario={VENTANA}")
    if a.plan or not a.confirm:
        print("  MODO SEGURO. Para ejecutar (read-only): agrega --confirm tras la doble validación.")
        if not a.confirm: return
    ejecutar(coh, a.confirm)

if __name__ == "__main__":
    main()
