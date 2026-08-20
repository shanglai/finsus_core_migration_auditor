"""Hace importable `engine` y `oraculos` al correr pytest desde cualquier lado."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
