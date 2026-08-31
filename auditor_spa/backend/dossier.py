# -*- coding: utf-8 -*-
"""Base de conocimiento del agente conversacional.

Parte el DOSSIER (y los documentos de apoyo) en secciones citables y las
escribe como JSON para que el SPA las recupere sin servidor.

El agente NO inventa: responde con secciones REALES de estos documentos y
siempre dice de cual salio. Si la pregunta no tiene respaldo en el corpus, lo
dice y remite al SOL correspondiente. Un tablero de auditoria que improvisa
una explicacion vale menos que uno que calla.
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ_REPO = Path(__file__).resolve().parent.parent.parent
VAL = RAIZ_REPO / "40_validaciones"
CONOCIMIENTO = RAIZ_REPO / "10_conocimiento"

# Orden = prioridad de recuperacion. El DOSSIER manda.
DOCUMENTOS = [
    (VAL / "DOSSIER_MOTORES_ORACULO_C.md", "DOSSIER", "Dossier de motores (fuente principal)"),
    (VAL / "NORTE_VALIDACION.md", "NORTE", "Matriz maestra de cobertura"),
    (VAL / "INDICE_PRODUCTOS_PROCESOS.md", "INDICE", "Indice de productos y procesos"),
    (VAL / "COMPARACION_C_vs_DOC.md", "COMPARACION", "Comparacion C contra el documento"),
    (VAL / "SOLICITUDES_FINSUS.md", "SOLICITUDES", "Lo que esta bloqueado y quien lo desbloquea"),
    (VAL / "REFERENCIA_TABLAS_POR_CASO.md", "TABLAS", "Tablas, columnas y filtros por caso"),
    # La "tablita de significados" que el grupo auditoria pidio en la sesion del
    # 2026-08-28. El tablero la RENDERIZA desde aqui en vez de mantener una copia
    # de las definiciones: dos glosarios se separan, y el que manda es el del
    # bundle.
    (VAL / "GLOSARIO_ESTADOS_TABLERO.md", "GLOSARIO",
     "Que significa cada etiqueta del tablero"),
    (VAL / "NORTE_SANIDAD.md", "SANIDAD", "Invariantes falsables del propio tablero"),
    (VAL / "INFORME_DETALLADO_AUDITORIA/00_INDICE.md", "ALCANCE",
     "Alcance, universo y representatividad por punto"),
]

_RE_ENC = re.compile(r"^(#{1,3})\s+(.*)$")


def _secciones(texto: str, doc: str, titulo_doc: str) -> list[dict]:
    """Corta el documento por encabezados. Cada seccion es una unidad citable."""
    out, actual = [], None
    for i, linea in enumerate(texto.splitlines(), 1):
        m = _RE_ENC.match(linea)
        if m:
            if actual and actual["cuerpo"].strip():
                out.append(actual)
            actual = {"doc": doc, "titulo_doc": titulo_doc, "nivel": len(m.group(1)),
                      "titulo": m.group(2).strip(), "linea": i, "cuerpo": ""}
        elif actual is not None:
            actual["cuerpo"] += linea + "\n"
    if actual and actual["cuerpo"].strip():
        out.append(actual)
    return out


def construir() -> dict:
    secciones, faltantes = [], []
    for ruta, doc, titulo in DOCUMENTOS:
        if not ruta.exists():
            faltantes.append(str(ruta.relative_to(RAIZ_REPO)))
            continue
        secciones.extend(_secciones(ruta.read_text(encoding="utf-8"), doc, titulo))

    # Piezas K: la regla de cada motor. Solo el encabezado y el cuerpo inicial,
    # para no inflar el corpus del navegador.
    if CONOCIMIENTO.exists():
        for ruta in sorted(CONOCIMIENTO.rglob("K-*.md")):
            texto = ruta.read_text(encoding="utf-8")
            secciones.append({
                "doc": "PIEZA-K", "titulo_doc": "Pieza de conocimiento (la regla)",
                "nivel": 1, "titulo": ruta.stem, "linea": 1,
                "cuerpo": texto[:4000],
            })

    for s in secciones:
        s["cuerpo"] = s["cuerpo"].strip()
        # Texto plano para buscar sin acentos ni marcas de markdown.
        plano = re.sub(r"[`*_>|#\[\]]", " ", (s["titulo"] + " " + s["cuerpo"]).lower())
        for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
            plano = plano.replace(a, b)
        s["busqueda"] = re.sub(r"\s+", " ", plano)

    return {
        "secciones": secciones,
        "documentos_faltantes": faltantes,
        "nota": ("El agente responde SOLO con estas secciones y siempre cita de cual sale. "
                 "Si algo no esta aqui, lo dice y remite al SOL correspondiente en vez de "
                 "improvisar una explicacion."),
    }
