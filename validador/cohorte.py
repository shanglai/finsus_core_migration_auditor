# -*- coding: utf-8 -*-
"""Genera un archivo de cohorte para `--cohorte-archivo`.

    python cohorte.py --producto 2301 --desde 2026-09-01 --hasta 2026-09-02 \
                      --delimitador live --n 300 --salida cuentas.txt

POR QUE ESTO NO ES SOLO UN `select ... limit N`.

En la sesion del 2026-08-28 la auditoria pregunto, sobre las 300 cuentas de
V-02: *"la metodologia con la que determinaron cuantos y POR QUE"*. No se pudo
contestar, y sin esa respuesta el 97.79% de ese punto **no es extrapolable** al
padron migrado. El archivo de cohorte era una lista de numeros de cuenta sin
procedencia: en cuanto sale de la carpeta, nadie puede reconstruir como se
eligio.

Por eso este generador escribe el METODO DENTRO DEL ARCHIVO, como comentarios
`#` que el lector de `cli.py` ignora al parsear pero que viajan con la cohorte:
que consulta la produjo, con que parametros, cuantas cuentas habia disponibles,
cuantas se tomaron y con que criterio. La cohorte carga su propia procedencia.

TRES CRITERIOS, y la diferencia importa:

  censo         se toman TODAS las cuentas que cumplen el filtro. No extrapola
                porque no hace falta: no quedo nada fuera.
  determinista  las primeras N por `account_number`. Reproducible al 100% —dos
                corridas dan la misma cohorte— pero NO es aleatoria: si el
                numero de cuenta correlaciona con algo (antiguedad, sucursal),
                la muestra hereda ese sesgo. Sirve para depurar, no para
                extrapolar.
  aleatorio     N al azar con SEMILLA declarada. Es el unico que permite
                extrapolar, y la semilla lo mantiene reproducible.

El default es `censo` a proposito: si cabe, no se muestrea. Los otros dos
obligan a pasar `--n`, para que reducir el universo sea siempre una decision
explicita y no un descuido.

Solo lectura, acotado, sin PII: devuelve numeros de cuenta, nada mas.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from engine import extract  # noqa: E402

CRITERIOS = ("censo", "determinista", "aleatorio")

# El universo disponible, ANTES de recortar. Se cuenta siempre, aunque se tome
# el censo: sin el denominador no se puede decir que representa la cohorte, que
# es justo lo que la auditoria pidio.
SQL_DISPONIBLES = """
select count(distinct a.account_number) as cuentas
from aurumcore.iv_payment_plan pp
join aurumcore.account a on a.account_id = pp.account_id
where pp.interest_paid = true
  and pp.interest_amount > 0
  and pp.payment_date >= %(desde)s
  and pp.payment_date <  %(hasta)s
  and a.account_number like %(patron)s
  and (
        (%(delim)s = 'migrado' and pp.origin = 'FINSUS')
     or (%(delim)s = 'live'    and pp.origin is null)
  )
"""

SQL_CUENTAS = """
select distinct a.account_number
from aurumcore.iv_payment_plan pp
join aurumcore.account a on a.account_id = pp.account_id
where pp.interest_paid = true
  and pp.interest_amount > 0
  and pp.payment_date >= %(desde)s
  and pp.payment_date <  %(hasta)s
  and a.account_number like %(patron)s
  and (
        (%(delim)s = 'migrado' and pp.origin = 'FINSUS')
     or (%(delim)s = 'live'    and pp.origin is null)
  )
