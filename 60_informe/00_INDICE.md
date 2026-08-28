# Informe detallado de auditoria — indice

> Una ficha por punto de validacion, con **alcance, periodo, universo, representatividad, racional del subconjunto y santo y sena**. Responde a lo que el equipo de auditoria pidio en la sesion del 2026-08-28 y que el informe de alto nivel no traia.

> Complementa —no reemplaza— `40_validaciones/PAQUETE_AUDITOR_DATOS/01_TABLA_MAESTRA_VALIDACIONES.md`.

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
| **V-01** Rendimiento plazo fijo — motor vivo (origin IS NULL) | 530,195 periodos (157,999 cuentas) | [PEND] | [PEND] | 2026-08-20 | [ver](detalle/V-01.md) |
| **V-02** Rendimiento plazo fijo — migrado (origin = FINSUS) | 3,748 periodos (300 cuentas) | [PEND] | [PEND] | 2026-08-20 | [ver](detalle/V-02.md) |
| **V-03** Rendimiento vista — integridad de posteo (feed ↔ DB) | 30,769 pagos capturados en el feed | 38,921 | 79.06% | 2026-08-18 | [ver](detalle/V-03.md) |
| **V-04** Rendimiento vista — oraculo independiente | 20,000 pagos de rendimiento vista | [PEND] | [PEND] | 2026-08-28 | [ver](detalle/V-04.md) |
| **V-05** Saldo promedio (SPM) — barrido de logs | 90 filas (27 cuentas) | [PEND] | [PEND] | 2026-08-23 | [ver](detalle/V-05.md) |
| **V-06** GAT inversion (nominal / real) | 126,465 inversiones (term 7) | [PEND] | [PEND] | 2026-08-20 | [ver](detalle/V-06.md) |

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
| **V-16** Credito — IVA sobre interes | 54,716 filas con IVA | [PEND] | [PEND] | 2026-08-20 | [ver](detalle/V-16.md) |
| **V-17** Credito — AMORTIZACION (tabla francesa) | 794 contratos | [PEND] | [PEND] | 2026-08-20 | [ver](detalle/V-17.md) |
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

## Estado de la representatividad

**4 de 19** puntos declaran su denominador. Los **15** restantes lo tienen `[PEND]` **con la consulta que lo mide** — ver [00_BRECHAS.md](00_BRECHAS.md).

Declarar el hueco no lo cierra. Se lista para que se cierre, no para que se de por contestado.
