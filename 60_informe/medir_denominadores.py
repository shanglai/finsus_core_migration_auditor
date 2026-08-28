# -*- coding: utf-8 -*-
"""Mide contra la base los denominadores que el informe declara `[PEND]`.

    python 60_informe/medir_denominadores.py

Solo lectura y solo AGREGACION: cuenta filas, no lee datos de cliente. Imprime
lo que hay que escribir en `puntos.py` — no lo escribe solo, a proposito: un
denominador es una afirmacion del informe y la revisa un humano antes de
publicarse.

Contesta la pregunta que la auditoria dejo abierta el 2026-08-28 [00:32:35]:
"cuanto representan esos items respecto del universo".
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ.parent / "validador"))

from engine import extract  # noqa: E402
from puntos import PUNTOS  # noqa: E402

# El SQL de cada denominador pendiente. Se mantiene aparte de `puntos.py` porque
# ahi la `consulta` es la DOCUMENTACION de como se cierra el hueco (va en la
# ficha que lee el auditor) y aqui es el SQL EJECUTABLE. Que sean dos cosas
# permite que la ficha explique y el script mida.
MEDICIONES: dict[str, tuple[str, str]] = {
    "V-01": ("periodos de plan de pago (todos los origin)", """
        select count(*) as total
        from aurumcore.iv_payment_plan p
        join aurumcore.account a on a.account_id = p.account_id
    """),
    "V-02": ("periodos de plan de pago de inversiones MIGRADAS", """
        select count(*) as total
        from aurumcore.iv_payment_plan p
        join aurumcore.account a on a.account_id = p.account_id
        where a.origin is not null
    """),
    "V-04": ("pagos de rendimiento VISTA del dia de proceso", """
        select count(*) as total
        from aurumcore.yield_dto y
        where y.iv_payment_plan_id is null
    """),
    "V-06": ("inversiones totales (denominador del GAT)", """
        select count(*) as total from aurumcore.iv_payment_plan
    """),
    "V-16": ("filas de amortizacion totales (con y sin IVA)", """
        select count(*) as total from aurumcore.lc_loan_amortization
    """),
    "V-17": ("contratos con tabla de amortizacion, y cuantos son FRENCH", """
        select count(distinct a.lc_contract_id) as total
        from aurumcore.lc_loan_amortization a
        join aurumcore.lc_loan_contract c on c.id = a.lc_contract_id
        where c.amortization_type = 'FRENCH'
    """),
    "V-19": ("filas del staging IFRS9 en etapa 3", """
        select count(*) as total
        from aurumcore.lc_finantial_data_stage
        where coalesce(capital_mora_days, 0) >= 90
    """),
    "V-21/22": ("dias contables disponibles en transaction_detail", """
        select count(distinct t.accounting_date) as total
        from aurumcore.transaction_detail t
    """),
    "V-23": ("padron completo de cuentahabientes", """
        select count(*) as total from aurumcore.accountholder
    """),
}


def main() -> int:
    pend = [p for p in PUNTOS if p.denominador.pendiente]
    print(f"Denominadores pendientes: {len(pend)} de {len(PUNTOS)} puntos\n")

    medibles = [p for p in pend if p.id in MEDICIONES]
    sin_sql = [p for p in pend if p.id not in MEDICIONES]

    resultados: dict[str, str] = {}
    for p in medibles:
        desc, sql = MEDICIONES[p.id]
        try:
            ex = extract.ejecutar("aurum", [sql], {}, archivo=f"denominador_{p.id}",
                                  max_filas=10)
            total = ex.principal.row(0)[0]
            resultados[p.id] = f"{total:,}"
            pct = p.denominador.pct(f"{total:,}")
            print(f"  {p.id:10} {desc}")
            print(f"             total = {total:>12,}   ->  n = {p.n_comparado:>10}  "
                  f"representatividad = {pct}")
        except Exception as exc:  # noqa: BLE001
            print(f"  {p.id:10} ERROR: {type(exc).__name__}: {str(exc)[:90]}")

    if sin_sql:
        print(f"\nSin SQL de medicion ({len(sin_sql)}) — el denominador no esta en la base "
              f"o requiere el otro core / los logs:")
        for p in sin_sql:
            print(f"  {p.id:10} {p.titulo}")
            print(f"             {p.denominador.consulta.strip()[:100]}")

    if resultados:
        print("\n--- Escribir en 60_informe/puntos.py ---")
        for pid, total in resultados.items():
            print(f'  {pid}:  Denominador(total="{total}", ...)')
        print("\nDespues: python 60_informe/generar.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