order by a.account_number
"""


def cabecera(args, disponibles: int, tomadas: int, cuando: str) -> list[str]:
    """La procedencia que viaja con el archivo."""
    pct = f"{tomadas / disponibles * 100:.2f}%" if disponibles else "[PEND]"
    L = [
        "# Cohorte para --cohorte-archivo. Generada por validador/cohorte.py.",
        "#",
        "# ---- COMO SE ELIGIO (esto es lo que la auditoria pregunta) ----",
        f"# criterio        : {args.criterio}",
        f"# disponibles     : {disponibles:,} cuentas cumplen el filtro",
        f"# tomadas         : {tomadas:,}",
        f"# representa      : {pct} del universo filtrado",
    ]
    if args.criterio == "aleatorio":
        L.append(f"# semilla         : {args.semilla}  (reproducible: misma semilla, misma cohorte)")
    elif args.criterio == "determinista":
        L += ["# orden           : primeras N por account_number ascendente",
              "# OJO             : NO es aleatoria. Si el numero de cuenta correlaciona",
              "#                   con antiguedad o sucursal, la muestra hereda ese sesgo.",
              "#                   Sirve para depurar; NO para extrapolar al padron."]
    elif args.criterio == "censo" and tomadas < disponibles:
        L += ["# OJO             : se pidio censo pero la cota lo corto. Deja de ser censo:",
              "#                   subir --n o declararlo como muestra."]
    L += [
        "#",
        "# ---- FILTRO ----",
        f"# producto        : {args.producto}   (patron account_number '100-{args.producto}-%')",
        f"# ventana         : payment_date >= {args.desde} y < {args.hasta}  (hasta EXCLUSIVA)",
        f"# delimitador     : {args.delimitador}  "
        f"({'origin = FINSUS, ingestado de OpenFin' if args.delimitador == 'migrado' else 'origin is null, generado por AurumCore'})",
        "#                   Los dos delimitadores son DOS EXPERIMENTOS distintos y no se mezclan:",
        "#                   'live' confirma C=B; 'migrado' confirma C=A.",
        "#",
        f"# generada        : {cuando}",
        "# fuente          : aurumcore.iv_payment_plan JOIN account (solo lectura)",
        "#",
        "# Las lineas que empiezan con # las ignora cli.py al parsear.",
        "",
    ]
    return L


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Genera un archivo de cohorte con su procedencia dentro.")
    ap.add_argument("--producto", default="2301",
                    help="segmento del account_number, p.ej. 2301 (inversion a plazo)")
    ap.add_argument("--desde", required=True, help="payment_date >= (AAAA-MM-DD)")
    ap.add_argument("--hasta", required=True, help="payment_date < (EXCLUSIVA)")
    ap.add_argument("--delimitador", choices=("live", "migrado"), default="live")
    ap.add_argument("--criterio", choices=CRITERIOS, default="censo")
    ap.add_argument("--n", type=int, default=0,
                    help="cuantas cuentas tomar. Obligatorio salvo en censo.")
    ap.add_argument("--semilla", type=int, default=None,
                    help="semilla del muestreo aleatorio. Obligatoria si --criterio aleatorio.")
    ap.add_argument("--salida", default="cuentas.txt")
    ap.add_argument("--max-filas", type=int, default=500_000)
    args = ap.parse_args(argv)

    if args.criterio != "censo" and args.n <= 0:
        raise SystemExit(f"--criterio {args.criterio} exige --n > 0: reducir el universo "
                         f"tiene que ser una decision explicita.")
    if args.criterio == "aleatorio" and args.semilla is None:
        raise SystemExit("--criterio aleatorio exige --semilla: sin ella la cohorte no es "
                         "reproducible y el resultado no se puede volver a obtener.")

    params = {"desde": args.desde, "hasta": args.hasta,
              "patron": f"100-{args.producto}-%", "delim": args.delimitador}

    ex = extract.ejecutar("aurum", [SQL_DISPONIBLES, SQL_CUENTAS], params,
                          archivo="cohorte", max_filas=args.max_filas)
    disponibles = int(ex.tablas[0].row(0)[0]) if ex.tablas[0].height else 0
    todas = [r[0] for r in ex.tablas[1].iter_rows()]

    if not todas:
        print(f"[!] Cero cuentas con ese filtro. NO se escribe archivo: una cohorte vacia "
              f"haria que el caso 'pase' sin haber comparado nada.")
        return 2

    if args.criterio == "censo":
        cuentas = todas if args.n <= 0 else todas[:args.n]
    elif args.criterio == "determinista":
        cuentas = todas[:args.n]
    else:
        import random
        cuentas = sorted(random.Random(args.semilla).sample(todas, min(args.n, len(todas))))

    cuando = datetime.now(timezone.utc).isoformat(timespec="seconds")
    destino = Path(args.salida)
    destino.write_text("\n".join(cabecera(args, disponibles, len(cuentas), cuando) + cuentas)
                       + "\n", encoding="utf-8")

    print(f"{len(cuentas):,} cuentas -> {destino}")
    print(f"  de {disponibles:,} disponibles "
          f"({len(cuentas) / disponibles * 100:.2f}%)" if disponibles else "")
    print(f"  criterio: {args.criterio}"
          + (f" · semilla {args.semilla}" if args.criterio == "aleatorio" else ""))
    if args.criterio == "determinista":
        print("  [!] determinista NO es aleatoria: sirve para depurar, no para extrapolar.")
    print(f"\nCorrer con:\n  python cli.py --caso REND-PLAZO --confirmar "
          f"--cohorte-archivo {destino} \\\n"
          f"    --param fecha_ini={args.desde} --param fecha_fin={args.hasta} "
          f"--param delimitador={args.delimitador}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
