# -*- coding: utf-8 -*-
"""Servidor del tablero: sirve el SPA y ejecuta los motores bajo demanda.

    python backend/servidor.py           http://localhost:8777
    python backend/servidor.py --puerto 9000

Contrato del boton "Ejecutar" (el frontend nunca se bloquea):

    POST /api/run/<motor>   -> {"job_id": "...", "estado": "en_ejecucion"}
    GET  /api/job/<job_id>  -> {"estado": "en_ejecucion"|"terminado"|"error",
                                "avance": 0..100, "mensaje": "...", "motor": "..."}
    GET  /api/motores       -> el indice
    GET  /api/resultado/<m> -> el JSON de ese motor, ya refrescado

El trabajo corre en un hilo aparte y el frontend hace poll. Solo se admite UN
trabajo por motor a la vez: dos corridas simultaneas del mismo motor pelearian
por el mismo archivo de resultado.

Solo lectura contra la base: el servidor no toca la BD por su cuenta, delega en
runner.py, que a su vez delega en el motor del validador — donde la sesion se
abre `readonly=True` y se rechaza cualquier verbo de escritura antes de conectar.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import traceback
import uuid
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ_SPA = Path(__file__).resolve().parent.parent
SPA = RAIZ_SPA / "spa"
RESULTADOS = RAIZ_SPA / "resultados"
sys.path.insert(0, str(RAIZ_SPA / "backend"))

import runner  # noqa: E402
from motores import POR_ID  # noqa: E402

# job_id -> estado. En memoria: si el servidor se reinicia, los trabajos se
# pierden, y esta bien — el resultado real vive en resultados/<motor>.json.
JOBS: dict[str, dict] = {}
_LOCK = threading.Lock()
_EN_CURSO: set[str] = set()


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _ejecutar(job_id: str, motor_id: str, params: dict) -> None:
    """Corre un motor en segundo plano y va publicando el avance."""
    job = JOBS[job_id]
    try:
        motor = POR_ID[motor_id]
        job.update(estado="en_ejecucion", avance=10, mensaje="verificando la formula")
        autos = runner.correr_autopruebas()

        job.update(avance=35, mensaje="extrayendo de la base (solo lectura)")
        con_bd = bool(params.pop("_con_bd", True))
        d = runner.construir(motor, autos, con_bd=con_bd, params=params,
                             desde_evidencia=not con_bd)

        cruce = d.get("cruce") or {}
        if cruce.get("origen_resultado") == "error":
            job.update(estado="error", avance=100,
                       mensaje=f"la corrida fallo: {cruce.get('motivo')}",
                       terminado=_ahora())
            return

        job.update(avance=85, mensaje="escribiendo el resultado")
        RESULTADOS.mkdir(parents=True, exist_ok=True)
        (RESULTADOS / f"{motor_id}.json").write_text(
            json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

        n = cruce.get("n_comparadas")
        nc = cruce.get("n_no_conformes")
        resumen = (f"{n} comparadas · {nc} no conformes" if n is not None
                   else "sin cruce contra la base")
        job.update(estado="terminado", avance=100, terminado=_ahora(),
                   mensaje=resumen, pct=d.get("pct_mostrado"),
                   origen=d.get("origen_resultado"))
    except Exception as exc:  # noqa: BLE001
        job.update(estado="error", avance=100, terminado=_ahora(),
                   mensaje=f"{type(exc).__name__}: {exc}",
                   traza=traceback.format_exc()[-1200:])
    finally:
        with _LOCK:
            _EN_CURSO.discard(motor_id)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(SPA), **kw)

    def log_message(self, fmt, *args):  # menos ruido en consola
        if "/api/" in (args[0] if args else ""):
            super().log_message(fmt, *args)

    def _json(self, codigo: int, cuerpo: dict) -> None:
        datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(datos)

    # --- GET ---------------------------------------------------------------
    def do_GET(self):
        ruta = self.path.split("?")[0]
        if ruta.startswith("/api/job/"):
            job = JOBS.get(ruta.rsplit("/", 1)[-1])
            return self._json(200 if job else 404, job or {"error": "job desconocido"})
        if ruta == "/api/motores":
            f = RESULTADOS / "indice.json"
            return self._json(200 if f.exists() else 404,
                              json.loads(f.read_text(encoding="utf-8")) if f.exists()
                              else {"error": "corre runner.py primero"})
        if ruta.startswith("/api/resultado/"):
            f = RESULTADOS / f"{ruta.rsplit('/', 1)[-1]}.json"
            return self._json(200 if f.exists() else 404,
                              json.loads(f.read_text(encoding="utf-8")) if f.exists()
                              else {"error": "sin resultado"})
        return super().do_GET()

    # --- POST --------------------------------------------------------------
    def do_POST(self):
        ruta = self.path.split("?")[0]
        if not ruta.startswith("/api/run/"):
            return self._json(404, {"error": "ruta desconocida"})

        motor_id = ruta.rsplit("/", 1)[-1]
        if motor_id not in POR_ID:
            return self._json(404, {"error": f"motor desconocido: {motor_id}"})

        motor = POR_ID[motor_id]
        if not motor.caso_validador:
            return self._json(409, {
                "error": "sin cruce",
                "mensaje": (f"{motor.nombre} no tiene un caso ejecutable asociado: "
                            f"hay formula y autoprueba, pero nada que correr contra la base."),
            })
        if not runner._caso_vigente(motor):
            from engine import catalogo as _cat
            caso = _cat.cargar_todos().get(motor.caso_validador)
            return self._json(409, {
                "error": "caso no ejecutable",
                "mensaje": (f"{motor.nombre} tiene un caso asociado ({motor.caso_validador}) que HOY "
                            f"no se puede correr: {caso.motivo_no_ejecutable() if caso else 'no existe'}."),
            })
        if motor.depende_de_logs:
            return self._json(409, {
                "error": "bloqueado",
                "mensaje": (f"{motor.nombre} depende de un feed de logs que otro proceso produce. "
                            f"Sin el feed no se corre: sustituirlo por una aproximacion seria "
                            f"presentar una estimacion como validacion."),
            })

        with _LOCK:
            if motor_id in _EN_CURSO:
                return self._json(409, {"error": "ya en ejecucion",
                                        "mensaje": f"{motor_id} ya se esta corriendo."})
            _EN_CURSO.add(motor_id)

        largo = int(self.headers.get("Content-Length") or 0)
        params = {}
        if largo:
            try:
                params = json.loads(self.rfile.read(largo).decode("utf-8")) or {}
            except Exception:  # noqa: BLE001
                params = {}

        job_id = uuid.uuid4().hex[:12]
        JOBS[job_id] = {"job_id": job_id, "motor": motor_id, "estado": "en_ejecucion",
                        "avance": 0, "mensaje": "encolado", "iniciado": _ahora()}
        threading.Thread(target=_ejecutar, args=(job_id, motor_id, params),
                         daemon=True).start()
        return self._json(202, JOBS[job_id])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Servidor del tablero del auditor.")
    ap.add_argument("--puerto", type=int, default=8777)
    args = ap.parse_args(argv)

    if not (SPA / "index.html").exists():
        print(f"[X] no existe {SPA / 'index.html'}")
        return 2
    if not (RESULTADOS / "indice.json").exists():
        print("[!] no hay resultados todavia: corre `python backend/runner.py` primero")

    srv = ThreadingHTTPServer(("127.0.0.1", args.puerto), Handler)
    print(f"Tablero del auditor en http://localhost:{args.puerto}")
    print("  Ctrl+C para apagar.  Solo lectura contra la base.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\napagando")
    finally:
        srv.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
