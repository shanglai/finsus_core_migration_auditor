"""Hace importable el backend del tablero al correr pytest."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
for p in (RAIZ / "backend", RAIZ.parent / "40_validaciones" / "comparadores",
          RAIZ.parent / "40_validaciones" / "entrega_finsus"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
