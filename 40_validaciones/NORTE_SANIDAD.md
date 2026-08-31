# NORTE de Sanidad — invariantes falsables del tablero y de cada afirmación mostrada

> El principio del proyecto (cada validación **devuelve las filas que violan la regla**; 0 = pasa) aplicado **al
> tablero mismo y a cada número que muestra**. Esto existe porque, cuatro veces seguidas, una regla nueva para
> evitar un engaño abrió la puerta a otro. Linko · tercero independiente.

## 0. La lección (por qué formato no basta)
Las cuatro recurrencias comparten una raíz: **una regla de *formato* se cumple con *fabricación*.**
- "No pintes de verde lo que no corrió" → escondió cobertura buena tras un `—` (IFRS 9).
- "Ningún % sin escala" → **inventó** una escala (`("11.6","1e-8")` como fallback de CAT).

**Regla madre:** todo invariante de sanidad verifica **derivabilidad desde la fuente (verdad)**, no **presencia de un
campo (formato)**. Y el *fallback* cuando un dato no se puede derivar es **siempre un "no lo sé" explícito**
(`[PEND]` / "sin escala declarada" / "sin cruce"), **nunca un valor por defecto**. Un default es una mentira con
la confianza de una etiqueta.

## 1. Cómo se lee este documento
Cada invariante: **afirma** algo · **devuelve** las cifras/cards que lo violan (0 = pasa) · es **falsable** (se puede
construir el caso que lo rompe). El **status global** es verde **solo si TODOS devuelven 0**. Se ejecuta con
`comparadores/sanity_check.py` sobre el **registro de claims** (nuestro) y debe correrse también sobre el **JSON del
tablero** (lado auditor). Ningún invariante se cierra con tolerancia negociada.

---

## 2. Familia H — Honestidad de la afirmación (lo que rompió 4 veces)
- **INV-H1 · Escala obligatoria.** Todo número mostrado lleva su **escala/unidad** explícita (`1e-8` / `1e-5` /
  `centavo` / `volumen` / `config` / `completitud`). *Viola:* toda cifra sin escala.
- **INV-H2 · Escala verdadera, no supuesta.** La escala mostrada **está respaldada por la fuente y corresponde al
  valor** (no es un fallback ni una etiqueta puesta para cumplir). *Viola:* escala que no existe en la matriz para
  ese motor+valor. **(Este es el defecto de CAT: `11.6%` etiquetado `1e-8` cuando es cruce a *volumen*.)**
- **INV-H3 · Prohibido el default fabricado.** Si el dato no se puede derivar, se muestra el "no lo sé" explícito.
  *Viola:* cualquier valor/escala por defecto que sustituya un dato faltante (fallback hardcodeado).
- **INV-H4 · Procedencia.** Todo número dice **de dónde salió**: "calculado aquí" (con corrida) o "citado de
  MATRIZ/DOSSIER" (con `n` y fecha). *Viola:* número sin fuente.
- **INV-H5 · Titular = negocio.** Cuando existe el cuadre al **centavo**, ese es el titular; el estricto (`1e-8`)
  **no se esconde ni se disfraza de titular**. *Viola:* titular ≠ centavo habiendo centavo; o estricto omitido.

## 3. Familia E — Espejo (no pintar de verde lo que no corrió)
- **INV-E1 · Verde solo con corrida.** "Calculado aquí / validado" exige corrida con datos (`n > 0`). *Viola:*
  pase sin corrida.
- **INV-E2 · Sin cruce ≠ pase.** Un motor sin datos ni config no muestra pase. *Viola:* `sin_cruce` con badge verde.
- **INV-E3 · Config se muestra, no se esconde.** `cobertura = config` exhibe la evidencia (`lc_reserve_ifrs 37/37`),
  nunca un `—`. *Viola:* config sin `evidencia_config`.
- **INV-E4 · Botón honesto.** "Ejecutar" activo **solo** si hay **caso ejecutable + insumo disponible**. *Viola:*
  botón activo sin caso o sin feed (p.ej. CRED-MOR sin `credits-closing-trans`).
- **INV-E5 · Alcance declarado.** Cada card declara **qué se valida, qué NO, sobre qué universo y cuánto representa**.
  *Viola:* card sin alcance · sin universo · con **representatividad inventada** sobre universo `[PEND]` (mismo
  criterio que INV-H3) · alcance que no dice **qué queda fuera**. (Añadido por el auditor 2026-08-28; verificado que
  atrapa los cuatro modos.)

## 4. Familia C — Consistencia entre fuentes (una cifra, un valor)
- **INV-C1 · Misma cifra en todos lados.** El % de un motor es **idéntico** en el tablero, `MATRIZ_TOLERANCIAS.md`
  y `DOSSIER`/`COMPARACION`. *Viola:* discrepancia entre artefactos. **(Ej. real a cazar: moratorio "89% al centavo"
  dicho en la reunión vs `95.7%` en la matriz.)**
- **INV-C2 · `n` y sesgo citados coinciden** con la fuente. *Viola:* `n`/sesgo que no cuadra con la matriz.
- **INV-C3 · No stale.** Si existe una corrida más reciente (`_resultados/RESULTADO_*`), la cifra citada no puede
  contradecirla en silencio; o se actualiza o se marca la fecha. *Viola:* cifra citada más vieja que una corrida que
  la cambia, sin nota. (Ej. VISTA: matriz `[PEND]` mientras existe `RESULTADO_vista_vivo` 94.76%.)

## 5. Familia T — Trazabilidad / no-invención (charter §3)
- **INV-T1 · Cita o degrada.** Toda cifra `[CONFIRMADO]` tiene fuente + ubicación; sin cita, baja a `[INFERIDO]`/
  `[PEND]`. *Viola:* `[CONFIRMADO]` sin cita.
- **INV-T2 · `[PEND]` visible.** Lo que falta se marca `[PEND]`, no se rellena. *Viola:* hueco rellenado con
  "valor típico" / estimación presentada como dato.

---

## 6. Status global de sanidad
```
SANO  ⟺  Σ violaciones (todos los invariantes, todos los motores) = 0
```
El reporte lista, por invariante, **cuántas cifras/cards lo violan y cuáles**. Verde global = 0 en todos. Cualquier
violación = **no sano**, con el detalle. Igual que el resto del proyecto: **no hay "casi sano"**.

## 7. Sanity check al detalle (motor por motor) + status global
`comparadores/sanity_check.py`:
1. Carga el **registro de claims** (lo que cada motor legítimamente muestra, derivado de la matriz/COMPARACION).
2. Corre H/E/C/T sobre cada claim → devuelve violaciones.
3. Cruza las cifras clave contra `COMPARACION_C_vs_DOC.md` (INV-C1) y contra los `RESULTADO_*` (INV-C3).
4. Imprime **status por invariante + status global**.
El **JSON del tablero** (lado auditor) debe conformar al **mismo esquema de claim** y pasar los **mismos** invariantes
— así el tablero y nuestro repo se auditan con la misma vara. (La suite de pruebas del auditor —"toda escala mostrada
debe estar respaldada por la matriz y corresponder al valor"— es INV-H2 ya implementado de su lado.)

## 8. Cómo se agrega un invariante (para que no vuelva a pasar)
Cuando aparezca un engaño nuevo: **no** agregues una regla de formato. Escribe el invariante que verifica **la verdad
de la afirmación** y su **prueba falsable**, y define su **fallback explícito de "no lo sé"**. Si tu regla se puede
cumplir fabricando un valor, **no es un invariante — es un formato**, y va a fallar en la otra dirección.
