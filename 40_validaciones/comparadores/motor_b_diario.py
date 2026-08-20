"""
Motor B - Validador de la transaccional diaria (Aurum vs OpenFin) - PRIMERA CORRIDA.

Tercero independiente (charter 9, K-PRC-001). SOLO LECTURA.
Reconstruye el mapeo 2:1 (peer-to-peer) / 1:1 (unidireccional) desde los catalogos
(OF cat_tx_cuadre <-> AU cat_finsus_transaction, misma numeracion de tipo) y clasifica
por prefijo de cuenta contable (21xx/24xx = cliente; 11xx = interbancaria/efectivo).

Alcance de esta primera corrida:
  - Clasifica los 314 tipos OF en PEER (2:1) vs UNI (1:1).
  - Para una fecha: normaliza los movimientos OF y los cuenta por clase/tipo.
  - Cruza el VOLUMEN OF-normalizado vs el conteo de transacciones de Aurum (nivel agregado).
  - Semilla de causuistica: desbalance cargo/abono en tipos PEER (piernas sin par).

NO cubre todavia (siguiente acotado, ver PLAN_MOTOR_B_DIARIO.md):
  - Match instancia-a-instancia: falta el crosswalk tipo-numerico (OF) <-> tipo-texto
    (AU transaction_detail: 'INTERNAL TRANSFER'/'DEPOSIT'/...). Aqui el cruce es de volumen.
  - Emparejamiento fino cargo<->abono (secuencia N/N+1) por operacion.

Uso:  python motor_b_diario.py [--fecha YYYY-MM-DD]
"""
import sys, argparse, yaml, psycopg2, time
from decimal import Decimal
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
CFG = yaml.safe_load(open(RAIZ / "db_connections.yaml", encoding="utf-8"))
RES = RAIZ / "40_validaciones" / "_resultados"
RES.mkdir(exist_ok=True)


def conn(name):
    C = CFG[name]
    kw = {k: C[k] for k in ("host", "port", "dbname", "user", "password", "sslmode") if k in C}
    for a in range(3):
        try:
            c = psycopg2.connect(**kw)
            c.set_session(readonly=True)
            return c
        except Exception as e:
            print(f"[{name}] retry {a}: {str(e).splitlines()[0][:60]}")
            time.sleep(4)
    raise RuntimeError(f"no conecta {name}")


def rows(cur, sql, args=None):
    cur.execute(sql, args)
    return cur.fetchall()


def clasifica_catalogo(cat_rows):
    """
    Clasificador refinado (PLAN_MOTOR_B_DIARIO.md 6.bis).
    PEER (2:1): el tipo aparece con pierna cargo (tipo=1) Y pierna abono (tipo=2) bajo la MISMA
                descripcion -> son las dos piernas de una transferencia interna entre cuentas de
                cliente. Ej.: 1 (transf interna), 177 (web banking), 306 (traspaso ahorro).
    UNI (1:1):  todo lo demas -> una sola pierna, o dos piernas con descripciones distintas
                (p.ej. SPEI tipo 3: 'saliente' != 'entrante' = dos operaciones unidireccionales).
    El prefijo de cuenta NO sirve: el catalogo usa cuentas puente 2401 entre las piernas cliente 2101.
    """
    from collections import defaultdict
    tipos = defaultdict(lambda: {"legs": set(), "descrs": set(), "dc": "", "da": ""})
    for t, leg, descr, cc, ca in cat_rows:
        d = tipos[int(t)]
        d["legs"].add(int(leg)); d["descrs"].add((descr or "").strip().lower())
        if int(leg) == 1: d["dc"] = descr or ""      # descripcion de la pierna cargo
        elif int(leg) == 2: d["da"] = descr or ""     # descripcion de la pierna abono
    out = {}
    for t, d in tipos.items():
        peer = (1 in d["legs"] and 2 in d["legs"] and len(d["descrs"]) == 1)
        out[t] = {"descr": (d["dc"] or d["da"])[:40], "descr_c": d["dc"], "descr_a": d["da"],
                  "clase": "PEER" if peer else "UNI"}
    return out


