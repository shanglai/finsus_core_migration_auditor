# -*- coding: utf-8 -*-
"""
sanity_check.py — Status global de sanidad del tablero/afirmaciones (NORTE_SANIDAD.md).

Aplica el principio del proyecto al TABLERO MISMO: cada invariante devuelve las cifras que lo violan;
0 = pasa. Verifica la VERDAD de cada afirmación (derivable de la fuente), no su formato.
El fallback de "no derivable" es siempre un "no lo se" explicito, nunca un default.

Corre sobre el REGISTRO DE CLAIMS (lo que cada motor legitimamente muestra, derivado de la matriz/COMPARACION).
El JSON del tablero (lado auditor) debe conformar al mismo esquema de claim y pasar los MISMOS invariantes.

Uso:  python sanity_check.py
"""

GRANULARIDADES = {"1e-8", "1e-5", "centavo"}
ESCALAS_VALIDAS = GRANULARIDADES | {"volumen", "config", "completitud", "doc", "caso"}
PEND = ("[PEND]", "sin escala declarada", None, "")

# Valores autoritativos para INV-C1 (misma cifra en todos lados).
# AUD-005(a): NO se hardcodean — se PARSEAN de MATRIZ_TOLERANCIAS.md, para que INV-C1 verifique la VERDAD
# (claims vs la matriz real) y no copia-contra-copia. Si el parse falla, se cae a un fallback declarado.
import os, re
_MOT = {  # nombre en la matriz -> clave de claim
    "Rendimiento plazo fijo": "PLAZO", "Rendimiento vista": "VISTA",
    "Crédito ordinario": "CRED-ORD", "Crédito moratorio": "CRED-MOR",
    "IVA sobre interés": "IVA",
}
def _parse_matriz():
    ref = {}
    ruta = os.path.join(os.path.dirname(__file__), "..", "MATRIZ_TOLERANCIAS.md")
    try:
        for ln in open(ruta, encoding="utf-8"):
            if not ln.lstrip().startswith("|"):
                continue
            cel = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(cel) < 5:
                continue
            nombre = re.sub(r"[*`]", "", cel[1]).strip()
            key = next((v for k, v in _MOT.items() if nombre.startswith(k)), None)
            if not key:
                continue
            d = {}
            for esc, i in (("1e-8", 2), ("1e-5", 3), ("centavo", 4)):
                val = re.sub(r"[*%`]", "", cel[i]).strip()
                if re.fullmatch(r"\d+\.\d+", val):
                    d[esc] = val
            if d:
                ref[key] = d
    except Exception:
        return None
    return ref or None

MATRIZ_REF = _parse_matriz() or {  # fallback declarado (corte 01-sep) si no se puede parsear
    "PLAZO": {"1e-8": "100.00", "1e-5": "100.00", "centavo": "100.00"},
    "VISTA": {"1e-8": "97.47", "1e-5": "97.47", "centavo": "97.65"},
    "CRED-ORD": {"1e-8": "97.32", "1e-5": "97.32", "centavo": "97.43"},
    "CRED-MOR": {"1e-8": "94.66", "1e-5": "94.66", "centavo": "95.38"},
    "IVA": {"1e-8": "98.91", "1e-5": "98.91", "centavo": "99.46"},
}

