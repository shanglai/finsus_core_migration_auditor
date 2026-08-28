"""Hace importable el modulo del informe al correr pytest."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
for p in (RAIZ, RAIZ.parent / "validador"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
