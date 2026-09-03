# -*- coding: utf-8 -*-
"""Doble check de la guia CONTRA EL CATALOGO, no releyendola."""
import re
import sys
import pathlib

RAIZ = pathlib.Path(__file__).resolve()
REPO = pathlib.Path("C:/Users/L_User/Documents/projects/finsus_core_migration_auditor")
sys.path.insert(0, str(REPO / "validador"))
from engine import catalogo  # noqa: E402

guia = (REPO / "GUIA_INSTALACION_GRUPO_AUDITORIA.md").read_text(encoding="utf-8")
casos = catalogo.cargar_todos()
ejec = {k: c for k, c in casos.items() if c.ejecutable}

fallos = []


def chk(cond, msg):
    if not cond:
        fallos.append(msg)


# --- 1) conteos ---------------------------------------------------------------
chk(f"**{len(casos)} casos**" in guia,
    f"la guia no dice que hay {len(casos)} casos")
chk(f"**{len(ejec)} son ejecutables**" in guia,
    f"la guia no dice que {len(ejec)} son ejecutables")

# --- 2) todos los ejecutables documentados, y ninguno de mas ------------------
documentados = set(re.findall(r"^### `([A-Z0-9-]+)`", guia, re.M))
faltan = set(ejec) - documentados
sobran = documentados - set(ejec)
chk(not faltan, f"casos EJECUTABLES sin documentar: {sorted(faltan)}")
chk(not sobran, f"casos documentados que NO son ejecutables: {sorted(sobran)}")

# --- 3) cada parametro requerido aparece en la seccion de su caso ------------
sec = {}
partes = re.split(r"^### `([A-Z0-9-]+)`", guia, flags=re.M)
for i in range(1, len(partes), 2):
    # La seccion termina en el siguiente encabezado de cualquier nivel; si no se
    # acota, la ULTIMA se lleva todo el texto que sigue (incluida la tabla de
    # fallas) y el verificador reporta parametros que no estan ahi.
    cuerpo = partes[i + 1]
    corte = re.search(r"^#{1,3} ", cuerpo, re.M)
    sec[partes[i]] = cuerpo[:corte.start()] if corte else cuerpo

for cid, c in ejec.items():
    cuerpo = sec.get(cid, "")
    for p in c.parametros:
        chk(p.nombre in cuerpo, f"{cid}: falta el parametro {p.nombre!r} en la guia")
        if p.requerido:
            chk("requerido" in cuerpo.lower(),
                f"{cid}: {p.nombre} es requerido y la guia no marca ninguno como tal")
        elif p.default is not None:
            chk(str(p.default) in cuerpo,
                f"{cid}: el default de {p.nombre} ({p.default!r}) no aparece en la guia")
    # parametros inventados: nombres en backticks de la tabla que no existan
    tabla = re.findall(r"^\| `([a-z_]+)`", cuerpo, re.M)
    reales = {p.nombre for p in c.parametros} | {"fecha_ini", "fecha_fin"}
    for t in tabla:
        base = {"fecha_ini", "fecha_fin"} if t in ("fecha_ini", "fecha_fin") else {t}
        chk(t in reales, f"{cid}: la guia documenta {t!r}, que NO es parametro del caso")

# --- 4) las tolerancias que afirma ------------------------------------------
for cid, esperado in (("CONTABLE-B1", "0.00"), ("GAPB-IDNC", "0.00"),
                      ("ISR-03", "0.00"), ("ISR-02", "0.02"),
                      ("CAT-01", "0.01"), ("IFRS9-E3", "0.01"),
                      ("REND-PLAZO", "0.01"), ("REND-VISTA", "0.01")):
    real = str(ejec[cid].tolerancia.max_evento)
    chk(real == esperado, f"{cid}: tolerancia real {real}, la guia dice {esperado}")
    chk(esperado in sec.get(cid, ""), f"{cid}: la guia no menciona su tolerancia {real}")

# --- 5) los comandos de ejemplo son sintacticamente correctos ---------------
for cid, cuerpo in sec.items():
    cmds = re.findall(r"^python validador\\cli\.py --caso (\S+) (.*)$", cuerpo, re.M)
    chk(cmds, f"{cid}: no hay comando de ejemplo")
    for caso_cmd, resto in cmds:
        chk(caso_cmd == cid, f"{cid}: el ejemplo invoca --caso {caso_cmd}")
        chk("--confirmar" in resto, f"{cid}: el ejemplo no lleva --confirmar")
        pasados = set(re.findall(r"--param (\w+)=", resto))
        reales = {p.nombre for p in ejec[cid].parametros}
        inventados = pasados - reales
        chk(not inventados, f"{cid}: el ejemplo pasa parametros inexistentes {sorted(inventados)}")
        req = {p.nombre for p in ejec[cid].parametros
               if p.requerido and p.tipo not in ("lista_cuentas", "lista_llaves_of")}
        falta = req - pasados
        chk(not falta, f"{cid}: el ejemplo NO pasa los requeridos {sorted(falta)}")
        # cohortes
        for p in ejec[cid].parametros:
            if p.requerido and p.tipo == "lista_cuentas":
                chk("--cohorte-archivo" in resto, f"{cid}: falta --cohorte-archivo en el ejemplo")
            if p.requerido and p.tipo == "lista_llaves_of":
                chk("--cohorte-of-archivo" in resto,
                    f"{cid}: falta --cohorte-of-archivo en el ejemplo")

# --- 6) rutas y archivos que la guia cita ------------------------------------
for ruta in re.findall(r"python ([\w\\.]+\.py)", guia):
    chk((REPO / ruta.replace("\\", "/")).exists(), f"la guia invoca {ruta}, que no existe")
for doc in ("40_validaciones/MANUAL_USO_ORACULO_AUDITOR.md",
            "40_validaciones/ACCESO_Y_RED.md",
            "validador/db_connections.example.yaml",
            "requirements.txt"):
    chk((REPO / doc).exists(), f"la guia cita {doc}, que no existe")

# --- 7) que NO haya vuelto a colarse sintaxis que rompe en Windows -----------
for linea_n, linea in enumerate(guia.splitlines(), 1):
    if linea.startswith(("python ", "conda ", "copy ", ".venv", "cd ", "Get-CimInstance")):
        chk("&&" not in linea, f"linea {linea_n}: comando con && ({linea[:50]})")
        chk(not linea.startswith("cp "), f"linea {linea_n}: usa cp en vez de copy")

print(f"casos en catalogo: {len(casos)} · ejecutables: {len(ejec)}")
print(f"documentados en la guia: {len(documentados)}")
if fallos:
    print(f"\n{len(fallos)} PROBLEMAS:")
    for f in fallos:
        print(f"  - {f}")
    sys.exit(1)
print("\nsin discrepancias entre la guia y el catalogo")
