"""Errores del VALIDADOR.

Regla de diseno: un error NUNCA se degrada a "paso". Cada excepcion de este
modulo termina escribiendo evidencia con resultado BLOQUEADO o ERROR, jamas
con resultado OK. Ver engine/runner.py y §5 del charter (NO all-pass).
"""


class ErrorValidador(Exception):
    """Raiz de todos los errores del VALIDADOR."""


class ReglaFaltante(ErrorValidador):
    """Falta la pieza de conocimiento (K) que sustenta el calculo.

    Se levanta cuando un caso no tiene oraculo implementable porque la regla
    no esta documentada en 10_conocimiento/. NO se inventa la regla: el caso
    queda BLOQUEADO y asi aparece en cobertura.md.
    """


class ExtraccionNoAcotada(ErrorValidador):
    """El SQL devolvio mas filas que el limite, o no declara su cota.

    Truncar en silencio seria peor que fallar: una muestra truncada se lee
    como universo completo.
    """


class SolaLecturaViolada(ErrorValidador):
    """Se detecto un verbo de escritura en un SQL del catalogo."""


class CatalogoInvalido(ErrorValidador):
    """Un YAML del catalogo no cumple el esquema de catalogo/_schema.md."""


class FloatEnDinero(ErrorValidador):
    """Se detecto una columna float en una columna monetaria.

    Todo calculo monetario va en decimal.Decimal. Un float en la ruta del
    dinero invalida la corrida completa.
    """


class ConexionNoConfigurada(ErrorValidador):
    """Falta db_connections.yaml o la entrada del core solicitado."""
