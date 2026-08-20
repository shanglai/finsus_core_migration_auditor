# Catálogo de Validaciones

Cada validación es una consulta que **devuelve las filas que violan la identidad**. Cero filas =
pasa. Nunca un total para comparar a ojo (CLAUDE.md §10).

Familias (orden de ejecución):
- **A** — Detalle consigo mismo (rollforward, unicidad de folios, reversas, signos, traspasos).
- **B** — Balanza consigo misma (doble partida, rollforward contable, continuidad, naturaleza).
- **C** — Amarre auxiliar ↔ balanza (stock y flujo por producto/movimiento-día, cuentas puente).
- **D** — Cross-motor (misma identidad en A/B/C; igualdad del **conjunto** de violaciones).

Tolerancias:
- Identidades contables (B y C): **0.00, sin excepción**.
- Cálculos con redondeo (devengo): `≤ $0.01 por evento` **y ausencia de sesgo** (prueba de signo;
  sesgo ≠ 0 estadísticamente = severidad 1).

Estado: **poblado** (2026-08-20) — las validaciones viven ahora como **casos ejecutables**
en `validador/catalogo/`, un YAML por caso.

> **Este documento ya no es la fuente de verdad de las validaciones; el catálogo lo es.**
> Cada caso declara ahí su identidad, su pieza `K-*`, su severidad, su tolerancia, su
> extracción y su oráculo, y el motor ejecuta exactamente lo declarado. Mantener una
> segunda lista aquí sólo produciría deriva.

- Índice legible: `validador/catalogo/manifest.yaml` (13 casos)
- Esquema de un caso: `validador/catalogo/_schema.md`
- Estado real de ejecución: `validador/reportes/cobertura.md` (`python cli.py --cobertura`)
- Ver un caso: `python cli.py --explicar <ID>`

Cobertura al 2026-08-20: **13 casos** dados de alta · **5** con insumos para correrse hoy
(`ISR-01`, `ISR-02`, `ISR-03`, `REND-PLAZO`, `COMPLETITUD`) · **8** esperando un insumo
documental, no código. **Ninguno corrido todavía por el validador** — y hasta que lo sea,
`cobertura.md` los marca `NO-CORRIDO`, que **no** es lo mismo que "pasa".

> Recordatorio (§10): **cada hallazgo confirmado se convierte en un invariante nuevo** y se queda
> permanentemente en la batería. Es la red de regresión del proyecto.
