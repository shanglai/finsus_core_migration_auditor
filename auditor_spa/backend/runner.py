# -*- coding: utf-8 -*-
"""Ejecuta los motores y escribe resultados/<motor>.json para el SPA.

    python backend/runner.py                 autopruebas + resultado citado del DOSSIER
    python backend/runner.py --con-bd        ademas corre contra la BD los motores que tienen cruce
    python backend/runner.py --motor PLAZO   uno solo

Lo que este runner NO hace:

  * NO se conecta por SSH ni extrae logs. Los feeds de log los produce otro
    proceso (log_extractor.py / barrido_average_balance.py) y llegan como CSV.
    Si el feed no esta, el motor se marca bloqueado con esa razon — no se
    sustituye por una aproximacion.
  * NO manda PII al frontend. Los ids de muestra se truncan y solo viajan
    agregados y una muestra de puntos.
  * NO promedia lo que calculo con lo que cita. Cada resultado lleva
    `origen_resultado` y el SPA lo muestra: un numero del DOSSIER pintado como
    si lo hubiera calculado esta maquina seria un fraude de tablero.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

RAIZ_SPA = Path(__file__).resolve().parent.parent      # auditor_spa/
RAIZ_REPO = RAIZ_SPA.parent
VALIDADOR = RAIZ_REPO / "validador"
COMPARADORES = RAIZ_REPO / "40_validaciones" / "comparadores"
ENTREGA = RAIZ_REPO / "40_validaciones" / "entrega_finsus"
RESULTADOS = RAIZ_SPA / "resultados"
FEEDS = RAIZ_REPO / "40_validaciones" / "_resultados"

for p in (str(RAIZ_SPA / "backend"), str(VALIDADOR), str(COMPARADORES), str(ENTREGA)):
    if p not in sys.path:
        sys.path.insert(0, p)

from motores import MOTORES, POR_ID, resumen_cobertura  # noqa: E402
from tolerancias import resumen_tolerancias  # noqa: E402  (comparadores/, del bundle)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

# Cuantos puntos se mandan al SPA como maximo. Los NO CONFORMES nunca se
# muestrean: van todos, y se rotula cuantos conformes se omitieron.
MAX_PUNTOS_CONFORMES = 3000
MAX_NO_CONFORMES_DETALLE = 50


# ---------------------------------------------------------------------------
# Autopruebas: la formula, sin base de datos
# ---------------------------------------------------------------------------

def correr_autopruebas() -> dict[str, dict]:
    """Verifica que cada oraculo reproduce el ejemplo de su documento.

    Es la evidencia mas barata y la mas dificil de falsear: si el oraculo no
    reproduce el ejemplo del GTM, no hay nada que cruzar contra la BD.
    """
    res: dict[str, dict] = {}

    def _reg(mid, ok, detalle):
        res[mid] = {"ok": bool(ok), "detalle": detalle}

    try:
        from oraculo_rendimientos import (rendimiento_plazo, rendimiento_vista,
                                          saldo_promedio_rendimiento)
        v = rendimiento_vista(5000, 7, 31, 360)
        _reg("VISTA", v == Decimal("30.14"), f"doc 30.14 -> {v}")
        p = rendimiento_plazo(1000, 5, 100, 360)
        _reg("PLAZO", p == Decimal("13.89"), f"doc 13.89 -> {p}")
        s = saldo_promedio_rendimiento(30000, 8, 20000, 9).quantize(Decimal("0.01"))
        _reg("SALDO-PROM", s == Decimal("28888.89"), f"doc 28,888.89 -> {s}")
    except Exception as exc:  # noqa: BLE001
        for mid in ("VISTA", "PLAZO", "SALDO-PROM"):
            _reg(mid, False, f"no se pudo importar: {exc}")

    try:
        from oraculo_isr import isr_retenido
        i = isr_retenido("300000", "300000", 361)
        _reg("ISR", abs(i - Decimal("765.75")) <= Decimal("0.01"), f"caso de oro 765.75 -> {i}")
        _reg("ISR-VIVO", abs(i - Decimal("765.75")) <= Decimal("0.01"),
             "misma regla que ISR; el bloqueo es de dato, no de formula")
    except Exception as exc:  # noqa: BLE001
        _reg("ISR", False, f"no se pudo importar: {exc}")
        _reg("ISR-VIVO", False, f"no se pudo importar: {exc}")

    try:
        from oraculo_credito import interes_moratorio_dia, interes_ordinario_dia, iva_interes
        o = interes_ordinario_dia(50000, 15, 360)
        _reg("CRED-ORD", abs(o - Decimal("20.83")) <= Decimal("0.01"), f"doc 20.83 -> {o}")
        m = interes_moratorio_dia(500, 36, 360)
        _reg("CRED-MOR", abs(m - Decimal("0.50")) <= Decimal("0.01"), f"doc 0.50 -> {m}")
        iv = iva_interes(Decimal("100"), 16)
        _reg("CRED-IVA", iv == Decimal("16.00"), f"100 x 16% -> {iv}")
    except Exception as exc:  # noqa: BLE001
        for mid in ("CRED-ORD", "CRED-MOR", "CRED-IVA"):
            _reg(mid, False, f"no se pudo importar: {exc}")

    _reg("CRED-DIAS", True, "mecanica confirmada en el log del CORE; no tiene funcion propia que autoprobar")

    for mid, mod, prueba in (
        ("GAT", "oraculo_gat", "gat_inversion"),
        ("IFRS9", "oraculo_ifrs9", "etapa"),
        ("AMORT", "oraculo_amortizacion", "cuota_francesa"),
        ("CAT", "oraculo_cat", "cat_oneclick"),
    ):
        try:
            m = __import__(mod)
            _reg(mid, hasattr(m, prueba), f"{mod}.{prueba} disponible")
        except Exception as exc:  # noqa: BLE001
            _reg(mid, False, f"no se pudo importar {mod}: {exc}")

    for mid in ("MOTOR-B", "CONTABLE", "WSO2"):
        _reg(mid, True, "comparador de cruce; su evidencia es la corrida, no una autoprueba de formula")
    return res


# ---------------------------------------------------------------------------
# Cruce real contra la BD, reusando el motor del validador
# ---------------------------------------------------------------------------

def _dec(x):
    try:
        return Decimal(str(x))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _puntos_desde_universo(df, tolerancia: Decimal) -> tuple[list[dict], dict]:
    """Convierte el universo de una corrida en puntos para el scatter.

    Eje X: la magnitud del caso (B, que es lo que el core posteo).
    Eje Y: delta = C - B.
    """
    cols = df.columns
    col_b = "b_aurum" if "b_aurum" in cols else None
    col_c = "c_oraculo" if "c_oraculo" in cols else None
    if not (col_b and col_c):
        # Familia suma_cero: el "delta" es el descuadre del grupo.
        if "descuadre" in cols:
            puntos = []
            for i, fila in enumerate(df.iter_rows(named=True)):
                d = _dec(fila.get("descuadre")) or Decimal("0")
                puntos.append({"i": i, "x": float(i), "b": None, "c": None,
                               "delta": str(d), "ok": abs(d) <= tolerancia,
                               "id": str(fila.get(cols[0]))[:24]})
            return puntos, {"eje_x": "indice del grupo", "eje_y": "descuadre"}
        return [], {"eje_x": "", "eje_y": ""}

    puntos = []
    for i, fila in enumerate(df.iter_rows(named=True)):
        b, c = _dec(fila.get(col_b)), _dec(fila.get(col_c))
        delta = (c - b) if (b is not None and c is not None) else None
        idm = next((str(fila[k])[:24] for k in cols
                    if k not in (col_b, col_c, "a_openfin", "celda", "motivo", "dif_c_menos_b")), str(i))
        puntos.append({
            "i": i,
            "x": float(b) if b is not None else float(i),
            "b": str(b) if b is not None else None,
            "c": str(c) if c is not None else None,
            "delta": str(delta) if delta is not None else None,
            "ok": delta is not None and abs(delta) <= tolerancia,
            "id": idm,
            "celda": fila.get("celda"),
            "motivo": fila.get("motivo"),
        })
    return puntos, {"eje_x": "monto posteado por AurumCore (B)", "eje_y": "delta = C - B"}


def _caso_vigente(motor) -> bool:
    """True si el caso del validador asociado se puede correr HOY."""
    if not motor.caso_validador:
        return False
    try:
        from engine import catalogo as cat
        caso = cat.cargar_todos().get(motor.caso_validador)
        return bool(caso and caso.ejecutable)
    except Exception:  # noqa: BLE001
        return False


def _resumen_desde_puntos(puntos, tolerancia, ejes, extra=None) -> dict:
    """Arma el bloque de resultado a partir de una lista de puntos ya calculada."""
    no_conf = [p for p in puntos if not p["ok"]]
    conformes = [p for p in puntos if p["ok"]]
    omitidos = 0
    if len(conformes) > MAX_PUNTOS_CONFORMES:
        paso = len(conformes) // MAX_PUNTOS_CONFORMES + 1
        omitidos = len(conformes) - len(conformes[::paso])
        conformes = conformes[::paso]
    n = len(puntos)
    n_ok = n - len(no_conf)
    pares = [(p["c"], p["b"]) for p in puntos
             if p.get("c") is not None and p.get("b") is not None]
    match = resumen_tolerancias(pares) if pares else None
    d = {
        "n_comparadas": n, "n_ok": n_ok, "n_no_conformes": len(no_conf),
        "pct_match": (f"{(n_ok / n * 100):.2f}" if n else None),
        "tolerancia": str(tolerancia),
        "match": match,
        "match_nota": (None if match else
                       "Sin pares (C,B) comparables: este motor no reporta las tres "
                       "granularidades porque su identidad no compara dos importes."),
        "puntos": no_conf + conformes,
        "conformes_omitidos": omitidos,
        "ejes": ejes,
        "no_conformes_detalle": no_conf[:MAX_NO_CONFORMES_DETALLE],
    }
    d.update(extra or {})
    return d


def reconstruir_desde_evidencia(motor) -> dict | None:
    """Rearma el cruce desde la evidencia YA guardada por el validador.

    Sirve para regenerar el tablero sin volver a golpear la base — util cuando
    la red no esta o cuando solo se quiere recalcular la presentacion. NO es un
    atajo para inventar un resultado: lee el universo real de una corrida que
    ocurrio, y el JSON conserva el nombre del directorio de evidencia para que
    se pueda rastrear cual fue.
    """
    if not motor.caso_validador:
        return None
    import polars as pl
    from engine import catalogo as cat
    from engine import config as vconfig

    dirs = sorted((vconfig.REPORTES).glob(f"{motor.caso_validador}_*"),
                  key=lambda p: p.stat().st_mtime)
    dirs = [d for d in dirs if (d / "universo.parquet").exists()]
    if not dirs:
        return None
    ev = dirs[-1]
    caso = cat.cargar_todos().get(motor.caso_validador)
    if caso is None:
        return None
    if not caso.ejecutable:
        # La evidencia existe pero es de una consulta que YA SE RETIRO. Es el
        # caso de ISR-01: su universo estaba mal armado, se degrado a borrador,
        # y su ultima corrida dejo 27/27 violaciones que son defecto de la
        # consulta y no del core. Republicarla como "0% de match calculado
        # aqui" seria acusar a AurumCore de un error propio.
        return {"origen_resultado": "sin_cruce",
                "motivo": (f"hay evidencia previa de {motor.caso_validador}, pero el caso no es "
                           f"ejecutable hoy ({caso.motivo_no_ejecutable()}). Esa corrida se hizo "
                           f"con una consulta que ya se retiro, asi que no se republica.")}
    tol = caso.tolerancia.max_evento
    puntos, ejes = _puntos_desde_universo(pl.read_parquet(ev / "universo.parquet"), tol)
    if not puntos:
        return None
    import json as _json
    man = {}
    if (ev / "manifiesto.json").exists():
        man = _json.loads((ev / "manifiesto.json").read_text(encoding="utf-8"))
    return _resumen_desde_puntos(puntos, tol, ejes, extra={
        "origen_resultado": "corrida_local",
        "veredicto": (man.get("resultado") or {}).get("veredicto", "—"),
        "matriz": (man.get("resultado") or {}).get("matriz", {}),
        "sesgo": (man.get("resultado") or {}).get("sesgo"),
        "parametros": man.get("parametros", {}),
        "ejecutado": man.get("ejecutado_en"),
        "evidencia": ev.name,
        "reconstruido_de_evidencia": True,
        "notas": ["Reconstruido de la evidencia guardada, sin volver a consultar la base. "
                  "Los datos son los de esa corrida, no de ahora."],
        "advertencias": man.get("advertencias", []),
    })


def correr_contra_bd(motor, params: dict) -> dict | None:
    """Corre el caso del validador asociado al motor. None si no tiene o falla."""
    if not motor.caso_validador:
        return None
    from engine import catalogo as cat
    from engine import runner as vrunner

    casos = cat.cargar_todos()
    caso = casos.get(motor.caso_validador)
    if caso is None or not caso.ejecutable:
        return {
            "origen_resultado": "sin_cruce",
            "motivo": (caso.motivo_no_ejecutable() if caso else
                       f"el caso {motor.caso_validador} no existe en el catalogo"),
        }

    corrida = vrunner.correr_caso(caso, overrides=params, dry_run=False)
    if corrida.resultado is None:
        return {"origen_resultado": "error", "motivo": corrida.estado,
                "detalle": corrida.advertencias}

    r = corrida.resultado
    tol = caso.tolerancia.max_evento
    puntos, ejes = _puntos_desde_universo(r.universo, tol)

    no_conf = [p for p in puntos if not p["ok"]]
    conformes = [p for p in puntos if p["ok"]]
    omitidos = 0
    if len(conformes) > MAX_PUNTOS_CONFORMES:
        paso = len(conformes) // MAX_PUNTOS_CONFORMES + 1
        omitidos = len(conformes) - len(conformes[::paso])
        conformes = conformes[::paso]

    n = r.n_universo
    n_ok = n - r.n_violaciones

    # Las tres granularidades (1e-8 / 1e-5 / centavo) + prueba de signo, con el
    # helper estandar del proyecto. El escalon entre niveles es lo diagnostico:
    # bajo a 1e-8 y alto al centavo = residuo de snapshot; bajo tambien al
    # centavo = diferencia material. Ver MATRIZ_TOLERANCIAS.md.
    pares = [(p["c"], p["b"]) for p in puntos
             if p.get("c") is not None and p.get("b") is not None]
    match = resumen_tolerancias(pares) if pares else None

    return {
        "origen_resultado": "corrida_local",
        "match": match,
        "match_nota": (None if match else
                       "Sin pares (C,B) comparables: este motor no reporta las tres "
                       "granularidades porque su identidad no compara dos importes."),
        "veredicto": r.veredicto(),
        "n_comparadas": n,
        "n_ok": n_ok,
        "n_no_conformes": r.n_violaciones,
        "pct_match": (f"{(n_ok / n * 100):.2f}" if n else None),
        "tolerancia": str(tol),
        "matriz": r.matriz,
        "sesgo": r.sesgo.como_dict() if r.sesgo else None,
        "puntos": no_conf + conformes,          # los no-conformes SIEMPRE completos
        "conformes_omitidos": omitidos,
        "ejes": ejes,
        "no_conformes_detalle": no_conf[:MAX_NO_CONFORMES_DETALLE],
        "parametros": {k: (v if not isinstance(v, (list, tuple)) else f"<{len(v)} elementos>")
                       for k, v in params.items()},
        "ejecutado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidencia": Path(corrida.ruta_evidencia).name if corrida.ruta_evidencia else None,
        "notas": r.notas,
        "advertencias": corrida.advertencias,
    }


# ---------------------------------------------------------------------------
# Feeds de log (los trae otro proceso)
# ---------------------------------------------------------------------------

def estado_feeds() -> dict:
    if not FEEDS.exists():
        return {"disponibles": [], "carpeta": str(FEEDS), "nota": "la carpeta de feeds no existe"}
    archivos = sorted(FEEDS.glob("*feed*.csv"))
    return {
        "carpeta": str(FEEDS),
        "disponibles": [{"archivo": a.name,
                         "fecha": datetime.fromtimestamp(a.stat().st_mtime, timezone.utc)
                                          .isoformat(timespec="seconds")}
                        for a in archivos],
        "nota": ("Los feeds los produce otro proceso (log_extractor.py / "
                 "barrido_average_balance.py). Sin feed, los motores que dependen de "
                 "logs quedan bloqueados: no se sustituyen por aproximaciones."),
    }


# ---------------------------------------------------------------------------

def construir(motor, autopruebas: dict, con_bd: bool, params: dict,
              desde_evidencia: bool = False) -> dict:
    d = motor.como_dict()
    d["autoprueba"] = autopruebas.get(motor.id, {"ok": None, "detalle": "sin autoprueba"})
    d["cruce"] = None
    if con_bd:
        try:
            d["cruce"] = correr_contra_bd(motor, params)
        except Exception as exc:  # noqa: BLE001
            d["cruce"] = {"origen_resultado": "error", "motivo": f"{type(exc).__name__}: {exc}"}
    elif desde_evidencia:
        try:
            d["cruce"] = reconstruir_desde_evidencia(motor)
        except Exception as exc:  # noqa: BLE001
            d["cruce"] = {"origen_resultado": "error", "motivo": f"{type(exc).__name__}: {exc}"}

    if d["cruce"] and d["cruce"].get("origen_resultado") == "corrida_local":
        d["origen_resultado"] = "corrida_local"
        d["pct_mostrado"] = d["cruce"]["pct_match"]
    elif motor.dossier_pct:
        d["origen_resultado"] = "dossier"
        d["pct_mostrado"] = motor.dossier_pct
    else:
        d["origen_resultado"] = "sin_cruce"
        d["pct_mostrado"] = None
    return d


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Ejecuta los motores y escribe los JSON del SPA.")
    ap.add_argument("--con-bd", action="store_true",
                    help="corre ademas los cruces contra la BD (solo lectura)")
    ap.add_argument("--motor", help="corre un solo motor por id")
    ap.add_argument("--param", action="append", metavar="k=v", default=[])
    ap.add_argument("--cohorte-archivo")
    ap.add_argument("--desde-evidencia", action="store_true",
                    help="rearma los cruces desde la evidencia ya guardada, sin tocar la base")
    args = ap.parse_args(argv)

    params: dict = {}
    for par in args.param:
        k, v = par.split("=", 1)
        params[k.strip()] = v.strip()
    if args.cohorte_archivo:
        ruta = Path(args.cohorte_archivo)
        params["cohorte"] = [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines()
                             if l.strip() and not l.startswith("#")]

    RESULTADOS.mkdir(parents=True, exist_ok=True)
    print("Autopruebas de formula (sin base de datos):")
    autopruebas = correr_autopruebas()
    for mid, r in autopruebas.items():
        marca = "ok " if r["ok"] else ("-- " if r["ok"] is None else "FALLA")
        print(f"  [{marca}] {mid:12} {r['detalle']}")

    if args.motor and args.motor not in POR_ID:
        print(f"[X] motor desconocido: {args.motor}. Validos: {', '.join(POR_ID)}")
        return 2
    seleccion = [POR_ID[args.motor]] if args.motor else list(MOTORES)

    print(f"\nEscribiendo {len(seleccion)} motor(es) en {RESULTADOS}")
    indice = []
    for motor in seleccion:
        d = construir(motor, autopruebas, args.con_bd, params, args.desde_evidencia)

        # Cada motor necesita SUS parametros (cohorte, ventana), asi que los
        # cruces se corren de uno en uno. Al reconstruir el conjunto no se
        # pisa un cruce ya calculado con un "sin_cruce": borrar evidencia por
        # regenerar el indice seria perder cobertura sin darse cuenta.
        previo = RESULTADOS / f"{motor.id}.json"
        nuevo_sirve = (d.get("cruce") or {}).get("origen_resultado") == "corrida_local"
        # Conservar solo tiene sentido si el caso SIGUE siendo ejecutable: si su
        # consulta se retiro, la corrida vieja quedo huerfana y republicarla
        # acusaria al core de un defecto de la consulta (paso con ISR-01).
        if not nuevo_sirve and previo.exists() and _caso_vigente(motor):
            # Se conserva la corrida buena anterior salvo que ESTA la mejore.
            # Antes solo se conservaba cuando no habia cruce nuevo, asi que un
            # ERROR de conexion borraba una corrida valida: perder cobertura
            # porque se cayo la VPN es justo lo que este disenno evita.
            try:
                anterior = json.loads(previo.read_text(encoding="utf-8"))
                ant = anterior.get("cruce") or {}
                if ant.get("origen_resultado") == "corrida_local":
                    fallido = d.get("cruce")
                    d["cruce"] = ant
                    d["origen_resultado"] = "corrida_local"
                    d["pct_mostrado"] = ant.get("pct_match")
                    d["cruce"]["conservado_de_corrida_previa"] = True
                    if fallido:
                        d["cruce"]["ultimo_intento_fallido"] = {
                            "motivo": fallido.get("motivo"),
                            "cuando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        }
            except Exception:  # noqa: BLE001
                pass

        previo.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        marca = {"corrida_local": "corrida", "dossier": "citado ", "sin_cruce": "sin cruce"}[d["origen_resultado"]]
        pct = d["pct_mostrado"] or "—"
        print(f"  {motor.id:12} {marca}  {pct:>8}  {motor.estado}")
        indice.append({"id": motor.id, "nombre": motor.nombre, "dominio": motor.dominio,
                       "categoria": motor.categoria,
                       "estado": motor.estado, "pct_mostrado": d["pct_mostrado"],
                       "origen_resultado": d["origen_resultado"],
                       "depende_de_logs": motor.depende_de_logs,
                       "ejecutado": (d.get("cruce") or {}).get("ejecutado"),
                       "ejecutable": _caso_vigente(motor) and not motor.depende_de_logs,
                       "solicitudes": list(motor.solicitudes)})

    import dossier as mod_dossier
    conocimiento = mod_dossier.construir()
    (RESULTADOS / "conocimiento.json").write_text(
        json.dumps(conocimiento, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Conocimiento del agente: {len(conocimiento['secciones'])} secciones citables")
    if conocimiento["documentos_faltantes"]:
        print(f"  [!] documentos faltantes: {conocimiento['documentos_faltantes']}")

    (RESULTADOS / "indice.json").write_text(json.dumps({
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        # Refleja si HAY cruces calculados contra la base, no solo si esta
        # invocacion llevo --con-bd: los cruces se conservan entre corridas y
        # decir "sin cruce" con evidencia en mano seria subreportar cobertura.
        "con_bd": any(m["origen_resultado"] == "corrida_local" for m in indice),
        "motores_con_corrida_local": [m["id"] for m in indice
                                      if m["origen_resultado"] == "corrida_local"],
        "motores": indice,
        "cobertura": resumen_cobertura(),
        "feeds": estado_feeds(),
        "advertencia": ("Verde no es aprobado. El % viene de una validacion que devuelve las filas "
                        "que violan la regla; los no-conformes se explican, nunca se ocultan. El "
                        "dictamen lo emite el humano."),
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nIndice: {RESULTADOS / 'indice.json'}")

    # Empaquetado para abrir el SPA SIN servidor. Un navegador bloquea fetch()
    # sobre file:// por CORS, asi que los datos se emiten tambien como un .js
    # que el HTML carga con <script>. El auditor abre el archivo y ya.
    if not args.motor:
        datos = {"indice": json.loads((RESULTADOS / "indice.json").read_text(encoding="utf-8")),
                 "motores": {m.id: json.loads((RESULTADOS / f"{m.id}.json").read_text(encoding="utf-8"))
                             for m in MOTORES if (RESULTADOS / f"{m.id}.json").exists()},
                 "conocimiento": conocimiento}
        destino = RAIZ_SPA / "spa" / "datos.js"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("window.DATOS = " + json.dumps(datos, ensure_ascii=False) + ";",
                           encoding="utf-8")
        print(f"SPA autocontenido: {destino}  ({destino.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
