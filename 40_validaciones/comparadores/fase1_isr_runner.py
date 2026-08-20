# -*- coding: utf-8 -*-
"""
Fase 1 · Runner de extraccion ISR (SOLO LECTURA, gated).
- Construye las cohortes desde el parquet local (sin BD).
- Por defecto corre en --dry-run: imprime cohortes, ventanas y el SQL que correria.
- Con --confirm conecta a la BD en modo READ ONLY, con statement_timeout, y escribe
  Parquet a 40_validaciones/_resultados/ (gitignored). Nunca hace DDL/writes.

Conexion por db_connections.yaml en la raiz (GITIGNORED, NUNCA versionar). Formato:
  openfin:
    host: ...
    port: 5432
    dbname: openfin_aurum
    user: ...
    password: ...
    sslmode: require        # opcional
  aurum:
    host: ...
    port: 5432
    dbname: aurumcore
    user: ...
    password: ...
Alternativa: variables de entorno OF_DSN / AC_DSN (DSN completo).

Uso:
  python fase1_isr_runner.py --plan                 # imprime cohortes y ventanas
  python fase1_isr_runner.py --query openfin_isr_diario --cohorte SEMILLA --dry-run
  python fase1_isr_runner.py --query openfin_isr_diario --cohorte SEMILLA --confirm
Requiere doble validacion humana antes de usar --confirm (regla del proyecto).
"""
import argparse, os, re, sys, pathlib
import polars as pl
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parents[2]
EXTRACCION = ROOT / "40_validaciones" / "extraccion"
RESULT = ROOT / "40_validaciones" / "_resultados"
JOIN_PARQUET = RESULT / "_isr_join_full.parquet"
CONN_YAML = ROOT / "db_connections.yaml"

# --- Ventanas de fecha (ver PLAN_FASE1_ISR.md seccion 2) ----------------------
VENTANAS = {
    "SEMILLA":  ("2025-08-01", "2026-08-04"),   # vida completa
    "TIPO_C":   ("2026-07-01", "2026-08-04"),   # ultimo ciclo
    "TIPO_B":   ("2026-07-01", "2026-08-04"),
    "COHORTE_250": ("2026-07-01", "2026-08-04"),
}
# Semilla: NO se hardcodean ids de cliente (PII fuera de git). Se derivan del parquet
# local (gitignored) por regla, o se leen de un archivo gitignored opcional.
SEMILLA_FILE = RESULT / "cohorte_semilla.txt"   # opcional, 1 id por linea (gitignored)

# Que base usa cada query
BASE_DE = {
    "00_volumetria_of":           "OF",
    "00_volumetria_ac":           "AC",
    "openfin_isr_diario":         "OF",
    "aurum_cat_tax":              "AC",
    "aurum_account_yield":        "AC",
    "aurum_isr_al_pago_discovery":"AC",
    "aurum_isr_al_pago":          "AC",
    "aurum_saldo_base_isr":       "AC",
}

