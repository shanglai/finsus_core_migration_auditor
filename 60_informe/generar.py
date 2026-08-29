# -*- coding: utf-8 -*-
"""Genera el informe DETALLADO de auditoria: un .md por punto de validacion.

    python 60_informe/generar.py

Escribe:
    60_informe/detalle/<ID>.md   una ficha por punto
    60_informe/00_INDICE.md      la tabla resumen con la representatividad
    60_informe/00_BRECHAS.md     TODO lo que sigue [PEND], con como cerrarlo

El generador NO redacta: toma lo declarado en `puntos.py` y lo formatea. Si un
campo falta, sale como hueco visible, no como texto de relleno. La regla dura
—ningun `n` sin denominador o sin la consulta que lo mediria— la verifica
`tests/test_informe.py`, no este archivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from puntos import PEND, PUNTOS, Punto  # noqa: E402

DESTINO = RAIZ / "detalle"

CABECERA = """> Ficha detallada del punto de validacion. Complementa
> `40_validaciones/PAQUETE_AUDITOR_DATOS/01_TABLA_MAESTRA_VALIDACIONES.md` (alto nivel).
> Generado por `60_informe/generar.py` — no editar a mano: editar `60_informe/puntos.py`.
"""


def _lista(items, vacio="—"):
    if not items:
        return vacio
    return "\n".join(f"- {x}" for x in items)


def _campo(v, vacio="—"):
    return v if v else vacio


def ficha(p: Punto) -> str:
    L = []
    A = L.append
    A(f"# {p.id} · {p.titulo}\n")
    A(CABECERA)
    A(f"| | |\n|---|---|")
    A(f"| **Familia** | {p.familia} |")
    A(f"| **Motores comparados** | {p.motores} |")
    A(f"| **Corte de datos** | {p.corte} |")
    A(f"| **Ejecutado (corrida)** | {p.ejecutado} |")
    A(f"| **Caso ejecutable en el validador** | "
      f"{'`' + p.caso_validador + '`' if p.caso_validador else 'no hay — este punto se cita del repo de validacion'} |")
    if p.solicitudes:
        A(f"| **Solicitudes abiertas** | {', '.join(p.solicitudes)} |")
    A("")

    A("## 1. Alcance\n")
    A("### Que SI se valida\n")
    A(p.que_se_valida + "\n")
    A("### Que NO se valida\n")
    A("Se declara explicitamente para que el resultado no se lea con mas cobertura de la "
      "que tiene.\n")
    A(_lista(p.que_NO_se_valida) + "\n")

    A("## 2. Periodo\n")
    A("| | |\n|---|---|")
    A(f"| **Ventana de datos** | {p.ventana_datos} |")
    A(f"| **Fecha de corte** | {p.corte} |")
    A(f"| **Cuando se corrio** | {p.ejecutado} |")
    A("\n> La fecha de corte es **con que datos** se valido; la de corrida es **cuando se "
      "ejecuto**. Pueden diferir y se reportan por separado.\n")

    A("## 3. Universo y representatividad\n")
    d = p.denominador
    A("| | |\n|---|---|")
    A(f"| **Comparado (n)** | **{p.n_comparado}** {p.unidad} |")
    A(f"| **De un total de** | {d.total} |")
    A(f"| **Segun que fuente** | {d.segun} |")
    A(f"| **Representatividad** | **{p.representatividad}** |")
    A(f"| **Conciliado contra** | {_campo(p.conciliacion)} |")
    A("")
    if d.nota:
        A(f"{d.nota}\n")
    if d.pendiente:
        A("> **Este denominador esta PENDIENTE.** Es la pregunta que la auditoria dejo "
          "abierta en la sesion del 2026-08-28 [00:32:35]: *\"cuanto representan esos items "
          "respecto del universo\"*. Se cierra con:\n")
        A(f"```sql\n{d.consulta}\n```\n")

    A("## 4. Racional del subconjunto\n")
    A("*Por que este recorte y no otro* — la otra mitad de lo que pidio la auditoria: "
      "*\"la metodologia con la que determinaron cuantos y por que\"*.\n")
    A(p.racional_subconjunto + "\n")

    A("## 5. Santo y sena — como se reproduce\n")
    A("| | |\n|---|---|")
    A(f"| **Tablas / fuentes** | {', '.join(f'`{t}`' for t in p.tablas)} |")
    A(f"| **Llave de comparacion** | `{p.llave}` |")
    A(f"| **Formula (motor C)** | `{p.formula}` |")
    A(f"| **Tolerancia** | {p.tolerancia} |")
    A(f"| **Oraculo** | `{p.oraculo}` |")
    if p.sql:
        A(f"| **SQL** | [`{p.sql}`](../../{p.sql}) |")
    A("")
    A("**Predicados exactos que definen el universo:**\n")
    A("```sql\n" + "\n".join(p.filtros) + "\n```\n")
    if p.reproducir and p.reproducir != PEND:
        A("**Reproducir:**\n")
        A(f"```bash\n{p.reproducir}\n```\n")

    A("## 6. Resultado\n")
    A(_campo(p.resultado) + "\n")
    if p.granularidades:
        A(f"**Cuadre por granularidad:** {p.granularidades}\n")
        A("> El **escalon** entre niveles es diagnostico: bajo a 1e-8 y alto al centavo = "
          "residuo sub-centavo (granularidad del snapshot, no defecto); bajo tambien al "
          "centavo = diferencia material. Ver `MATRIZ_TOLERANCIAS.md`.\n")
    if p.sesgo:
        A(f"**Prueba de signo:** {p.sesgo}\n")
    if p.no_conformes:
        A("**No conformes**"
          + (f" — clase `{p.clase_no_conforme}`" if p.clase_no_conforme else "") + ":\n")
        A(p.no_conformes + "\n")

    if p.contraste:
        A("## 7. Contraste con el informe detallado de Linko\n")
        A("> Este tablero es un tercero: donde su medicion y la del repo de "
          "validacion no coinciden, se dice — no se alinea en silencio.\n")
        A(p.contraste + "\n")

    A(f"## {8 if p.contraste else 7}. Lo que este punto NO concluye\n")
    if p.no_concluye:
        A("Los limites de la afirmacion. Un resultado leido fuera de estos limites dice "
          "mas de lo que la prueba soporta.\n")
        A(_lista(p.no_concluye) + "\n")
    else:
        A("— (sin limites adicionales declarados)\n")

    _n = 8 + (1 if p.contraste else 0)
    if p.bloqueo or p.insumo_requerido:
        A(f"## {_n}. Bloqueo — que hace falta y cuando\n")
        if p.bloqueo:
            A(f"**Que bloquea:** {p.bloqueo}\n")
        if p.insumo_requerido:
            A(f"**Insumo requerido:** {p.insumo_requerido}\n")

    A(f"## {_n + (1 if (p.bloqueo or p.insumo_requerido) else 0)}. Evidencia\n")
    A(_lista([f"`{e}`" for e in p.evidencia]) + "\n")
    A("---\n")
    A("*Verde no es dictamen. Cada validacion devuelve las filas que violan la regla; "
      "cero filas significa cero violaciones en ESTE universo, no que el motor este bien "
      "fuera de el. El dictamen lo emite el humano.*\n")
    return "\n".join(L)


def indice() -> str:
    L = ["# Reconciliacion del auditor — alcance y representatividad por punto\n"]
    L.append(
        "> **Que es esto.** El repo de validacion publico su "
        "`40_validaciones/INFORME_DETALLADO_AUDITORIA/` con los denominadores "
        "cerrados contra la base el 2026-08-28. Este documento es la vista del "
        "**tercero**: los mismos puntos con lo que ESTE tablero puede reproducir, y "
        "**donde las dos mediciones no coinciden, se dice**.\n")
    L.append(
        "> No reemplaza al informe de Linko ni al `PAQUETE_AUDITOR_DATOS/`. Aporta "
        "el contraste y los comandos para reproducir cada corrida desde este lado.\n")
    L.append("## Lo que este informe agrega\n")
    L.append(
        "| Pregunta de la sesion | Donde se contesta |\n|---|---|\n"
        "| *\"Cual fue el universo? Lo conciliaste contra algo?\"* [00:26:55] | §3 de cada ficha |\n"
        "| *\"4,091 contratos, de cuantos? Y segun quien?\"* [00:27:52] | §3 — denominador y fuente |\n"
        "| *\"La metodologia con la que determinaron cuantos y POR QUE\"* [00:32:35] | §4 racional |\n"
        "| *\"Cuanto representan esos items respecto del universo\"* [00:32:35] | §3 representatividad |\n"
        "| *\"Que es lo que se esta tomando... a que esta enfocada la prueba\"* [00:49:04] | §1 alcance |\n"
        "| *\"(bloqueados) que es lo que le hace falta\"* [00:52:11] | §8 bloqueo e insumo |\n")

    L.append("\n## Puntos\n")
    fam = None
    for p in PUNTOS:
        if p.familia != fam:
            fam = p.familia
            L.append(f"\n### {fam}\n")
            L.append("| Punto | n comparado | de un total de | representatividad | corte | ficha |")
            L.append("|---|---:|---:|---:|---|---|")
        L.append(f"| **{p.id}** {p.titulo} | {p.n_comparado} {p.unidad} | {p.denominador.total} "
                 f"| {p.representatividad} | {p.corte} | [ver](detalle/{_slug(p.id)}.md) |")

    contr = [p for p in PUNTOS if p.contraste]
    if contr:
        L.append("\n## Contrastes abiertos con el informe de Linko\n")
        L.append("Lo que un tercero aporta no es repetir la cifra: es decir "
                 "donde no cuadra.\n")
        for q in contr:
            L.append(f"### {q.id} · {q.titulo}\n")
            L.append(q.contraste + "\n")

    pend = [p for p in PUNTOS if p.denominador.pendiente]
    L.append(f"\n## Estado de la representatividad\n")
    L.append(f"**{len(PUNTOS) - len(pend)} de {len(PUNTOS)}** puntos declaran su denominador. "
             f"Los **{len(pend)}** restantes lo tienen `[PEND]` **con la consulta que lo "
             f"mide** — ver [00_BRECHAS.md](00_BRECHAS.md).\n")
    L.append("Declarar el hueco no lo cierra. Se lista para que se cierre, no para que se "
             "de por contestado.\n")
    return "\n".join(L)


def brechas() -> str:
    L = ["# Brechas del informe detallado — lo que sigue pendiente\n"]
    L.append("> Todo lo que este informe NO puede afirmar todavia, con **como se cierra**. "
             "Un pendiente sin instruccion de cierre se vuelve permanente.\n")

    pend = [p for p in PUNTOS if p.denominador.pendiente]
    L.append(f"## 1. Denominadores sin medir ({len(pend)} de {len(PUNTOS)} puntos)\n")
    L.append("Es la pregunta central de la auditoria [00:32:35]. Cada uno trae la consulta "
             "que lo cierra; todas son de solo lectura y de agregacion (no leen datos de "
             "cliente).\n")
    for p in pend:
        L.append(f"### {p.id} · {p.titulo}\n")
        L.append(f"Comparado **{p.n_comparado}** {p.unidad}, de un total **no declarado** "
                 f"segun {p.denominador.segun}.\n")
        if p.denominador.nota:
            L.append(f"{p.denominador.nota}\n")
        L.append(f"```sql\n{p.denominador.consulta}\n```\n")

    sin_conc = [p for p in PUNTOS if p.conciliacion in (PEND, "", None) or p.conciliacion.startswith("PEND")]
    L.append(f"\n## 2. Universos sin conciliar ({len(sin_conc)})\n")
    L.append("Un universo que solo se cuenta a si mismo confirma consistencia interna, no "
             "completitud.\n")
    for p in sin_conc:
        L.append(f"- **{p.id}** {p.titulo}")

    bloq = [p for p in PUNTOS if p.bloqueo or p.insumo_requerido]
    L.append(f"\n\n## 3. Puntos bloqueados por insumo ({len(bloq)})\n")
    for p in bloq:
        L.append(f"### {p.id} · {p.titulo}\n")
        L.append(f"**Bloquea:** {p.bloqueo}\n")
        L.append(f"**Se necesita:** {p.insumo_requerido}\n")

    muestreo = [p for p in PUNTOS if "[PEND]" in p.racional_subconjunto
                or "no esta declarado" in p.racional_subconjunto]
    if muestreo:
        L.append(f"\n## 4. Metodo de muestreo sin declarar ({len(muestreo)})\n")
        L.append("Sin el metodo, el porcentaje **no es extrapolable** al universo.\n")
        for p in muestreo:
            L.append(f"- **{p.id}** {p.titulo}")

    L.append("\n\n---\n")
    L.append("*Estas brechas son del informe, no del core. Ninguna de ellas es una "
             "desviacion de calculo: son cosas que todavia no se han medido o declarado.*\n")
    return "\n".join(L)


def _slug(pid: str) -> str:
    return pid.replace("/", "-")


def main() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for p in PUNTOS:
        (DESTINO / f"{_slug(p.id)}.md").write_text(ficha(p), encoding="utf-8")
    (RAIZ / "00_INDICE.md").write_text(indice(), encoding="utf-8")
    (RAIZ / "00_BRECHAS.md").write_text(brechas(), encoding="utf-8")
    pend = sum(1 for p in PUNTOS if p.denominador.pendiente)
    print(f"{len(PUNTOS)} fichas en {DESTINO}")
    print(f"  denominador declarado: {len(PUNTOS) - pend}/{len(PUNTOS)}")
    print(f"  indice:  {RAIZ / '00_INDICE.md'}")
    print(f"  brechas: {RAIZ / '00_BRECHAS.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
