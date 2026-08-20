# Contradicciones

Conflictos entre fuentes, **sin resolver**. Prohibido elegir ganador por cuenta propia (§3.3,
§14.4 del CLAUDE.md). Cada entrada cita **ambas** fuentes y se escala.

| id | dominio | fuente A (cita) | fuente B (cita) | qué está en conflicto | estado | escalado a |
|----|---------|-----------------|-----------------|-----------------------|--------|------------|
| C-001 | FIS | Caso de oro + **valor APLICADO por AurumCore**: exención **213,973.20** (= 5 × UMA 42,794.64, UMA 2026). Evidencia dura: cliente `1-10-370`, 1 inversión de 300,000, 361 días, ISR posteado 765.75 → despeje da exención 213,973.92 ≈ 213,973.20; C con 213,973.20 = 765.76 (= B); con 206,367.60 = 833.46 (≠ B). | `system_configuration.yield.tax.exempt.amount = 206,367.60` (= 5 × UMA 2025), única fila, consultado 2026-08-18 | El **monto de exención**: lo que AurumCore APLICA (213,973.20, UMA 2026) NO coincide con lo que tiene CONFIGURADO (206,367.60, UMA 2025). | ANALIZADA · valor aplicado determinado (213,973.20); **falta escalar a Finsus** el porqué del config stale | Finsus (config) / INEGI (verificar UMA 2026) |
| C-002 | FIS | ~~F-016: `Proporción Cuenta = ÷ Base Gravable`~~ | F-010 + BD real: `÷ saldo_total` | Denominador de la proporción del ISR | **RESUELTA 2026-08-19** a favor de ÷saldo_total | — |

> **C-002 RESUELTA (2026-08-19):** el doc actualizado **F-019** corrige la fórmula a
> `Proporción Cuenta = Trunc20(Saldo de la Cuenta / Saldo total)` — exactamente lo que dedujimos del
> comportamiento real y del agregado. El oráculo C ya usaba ÷saldo_total → **no cambia nada en C**.
> **Residuo (calidad de doc, no del sistema):** el EJEMPLO de F-019 quedó inconsistente — sigue usando
> `30,000 / 300,000 = 0.1 → 22.93` (÷base_gravable); con la fórmula corregida sería `30,000 / 513,973.20
> = 0.0584 → 13.38`. Avisar a Finsus para que corrijan el ejemplo. Ver [[K-FIS-002]] v2.

> **Análisis (2026-08-18):** el valor APLICADO es 213,973.20 (el motor calcula 5×UMA en vivo con la
> UMA vigente 2026); el `exempt.amount=206,367.60` de `system_configuration` es un valor **stale/no
> usado** (UMA 2025). No es un defecto de cálculo del ISR, pero es **config desactualizada** (riesgo
> latente si algún proceso lo leyera). Para C: usar **213,973.20**.
>
> **Validación (2026-08-18, sobre `isr_diario` OpenFin, 728 días‑cliente):** se despejó la exención
> implícita por día (`exención = saldo − isr×365/0.009`). De 538 días con ISR>0: **511 → UMA 2026**
> (213,973.20) y **27 → UMA 2025** (206,367.60). Los 27 son un **bloque contiguo 2026‑02‑03 a ~02‑11**
> (9 días) en TODOS los clientes → es el **rezago de la actualización anual de la UMA** (efectiva ~1‑feb):
> la tabla se refrescó al valor 2026 unos días tarde. Del ~12‑feb en adelante, todo es UMA 2026.
> → **El cálculo SÍ usa UMA 2026; el 206,367.60 es un artefacto de transición, no sistemático.**
> Efecto real acotado: esos ~9 días el ISR se calculó con exención menor (2025) → ligeramente **mayor**
> (menor exención = más expuesto). Estatus: **degradada de contradicción a rezago‑de‑transición
> documentado.**
>
> **Cierre del residuo (2026-08-19, [[K-FIS-004]]):** la UMA 2026 es oficialmente vigente **desde el
> 1-feb-2026** (INEGI, DOF 9-ene-2026). Por tanto los días **2026-02-03 a ~02-11** que usaron la UMA 2025
> (206,367.60) **sí fueron técnicamente incorrectos** — el sistema aplicó el valor nuevo con ~10 días de
> rezago → sobre-retención menor y acotada esos días. Hallazgo menor (documentado), no sistémico.