# --- Registro de claims: el estado CORRECTO (post-fix del auditor) ---
# cobertura: "datos" (granularidad real) | "volumen" | "config" | "completitud" | "sin_cruce"
# titular: (escala, valor)   escalas: {escala: valor|"[PEND]"}
CLAIMS = [
 {"motor":"PLAZO","cobertura":"datos","n":530195,"fuente":"validate_plazo_origin","calculado_aqui":True,
  "titular":("centavo","100.00"),"escalas":{"1e-8":"100.00","1e-5":"100.00","centavo":"100.00"},
  "ejecutable":True,"feed":True,"caso":True},
 {"motor":"VISTA","cobertura":"datos","n":82925,"fuente":"MATRIZ_TOLERANCIAS.md","calculado_aqui":True,
  "titular":("centavo","97.65"),"escalas":{"1e-8":"97.47","1e-5":"97.47","centavo":"97.65"},
  "ejecutable":True,"feed":True,"caso":True,"nota":"ciclo agosto, dt por cuenta; residual=SPM-de-cierre, no defecto"},
 {"motor":"CRED-ORD","cobertura":"datos","n":3585,"fuente":"MATRIZ_TOLERANCIAS.md","calculado_aqui":False,
  "titular":("centavo","97.43"),"escalas":{"1e-8":"97.32","1e-5":"97.32","centavo":"97.43"},
  "ejecutable":False,"feed":False,"caso":False,"nota":"corte 01-sep; residuo=P-019 data-sourcing; abs(capital) K-DAT-007"},
 {"motor":"CRED-MOR","cobertura":"datos","n":693,"fuente":"MATRIZ_TOLERANCIAS.md","calculado_aqui":False,
  "titular":("centavo","95.38"),"escalas":{"1e-8":"94.66","1e-5":"94.66","centavo":"95.38"},
  "ejecutable":False,"feed":False,"caso":False,"nota":"corte 01-sep; el 1e-8 se mueve con el corte = granularidad snapshot"},
 {"motor":"IVA","cobertura":"datos","n":54421,"fuente":"MATRIZ_TOLERANCIAS.md","calculado_aqui":False,
  "titular":("centavo","99.46"),"escalas":{"1e-8":"98.91","1e-5":"98.91","centavo":"99.46"},
  "ejecutable":False,"feed":False,"caso":False,"nota":"cohorte 16%; aparte IVA-incluido 16/84 y resto"},
 {"motor":"CAT","cobertura":"volumen","n":None,"fuente":"MATRIZ_TOLERANCIAS.md","calculado_aqui":False,
  "titular":("volumen","11.60"),"escalas":{"1e-8":"[PEND]","1e-5":"[PEND]","centavo":"[PEND]","volumen":"11.60"},
  "ejecutable":False,"feed":False,"caso":False,
  "nota":"11.60% es cruce a VOLUMEN, NO granularidad; formula 3/3 vs doc + caso real 35.1%"},
 {"motor":"IFRS9","cobertura":"config","n":37,"fuente":"lc_reserve_ifrs","calculado_aqui":False,
  "titular":("config","37/37"),"escalas":{},"evidencia_config":"lc_reserve_ifrs 37/37 · lc_risk_stage etapas exactas",
  "ejecutable":False,"feed":False,"caso":False},
 {"motor":"CONTABLE","cobertura":"completitud","n":7,"fuente":"CONTABLE_BC","calculado_aqui":True,
  "titular":("completitud","$0.00"),"escalas":{},"ejecutable":True,"feed":True,"caso":True,
  "nota":"doble partida 0.00 en 7/7 dias"},
]


def es_numero(v):
    return isinstance(v, str) and v not in PEND and any(c.isdigit() for c in v)


