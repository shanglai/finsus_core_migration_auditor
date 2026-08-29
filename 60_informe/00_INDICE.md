# Reconciliacion del auditor — alcance y representatividad por punto

> **Que es esto.** El repo de validacion publico su `40_validaciones/INFORME_DETALLADO_AUDITORIA/` con los denominadores cerrados contra la base el 2026-08-28. Este documento es la vista del **tercero**: los mismos puntos con lo que ESTE tablero puede reproducir, y **donde las dos mediciones no coinciden, se dice**.

> No reemplaza al informe de Linko ni al `PAQUETE_AUDITOR_DATOS/`. Aporta el contraste y los comandos para reproducir cada corrida desde este lado.

## Lo que este informe agrega

| Pregunta de la sesion | Donde se contesta |
|---|---|
| *"Cual fue el universo? Lo conciliaste contra algo?"* [00:26:55] | §3 de cada ficha |
| *"4,091 contratos, de cuantos? Y segun quien?"* [00:27:52] | §3 — denominador y fuente |
| *"La metodologia con la que determinaron cuantos y POR QUE"* [00:32:35] | §4 racional |
| *"Cuanto representan esos items respecto del universo"* [00:32:35] | §3 representatividad |
| *"Que es lo que se esta tomando... a que esta enfocada la prueba"* [00:49:04] | §1 alcance |
| *"(bloqueados) que es lo que le hace falta"* [00:52:11] | §8 bloqueo e insumo |


## Puntos


### Captacion

| Punto | n comparado | de un total de | representatividad | corte | ficha |
|---|---:|---:|---:|---|---|
| **V-01** Rendimiento plazo fijo — motor vivo (origin IS NULL) | 530,195 periodos (157,999 cuentas) | 1,339,023 | 39.60% | 2026-08-20 | [ver](detalle/V-01.md) |
| **V-02** Rendimiento plazo fijo — migrado (origin = FINSUS) | 3,748 periodos (300 cuentas) | 32,986,518 | 0.01% | 2026-08-20 | [ver](detalle/V-02.md) |
| **V-03** Rendimiento vista — integridad de posteo (feed ↔ DB) | 30,769 pagos capturados en el feed | 38,921 | 79.06% | 2026-08-18 | [ver](detalle/V-03.md) |
| **V-04** Rendimiento vista — oraculo independiente | 20,000 pagos de rendimiento vista | [PEND] | [PEND] | 2026-08-28 | [ver](detalle/V-04.md) |
| **V-05** Saldo promedio (SPM) — barrido de logs | 90 filas (27 cuentas) | [PEND] | [PEND] | 2026-08-23 | [ver](detalle/V-05.md) |
| **V-06** GAT inversion (nominal / real) | 126,465 inversiones (term 7) | 706,600 | 17.90% | 2026-08-20 | [ver](detalle/V-06.md) |

### Fiscal

| Punto | n comparado | de un total de | representatividad | corte | ficha |
|---|---:|---:|---:|---|---|
| **V-07/08** ISR inversiones — join A/B/C completo y desviacion clasificada | 18,599 inversiones (14,913 clientes) | [PEND] | [PEND] | 2026-08-03 | [ver](detalle/V-07-08.md) |
| **V-09/10/11** ISR — reconciliacion al pago, devengo diario e insumo de saldo base | 728 dias-cliente (V-10); 2 pagos (V-09); 65 filas (V-11) | [PEND] | [PEND] | 2026-08-03 | [ver](detalle/V-09-10-11.md) |
| **V-12** ISR-vivo nativo (post-cutover) | [PEND] pagos | [PEND] | [PEND] | 2026-08-20 | [ver](detalle/V-12.md) |

### Credito