# --- Crosswalk por CATEGORIA semantica (paso 3) ---
# OF: se deriva de la descripcion del tipo (cat_tx_cuadre). AU: del transaction_type texto.
def categoria_of(descr):
    d = (descr or "").lower()
    if "spei" in d:                                   # Aurum contabiliza el SPEI-in como DEPOSIT
        return "DEPOSITO" if "entrante" in d else "SPEI_EXTERNA"
    if ("interna" in d or "traspaso" in d or "web bank" in d or "dimo" in d
            or "wallet" in d):                        return "TRANSFER_INTERNA"
    if "deposit" in d or "dépos" in d or "depós" in d: return "DEPOSITO"
    if "retiro" in d or "extracash" in d:             return "RETIRO_EFECTIVO"
    if "tdd" in d or "tpv" in d or "purchase" in d or "compra" in d or "pomelo" in d or "tdc" in d: return "TARJETA"
    if "servicio" in d or "colegiatura" in d or "pago de servicios" in d: return "SERVICIOS"
    if "recompensa" in d:                             return "RECOMPENSAS"
    return "OTRO"

def categoria_au(tt):
    m = {
        "INTERNAL TRANSFER": "TRANSFER_INTERNA", "INTERNAL CREDIT TRANSFER": "TRANSFER_INTERNA",
        "EXTERNAL TRANSFER": "SPEI_EXTERNA", "DEPOSIT": "DEPOSITO",
        "DEBIT CARD CHARGE": "TARJETA", "DEBIT CARD REFUND": "TARJETA",
        "REVERSAL PAYMENT": "OTRO",
    }
    return m.get(tt, "OTRO")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fecha", default="2026-08-14")
    a = ap.parse_args()
    fecha = a.fecha

    of = conn("openfin"); cof = of.cursor(); cof.execute("SET statement_timeout='180s'")
    au = conn("aurum");   cau = au.cursor(); cau.execute("SET statement_timeout='180s'")

    # --- 1. Clasificacion de tipos desde cat_tx_cuadre (refinada por descripcion) ---
    cat = rows(cof, """
        select tipo_transaccion, tipo, descripcion, cuenta_contable_cargo, cuenta_contable_abono
        from public.cat_tx_cuadre""")
    clase = clasifica_catalogo(cat)
    n_peer = sum(1 for v in clase.values() if v["clase"] == "PEER")
    print(f"Catalogo OF cat_tx_cuadre: {len(clase)} tipos  |  PEER(2:1)={n_peer}  UNI(1:1)={len(clase)-n_peer}")

    # --- 2. Movimientos OF del dia, por tipo ---
    def carga(tabla):
        d = {}
        nulos = [0, Decimal(0)]
        for t, n, m in rows(cof, f"""
            select tipo_transaccion, count(*), coalesce(sum(monto),0)
            from public.{tabla} where fecha=%s group by 1""", (fecha,)):
            if t is None:
                nulos[0] += n; nulos[1] += (m or Decimal(0))
            else:
                d[int(t)] = (n, m or Decimal(0))
        return d, tuple(nulos)
    car, car_nulos = carga("vista_movimientos_cargos")
    abo, abo_nulos = carga("vista_movimientos_abonos")

    tipos = sorted(set(car) | set(abo))
    tot_legs = 0
    tot_ops = 0
    tot_monto = Decimal(0)
    peer_imbalance = []   # causuistica: piernas PEER sin par
    filas = []
    for t in tipos:
        nc, mc = car.get(t, (0, Decimal(0)))
        na, ma = abo.get(t, (0, Decimal(0)))
        info = clase.get(t, {"descr": "(tipo sin catalogo)", "clase": "UNI"})
        cl = info["clase"]
        legs = nc + na
        if cl == "PEER":
            ops = max(nc, na)                 # una operacion por par; el max capta piernas sueltas
            if nc != na:
                peer_imbalance.append((t, info["descr"], nc, na, nc - na))
        else:
            ops = legs                        # unidireccional: cada pierna es una operacion
        tot_legs += legs; tot_ops += ops; tot_monto += (mc + ma)
        filas.append((t, cl, info["descr"], nc, na, ops, mc + ma))
    # Agregado por categoria (OF) — POR PIERNA (cargo usa descr_c, abono usa descr_a).
    # Un tipo puede reusar el numero para ambas direcciones (SPEI saliente=cargo / entrante=abono).
    from collections import defaultdict
    of_cat = defaultdict(int)
    for t in tipos:
        nc, _ = car.get(t, (0, Decimal(0)))
        na, _ = abo.get(t, (0, Decimal(0)))
        info = clase.get(t, {"clase": "UNI", "descr_c": "", "descr_a": ""})
        cat_c = categoria_of(info.get("descr_c") or info.get("descr", ""))
        cat_a = categoria_of(info.get("descr_a") or info.get("descr", ""))
        if info["clase"] == "PEER":
            of_cat[cat_c] += max(nc, na)          # 1 op por transferencia (2 piernas -> 1)
        else:
            of_cat[cat_c] += nc                    # cargo (p.ej. SPEI saliente)
            of_cat[cat_a] += na                    # abono (p.ej. SPEI entrante = DEPOSITO)

    # --- 3. Aurum: conteo de transaccional del dia ---
    au_tipos = rows(cau, """
        select transaction_type, count(*) n
        from aurumcore.transaction_detail where created::date=%s group by 1 order by n desc""", (fecha,))
    au_total = sum(n for _, n in au_tipos)
    # Aurum: separar transaccional de CLIENTE (canales) vs core-INTERNO (rendimiento/ISR/inversion).
    AU_CORE = {"YIELD PAYMENT", "YIELD TAX PAYMENT", "CAPITAL RETURN", "INTERNAL INVESTMENT TRANSFER"}
    au_cliente = sum(n for tt, n in au_tipos if tt not in AU_CORE)
    au_core = au_total - au_cliente

    # --- 4. Reporte ---
    print(f"\n=== Motor B (primera corrida) - fecha {fecha} ===")
    print(f"\nOpenFin - movimientos por tipo (top 20 por piernas):")
    print(f"  {'tipo':>4} {'clase':<5} {'descr':<40} {'cargos':>7} {'abonos':>7} {'ops':>7}")
    for t, cl, descr, nc, na, ops, monto in sorted(filas, key=lambda r: -(r[3] + r[4]))[:20]:
        print(f"  {t:>4} {cl:<5} {descr:<40} {nc:>7} {na:>7} {ops:>7}")

    print(f"\nOpenFin agregado {fecha}:  piernas={tot_legs:,}  ops_normalizadas={tot_ops:,}  monto=${tot_monto:,.2f}")
    print(f"Aurum agregado    {fecha}:  transaction_detail={au_total:,}  (cliente={au_cliente:,}  core-interno={au_core:,})")
    delta = tot_ops - au_cliente
    pct = (delta / au_cliente * 100) if au_cliente else 0
    print(f"\n>>> CRUCE DE VOLUMEN (peras con peras):  OF ops_norm={tot_ops:,}  vs  AU cliente={au_cliente:,}"
          f"   delta={delta:+,} ({pct:+.1f}%)")
    print("    (core-interno de Aurum -rendimiento/ISR/inversion- se excluye: no viene de canal)")
    print(f"\nAurum por transaction_type (top 12):")
    for tt, n in au_tipos[:12]:
        print(f"  {n:>8,}  {tt}")

    # --- Crosswalk por categoria: OF ops vs AU cliente ---
    au_cat = {}
    for tt, n in au_tipos:
        if tt in AU_CORE:
            continue
        au_cat[categoria_au(tt)] = au_cat.get(categoria_au(tt), 0) + n
    cats = sorted(set(of_cat) | set(au_cat))
    print(f"\n>>> CROSSWALK POR CATEGORIA (OF ops_norm vs AU cliente):")
    print(f"  {'categoria':<18} {'OF':>9} {'AU':>9} {'delta':>8} {'%':>7}")
    for c in cats:
        o = of_cat.get(c, 0); au_ = au_cat.get(c, 0); dl = o - au_
        p = (dl / au_ * 100) if au_ else float('nan')
        print(f"  {c:<18} {o:>9,} {au_:>9,} {dl:>+8,} {p:>+6.1f}%")

    print(f"\n[CAUSUISTICA] Movimientos OF con tipo_transaccion NULL:  cargos={car_nulos[0]:,} (${car_nulos[1]:,.2f})  abonos={abo_nulos[0]:,} (${abo_nulos[1]:,.2f})")
    print(f"[CAUSUISTICA] Tipos PEER con desbalance cargo!=abono (piernas sin par): {len(peer_imbalance)}")
    for t, descr, nc, na, d in sorted(peer_imbalance, key=lambda r: -abs(r[4]))[:10]:
        print(f"   tipo {t:>3} {descr:<40} cargos={nc} abonos={na} delta={d:+d}")

    print("\nNOTA: cruce de VOLUMEN (no instancia-a-instancia). Falta el crosswalk tipo-numerico OF")
    print("      <-> tipo-texto Aurum (transaction_detail) para el match por tipo. Ver PLAN_MOTOR_B_DIARIO.md.")

    of.close(); au.close()


if __name__ == "__main__":
    main()