def cargar_cohortes():
    """Deriva las cohortes desde el parquet local del join A/B (sin tocar la BD)."""
    if not JOIN_PARQUET.exists():
        print(f"[!] No existe {JOIN_PARQUET}. Corre primero recon (build offline).")
        return {}
    m = pl.read_parquet(JOIN_PARQUET)
    big = m.filter(pl.col("diff") > 0.10).sort("diff", descending=True)
    tipo_c_all = big.filter(pl.col("isr_ac") < 0.05).select("id_cliente").unique(maintain_order=True)["id_cliente"].to_list()
    tipo_b_all = big.filter(pl.col("isr_ac") >= 0.05).select("id_cliente").unique(maintain_order=True)["id_cliente"].to_list()
    # Semilla: 2 exento + 2 expuesto derivados por regla (+ ids del archivo opcional gitignored)
    semilla = tipo_c_all[:2] + tipo_b_all[:2]
    if SEMILLA_FILE.exists():
        extra = [l.strip() for l in SEMILLA_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
        semilla = list(dict.fromkeys(extra + semilla))   # los del archivo primero, sin duplicar
    return {"SEMILLA": semilla, "TIPO_C": tipo_c_all[:25], "TIPO_B": tipo_b_all[:25]}

def cliente_a_llaves(ids):
    """'suc-rol-asoc' -> (suc,rol,asoc) int para OpenFin; y el string para Aurum."""
    of, ac = [], []
    for cid in ids:
        p = cid.split("-")
        if len(p) == 3 and all(x.lstrip("-").isdigit() for x in p):
            of.append((int(p[0]), int(p[1]), int(p[2])))
            ac.append(cid)
    return of, ac

def cuentas_aurum(ids):
    """account_number ('100-2301-X') de las inversiones de esos clientes, desde el parquet local.
    En Aurum la cohorte se ancla por account_number (la llave de cliente '100-10-X' NO existe alli:
    accountholder.external_id es un entero interno). Ver bitacora 2026-08-18."""
    if not JOIN_PARQUET.exists():
        return []
    m = pl.read_parquet(JOIN_PARQUET)
    return (m.filter(pl.col("id_cliente").is_in(ids))["id_inversion_aurumcore"]
             .unique().to_list())

def cte_cohorte(of_keys, ac_keys, acc_nums):
    """CTEs con VALUES para inyectar la cohorte SIN crear temp tables (read-only safe)."""
    of_vals  = ",".join(f"({s},{r},{a})" for (s, r, a) in of_keys) or "(NULL,NULL,NULL)"
    ac_vals  = ",".join("('" + c.replace("'", "''") + "')" for c in ac_keys) or "('')"
    acc_vals = ",".join("('" + c.replace("'", "''") + "')" for c in acc_nums) or "('')"
    return (f"with cohorte_of(id_sucursal,id_role,id_asociado) as (values {of_vals}),\n"
            f"     cohorte(accountholder_number) as (values {ac_vals}),\n"
            f"     cohorte_acc(account_number) as (values {acc_vals})\n")

def preparar_sql(texto, of_keys, ac_keys, acc_nums, fecha_ini, fecha_fin, cuentas_semilla=None, isr_txn_type=None):
    """Divide en statements, inyecta CTE de cohorte donde se usa, y convierte :param -> %(param)s."""
    # Quitar comentarios de linea ANTES de partir por ';' (evita romper en un ';' dentro
    # de un comentario). Nuestros SQL no usan '--' dentro de literales.
    sin_com = "\n".join(re.sub(r"--.*$", "", ln) for ln in texto.splitlines())
    stmts = [s.strip() for s in sin_com.split(";") if s.strip()]
    out = []
    for s in stmts:
        if re.search(r"\bcohorte(_of|_acc)?\b", s):
            s = cte_cohorte(of_keys, ac_keys, acc_nums) + s
        s = s.replace(":fecha_ini", "%(fecha_ini)s").replace(":fecha_fin", "%(fecha_fin)s")
        s = s.replace(":isr_txn_type", "%(isr_txn_type)s")
        if ":cuentas_semilla" in s:
            s = s.replace(":cuentas_semilla", "%(cuentas_semilla)s")
        out.append(s)
    params = {"fecha_ini": fecha_ini, "fecha_fin": fecha_fin,
              "cuentas_semilla": tuple(cuentas_semilla or acc_nums or []), "isr_txn_type": isr_txn_type}
    return out, params

def conn_kwargs(base):
    """kwargs de conexion psycopg2 para 'OF'/'AC'. Prioriza db_connections.yaml (gitignored)."""
    seccion = "openfin" if base == "OF" else "aurum"
    if CONN_YAML.exists():
        import yaml
        cfg = yaml.safe_load(CONN_YAML.read_text(encoding="utf-8")) or {}
        if seccion in cfg and cfg[seccion]:
            c = cfg[seccion]
            kw = {k: c[k] for k in ("host", "port", "dbname", "user", "password", "sslmode") if k in c}
            host = kw.get("host", "?")
            print(f"  conexion {base}: db_connections.yaml [{seccion}] host={host} db={kw.get('dbname','?')}")
            return kw
        print(f"[!] {CONN_YAML.name} no tiene la seccion '{seccion}'.")
    dsn = os.environ.get("OF_DSN" if base == "OF" else "AC_DSN")
    if dsn:
        print(f"  conexion {base}: env {'OF_DSN' if base=='OF' else 'AC_DSN'}")
        return {"dsn": dsn}
    print(f"[!] Sin credenciales para {base}: falta seccion '{seccion}' en {CONN_YAML.name} o env DSN.")
    return None

def ejecutar(base, stmts, params, salida_prefix, confirm):
    if not confirm:
        print("  [dry-run] NO se conecta. SQL preparado:")
        for i, s in enumerate(stmts, 1):
            print(f"  --- statement {i} ---\n{s}\n  params={ {k:('<oculto>' if k=='password' else v) for k,v in params.items()} }")
        return
    import psycopg2  # se importa solo si se confirma
    kw = conn_kwargs(base)
    if not kw:
        sys.exit(2)
    RESULT.mkdir(exist_ok=True)
    conn = psycopg2.connect(kw["dsn"]) if "dsn" in kw else psycopg2.connect(**kw)
    conn.set_session(readonly=True, autocommit=False)
    with conn.cursor() as cur:
        cur.execute("SET statement_timeout = '120s'; SET default_transaction_read_only = on;")
        for i, s in enumerate(stmts, 1):
            print(f"  ejecutando statement {i}/{len(stmts)} ...")
            cur.execute(s, params)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall() if cur.description else []
            df = pl.DataFrame(rows, schema=cols, orient="row") if cols else pl.DataFrame()
            dest = RESULT / f"{salida_prefix}_s{i}.parquet"
            df.write_parquet(dest)
            print(f"    -> {dest}  ({df.height} filas)")
    conn.rollback(); conn.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true", help="imprime cohortes y ventanas y sale")
    ap.add_argument("--query", help="nombre del .sql en extraccion/ (sin extension)")
    ap.add_argument("--cohorte", default="SEMILLA", choices=list(VENTANAS.keys()))
    ap.add_argument("--isr-txn-type", default=None, help="tipo de transaccion ISR (se fija en P3)")
    ap.add_argument("--confirm", action="store_true", help="CONECTA a la BD (read-only). Requiere doble validacion.")
    ap.add_argument("--dry-run", action="store_true", help="explicito; es el default de todas formas")
    args = ap.parse_args()

    cohortes = cargar_cohortes()
    if args.plan or not args.query:
        print("VENTANAS:", VENTANAS)
        for k, v in cohortes.items():
            print(f"\nCohorte {k} ({len(v)} clientes): {v}")
        print("\nUsa --query <archivo> --cohorte <NOMBRE> [--confirm]")
        return

    ids = cohortes.get(args.cohorte, [])
    of_keys, ac_keys = cliente_a_llaves(ids)
    acc_nums = cuentas_aurum(ids)
    fecha_ini, fecha_fin = VENTANAS[args.cohorte]
    sqlfile = EXTRACCION / f"{args.query}.sql"
    if not sqlfile.exists():
        print(f"[!] No existe {sqlfile}"); sys.exit(2)
    texto = sqlfile.read_text(encoding="utf-8")
    stmts, params = preparar_sql(texto, of_keys, ac_keys, acc_nums, fecha_ini, fecha_fin,
                                 cuentas_semilla=acc_nums, isr_txn_type=args.isr_txn_type)
    base = BASE_DE.get(args.query, "AC")
    print(f"Query={args.query}  base={base}  cohorte={args.cohorte} ({len(ids)} clientes, {len(acc_nums)} cuentas)  ventana=[{fecha_ini},{fecha_fin})")
    if not args.confirm:
        print("  MODO SEGURO (dry-run). Para ejecutar: agrega --confirm tras la doble validacion.")
    ejecutar(base, stmts, params, salida_prefix=f"f1_{args.query}_{args.cohorte}", confirm=args.confirm)

if __name__ == "__main__":
    main()
