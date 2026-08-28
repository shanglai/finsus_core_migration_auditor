# Informe detallado de auditoría

Lo que se comprometió en la sesión del **2026-08-28** con el equipo de auditoría: bajar del
informe de alto nivel al detalle por punto de validación, con **alcance, periodo, universo,
representatividad, racional del subconjunto y santo y seña**.

```bash
python 60_informe/generar.py
```

Escribe `detalle/<ID>.md` (una ficha por punto), `00_INDICE.md` y `00_BRECHAS.md`.

## Qué contesta, y de dónde salió la pregunta

Las cinco preguntas de la sesión que el informe de alto nivel no traía:

| Pregunta (transcripción) | Dónde se contesta |
|---|---|
| *"¿Cuál fue el universo? ¿Y si ese universo lo conciliaste contra algo?"* `[00:26:55]` | §3 de cada ficha |
| *"4,091 contratos, ¿de cuántos? ¿Y según quién?"* `[00:27:52]` | §3 — denominador **y fuente** |
| *"La metodología con la que determinaron cuántos y **por qué**"* `[00:32:35]` | §4 racional del subconjunto |
| *"Cuánto representan esos ítems respecto del universo"* `[00:32:35]` | §3 representatividad |
| *"Qué estamos validando y qué **no** estamos validando"* `[00:49:04]` | §1 alcance |
| *"(bloqueados) qué es lo que le hace falta"* `[00:52:11]` | §8 bloqueo e insumo requerido |

## Cómo está construido

`puntos.py` declara; `generar.py` formatea. **El generador no redacta**: si un campo falta,
sale como hueco visible. Para cambiar una ficha se edita el registro, no el `.md`.

La regla que sostiene el documento:

> Ningún punto declara `n` sin declarar su **denominador**, o marcarlo `[PEND]` **con la
> consulta que lo mediría**.

Un porcentaje de representatividad que nadie puede reproducir es peor que un hueco declarado —
mismo criterio que `NORTE_SANIDAD.md`: el fallback de lo no derivable es un "no lo sé" con
instrucciones de cierre, nunca un valor por defecto. `tests/test_informe.py` lo verifica, junto
con que todo punto declare qué deja fuera, por qué eligió ese subconjunto, y —si está
bloqueado— **qué** insumo necesita y **cuándo**.

## Estado

**4 de 19** puntos tienen su denominador medido. Los 15 restantes están en
[`00_BRECHAS.md`](00_BRECHAS.md) con el SQL que los cierra. Para medirlos:

```bash
python 60_informe/medir_denominadores.py
```

Es solo lectura y solo agregación —cuenta filas, no lee datos de cliente—. Imprime lo que hay
que escribir en `puntos.py`; **no lo escribe solo**, a propósito: un denominador es una
afirmación del informe y la revisa un humano antes de publicarse.

Declarar el hueco no lo cierra. Se lista para que se cierre, no para darlo por contestado.

## Lo que este informe no es

No es un dictamen. Cada validación devuelve las filas que violan la regla; **cero filas
significa cero violaciones en ese universo**, no que el motor esté bien fuera de él. Y las
brechas listadas son del **informe**, no del core: ninguna es una desviación de cálculo.
