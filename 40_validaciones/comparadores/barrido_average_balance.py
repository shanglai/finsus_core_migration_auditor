"""
barrido_average_balance.py — barrido read-only del saldo base punto-en-tiempo (SOL-003).

OBJETIVO: cosechar la traza `calculateSumOfBalance ... average balance for [uuid] and amount [X]`
de los logs del CORE (dispersa por pod en los `trace-node-*.gz`), para desbloquear las dos
validaciones independientes que quedan abiertas:
  - Paso 2: rendimiento vista independiente  (rendimiento = saldo_promedio × tasa / base)
  - Paso 4: ISR-vivo                          (ISR retenido = f(saldo_total, saldo_cuenta, dias))

RESTRICCION: SSH a la VPN de logs (10.10.160.34, NFS /mnt/aurumcore_nfs/Logs), que NO coexiste con
la VPN de datos. Este runner SOLO lee (zcat|grep remoto); nunca escribe en el servidor. La salida
va a `_resultados/` (gitignored) para cruzar despues contra la DB (fase C) en la VPN de datos.

METODO (robusto a archivos grandes/lentos):
  1. Lista los archivos objetivo (por defecto `trace-node-*.gz` + `mule.log*` en core-rendimientos).
  2. Procesa UN archivo por exec_command con timeout propio; si uno falla/expira, lo salta y sigue.
  3. Parsea (fecha, timestamp, uuid, avg_balance) por linea; acumula por (uuid, fecha) -> ultimo.
  4. Escribe incrementalmente (append) para ser resume-friendly; puede reanudarse (--skip-hechos).
  5. Reporta por archivo y un resumen final (filas, uuids distintos, rango de fechas, signo).

Uso:
  # barrido completo de core-rendimientos (trace-node + mule):
  python barrido_average_balance.py
  # solo ciertos archivos / otro servicio / limitar:
  python barrido_average_balance.py --servicio core-rendimientos --glob 'trace-node-*.gz' --max-archivos 5
  python barrido_average_balance.py --servicio ms-investments --glob 'mule.log*'

Servicios candidatos (saldo promedio de inversion/vista puede vivir en otro): core-rendimientos
(confirmado), ms-investments, lms-legacy-investments, lms-legacy-balance.
"""
import sys, os, re, csv, argparse, yaml, paramiko

BASE = "/mnt/aurumcore_nfs/Logs"
OUTDIR = os.path.join(os.path.dirname(__file__), "..", "_resultados")
# 2026-08-18 23:00:00.426 [pool-..] [id] INFO [InternalPaymentGateway] - calculateSumOfBalance with average balance for [uuid] and amount [X]
RX = re.compile(r"^(\d{4}-\d{2}-\d{2})\s+([\d:.]+).*?average balance for \[([0-9a-f-]{36})\] and amount \[(-?[0-9.]+(?:[eE][-+]?\d+)?)\]")


def _conn():
    cfg = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "..", "..", "other_connections.yaml"),
                              encoding="utf-8"))["logs_aurum"]
    cli = paramiko.SSHClient()
    cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cli.connect(cfg["host"], username=cfg["user"], password=cfg["password"],
                timeout=25, banner_timeout=25, auth_timeout=25)
    return cli


def _run(cli, cmd, timeout):
    _i, o, e = cli.exec_command(cmd, timeout=timeout)
    out = o.read().decode("utf-8", "replace")
    err = e.read().decode("utf-8", "replace")
    return out, err


def listar_archivos(cli, servicio, glob):
    out, _ = _run(cli, f"ls -1 {BASE}/{servicio}/{glob} 2>/dev/null", timeout=40)
    return [l.strip() for l in out.splitlines() if l.strip()]


def grep_archivo(cli, ruta, timeout):
    """zcat|grep si es gz; grep directo si es texto plano. Devuelve texto crudo de matches."""
    if ruta.endswith(".gz"):
        cmd = f'zcat {ruta} 2>/dev/null | grep -aE "average balance for"'
    else:
        cmd = f'grep -aE "average balance for" {ruta}'
    out, _ = _run(cli, cmd, timeout=timeout)
    return out


def parse(txt):
    """[(fecha, ts, uuid, amount_str)]."""
    filas = []
    for l in txt.splitlines():
        m = RX.match(l)
        if m:
            filas.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return filas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--servicio", default="core-rendimientos")
    ap.add_argument("--glob", default="trace-node-*.gz", help="patron de archivos; repetible con coma")
    ap.add_argument("--incluir-mule", action="store_true", help="agrega mule.log* al barrido")
    ap.add_argument("--max-archivos", type=int, default=0, help="0 = todos")
    ap.add_argument("--timeout-archivo", type=int, default=180)
    ap.add_argument("--salida", default=None)
    ap.add_argument("--skip-hechos", action="store_true", help="reanuda: salta archivos ya en la salida")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUTDIR, exist_ok=True)
    salida = a.salida or os.path.join(OUTDIR, f"average_balance_sweep_{a.servicio}.csv")

    cli = _conn()
    globs = a.glob.split(",")
    if a.incluir_mule:
        globs.append("mule.log*")
    archivos = []
    for g in globs:
        archivos += listar_archivos(cli, a.servicio, g.strip())
    archivos = sorted(set(archivos))
    if a.max_archivos:
        archivos = archivos[:a.max_archivos]
    print(f"archivos objetivo: {len(archivos)} en {a.servicio} ({', '.join(globs)})")

    hechos = set()
    modo = "w"
    if a.skip_hechos and os.path.exists(salida):
        for r in csv.DictReader(open(salida, encoding="utf-8")):
            hechos.add(r.get("source_file", ""))
        modo = "a"
        print(f"reanudando: {len(hechos)} archivos ya hechos")

    f = open(salida, modo, newline="", encoding="utf-8")
    w = csv.writer(f)
    if modo == "w":
        w.writerow(["fecha", "timestamp", "account_uuid", "avg_balance", "source_file"])
    total = 0; fallidos = []
    for i, ruta in enumerate(archivos, 1):
        base = os.path.basename(ruta)
        if base in hechos:
            continue
        try:
            txt = grep_archivo(cli, ruta, a.timeout_archivo)
            filas = parse(txt)
            for fecha, ts, uuid, amt in filas:
                w.writerow([fecha, ts, uuid, amt, base])
            f.flush()
            total += len(filas)
            print(f"  [{i}/{len(archivos)}] {base}: {len(filas)} trazas (acum {total})")
        except Exception as ex:
            fallidos.append((base, str(ex)[:80]))
            print(f"  [{i}/{len(archivos)}] {base}: FALLO {str(ex)[:80]}")
            # reconectar por si el canal murio
            try:
                cli.close()
            except Exception:
                pass
            cli = _conn()
    f.close()
    cli.close()
    print(f"\nTOTAL trazas: {total} -> {salida}")
    if fallidos:
        print("archivos fallidos (reintentar con --skip-hechos):")
        for b, e in fallidos:
            print(f"  {b}: {e}")


if __name__ == "__main__":
    main()
