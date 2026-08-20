# -*- coding: utf-8 -*-
"""VALIDADOR Independiente del motor C — interfaz de operacion.

Lo que Finsus opera. Con sus propios accesos, elige caso y parametros, puede
LEER cada consulta antes de que toque la base, y obtiene las violaciones mas
la ruta a la evidencia.

    python cli.py                             menu interactivo
    python cli.py --listar                    catalogo por motor, con estado
    python cli.py --explicar ISR-01           que valida, con que datos y como
    python cli.py --caso ISR-01 --dry-run     ensena el plan y el SQL, no conecta
    python cli.py --caso ISR-01 --confirmar   corre contra la BD (solo lectura)
    python cli.py --cobertura                 regenera reportes/cobertura.md
    python cli.py --autopruebas               corre la bateria sin BD

Por diseno, correr contra la base exige `--confirmar`. Sin esa bandera todo es
dry-run: es la misma doble validacion humana que ya usa fase1_isr_runner.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import catalogo as cat            # noqa: E402
from engine import cobertura, config, runner  # noqa: E402
from engine.errores import ErrorValidador     # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")   # consolas Windows (cp1252)
except Exception:  # noqa: BLE001
    pass

MARCA = {
    "VALIDADO": "[OK]", "PARCIAL": "[~]", "PENDIENTE": "[ ]",
    "BLOQUEADO": "[X]", "HALLAZGO": "[!]",
}


# ---------------------------------------------------------------------------
# Listado
# ---------------------------------------------------------------------------

def listar(casos: dict[str, cat.Caso]) -> None:
    print("\nCATALOGO DE CASOS — el catalogo es la fuente de verdad de QUE se valida\n")
    por_motor: dict[str, list[cat.Caso]] = {}
    for c in casos.values():
        por_motor.setdefault(c.motor, []).append(c)

    for motor in sorted(por_motor):
        print(f"  {motor}")
        for c in sorted(por_motor[motor], key=lambda x: x.id):
            marca = MARCA.get(c.estado, "[?]")
            corre = "ejecutable" if c.ejecutable else "SIN INSUMOS"
            print(f"    {marca} {c.id:16} sev{c.severidad}  {c.estado:10} {corre:12} {c.titulo}")
        print()

    ejec = sum(1 for c in casos.values() if c.ejecutable)
    print(f"  {ejec} de {len(casos)} casos tienen hoy con que correr.")
    print("  Los demas esperan un insumo (pieza de conocimiento, acceso, log o definicion),")
    print("  no mas codigo. Ver detalle con --explicar <ID> o --cobertura.\n")


# ---------------------------------------------------------------------------
# Explicacion de un caso (apartados a-e, auto-generados desde el YAML)
# ---------------------------------------------------------------------------

def explicar(caso: cat.Caso, params: dict | None = None) -> None:
    print(f"\n{'=' * 78}")
    print(f"{caso.id} — {caso.titulo}")
    print(f"{'=' * 78}")

    print("\n(a) QUE AFIRMA Y DE DONDE SALE LA REGLA")
    print(f"    identidad : {' '.join(caso.identidad.split())}")
    print(f"    sustento  : {', '.join(caso.regla_ref)}")
    print(f"    motor     : {caso.motor} · dominio {caso.dominio} · severidad {caso.severidad}")
    print(f"    estado    : {caso.estado}")
    if caso.cobertura_nota:
        print(f"    cobertura : {' '.join(caso.cobertura_nota.split())}")

    print("\n(b) DATOS: DE DONDE SALEN Y CON QUE LLAVES SE CRUZAN")
    for core, ruta in caso.extraccion.items():
        estado = "PENDIENTE — sin consulta" if str(ruta).upper() == cat.PENDIENTE else ruta
        print(f"    {core:8} : {estado}")
    print(f"    llaves   : {', '.join(caso.comparacion.llaves)}")
    print(f"    tipo     : {caso.comparacion.tipo}")
    if caso.comparacion.tipo == "igualdad_montos":
        print(f"    A (openfin) : {caso.comparacion.columna_a or '— sin motor A en este caso'}")
        print(f"    B ({caso.comparacion.fuente_b}) : {caso.comparacion.columna_b}")
        print(f"    C (oraculo) : {caso.comparacion.columna_c}")
    print(f"    oraculo  : {caso.oraculo}")

    print("\n(c) PARAMETROS")
    if not caso.parametros:
        print("    (ninguno)")
    for p in caso.parametros:
        req = "REQUERIDO" if p.requerido else "opcional "
        val = (params or {}).get(p.nombre, p.default)
        muestra = val if not isinstance(val, (list, tuple)) else f"<{len(val)} elementos>"
        print(f"    {req} {p.nombre:20} ({p.tipo}) = {muestra}")
        if p.nota:
            for linea in _envolver(p.nota, 66):
                print(f"              {linea}")

    print("\n(d) TOLERANCIA")
    t = caso.tolerancia
    print(f"    tipo {t.tipo} · maximo por evento {t.max_evento}")
    if t.prueba_sesgo:
        print(f"    prueba de signo OBLIGATORIA (alfa={t.alfa_sesgo}). Sesgo estadistico = severidad 1,")
        print("    aunque cada diferencia individual sea de un centavo.")
    else:
        print("    identidad exacta: no admite holgura.")

    print("\n(e) QUE SIGNIFICA EL RESULTADO")
    print(f"    matriz esperada : {' '.join(caso.matriz_esperada.split())}")
    print("    salida          : violaciones.parquet = las filas que NO cumplen la identidad.")
    print("    cero filas      = ningun evento del universo extraido viola la regla. NO significa")
    print("                      que el motor este bien fuera de ese universo, ni que los casos")
    print("                      no corridos pasen.")
    if not caso.ejecutable:
        print(f"\n    [X] HOY NO SE PUEDE CORRER: {caso.motivo_no_ejecutable()}")
    if caso.supuestos:
        print("\n    SUPUESTOS (viajan a la evidencia de cada corrida):")
        for s in caso.supuestos:
            for i, linea in enumerate(_envolver(s, 70)):
                print(f"      {'-' if i == 0 else ' '} {linea}")
    print()


def _envolver(texto: str, ancho: int) -> list[str]:
    palabras = " ".join(texto.split()).split(" ")
    lineas, actual = [], ""
    for p in palabras:
        if len(actual) + len(p) + 1 > ancho:
            lineas.append(actual)
            actual = p
        else:
            actual = f"{actual} {p}".strip()
    if actual:
        lineas.append(actual)
    return lineas


# ---------------------------------------------------------------------------
# Parametros desde la linea de comandos
# ---------------------------------------------------------------------------

def parsear_params(pares: list[str], archivo_cohorte: str | None,
                   archivo_cohorte_of: str | None) -> dict:
    params: dict = {}
    for par in pares or []:
        if "=" not in par:
            raise SystemExit(f"--param mal formado: {par!r}. Usar nombre=valor")
        k, v = par.split("=", 1)
        params[k.strip()] = v.strip()

    if archivo_cohorte:
        ruta = Path(archivo_cohorte)
        if not ruta.exists():
            raise SystemExit(f"No existe el archivo de cohorte: {ruta}")
        params["cohorte"] = [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines()
                             if l.strip() and not l.strip().startswith("#")]
    if archivo_cohorte_of:
        ruta = Path(archivo_cohorte_of)
        if not ruta.exists():
            raise SystemExit(f"No existe el archivo de cohorte OF: {ruta}")
        llaves = []
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            partes = [p.strip() for p in linea.replace(",", "-").split("-")]
            if len(partes) == 3 and all(p.isdigit() for p in partes):
                llaves.append(tuple(int(p) for p in partes))
        params["cohorte_of"] = llaves
    return params


# ---------------------------------------------------------------------------
# Corrida
# ---------------------------------------------------------------------------

def correr(caso: cat.Caso, params: dict, dry_run: bool, max_filas: int | None) -> int:
    explicar(caso, params)

    if dry_run:
        print("MODO SEGURO (dry-run): no se conecta a ninguna base.")
        print("Estas son las consultas EXACTAS que se enviarian:\n")

    corrida = runner.correr_caso(caso, overrides=params, dry_run=dry_run,
                                 max_filas=max_filas)

    if dry_run:
        for core, info in corrida.consultas.items():
            print(f"-- ===== {core} · {info.get('archivo')} =====")
            if info.get("error"):
                print(f"   [!] {info['error']}\n")
                continue
            for i, s in enumerate(info.get("statements") or [], 1):
                print(f"-- statement {i}")
                print(s.strip())
                print(";")
            if info.get("params"):
                print(f"-- parametros: {info['params']}")
            print()
        print(f"Estado del plan: {corrida.estado}")
        for a in corrida.advertencias:
            print(f"  [aviso] {a}")
        print("\nPara ejecutarlo contra la base agrega --confirmar.")
        return 0

    print(corrida.resumen_texto())

    if corrida.resultado and corrida.resultado.n_violaciones:
        print("\nVIOLACIONES (primeras 20):")
        import polars as pl
        with pl.Config(tbl_rows=20, fmt_str_lengths=40, tbl_cols=12):
            print(corrida.resultado.violaciones.head(20))

    if corrida.estado in ("BLOQUEADO", "ERROR"):
        print("\n  Recordatorio: NO-CORRIDO no es lo mismo que PASA. Este caso no aporta cobertura.")

    cobertura.escribir()
    print(f"\nCobertura actualizada: {config.REPORTES / 'cobertura.md'}")
    return 0 if corrida.estado in ("SIN-VIOLACIONES",) else 1


# ---------------------------------------------------------------------------
# Menu interactivo
# ---------------------------------------------------------------------------

def menu(casos: dict[str, cat.Caso]) -> int:
    listar(casos)
    ids = sorted(casos)
    print("Escribe el ID de un caso para ver su detalle (o Enter para salir).")
    try:
        eleccion = input("  caso> ").strip().upper()
    except (EOFError, KeyboardInterrupt):
        print()
        return 0
    if not eleccion:
        return 0
    if eleccion not in casos:
        print(f"  No existe el caso {eleccion!r}. Casos: {', '.join(ids)}")
        return 2
    explicar(casos[eleccion])
    print("Para correrlo:")
    print(f"  python cli.py --caso {eleccion} --dry-run")
    print(f"  python cli.py --caso {eleccion} --confirmar --param fecha_ini=2026-07-01 ...")
    return 0


# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="cli.py",
        description="VALIDADOR Independiente del motor C — auditor de AurumCore (solo lectura).",
    )
    ap.add_argument("--caso", help="id del caso a correr (ver --listar)")
    ap.add_argument("--listar", action="store_true", help="lista el catalogo por motor")
    ap.add_argument("--explicar", metavar="ID", help="explica un caso sin correrlo")
    ap.add_argument("--dry-run", action="store_true",
                    help="ensena el plan y las consultas sin tocar la base (default)")
    ap.add_argument("--confirmar", action="store_true",
                    help="CONECTA a la base en solo lectura. Requiere doble validacion humana.")
    ap.add_argument("--param", action="append", metavar="k=v",
                    help="sobreescribe un parametro del caso; se puede repetir")
    ap.add_argument("--cohorte-archivo", metavar="RUTA",
                    help="archivo con un account_number por linea")
    ap.add_argument("--cohorte-of-archivo", metavar="RUTA",
                    help="archivo con 'sucursal-rol-asociado' por linea (llave OpenFin)")
    ap.add_argument("--max-filas", type=int,
                    help="cota de filas por consulta; si se excede, la corrida ABORTA (no trunca)")
    ap.add_argument("--cobertura", action="store_true",
                    help="regenera reportes/cobertura.md y lo imprime")
    ap.add_argument("--autopruebas", action="store_true",
                    help="corre la bateria de tests (sin base de datos)")
    args = ap.parse_args(argv)

    if args.autopruebas:
        import subprocess
        return subprocess.call([sys.executable, "-m", "pytest", "-q"],
                               cwd=str(config.RAIZ))

    if args.cobertura:
        destino = cobertura.escribir()
        print(destino.read_text(encoding="utf-8"))
        print(f"\n-> {destino}")
        return 0

    try:
        casos = cat.cargar_todos()
    except ErrorValidador as exc:
        print(f"[X] Catalogo invalido: {exc}")
        return 2

    if args.listar:
        listar(casos)
        return 0

    if args.explicar:
        cid = args.explicar.upper()
        if cid not in casos:
            print(f"[X] No existe el caso {cid!r}. Ver --listar.")
            return 2
        explicar(casos[cid])
        return 0

    if not args.caso:
        return menu(casos)

    cid = args.caso.upper()
    if cid not in casos:
        print(f"[X] No existe el caso {cid!r}. Ver --listar.")
        return 2

    try:
        params = parsear_params(args.param, args.cohorte_archivo, args.cohorte_of_archivo)
    except SystemExit as exc:
        print(f"[X] {exc}")
        return 2

    # Sin --confirmar todo es dry-run: la conexion a produccion no se abre por descuido.
    dry = not args.confirmar
    if args.dry_run:
        dry = True

    try:
        return correr(casos[cid], params, dry_run=dry, max_filas=args.max_filas)
    except ErrorValidador as exc:
        print(f"\n[X] {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
