# Glosario de estados del tablero — qué significa cada etiqueta

> La "tablita de significados" del tablero/informe. Cada card lleva **cuatro ejes** que miden cosas distintas; juntos
> dicen exactamente en qué punto está cada validación. Ninguna etiqueta, por sí sola, dice "está mal". Linko · corte
> 2026-08-28. Ver `NORTE_SANIDAD.md` (invariantes) y `PROMPT_AUDITOR_SPA.md` §3 (despliegue).

## 1. ESTADO (la primera marca de la card)
| Etiqueta | Significado | Ojo |
|---|---|---|
| **Validado** | Regla + oráculo + **cruce corrido** + documentado. | — |
| **Parcial** | Mecánica/fórmula **confirmada** y ciertas validaciones hechas; **falta cerrar alcance** (ampliarlo). | **NO** es "match parcial" ni calidad menor. Ej.: IFRS 9 cuadra 100% y es *parcial* porque falta ampliar a comercio/reestructurado. |
| **Bloqueado** | Falta un **insumo externo** (p.ej. logs del cierre 31-ago, saldo base punto-en-tiempo). | No es defecto; es dependencia. |
| **Sin cruce** | La **fórmula está lista** pero **no se ha cruzado** contra datos todavía. | Se resuelve corriendo la ejecución. |

## 2. ORIGEN del número
| Etiqueta | Significado |
|---|---|
| **Calculado aquí** | Este tablero corrió el cruce (corrida local). |
| **Citado del dossier** | El número viene de una corrida del repo de validación (`MATRIZ_TOLERANCIAS.md`/DOSSIER); **este tablero NO lo recalculó**. |

## 3. COBERTURA (qué clase de evidencia)
| Etiqueta | Significado |
|---|---|
| **datos** | Se tomó un **cohorte/subconjunto** y se comparó **importe contra importe** en ese universo. |
| **volumen** | Cruce **1-a-1 masivo** (conteo/monto). *No es una granularidad de precisión.* |
| **config** | El oráculo **reproduce la tabla de configuración del propio core** (p.ej. `lc_reserve_ifrs` 37/37). Es la validación más fuerte: no depende de la cohorte. |
| **completitud** | Se valida **identidad exacta** (doble partida = $0.00) o que **no falte** una transacción (A ≥ B). |

## 4. ESCALA (a qué precisión cuadra el número)
| Etiqueta | Umbral | Qué prueba |
|---|---|---|
| **1e-8** | \|C−B\| ≤ 0.00000001 | Exactitud aritmética estricta (8 decimales) — el mismo cálculo, sin diferencia perceptible. |
| **1e-5** | ≤ 0.00001 | Precisión intermedia (5 decimales). |
| **centavo** | ≤ 0.01 | **Tolerancia de negocio** (2 decimales) — lo que le importa al cliente y a la contabilidad. **Es el titular.** |
| **[PEND]** | — | No computado a esa escala todavía (se llena al re-correr). **No se inventa.** |

> **Regla dura:** ningún porcentaje se muestra **sin su escala**. Un `81.10%` a secas hace pensar que el motor falla
> 1 de cada 5; con su escala se lee bien: `81.10% a 1e-8 → 95.70% al centavo` (el escalón es **granularidad del
> snapshot**, no defecto).

## 5. SESGO (prueba de signo)
Tendencia **sistemática** de las diferencias que caen fuera de 1e-8. **sí** = se cargan a un lado (candidato a
severidad 1 **si sobrevive** a descartar redondeo y precisión de base) · **no** = signo aleatorio (ruido de snapshot).

## 6. ALCANCE (qué se valida y qué NO)
Cada punto declara su **alcance** (qué toma / qué deja fuera), el **universo** y **cuánto representa** — en
`INFORME_DETALLADO_AUDITORIA/`. Ej.: plazo live = **censo del cohorte ≥2 pagos (~39.6% de los periodos live-pagados)**;
las cuentas de un pago quedan fuera **por metodología**, no por muestreo.

---

## Cómo leer una card (ejemplo completo)
```
CRÉDITO MORATORIO   [Parcial · Citado del dossier · datos]
  95.70%  al centavo        ← titular (tolerancia de negocio)
    1e-8     81.10%
    1e-5     [PEND]
    centavo  95.70%
  Escalón 81.10 → 95.70 = residuo sub-centavo (granularidad del snapshot), no defecto. Sesgo: no.
  Universo: 1,274 provisiones (censo del día 08-20). Este tablero NO lo recalculó.
```
- **Parcial** no significa que falle; significa que el alcance se puede ampliar. **95.70%** es la cifra de negocio.
  El **1e-8** no se esconde: va debajo. Y todo número dice **a qué escala** está y **de dónde salió**.
