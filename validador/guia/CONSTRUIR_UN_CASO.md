# Guía para construir un caso ejecutable

> §11 del brief del auditor, con lo que ya costó redescubrir. **No es opcional
> y no es sólo documentación**: cada regla de aquí tiene una prueba en
> `validador/tests/test_guia_casos.py` que falla si un caso nuevo la ignora.
> Un documento que nadie lee se rompe en silencio; una prueba, no.

---

## 1. Independencia — de dónde salen los parámetros

El oráculo (C) es **árbitro independiente**. Sus parámetros —porcentajes, tasas,
base de días, tramos— salen de la **fuente independiente** (norma / GTM /
contrato / doc oficial), **no** de la tabla de configuración del core que estás
probando.

**Ejemplo, `IFRS9-E3`:** el `pct(días_mora)` de C (75/90/100) sale de las Tablas
del GTM, no de `lc_reserve_ifrs`. Leer el % de la configuración del core y
compararlo contra el mismo core probaría que **es consistente consigo mismo**,
no que aplica la norma. Que además `lc_reserve_ifrs` coincida 37/37 es un
**resultado** —y de los fuertes— no el método.

> **Regla:** si para construir el caso necesitas leer un parámetro del core,
> **detente**. Ese parámetro debe venir de la fuente. Si la fuente no lo tiene,
> es `[PENDIENTE]` — no lo tomes del core.

**Excepción declarable:** hay parámetros que son *hechos del contrato*, no
reglas — la tasa pactada de una cuenta concreta, por ejemplo. Leerlos del core
es inevitable, pero **se declara en `supuestos:`** diciendo qué se está leyendo
y qué prueba se pierde por hacerlo.

## 2. Convenciones de cálculo ya confirmadas — heredarlas

| convención | valor | dónde se confirmó |
|---|---|---|
| Redondeo | **half-up, por evento** (no al cierre) | Finsus 2026-08-24 · `S-FIS-001` |
| Base de días | **por producto** (360 / 365) — *no asumir* | `account_yield.days_in_year` |
| Aritmética | `decimal.Decimal`, cero `float`, modo de redondeo **explícito** | charter §1.3 |

El redondeo es **la causa número uno de sesgo espurio**. Si tu C no redondea
como el core, la prueba de signo te va a marcar un sesgo que es tuyo.

La base de días **se confirma del esquema**, no se asume. Probar las
convenciones y reportar cuál ajusta es válido y no es circular; fijar 360
"porque suele ser" no lo es.

## 3. Playbook del sesgo — antes de gritar "severidad 1"

Cuando `tolerancias.py` marca sesgo (diferencias del mismo signo, sub-centavo),
**no lo reportes como defecto todavía**. Pártelo en este orden:

1. **¿Redondeaste half-up por evento, como el core?**
   En `IFRS9-E3` esto explicó la mitad: 5,133 → 2,381 diferencias.
2. **¿Es precisión de la base?**
   Si lees el insumo (`capital_venc`, `SPM`, capital) a N decimales y el core
   calculó con más, el residual sub-centavo es granularidad del snapshot —
   patrón **P-019**. Se verifica así: si el **porcentaje o la tasa implícita**
   en las filas que fallan sale correcta (75.0000 / 90.0001 / 100.0000), la
   fórmula está bien y la diferencia es la base.
3. **Sólo si sobrevive a (1) y (2) y es material** → candidato a defecto del
   core. Escálalo.

> **Regla:** un sesgo sub-centavo de un solo signo es, por omisión, **tu
> redondeo o la precisión de tu base** — no un defecto de Aurum — hasta
> descartar ambos.

Ha pasado **tres veces** en este proyecto (`VISTA`, `IFRS9-E3`, y el moratorio
del dossier) y las tres el sesgo era del método.

La bandera roja **se muestra igual** — ocultarla sería peor (§3.2). Lo que
cambia es la lectura escrita junto a ella: *"sesgo del método (redondeo/base),
no del core"*.

## 4. Declaración de alcance — escribe lo que dejas fuera

Cubre **sólo lo que la fuente sustenta**. Lo que quede fuera se escribe en el
caso, con su motivo.

**Ejemplo, `IFRS9-E3`:** cubre etapa 3, consumo, zona no marginada. Declara
fuera E1/E2 amortizando y la composición de `reserva_int` —dependen de fórmulas
que siguen en el documento pendiente— y comercio/reestructurado, que necesitan
las 9 tablas. Cubrirlos hoy exigiría **inventar la base**, y eso no se hace.

El caso muestra el alcance cubierto **y** el declarado-fuera. El badge y el
botón no insinúan más cobertura de la real.

## 5. Punteros

| tema | dónde vive |
|---|---|
| Half-up y parámetros | `S-FIS-001` · `COMPARACION_C_vs_DOC.md` · los `oraculo_*.py` · `ESTADO_RESUMEN.md` |
| Precisión de base / P-019 | `COMPARACION_C_vs_DOC.md` · `DOSSIER_MOTORES_ORACULO_C.md` · `MATRIZ_TOLERANCIAS.md` · `K-DAT-002` |
| Tres granularidades y sesgo | `MATRIZ_TOLERANCIAS.md` · `comparadores/tolerancias.py` |
