# -*- coding: utf-8 -*-
"""sanidad.py — el tablero se audita a si mismo (NORTE_SANIDAD.md, brief §12).

El principio del proyecto —cada validacion DEVUELVE LAS FILAS QUE VIOLAN LA
REGLA; 0 = pasa— aplicado al tablero y a cada numero que muestra.

Por que existe (la leccion de las cuatro recurrencias):

    Cada regla de FORMATO se termina cumpliendo FABRICANDO.
      "no pintes de verde lo que no corrio"  -> escondio cobertura buena tras un guion
      "ningun % sin escala"                  -> INVENTO una escala (CAT: 11.6% como "1e-8")

    Por eso aqui ningun invariante verifica que un campo ESTE; verifican que la
    afirmacion sea DERIVABLE DE LA FUENTE. Y el fallback cuando algo no se puede
    derivar es siempre un "no lo se" explicito ([PEND] / "sin escala declarada" /
    "sin cruce"), NUNCA un valor por defecto: un default es una mentira con la
    confianza de una etiqueta.

Diferencia deliberada con `comparadores/sanity_check.py` (la implementacion
canonica del lado de Finsus): alla el registro de claims esta ESCRITO A MANO con
el estado correcto esperado. Aqui los claims se DERIVAN de los
`resultados/<motor>.json` que el SPA realmente sirve, y la referencia se PARSEA
de `MATRIZ_TOLERANCIAS.md`. Auditar una transcripcion de lo que uno cree seria
el mismo error una vez mas: comprobaria que copie bien, no que el tablero diga
la verdad.

Uso:  python sanidad.py          (status por invariante + status global)
      python sanidad.py --json   (para el endpoint del SPA)
"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAIZ_SPA = Path(__file__).resolve().parent.parent          # auditor_spa/
RAIZ_REPO = RAIZ_SPA.parent                                 # repo/
RESULTADOS = RAIZ_SPA / "resultados"
MATRIZ = RAIZ_REPO / "40_validaciones" / "MATRIZ_TOLERANCIAS.md"

# --- Vocabulario de escalas -------------------------------------------------
# Una GRANULARIDAD es un umbral de |C-B|. `volumen`, `config` y `completitud`
# NO lo son: son otra clase de cobertura, y etiquetarlas como granularidad es
# justo el defecto que destapo CAT.
GRANULARIDADES = {"1e-8", "1e-5", "centavo"}
ESCALAS_VALIDAS = GRANULARIDADES | {"volumen", "config", "completitud", "doc", "caso"}

# Las formas explicitas de decir "no lo se". Ninguna es un valor.
PEND_MARCA = "[PEND]"
NO_SE = ("[PEND]", "sin escala declarada", "sin cruce", None, "")

# La cobertura declara de QUE clase es la evidencia; INV-H2 la usa para negarse
# a leer como granularidad un numero que no lo es.
COBERTURAS = {"datos", "volumen", "config", "completitud", "sin_cruce"}

# Que escala puede llevar el titular SEGUN la clase de evidencia. Un cruce a
# volumen no se lee "al 1e-8" y una identidad contable no tiene granularidad:
# la escala pertenece a la cobertura, no se elige.
ESCALAS_POR_COBERTURA = {
    "datos": GRANULARIDADES,
    "volumen": {"volumen"},
    "completitud": {"completitud"},
    "config": {"config"},
    "sin_cruce": set(),          # sin cruce no hay cifra que escalar
}


def es_numero(v) -> bool:
    """Un valor que un lector leeria como cifra. `[PEND]` no lo es."""
    return isinstance(v, str) and v not in NO_SE and any(c.isdigit() for c in v)


def _plano(s: str) -> str:
    s = s.lower()
    for a, b in (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")):
        s = s.replace(a, b)
    return s


# ---------------------------------------------------------------------------
# Referencia autoritativa: se PARSEA de MATRIZ_TOLERANCIAS.md
# ---------------------------------------------------------------------------
# Un dict de referencia hardcodeado seria el mismo pecado que INV-H3 castiga:
# un valor por defecto que nadie vuelve a cruzar contra la fuente. Si la matriz
# cambia, esto tiene que cambiar solo — o INV-C1 deja de probar nada.

# Lo unico declarado a mano es la correspondencia nombre-en-el-doc -> id del
# tablero. Es un hecho sobre el documento, no una cifra.
NOMBRE_A_ID = {
    "rendimiento plazo fijo": "PLAZO",
    "credito ordinario": "CRED-ORD",
    "credito moratorio": "CRED-MOR",
    "iva sobre interes": "CRED-IVA",
    "amortizacion": "AMORT",
    "gat inversion": "GAT",
    "cat": "CAT",
    "ifrs 9": "IFRS9",
    "isr retencion": "ISR",
    "rendimiento vista": "VISTA",
    "saldo promedio": "SALDO-PROM",
    "isr-vivo nativo": "ISR-VIVO",
}


def _celda(txt: str) -> str | None:
    """Normaliza una celda de la matriz a un porcentaje, o a None.

    Devuelve None cuando la celda NO es un porcentaje comparable (`n/a`,
    `exacto`, `3/3`, `[PEND]`). No inventa: si no hay cifra, no hay cifra.
    """
    t = re.sub(r"[*`]", "", txt).strip()
    t = re.sub(r"[¹²³⁴]", "", t)          # superindices de nota
    if not t or t.lower() in {"n/a", "—", "-"} or "PEND" in t:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", t)
    if not m:
        return None
    return f"{float(m.group(1)):.2f}"


def leer_matriz(ruta: Path = MATRIZ) -> dict:
    """Devuelve {id_motor: {'1e-8':…, '1e-5':…, 'centavo':…, 'n':…, 'sesgo':…}}.

    Solo lo que la matriz AFIRMA. Las celdas `[PEND]` / `n/a` / `exacto` quedan
    fuera: no son cifras que se puedan cruzar.
    """
    if not ruta.exists():
        return {}
    ref: dict[str, dict] = {}
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if not linea.startswith("|"):
            continue
        cols = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(cols) < 8:
            continue
        nombre = _plano(re.sub(r"[*`🔒◐]", "", cols[1])).strip()
        mid = next((v for k, v in NOMBRE_A_ID.items() if k in nombre), None)
        if not mid:
            continue
        fila: dict = {e: _celda(cols[i]) for i, e in ((2, "1e-8"), (3, "1e-5"), (4, "centavo"))}
        fila["n"] = re.sub(r"[*`¹²³⁴]", "", cols[5]).strip() or None
        # El marcador de nota al pie (`no¹`) no cambia el valor: es "no" con
        # una aclaracion abajo. Y un `[PEND]` en la columna de sesgo es un "no
        # lo se", no un valor contra el cual cotejar.
        sesgo = re.sub(r"[*`\[\]¹²³⁴]", "", cols[6]).strip()
        fila["sesgo"] = None if sesgo.upper() in {"", "PEND", "N/A"} else sesgo
        ref[mid] = fila
    return ref


# ---------------------------------------------------------------------------
# Claims: derivados del JSON que el SPA realmente sirve
# ---------------------------------------------------------------------------

def claim_de(d: dict) -> dict:
    """Traduce un `resultados/<motor>.json` al esquema de claim de NORTE_SANIDAD §7.

    Lee EXACTAMENTE lo que la tarjeta muestra (`pct_mostrado`, `pct_escala`,
    `cobertura`, `ejecutable`), no lo que deberia mostrar. Si esta funcion
    "arreglara" el claim al derivarlo, el chequeo se volveria decorativo.
    """
    cr = d.get("cruce") or {}
    local = cr.get("origen_resultado") == "corrida_local"

    escalas: dict[str, str] = {}
    # Una corrida SUPERADA por un corte declarado no manda las barras: el
    # titular es la cifra en firme, y mezclar las dos series haria que la
    # tarjeta se contradijera a si misma. La corrida sigue publicada aparte,
    # etiquetada como preview.
    superada = bool(cr.get("superada"))
    if local and not superada and cr.get("match"):
        for e in cr["match"].get("escalas", []):
            escalas[e["nombre"]] = e["pct"]
    dm = d.get("dossier_match") or {}
    for e in ("1e-8", "1e-5", "centavo", "volumen"):
        if e in dm and e not in escalas:
            escalas[e] = dm[e] if dm[e] else "[PEND]"
    # Las tres granularidades se declaran SIEMPRE que el motor sea de calculo:
    # omitir una es indistinguible de no tener el dato (INV-T2).
    if escalas and d.get("cobertura") in {"datos", "volumen"}:
        for e in GRANULARIDADES:
            escalas.setdefault(e, "[PEND]")

    if local and not superada:
        fuente = ("corrida local " + (cr.get("ejecutado") or "")).strip()
        n = cr.get("n_comparadas")
        s = (cr.get("sesgo") or {}).get("sesgo_detectado") if cr.get("sesgo") else None
        sesgo = None if s is None else ("si" if s else "no")
    elif d.get("dossier_pct"):
        fuente = "MATRIZ_TOLERANCIAS.md"
        n = dm.get("n")
        sesgo = dm.get("sesgo")
    else:
        # Un motor sin porcentaje NO es un motor sin procedencia: se contrasta
        # contra config, norma o doc, y la tarjeta muestra esa cita. Dejar el
        # campo vacio lo hacia leer como "de aqui no se sabe nada", que es el
        # mismo subreporte que el guion sobre una cobertura de config (§3.2).
        # Lo destapo correr `comparadores/sanity_check.py` contra estos claims:
        # su INV-H4 exige fuente en TODO claim, no solo en los que traen cifra.
        orden = {"config": 0, "norma": 1, "doc": 2, "inferencia": 3}
        citas = sorted(d.get("valida_contra") or [],
                       key=lambda f: orden.get(f["tipo"], 9))
        fuente = f"{citas[0]['tipo']}: {citas[0]['cita']}" if citas else None
        n = dm.get("n")
        sesgo = dm.get("sesgo")

    return {
        "motor": d["id"],
        "cobertura": d.get("cobertura"),
        "titular": {"escala": d.get("pct_escala"), "valor": d.get("pct_mostrado")},
        "escalas": escalas,
        "evidencia_config": d.get("evidencia_config") or "",
        "ejecutable": bool(d.get("ejecutable")),
        "caso": bool(d.get("caso_validador")),
        "feed": not d.get("depende_de_logs", False),
        "fuente": fuente,
        "n": n,
        "sesgo": sesgo,
        "calculado_aqui": local and not superada,
        "estado": d.get("estado"),
        "alcance": d.get("alcance"),
    }


def cargar_claims(carpeta: Path = RESULTADOS) -> list[dict]:
    claims = []
    for f in sorted(carpeta.glob("*.json")):
        if f.stem in {"indice", "conocimiento"}:
            continue
        claims.append(claim_de(json.loads(f.read_text(encoding="utf-8"))))
    return claims


# ---------------------------------------------------------------------------
# Los invariantes. Cada uno DEVUELVE las cards que lo violan.
# ---------------------------------------------------------------------------

INVARIANTES = {
    "INV-H1": "Escala obligatoria — todo numero mostrado lleva su escala explicita.",
    "INV-H2": "Escala verdadera — la escala esta respaldada y corresponde al valor; "
              "una granularidad no se cuelga de un numero que es volumen/config.",
    "INV-H3": "Prohibido el default fabricado — lo no derivable se dice, no se rellena.",
    "INV-H4": "Procedencia — todo numero dice de donde salio.",
    "INV-H5": "Titular = negocio — habiendo centavo, ese es el titular; el estricto no se esconde.",
    "INV-E1": "Verde solo con corrida — 'calculado aqui' exige n > 0.",
    "INV-E2": "Sin cruce no es pase — un motor sin datos ni config no muestra porcentaje.",
    "INV-E3": "Config se muestra — cobertura=config exhibe su evidencia, nunca un guion.",
    "INV-E4": "Boton honesto — 'Ejecutar' activo solo con caso ejecutable + insumo.",
    "INV-E5": "Alcance declarado — un % dice sobre que universo se calculo y cuanto representa; "
              "la representatividad no se inventa cuando el universo esta pendiente.",
    "INV-C1": "Misma cifra en todos lados — el % coincide con MATRIZ_TOLERANCIAS.md.",
    "INV-C2": "n y sesgo citados coinciden con la fuente.",
    "INV-C3": "No stale — una cifra citada no contradice en silencio una corrida mas reciente.",
    "INV-T1": "Cita o degrada — sin fuente, el numero baja a [PEND].",
    "INV-T2": "[PEND] visible — lo que falta se marca, no se rellena ni se omite.",
}


def revisar(claims: list[dict], ref: dict | None = None) -> list[dict]:
    """Devuelve la lista de violaciones: [{invariante, motor, detalle}]. Vacia = SANO."""
    ref = leer_matriz() if ref is None else ref
    V: list[dict] = []

    def v(inv, motor, detalle):
        V.append({"invariante": inv, "motor": motor, "detalle": detalle})

    for c in claims:
        m = c["motor"]
        esc_t, val_t = c["titular"]["escala"], c["titular"]["valor"]
        escs, cob = c["escalas"], c["cobertura"]

        # --- H1: ninguna cifra sin escala ---------------------------------
        if es_numero(val_t) and esc_t in NO_SE:
            dice = "" if esc_t is None else f" (dice: {esc_t!r})"
            v("INV-H1", m, f"el titular {val_t}% se muestra sin escala{dice}")

        # --- H2: la escala es verdadera, no supuesta ----------------------
        if esc_t is not None and esc_t not in ESCALAS_VALIDAS and esc_t not in NO_SE:
            v("INV-H2", m, f"escala '{esc_t}' fuera del vocabulario")
        if cob not in COBERTURAS:
            v("INV-H2", m, f"cobertura '{cob}' fuera del vocabulario")
        # La cobertura declara DE QUE CLASE es la evidencia; la escala del
        # titular tiene que pertenecer a esa clase. Es la forma general del
        # defecto de CAT: un cruce a volumen leido como precision aritmetica.
        if es_numero(val_t) and esc_t not in NO_SE:
            permitidas = ESCALAS_POR_COBERTURA.get(cob)
            if permitidas is not None and esc_t not in permitidas:
                v("INV-H2", m, f"titular etiquetado '{esc_t}' con cobertura '{cob}'; "
                               f"esa cobertura solo admite {'/'.join(sorted(permitidas))}")
        # el titular tiene que ser el valor que esa escala reporta
        if es_numero(val_t) and esc_t in escs and es_numero(escs[esc_t]) \
                and float(escs[esc_t]) != float(val_t):
            v("INV-H2", m, f"titular {val_t}@{esc_t} != escalas[{esc_t}]={escs[esc_t]}")
        # una escala afirmada sin valor detras no esta respaldada
        if es_numero(val_t) and esc_t in GRANULARIDADES and esc_t not in escs:
            v("INV-H2", m, f"titular etiquetado '{esc_t}' pero ese nivel no esta en las escalas")

        # --- H3: el fallback fabricado historico --------------------------
        # No se prueba "la cifra correcta": se prueba que ningun valor se haya
        # rellenado por defecto. La marca es una escala afirmada que la fuente
        # no respalda.
        if es_numero(val_t) and esc_t in GRANULARIDADES and cob == "volumen":
            v("INV-H3", m, f"cruce a volumen presentado con granularidad '{esc_t}' "
                           f"(el fallback fabricado que destapo CAT)")

        # --- H4: procedencia ----------------------------------------------
        # Se exige a TODO claim, no solo a los que traen cifra: un motor sin
        # porcentaje igual afirma algo ("validado contra la config real") y esa
        # afirmacion tambien tiene que decir de donde sale. Es el criterio de
        # `comparadores/sanity_check.py`, mas estricto que el que tenia aqui.
        if not c.get("fuente"):
            que = f"el {val_t}%" if es_numero(val_t) else "lo que afirma la tarjeta"
            v("INV-H4", m, f"{que} no declara de donde salio")

        # --- H5: el titular es el de negocio ------------------------------
        cent = escs.get("centavo")
        if es_numero(cent) and esc_t in GRANULARIDADES and esc_t != "centavo":
            v("INV-H5", m, f"hay cuadre al centavo ({cent}%) pero el titular es '{esc_t}'")

        # --- E1: verde solo con corrida -----------------------------------
        if c["calculado_aqui"] and not (isinstance(c["n"], int) and c["n"] > 0):
            v("INV-E1", m, f"dice 'calculado aqui' con n={c['n']!r}")

        # --- E2: sin cruce no es pase -------------------------------------
        if cob == "sin_cruce" and es_numero(val_t):
            v("INV-E2", m, f"cobertura 'sin_cruce' pero muestra {val_t}%")

        # --- E3: la config se exhibe --------------------------------------
        if cob == "config" and not c["evidencia_config"]:
            v("INV-E3", m, "cobertura 'config' sin evidencia_config que mostrar")

        # --- E4: el boton dice la verdad ----------------------------------
        if c["ejecutable"] and not (c["caso"] and c["feed"]):
            v("INV-E4", m, "boton 'Ejecutar' activo sin caso ejecutable o sin insumo")

        # --- E5: el alcance se declara ------------------------------------
        # Un porcentaje sin universo se lee con la cobertura que el lector le
        # suponga. El caso que lo motivo: PLAZO publicaba 100% y se leia como
        # "todo lo live", cuando el cohorte es el 39.6% de los periodos
        # live-pagados. El resultado no cambia; el denominador si.
        a = c.get("alcance")
        if es_numero(val_t):
            if not a:
                v("INV-E5", m, f"muestra {val_t}% y no declara su alcance")
            else:
                if not a.get("universo"):
                    v("INV-E5", m, "alcance sin universo declarado")
                if not a.get("representatividad"):
                    v("INV-E5", m, "alcance sin representatividad declarada")
                # Mismo criterio que INV-H3: si el universo no se conoce, la
                # representatividad NO se rellena con un numero.
                if a.get("universo", "").startswith(PEND_MARCA)                         and es_numero(a.get("representatividad", "")):
                    v("INV-E5", m, f"universo [PEND] pero publica representatividad "
                                   f"{a['representatividad']}")
        if a and a.get("no") == []:
            v("INV-E5", m, "declara alcance sin decir que queda FUERA")

        # --- C1 / C2: una cifra, un valor ---------------------------------
        r = ref.get(m, {})
        for e in GRANULARIDADES:
            mio, suyo = escs.get(e), r.get(e)
            if es_numero(mio) and suyo and not c["calculado_aqui"] \
                    and float(mio) != float(suyo):
                v("INV-C1", m, f"{e}: el tablero cita {mio}% y la matriz dice {suyo}%")
        if not c["calculado_aqui"] and r and c["sesgo"] and r.get("sesgo"):
            if _plano(str(c["sesgo"])) != _plano(str(r["sesgo"])):
                v("INV-C2", m, f"sesgo citado '{c['sesgo']}' != matriz '{r['sesgo']}'")

        # --- T1 / T2 -------------------------------------------------------
        if es_numero(val_t) and c["fuente"] in NO_SE:
            v("INV-T1", m, f"{val_t}% afirmado sin cita — deberia degradar a [PEND]")
        if cob in {"datos", "volumen"} and escs:
            faltan = sorted(e for e in GRANULARIDADES if e not in escs)
            if faltan:
                v("INV-T2", m, "granularidad(es) omitida(s) en vez de marcadas [PEND]: "
                               + ", ".join(faltan))

    return V


# ---------------------------------------------------------------------------
# INV-C3: cifras citadas contra corridas nuestras mas recientes
# ---------------------------------------------------------------------------

def avisos_upstream(claims: list[dict], ref: dict | None = None) -> list[dict]:
    """Filas donde NUESTRA corrida ya supero a la matriz.

    NO son violaciones del tablero: el tablero muestra la cifra fresca. Son un
    pendiente aguas arriba (la matriz sigue en [PEND]). Se listan aparte, y la
    regla de entrada es mecanica para que este cajon no sirva de escondite:
    solo entra lo que el tablero muestra MAS NUEVO que la fuente. Si el tablero
    mostrara lo viejo, seria INV-C3 y saldria como violacion.
    """
    ref = leer_matriz() if ref is None else ref
    out = []
    for c in claims:
        if not c["calculado_aqui"]:
            continue
        r = ref.get(c["motor"], {})
        if not r:
            continue
        pend = sorted(e for e in GRANULARIDADES
                      if r.get(e) is None and es_numero(c["escalas"].get(e)))
        if pend:
            corridos = ", ".join(f"{e}={c['escalas'][e]}%" for e in pend)
            out.append({
                "motor": c["motor"],
                "detalle": (f"la matriz trae [PEND] en {', '.join(pend)}; este tablero ya "
                            f"lo corrio ({corridos}). El tablero muestra lo mas nuevo; "
                            f"actualizar MATRIZ_TOLERANCIAS.md aguas arriba."),
            })
    return out


# ---------------------------------------------------------------------------
# Auto-prueba de falsabilidad: un invariante que no atrapa su bug esta vacio
# ---------------------------------------------------------------------------

def bugs_historicos() -> list[dict]:
    """Los dos enganos que ya ocurrieron en ESTE tablero, como claims."""
    return [
        # 1) CAT: 11.6% (cruce a VOLUMEN) etiquetado como granularidad 1e-8.
        {"motor": "CAT", "cobertura": "volumen",
         "titular": {"escala": "1e-8", "valor": "11.60"},
         "escalas": {"1e-8": "[PEND]", "1e-5": "[PEND]", "centavo": "[PEND]", "volumen": "11.60"},
         "evidencia_config": "", "ejecutable": False, "caso": False, "feed": True,
         "fuente": "MATRIZ_TOLERANCIAS.md", "n": None, "sesgo": None,
         "calculado_aqui": False, "estado": "parcial"},
        # 2) CRED-MOR: titular 81.10% (el estricto) ocultando el 95.70% al centavo.
        {"motor": "CRED-MOR", "cobertura": "datos",
         "titular": {"escala": "1e-8", "valor": "81.10"},
         "escalas": {"1e-8": "81.10", "1e-5": "[PEND]", "centavo": "95.70"},
         "evidencia_config": "", "ejecutable": False, "caso": False, "feed": True,
         "fuente": "MATRIZ_TOLERANCIAS.md", "n": "1,274", "sesgo": "no",
         "calculado_aqui": False, "estado": "validado"},
    ]


def autoprueba_falsabilidad(ref: dict | None = None) -> dict:
    cat, mor = bugs_historicos()
    v_cat = revisar([cat], ref)
    v_mor = revisar([mor], ref)
    cat_ok = any(x["invariante"] in {"INV-H2", "INV-H3"} for x in v_cat)
    mor_ok = any(x["invariante"] == "INV-H5" for x in v_mor)
    return {
        "casos": [
            {"bug": "CAT: 11.6% (cruce a volumen) etiquetado como granularidad 1e-8",
             "atrapado": cat_ok,
             "por": sorted({x["invariante"] for x in v_cat}) or None},
            {"bug": "CRED-MOR: titular 81.10% (1e-8) ocultando el 95.70% al centavo",
             "atrapado": mor_ok,
             "por": sorted({x["invariante"] for x in v_mor}) or None},
        ],
        "ok": cat_ok and mor_ok,
        "porque": ("Un invariante que no atrapa el engano que lo motivo no prueba nada. "
                   "Estos dos ya ocurrieron en este tablero."),
    }


# ---------------------------------------------------------------------------

def reporte(carpeta: Path = RESULTADOS) -> dict:
    ref = leer_matriz()
    claims = cargar_claims(carpeta)
    V = revisar(claims, ref)
    porinv: dict[str, list] = {}
    for x in V:
        porinv.setdefault(x["invariante"], []).append(x)
    return {
        "status": "SANO" if not V else "NO SANO",
        "n_violaciones": len(V),
        "n_motores": len(claims),
        "invariantes": [
            {"id": k, "afirma": t, "violaciones": porinv.get(k, []),
             "n": len(porinv.get(k, []))}
            for k, t in INVARIANTES.items()
        ],
        "violaciones": V,
        "avisos_upstream": avisos_upstream(claims, ref),
        "falsabilidad": autoprueba_falsabilidad(ref),
        "matriz_leida": sorted(ref),
        "regla": ("Verde global = 0 violaciones en TODOS los invariantes y TODOS los "
                  "motores. No hay 'casi sano'. El tablero no publica en NO SANO sin "
                  "mostrar las violaciones."),
    }


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Sanidad del tablero (NORTE_SANIDAD.md).")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    r = reporte()
    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
        return 0 if r["status"] == "SANO" and r["falsabilidad"]["ok"] else 1

    print("SANIDAD DEL TABLERO — NORTE_SANIDAD.md · invariante por invariante")
    print(f"  matriz de referencia: {len(r['matriz_leida'])} motores leidos de "
          f"MATRIZ_TOLERANCIAS.md")
    print(f"  claims derivados de resultados/: {r['n_motores']} motores\n")
    for inv in r["invariantes"]:
        marca = "ok   " if inv["n"] == 0 else f"{inv['n']:>3} X"
        print(f"  [{marca}] {inv['id']}  {inv['afirma']}")
        for x in inv["violaciones"]:
            print(f"           -> {x['motor']}: {x['detalle']}")
    print(f"\n  STATUS GLOBAL: {r['status']} ({r['n_violaciones']} violaciones)")
    if r["avisos_upstream"]:
        print("\n  Avisos aguas arriba (el tablero muestra lo MAS NUEVO; la fuente va atras):")
        for a in r["avisos_upstream"]:
            print(f"    - {a['motor']}: {a['detalle']}")
    print("\n  Auto-prueba de falsabilidad:")
    for c in r["falsabilidad"]["casos"]:
        marca = "SI" if c["atrapado"] else "NO"
        porque = ("  [" + ", ".join(c["por"]) + "]") if c["por"] else ""
        print(f"    {marca}  {c['bug']}{porque}")
    ok = r["status"] == "SANO" and r["falsabilidad"]["ok"]
    print(f"\n  RESULTADO: {'tablero sano y los invariantes son reales' if ok else 'REVISAR'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
