# -*- coding: utf-8 -*-
"""ORACULO CAT (motor C) — Costo Anual Total del credito.

REUSA `40_validaciones/comparadores/oraculo_cat.py` (autoprueba 3/3 contra los
ejemplos del doc, mas un caso real exacto de 35.1%) en vez de reescribir la
biseccion: dos implementaciones de la misma regla son dos cosas que pueden
divergir. Aqui solo vive el adaptador fila -> Decimal.

    CAT = la tasa anual i que iguala VP(disposicion) = VP(pagos)
          (Circular 21/2009 Banxico; doc "Calculos Motor de creditos" §8)

INDEPENDENCIA (§11.1). La FORMULA sale de la Circular, no del core. Lo que si
se lee del core son HECHOS DEL CONTRATO —monto, cronograma de pagos, comision
pactada—, que son insumos, no parametros de la regla. Leer del core el CAT para
"calibrar" el CAT seria circular; leer el monto del credito no lo es.

CONVENCIONES, Y COMO SE CONFIRMARON (§11.2 permite probar convenciones y
reportar cual ajusta: es no-circular porque no toca la formula).
Se despejo el `monto_recibido` IMPLICITO en el `cat` que guarda el core:

    recibido_implicito = pago / (1 + CAT/100) ^ (dias/360)

y se comparo contra el monto del credito. La diferencia salio entre 2% y 6% del
monto —el rango de las comisiones pactadas—, y en la subpoblacion donde la
comision configurada es la que se aplico, el CAT sale EXACTO. De ahi:

  * La comision de apertura se DESCUENTA de la disposicion. El core la marca
    `financed = 1`, pero los datos dicen que el cliente recibe el monto menos la
    comision. Se sigue el dato, y la discrepancia con la bandera se reporta.
  * Los dias corren desde `activation_date` hasta `demandable_date`.
  * El pago para CAT es capital + interes + seguros + otros, SIN IVA.
  * Base 360 (la de la Circular y la del oraculo del proyecto).

LO QUE NO SE PUEDE AFIRMAR TODAVIA (SOL-015). En una parte del universo la
comision implicita no coincide con la configurada. El caso lo
reporta como violacion —ocultarlo seria peor— pero clasificada `data-sourcing`:
falta saber que comision se COBRO de verdad, que no es la misma pregunta que si
la formula esta bien. La formula no esta en duda: 3/3 contra el doc.

PRECISION Y REDONDEO. `lc_loan_contract.cat` guarda DOS DECIMALES en las 4,224
filas del universo, asi que C se redondea half-up a dos decimales antes de
comparar — la convencion confirmada del proyecto (§11.2). Sin ese redondeo, la
prueba de signo marcaba sesgo (p = 0.0089) y con el desaparece
(p = 0.67, +1629/-1604): era medio centesimo en una sola direccion, defecto del
metodo y no del core. Con el redondeo puesto, los tres niveles miden algo real:
1e-8 y 1e-5 cuentan las coincidencias exactas al centesimo y el centavo admite
una unidad mas en el ultimo decimal.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

_COMPARADORES = Path(__file__).resolve().parents[2] / "40_validaciones" / "comparadores"
if str(_COMPARADORES) not in sys.path:
    sys.path.insert(0, str(_COMPARADORES))

from oraculo_cat import cat_frances  # noqa: E402

from engine.redondeo import aplicar  # noqa: E402

VERSION_REGLA = "C-006 / Circular 21/2009 Banxico + doc Motor de creditos §8"

D = lambda x: x if isinstance(x, Decimal) else Decimal(str(x))  # noqa: E731

BASE_DIAS = 360          # Circular 21/2009


def comision_apertura(monto: Decimal, pct, fija) -> Decimal:
    """Lo que se descuenta de la disposicion.

    Un monto fijo pactado gana al porcentaje cuando existe; si no hay ninguno,
    la comision es cero y el cliente recibe el monto completo. No se inventa un
    valor "tipico" cuando el contrato no declara comision.
    """
    f = D(fija or 0)
    if f > 0:
        return f
    p = D(pct or 0)
    return monto * p / D(100)


def monto_recibido(fila: dict) -> Decimal:
    monto = D(fila["monto"])
    return monto - comision_apertura(monto, fila.get("comision_pct"),
                                     fila.get("comision_fija"))


def flujos(fila: dict) -> list[tuple[Decimal, int]]:
    """[(pago sin IVA, dias desde la disposicion), ...], solo dias > 0.

    Un pago con `dias <= 0` no se descuenta: caeria en t=0 o antes, donde no es
    un pago futuro sino parte de la disposicion. Se excluye en vez de forzarlo.
    """
    pagos, dias = fila.get("pago_sin_iva") or [], fila.get("dias") or []
    return [(D(p), int(d)) for p, d in zip(pagos, dias) if d is not None and int(d) > 0]


def fila_cat(fila: dict, params: dict) -> Decimal:
    """Adaptador de CAT-01. Devuelve el CAT en % (Decimal)."""
    f = flujos(fila)
    recibido = monto_recibido(fila)
    if not f or recibido <= 0:
        # Sin flujo futuro o sin disposicion positiva no hay CAT que calcular.
        # Devolver 0 seria fabricar el mismo cero que este caso denuncia.
        raise ValueError(
            f"contrato {fila.get('contrato')}: sin flujo descontable "
            f"(pagos futuros={len(f)}, recibido={recibido})")
    # El core GUARDA el CAT con dos decimales (verificado: 4,224 de 4,224 filas
    # del universo). Comparar un C sin redondear contra un B redondeado mete un
    # sesgo de medio centesimo en una sola direccion — el paso 1 del playbook
    # (§11.3): antes de gritar defecto, redondear como el core.
    return aplicar(cat_frances(recibido, f), "Round2")


def comision_implicita(fila: dict) -> Decimal | None:
    """Diagnostico: que comision explicaria el `cat` que guarda el core.

    Se despeja el recibido de la identidad del CAT y se expresa como % del
    monto. Es lo que separa "la formula esta mal" de "no sabemos que comision
    se cobro": si la implicita es un porcentaje sensato y distinto del pactado,
    el motor no esta en duda — el insumo si. Mismo metodo que el porcentaje
    implicito del playbook de sesgo (§11.3, paso 2).

    Solo aplica al credito de un pago, donde la identidad se puede invertir en
    forma cerrada. Devuelve None en el resto.
    """
    f = flujos(fila)
    if len(f) != 1:
        return None
    pago, dias = f[0]
    monto, b = D(fila["monto"]), D(fila["cat_almacenado"])
    if monto <= 0 or dias <= 0 or b <= -100:
        return None
    recibido = pago / (1 + b / D(100)) ** (D(dias) / D(BASE_DIAS))
    return (monto - recibido) / monto * D(100)