| Punto | n comparado | de un total de | representatividad | corte | ficha |
|---|---:|---:|---:|---|---|
| **V-13** Credito — interes ORDINARIO | 4,091 provisiones de interes ordinario | 5,365 | 76.25% | 2026-08-20 | [ver](detalle/V-13.md) |
| **V-14** Credito — interes MORATORIO | 1,274 provisiones de moratorio (692 con capital_venc) | 5,365 | 23.75% | 2026-08-20 | [ver](detalle/V-14.md) |
| **V-15** Credito — conteo de DIAS de devengo | 3 contratos (traza de log) | [PEND] | [PEND] | 2026-08-23 | [ver](detalle/V-15.md) |
| **V-16** Credito — IVA sobre interes | 54,716 filas con IVA | 55,636 | 98.35% | 2026-08-20 | [ver](detalle/V-16.md) |
| **V-17** Credito — AMORTIZACION (tabla francesa) | 794 contratos | 31,970 | 2.48% | 2026-08-20 | [ver](detalle/V-17.md) |
| **V-18** Credito — CAT (Costo Anual Total) | 4,225 contratos del estrato per-contrato | 31,866 | 13.26% | 2026-08-28 | [ver](detalle/V-18.md) |
| **V-19** IFRS 9 — etapas y porcentaje de reserva | 20,000 filas de staging en etapa 3 | [PEND] | [PEND] | 2026-08-28 | [ver](detalle/V-19.md) |

### Transaccional/Contable

| Punto | n comparado | de un total de | representatividad | corte | ficha |
|---|---:|---:|---:|---|---|
| **V-20** Motor B diario — completitud A vs B | 6 dias (21K-29K operaciones por dia) | [PEND] | [PEND] | 2026-08-18 | [ver](detalle/V-20.md) |
| **V-21/22** Contable — doble partida diaria y detalle transaccional | 7 dias (17K-220K asientos por dia) | [PEND] | [PEND] | 2026-08-16 | [ver](detalle/V-21-22.md) |

### Padron

| Punto | n comparado | de un total de | representatividad | corte | ficha |
|---|---:|---:|---:|---|---|
| **V-23** Cuentahabientes — WSO2 vs padron Aurum | 20 huerfanos Aurum -> WSO2 | [PEND] | [PEND] | 2026-08-20 | [ver](detalle/V-23.md) |

## Contrastes abiertos con el informe de Linko

Lo que un tercero aporta no es repetir la cifra: es decir donde no cuadra.

### V-01 · Rendimiento plazo fijo — motor vivo (origin IS NULL)

CORREGIDO CONTRA EL INFORME DE LINKO. La version anterior de esta ficha afirmaba cobertura completa de lo live. Es sobre-afirmacion —el problema-espejo en su direccion facil— y se corrige: ~39.6%, no 100%.

### V-04 · Rendimiento vista — oraculo independiente

NO SON COMPARABLES Y HAY QUE DECIRLO. Esta corrida es del CIERRE DE AGOSTO sobre una cota de 20,000 filas y da 96.62% al centavo. El informe de Linko reporta el CICLO DE JULIO como CENSO de 83,094 cuentas (~100% de los pagadores del ciclo, de 915,016 cuentas vista, la mayoria con interes 0) con 94.76% a 1e-8 y 95.03% al centavo, con `oraculo_vista_finsus_history.py`, base 360 y dt 31. Ciclos y universos distintos: ni se contradicen ni se promedian. Ademas `MATRIZ_TOLERANCIAS.md` mantiene VISTA en [PEND] A PROPOSITO porque se sella con el ciclo vivo del 31-ago; por eso el tablero muestra su cifra con fecha y nota y no como si cerrara el punto (INV-C3).

### V-18 · Credito — CAT (Costo Anual Total)

DISCREPANCIA MENOR ABIERTA: este tablero midio 31,866 contratos en `lc_loan_contract` el 2026-08-28 y el informe detallado de Linko dice 31,867. Un contrato de diferencia, casi seguro por el instante de la medicion. Se levanta en vez de alinearla en silencio: si las dos partes miden el mismo universo con un dia de diferencia y no coinciden, eso lo tiene que saber quien lee los dos documentos.


## Estado de la representatividad

**9 de 19** puntos declaran su denominador. Los **10** restantes lo tienen `[PEND]` **con la consulta que lo mide** — ver [00_BRECHAS.md](00_BRECHAS.md).

Declarar el hueco no lo cierra. Se lista para que se cierre, no para que se de por contestado.
