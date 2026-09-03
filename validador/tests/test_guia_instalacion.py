# -*- coding: utf-8 -*-
"""La guia del grupo auditoria no puede separarse del catalogo.

Una guia con un parametro renombrado o una tolerancia caduca hace que quien la
siga obtenga un error en su primera corrida — y la primera corrida es donde se
gana o se pierde la confianza en la herramienta. Por eso esto se verifica
MECANICAMENTE contra el catalogo, no releyendo el documento.
"""

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
SCRIPT = RAIZ / "validador" / "tests" / "verifica_guia.py"


def test_la_guia_cuadra_con_el_catalogo():
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True,
                       text=True, timeout=120, cwd=str(RAIZ))
    assert r.returncode == 0, r.stdout + r.stderr


def test_el_verificador_sabe_fallar():
    """Un verificador que solo sabe decir OK no verifica nada.

    Se le da una guia con un parametro inventado y se exige que lo cace.
    """
    import re
    guia = (RAIZ / "GUIA_INSTALACION_GRUPO_AUDITORIA.md").read_text(encoding="utf-8")
    roto = guia.replace("| `umbral_constante` | entero |",
                        "| `umbral_inventado` | entero |", 1)
    assert roto != guia, "no se pudo inyectar el error; revisar la prueba"
    tmp = RAIZ / "GUIA_INSTALACION_GRUPO_AUDITORIA.md.tmp"
    original = (RAIZ / "GUIA_INSTALACION_GRUPO_AUDITORIA.md").read_text(encoding="utf-8")
    try:
        (RAIZ / "GUIA_INSTALACION_GRUPO_AUDITORIA.md").write_text(roto, encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True,
                           text=True, timeout=120, cwd=str(RAIZ))
        assert r.returncode != 0, "el verificador no caza un parametro inventado"
        assert "umbral_inventado" in r.stdout
    finally:
        (RAIZ / "GUIA_INSTALACION_GRUPO_AUDITORIA.md").write_text(original, encoding="utf-8")
        tmp.unlink(missing_ok=True)