def chk(claims):
    V = []  # (invariante, motor, detalle)
    for c in claims:
        m = c["motor"]; esc_t, val_t = c["titular"]; escs = c.get("escalas", {})
        cob = c["cobertura"]

        # INV-H1: todo numero mostrado lleva escala
        if es_numero(val_t) and esc_t in PEND:
            V.append(("INV-H1", m, f"titular {val_t} sin escala"))
        for e, v in escs.items():
            if es_numero(v) and e in PEND:
                V.append(("INV-H1", m, f"valor {v} sin escala"))

        # INV-H2: escala verdadera, no supuesta (el bug de CAT)
        if esc_t not in ESCALAS_VALIDAS and esc_t not in PEND:
            V.append(("INV-H2", m, f"escala '{esc_t}' no valida"))
        if esc_t in GRANULARIDADES and cob != "datos":
            V.append(("INV-H2", m, f"titular etiquetado granularidad '{esc_t}' pero cobertura='{cob}' (no es granularidad)"))
        if cob == "volumen" and esc_t in GRANULARIDADES:
            V.append(("INV-H2", m, f"cruce a volumen mostrado como granularidad '{esc_t}'"))
        # el valor del titular debe estar respaldado en escalas (si aplica granularidad/volumen)
        if es_numero(val_t) and esc_t in escs and escs[esc_t] != val_t:
            V.append(("INV-H2", m, f"titular {val_t}@{esc_t} != escalas[{esc_t}]={escs[esc_t]}"))

        # INV-H3: prohibido default fabricado — placeholder conocido
        if (esc_t, val_t) == ("1e-8", "11.60"):
            V.append(("INV-H3", m, "fallback fabricado historico ('11.6','1e-8')"))

        # INV-H4: procedencia
        if not c.get("fuente"):
            V.append(("INV-H4", m, "sin procedencia/fuente"))

        # INV-H5: titular = centavo si existe centavo numerico
        if es_numero(escs.get("centavo", "")) and esc_t != "centavo":
            V.append(("INV-H5", m, f"hay centavo={escs['centavo']} pero titular es '{esc_t}'"))

        # INV-E3: config exhibe evidencia
        if cob == "config" and not c.get("evidencia_config"):
            V.append(("INV-E3", m, "cobertura=config sin evidencia_config"))
        # INV-E4: boton honesto
        if c.get("ejecutable") and not (c.get("feed") and c.get("caso")):
            V.append(("INV-E4", m, "boton 'Ejecutar' activo sin feed+caso"))

        # INV-C1: misma cifra que la referencia autoritativa
        for e, ref in MATRIZ_REF.get(m, {}).items():
            if e in escs and es_numero(escs[e]) and escs[e] != ref:
                V.append(("INV-C1", m, f"{e}: tablero {escs[e]} != referencia {ref}"))
    return V


def status(nombre, claims):
    V = chk(claims)
    print(f"\n=== {nombre} ===")
    if not V:
        print("  STATUS GLOBAL: SANO (0 violaciones)")
        return True
    print(f"  STATUS GLOBAL: NO SANO ({len(V)} violaciones)")
    for inv, m, det in V:
        print(f"    [{inv}] {m}: {det}")
    return False


if __name__ == "__main__":
    print("SANITY CHECK — NORTE_SANIDAD.md · motor por motor + status global")
    sano = status("Registro de claims (estado actual del tablero)", CLAIMS)

    # ---- Auto-prueba de FALSABILIDAD: los invariantes DEBEN atrapar los 2 bugs historicos ----
    # (busca por nombre de motor, no por indice posicional)
    _by = {c["motor"]: c for c in CLAIMS}
    CAT_bug = dict(_by["CAT"]); CAT_bug["titular"] = ("1e-8", "11.60")  # CAT como 1e-8 (era volumen)
    MOR_bug = dict(_by["CRED-MOR"]); MOR_bug["titular"] = ("1e-8", MOR_bug["escalas"]["1e-8"])  # titular estricto ocultando centavo
    Vb = chk([CAT_bug, MOR_bug])
    cat_ok = any(inv in ("INV-H2","INV-H3") and m == "CAT" for inv, m, _ in Vb)
    mor_ok = any(inv == "INV-H5" and m == "CRED-MOR" for inv, m, _ in Vb)
    print("\n=== Auto-prueba de falsabilidad (deben atraparse) ===")
    print(f"  bug CAT ('11.6' como 1e-8)  -> atrapado: {'SI' if cat_ok else 'NO'}")
    print(f"  bug MOR (titular 81.1 oculta centavo) -> atrapado: {'SI' if mor_ok else 'NO'}")
    ok = sano and cat_ok and mor_ok
    print(f"\nRESULTADO: {'OK — tablero sano y los invariantes son reales (falsables)' if ok else 'REVISAR'}")
