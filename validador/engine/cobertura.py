"""Manifiesto de cobertura — defensa anti-all-pass #3 (charter §5.3).

Regla que este modulo hace estructural: **NO-CORRIDO NO ES PASO.**

cobertura.md lista TODOS los casos del catalogo, no solo los que se corrieron.
Un caso sin corrida aparece como `NO-CORRIDO` con esas palabras, nunca en
blanco y nunca en verde. Es la defensa contra el tablero que se pinta completo
porque nadie miro lo que falta.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import catalogo as cat
from . import config, evidencia

# Como se lee cada resultado. El texto importa: es lo que Finsus va a leer.
LECTURA = {
    "SIN-VIOLACIONES": "corrido · cero violaciones",
    "VIOLACIONES": "corrido · CON VIOLACIONES",
    "SESGO": "corrido · SESGO DETECTADO (severidad 1)",
    "UNIVERSO-VACIO": "corrido · UNIVERSO VACIO (no prueba nada)",
    "BLOQUEADO": "NO-CORRIDO · bloqueado",
    "ERROR": "NO-CORRIDO · error de ejecucion",
    "DRY-RUN": "NO-CORRIDO · solo plan",
}

SIN_CORRIDA = "NO-CORRIDO · nunca ejecutado"


def _fila_estado(caso: cat.Caso, man: dict | None) -> tuple[str, str, str, str]:
    """(lectura, fecha, violaciones, evidencia)"""
    if not man:
        return SIN_CORRIDA, "—", "—", "—"
    global_ = man.get("resultado_global", "")
    lectura = LECTURA.get(global_, f"NO-CORRIDO · {global_ or 'desconocido'}")
    fecha = (man.get("ejecutado_en") or "—")[:10]
    res = man.get("resultado") or {}
    n = res.get("n_violaciones")
    viol = str(n) if n is not None else "—"
    ruta = man.get("_ruta", "")
    ev = Path(ruta).name if ruta else "—"
    return lectura, fecha, viol, ev


def generar(directorio_catalogo: Path | None = None,
            raiz_reportes: Path | None = None) -> str:
    """Genera el texto de cobertura.md."""
    casos = cat.cargar_todos(directorio_catalogo)
    ultimos = evidencia.ultimo_por_caso(raiz_reportes)
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")

    corridos = sum(1 for cid in casos if ultimos.get(cid, {}).get("resultado_global")
                   in ("SIN-VIOLACIONES", "VIOLACIONES", "SESGO"))
    con_hallazgo = sum(1 for cid in casos if ultimos.get(cid, {}).get("resultado_global")
                       in ("VIOLACIONES", "SESGO"))
    no_corridos = len(casos) - corridos

    L: list[str] = []
    L.append("# Cobertura del VALIDADOR — que se corrio, que no y que esta bloqueado")
    L.append("")
    L.append(f"> Generado: {ahora} · `python cli.py --cobertura`")
    L.append(">")
    L.append("> **NO-CORRIDO NO ES PASO.** Un caso que no se ejecuto no aporta cobertura y no")
    L.append("> puede pintarse verde en ningun tablero. Esta tabla existe para que la ausencia")
    L.append("> de evidencia sea tan visible como la evidencia (charter §5.3).")
    L.append("")
    L.append(f"**{corridos} de {len(casos)} casos corridos** · {con_hallazgo} con hallazgo · "
             f"{no_corridos} sin corrida util.")
    L.append("")

    L.append("| caso | motor | sev | estado catalogo | ultima corrida | fecha | violaciones | evidencia |")
    L.append("|---|---|---|---|---|---|---|---|")
    for cid in sorted(casos):
        c = casos[cid]
        lectura, fecha, viol, ev = _fila_estado(c, ultimos.get(cid))
        L.append(f"| **{c.id}** | {c.motor} | {c.severidad} | {c.estado} | {lectura} | "
                 f"{fecha} | {viol} | {ev} |")
    L.append("")

    # --- Detalle de lo bloqueado ------------------------------------------
    bloqueados = [c for c in casos.values() if not c.ejecutable]
    if bloqueados:
        L.append("## Casos que hoy NO se pueden correr (y por que)")
        L.append("")
        L.append("| caso | falta | pieza / pregunta abierta |")
        L.append("|---|---|---|")
        for c in sorted(bloqueados, key=lambda x: x.id):
            L.append(f"| {c.id} | {c.motivo_no_ejecutable()} | {', '.join(c.regla_ref)} |")
        L.append("")
        L.append("> Cada linea de esta tabla es un hueco de cobertura declarado. Cerrarlo exige")
        L.append("> un insumo (pieza de conocimiento, acceso, log o definicion), no mas codigo.")
        L.append("")

    # --- Hallazgos vivos ---------------------------------------------------
    hallazgos = [(cid, m) for cid, m in ultimos.items()
                 if m.get("resultado_global") in ("VIOLACIONES", "SESGO")]
    if hallazgos:
        L.append("## Hallazgos de la ultima corrida")
        L.append("")
        for cid, m in sorted(hallazgos):
            res = m.get("resultado") or {}
            L.append(f"### {cid} — {(m.get('caso') or {}).get('titulo', '')}")
            L.append("")
            L.append(f"- veredicto: **{m.get('resultado_global')}** · "
                     f"violaciones: **{res.get('n_violaciones')}** de {res.get('n_universo')} filas")
            if res.get("celda_dominante"):
                L.append(f"- celda dominante de la matriz A/B/C: `{res['celda_dominante']}`")
            if res.get("matriz"):
                L.append(f"- matriz: {res['matriz']}")
            sesgo = res.get("sesgo")
            if sesgo and sesgo.get("sesgo_detectado"):
                L.append(f"- **sesgo detectado** (p={sesgo.get('p_valor')}): {sesgo.get('nota')}")
            L.append(f"- evidencia: `{Path(m.get('_ruta', '')).name}`")
            L.append("")
        L.append("> Recordatorio (§7.3): **cada hallazgo confirmado se convierte en un invariante**")
        L.append("> permanente en `tests/`. La red de regresion solo crece.")
        L.append("")

    # --- Sincronia de indices ---------------------------------------------
    problemas = cat.verificar_sincronia(directorio_catalogo)
    L.append("## Sincronia de indices (§7.4)")
    L.append("")
    if problemas:
        L.append("Discrepancias entre los YAML y `manifest.yaml`:")
        L.append("")
        for p in problemas:
            L.append(f"- {p}")
    else:
        L.append("`catalogo/*.yaml` y `catalogo/manifest.yaml` estan sincronizados.")
    L.append("")
    L.append("Pendiente de sincronizar a mano: `40_validaciones/NORTE_VALIDACION.md` "
             "(misma nomenclatura y estado que este catalogo).")
    L.append("")
    return "\n".join(L)


def escribir(destino: Path | None = None, **kwargs) -> Path:
    destino = destino or (config.REPORTES / "cobertura.md")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(generar(**kwargs), encoding="utf-8")
    return destino
