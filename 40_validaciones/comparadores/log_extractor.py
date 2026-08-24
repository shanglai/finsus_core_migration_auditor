"""
log_extractor.py — extractor read-only de trazas del CORE de AurumCore (SOL-003, logs por SSH).

CONTEXTO / RESTRICCION DURA: los logs (host 10.10.160.34, NFS /mnt/aurumcore_nfs/Logs) se
alcanzan por una SEGUNDA VPN que NO coexiste con la VPN de datos (DB aurum 10.10.160.53).
Por eso el cruce log<->DB es en TRES FASES:

  FASE A (VPN datos)  : sacar la cohorte viva de la DB (contratos/cuentas + valores esperados
                        io/im/rendimiento) -> CSV local en _resultados/.
  FASE B (VPN logs)   : para ESOS ids, extraer las trazas (dias / saldo promedio / yield) -> CSV.
  FASE C (cualquiera) : cruzar local: log(dias|saldo) + DB(tasa|monto) -> oraculo -> vs io/im/rend.

Este modulo cubre la FASE B. Solo lectura (grep remoto), nunca escribe en el servidor.

Trazas objetivo (confirmadas en core-rendimientos/mule.log 2026-08-23):
  - Credito dias ORD : "CreditAmortizationChargeServiceImpl.java:844) - Days N"
  - Credito dias MORA: "InterestMoraDays db[N]"  (java:805)
  - contrato del bloque: "findOldestChargeWithouthPayment [<uuid>]" (mismo [pool-N-thread-M])
  - Saldo promedio   : "calculateSumOfBalance ... average balance for [<uuid>] and amount [<x>]"
  - Rendimiento vista: "Calculating yield amount Using RATE ..., DaysOfYear[360|365]"  (por verificar)

Uso:
  python log_extractor.py --patron avgbal --servicio core-rendimientos --archivo mule.log
  python log_extractor.py --patron dias   --servicio core-rendimientos
  python log_extractor.py --patron raw --regex "average balance for" --servicio ms-investments
"""
import sys, os, csv, re, argparse, yaml, paramiko
from datetime import date

BASE = "/mnt/aurumcore_nfs/Logs"
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "_resultados")

PATRONES = {
    # nombre -> regex grep remoto
    "avgbal": r"average balance for",                 # CREDITO: calculateSumOfBalance ... average balance for [uuid] (negativo)
    # VISTA (rendimiento): strings EXACTOS del doc oficial GTM-Saldo Promedio (p.8-10). trace.log.
    "vista_saldoprom": r"Calculating with average balance",           # da difference of days + ELAPSED DAYS
    "vista_yield":     r"Calculating yield amount Using RATE",         # da saldo promedio, tasa, DaysOfYear[360|365]
    "yield":  r"yield amount|DaysOfYear|Using RATE",
    "dias":   r"findOldestChargeWithouthPayment|CreditAmortizationChargeServiceImpl.java:844|InterestMoraDays",
}


def _conn():
    C = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "..", "other_connections.yaml"),
                            encoding="utf-8"))["logs_aurum"]
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(C["host"], username=C["user"], password=C["password"],
                timeout=25, banner_timeout=25, auth_timeout=25)
    return cli


def _run(cli, cmd, timeout=90):
    _i, o, _e = cli.exec_command(cmd, timeout=timeout)
    return o.read().decode("utf-8", "replace")


def extraer_raw(servicio, archivo, regex, timeout=90):
    """grep -aE remoto de una traza; devuelve el texto crudo (una linea por match)."""
    cli = _conn()
    try:
        ruta = f"{BASE}/{servicio}/{archivo}"
        # -a: tratar binario como texto; -E: regex extendida. Sin -r para no barrer rotados por accidente.
        # regex va entre comillas dobles (permite espacios); NO se re.escape (rompe la semantica -E).
        # gz -> zcat|grep (zgrep); texto plano -> grep directo.
        if archivo.endswith(".gz"):
            return _run(cli, f'zcat {ruta} 2>/dev/null | grep -aE "{regex}"', timeout=timeout)
        return _run(cli, f'grep -aE "{regex}" {ruta}', timeout=timeout)
    finally:
        cli.close()


def parse_avgbal(txt):
    """[(uuid, amount_str)] de 'average balance for [uuid] and amount [x]'."""
    return re.findall(r"average balance for \[([0-9a-f-]{36})\] and amount \[(-?[0-9.]+)\]", txt)


def parse_dias(txt):
    """{contract_id: {'dias_ord': set, 'dias_mora': set}} keyeado por thread + findOldestCharge."""
    thr_cid, rows = {}, {}
    for l in txt.splitlines():
        tm = re.search(r"\[(pool-[0-9]+-thread-[0-9]+)\]", l)
        thr = tm.group(1) if tm else None
        c = re.search(r"findOldestChargeWithouthPayment \[([0-9a-f-]{36})\]", l)
        if c and thr:
            thr_cid[thr] = c.group(1); continue
        if thr and thr in thr_cid:
            cid = thr_cid[thr]; r = rows.setdefault(cid, {"dias_ord": set(), "dias_mora": set()})
            d = re.search(r"CreditAmortizationChargeServiceImpl\.java:844\) - Days (\d+)", l)
            if d: r["dias_ord"].add(int(d.group(1)))
            m = re.search(r"InterestMoraDays db\[(\d+)\]", l)
            if m: r["dias_mora"].add(int(m.group(1)))
    return {k: v for k, v in rows.items() if v["dias_ord"] or v["dias_mora"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patron", choices=list(PATRONES) + ["raw"], required=True)
    ap.add_argument("--servicio", default="core-rendimientos")
    ap.add_argument("--archivo", default="mule.log")
    ap.add_argument("--regex", default=None, help="para --patron raw")
    ap.add_argument("--timeout", type=int, default=90)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUTDIR, exist_ok=True)
    hoy = date.today().isoformat()

    regex = a.regex if a.patron == "raw" else PATRONES[a.patron]
    print(f"grep [{regex}] en {a.servicio}/{a.archivo} ...")
    txt = extraer_raw(a.servicio, a.archivo, regex, timeout=a.timeout)
    print("lineas:", len(txt.splitlines()))

    if a.patron == "avgbal":
        pares = parse_avgbal(txt)
        out = os.path.join(OUTDIR, f"saldo_promedio_log_{a.servicio}_{hoy}.csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["account_uuid", "avg_balance"])
            w.writerows(dict((u, x) for u, x in pares).items())
        print(f"saldo promedio: {len(set(u for u,_ in pares))} cuentas -> {out}")
    elif a.patron == "dias":
        rows = parse_dias(txt)
        out = os.path.join(OUTDIR, f"credito_dias_log_{a.servicio}_{hoy}.csv")
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["contract_id", "dias_ord", "dias_mora"])
            for cid, v in rows.items():
                w.writerow([cid, ";".join(map(str, sorted(v["dias_ord"]))),
                            ";".join(map(str, sorted(v["dias_mora"])))])
        print(f"credito dias: {len(rows)} contratos -> {out}")
    else:
        out = os.path.join(OUTDIR, f"raw_{a.patron}_{a.servicio}_{hoy}.txt")
        open(out, "w", encoding="utf-8").write(txt)
        print(f"raw -> {out}")


if __name__ == "__main__":
    main()
