# Cómo revisar el auditor — mapa, ejecución y tripas

> Para quien llega a auditar **al auditor**: dónde vive cada cosa, cómo se corre, cómo se lee
> un resultado y qué hay que saber para no darle crédito de más.
> Corte 2026-08-28.

**La regla que ordena todo lo demás:** cada validación **devuelve las filas que violan la regla**.
Cero filas = cero violaciones *en ese universo*, nunca "el motor está bien". No hay ningún camino
en el código que devuelva "pasa" — sólo conjuntos de violaciones, que pueden estar vacíos.

---

## 1. Dónde está qué

Son dos piezas: el **validador** (el motor, línea de comandos) y el **tablero** encima de él.

```
validador/
  cli.py                     ← el único punto de entrada
  catalogo/*.yaml            un caso por archivo (CAT-01, IFRS9-E3, REND-VISTA…)
  catalogo/manifest.yaml     el índice; un YAML sin fila aquí rompe las pruebas
  extraccion/aurum/*.sql     el SQL de cada caso (solo lectura)
  extraccion/openfin/*.sql
  oraculos/*.py              motor C: cat · ifrs9 · isr · rendimientos · parametros_isr
  engine/*.py                extract · compare · sesgo · evidencia · redondeo · warehouse
  guia/CONSTRUIR_UN_CASO.md  las convenciones, antes de escribir un caso nuevo
  reportes/<CASO>_<fecha>_<hash>/   la evidencia de cada corrida
  datos/validador.duckdb     los universos extraídos (local, gitignored)

auditor_spa/
  backend/motores.py         tabla declarativa de los 16 motores — NO calcula nada
  backend/runner.py          corre los motores y escribe los JSON + datos.js
  backend/sanidad.py         los invariantes del propio tablero
  backend/servidor.py        el servidor del SPA (API + estáticos)
  backend/dossier.py         corta los documentos en secciones citables para el agente
  resultados/<MOTOR>.json    lo que el tablero muestra
  spa/index.html             el tablero, autocontenido, sin CDN

40_validaciones/             el bundle que manda Finsus (NORTE, DOSSIER, MATRIZ, oráculos)
50_hallazgos/                lo que sale de este lado: HALLAZGOS · CANDIDATOS · SOLICITUDES
```

**El reparto que importa:** `engine/` es genérico; `catalogo/` + `extraccion/` + `oraculos/` es lo
específico de cada caso. Un caso nuevo son **tres archivos** (yaml + sql + adaptador) y **cero**
cambios en `engine/`. Si un caso te obliga a tocar `engine/`, o el caso está mal planteado o el
motor le falta una capacidad genuina — no lo resuelvas con un parche en el caso.

---

## 2. Antes de correr nada: credenciales

```bash
cp validador/db_connections.example.yaml validador/db_connections.yaml
```

Se llena con credenciales de **solo lectura**. Está en `.gitignore`, junto con cualquier derivado
(`.bak`, `.old`, copias con fecha). El archivo se admite en `validador/` o en la raíz del repo.

```bash
cd validador && python cli.py --probar-conexion
```

Esto no sólo hace un `select 1`: **intenta escribir y verifica que el servidor lo rechace**. Si la
escritura pasa, el usuario de BD no es de solo lectura y hay que parar ahí.

---

## 3. Correr un caso

```bash
cd validador && python cli.py --listar
```

```bash
cd validador && python cli.py --caso CAT-01 --explicar
```

`--explicar` da la identidad, la tolerancia, los supuestos y **lo que el caso deja fuera**, sin
tocar la base. Por defecto todo es `--dry-run`: enseña el SQL exacto y no conecta.

Para correr de verdad hay que decirlo:

```bash
cd validador && python cli.py --caso CAT-01 --confirmar
```

Parámetros sobre la marcha: `--param umbral_constante=50 --param limite=5000`.
Cohortes desde archivo: `--cohorte-archivo cuentas.txt` (un `account_number` por línea).

---

## 4. Leer un resultado

La consola imprime `universo · violaciones · matriz A/B/C · sesgo · evidencia`. Lo que importa
está en la carpeta que nombra al final:

```
reportes/CAT-01_2026-08-28_<hash>/
  manifiesto.json      parámetros, snapshot, hash de la regla, tolerancia, resultado, supuestos
  consultas.sql        el SQL EXACTO que se envió al servidor
  universo.parquet     todo lo que se comparó
  violaciones.parquet  las filas que rompen la regla   ← el producto
```

Los `.parquet` se abren con DuckDB o DBeaver (ver §9). El `manifiesto.json` es lo que hace la
corrida **reproducible por un tercero**: trae el snapshot, los parámetros y el hash, así que no
hay que creerle al resumen de consola.

Vista agregada de qué se ha corrido y qué no:

```bash
cd validador && python cli.py --cobertura
```

Un caso marcado `VALIDADO` en el catálogo que este validador nunca ejecutó aparece aquí como
**NO-CORRIDO**. Son dos ejes distintos a propósito: el estado dice lo que se sabe de la
validación, la cobertura dice lo que *esta herramienta* corrió.

---

## 5. Desde el tablero

```bash
cd auditor_spa/backend && python servidor.py --puerto 8777
```

Abre http://localhost:8777. El botón **Ejecutar** de cada tarjeta llama al mismo motor del §3 y
refresca la tarjeta al terminar. Sin servidor también sirve: `python runner.py` regenera
`spa/datos.js` y el `index.html` se abre directo desde el disco.

```bash
cd auditor_spa/backend && python runner.py --con-bd --motor CAT
```

Sin `--con-bd` sólo reescribe los JSON **conservando** las corridas que ya existen — una caída de
VPN no borra cobertura ya obtenida.

Y antes de creerle al tablero:

```bash
cd auditor_spa/backend && python sanidad.py
```

Devuelve las tarjetas que violan cada uno de los 14 invariantes. **`SANO` = 0 en los 14 sobre los
16 motores**; no hay "casi sano". El mismo reporte está en `GET /api/sanidad` y en el badge del
home.

---

## 6. Las tripas — lo que hay que saber para no dar crédito de más

### 6.1 La matriz A/B/C: no hay booleanos

`engine/compare.py` no devuelve "pasa/falla". Clasifica cada fila en una celda:

| celda | qué significa |
|---|---|
| `A=B=C` | los tres coinciden |
| `A=B!=C` | **ambos cores mal contra la norma** — severidad máxima, y es la que el "todo pasa" esconde |
| `A!=B=C` | defecto de OpenFin ya corregido en AurumCore |
| `A=C!=B` | defecto de AurumCore |
| `A!=B!=C` | los tres distintos: **la regla está mal especificada**, no el core |
| `B=C (sin A)` / `B!=C (sin A)` | no hay motor A comparable para esa fila |
| `sin B` | el core bajo prueba no tiene la fila |
| `sin C` | **el oráculo no pudo calcular** — cuenta como violación, no se descarta |

`sin C` es la que más se presta al autoengaño: descartar lo que no se pudo medir sube el
porcentaje **por no haberlo medido**. Aquí cuenta como no conforme.

### 6.2 Independencia del oráculo (§11.1 del brief)

Los parámetros de C —%, tasas, tramos, bases de días— salen de la **fuente independiente**
(norma / GTM / contrato), **no** de la tabla de configuración del core que se está probando. Leer
el % de `lc_reserve_ifrs` y compararlo contra el mismo core probaría que **es consistente consigo
mismo**, no que aplica la norma.

Lo que **sí** se lee del core son hechos del contrato (monto, plazo, cronograma, comisión
pactada): son insumos, no parámetros de la regla. La línea es: *leer del core el CAT para calibrar
el CAT sería circular; leer el monto del crédito no lo es.*

Que además la config del core coincida (IFRS 9: `lc_reserve_ifrs` 37/37) es un **resultado**
—fuerte—, nunca el método.

### 6.3 El playbook del sesgo (§11.3) — ya acertó cuatro veces

`tolerancias.py` corre una prueba de signo. Cuando marca sesgo, **no es un defecto todavía**:

1. **¿Redondeaste half-up por evento, como el core?** (Confirmado por Finsus el 2026-08-24.)
2. **¿Es precisión de la base?** Si lees el insumo a N decimales y el core calculó con más, el
   residuo sub-centavo es granularidad del snapshot — **patrón P-019**. Se verifica con el
   **porcentaje implícito**: si en las filas que fallan sale correcto, la fórmula está bien.
3. **Sólo si sobrevive a (1) y (2) y es material** → candidato a defecto del core.

Las cuatro veces que se ha marcado sesgo, era del método. La bandera roja **se muestra igual**
—ocultarla sería peor—; lo que cambia es la lectura escrita al lado.

### 6.4 Solo lectura, de verdad

- `engine/extract.py::asegurar_solo_lectura` rechaza cualquier SQL con verbos de escritura
  **antes de abrir el socket**.
- La sesión abre con `SET default_transaction_read_only = on`.
- La extracción es **acotada**: `fetchmany(limite+1)` y si sobra fila levanta `ExtraccionNoAcotada`.
  Un `select *` sin límite no sale de aquí.
- Destinos marcados `sensible: true` (p. ej. `identityshared`) levantan `DestinoSensible` **antes**
  de conectar. Se saltan sólo con `--permitir-sensible` y cohorte mínima.
- La defensa de la aplicación **no sustituye** un rol de solo lectura en el servidor.

### 6.5 El catálogo se valida a sí mismo

El cargador rechaza casos incoherentes antes de correrlos: un caso `VALIDADO` tiene que ser
ejecutable; los montos van como **cadenas** (nunca `float` en YAML); `tipo: contable` obliga a
tolerancia `0.00`; `tipo: redondeo` obliga a `prueba_sesgo: true`; y todo caso con prueba de sesgo
tiene que **declarar cómo leer la bandera**. Esa última atrapó a `CAT-01` mientras se construía.

### 6.6 El tablero se audita a sí mismo

`auditor_spa/backend/sanidad.py` aplica al tablero la misma vara: 14 invariantes (familias
H/E/C/T de `NORTE_SANIDAD.md`) que devuelven las tarjetas que los violan.

Tres cosas lo mantienen honesto, y conviene verificarlas si se desconfía:

1. **Los claims se derivan de los `resultados/<motor>.json` que el SPA sirve**, no de una lista
   escrita a mano. Auditar una transcripción comprobaría que se copió bien, no que el tablero diga
   la verdad.
2. **La referencia se parsea de `MATRIZ_TOLERANCIAS.md`.** Un dict hardcodeado sería el mismo
   pecado que INV-H3 castiga, y un `INV-C1` sin nada con qué comparar "pasaría" siempre — hay una
   prueba que exige que el parser saque cifras reales.
3. **Auto-prueba de falsabilidad**: se inyectan los dos bugs históricos (CAT `11.6` etiquetado
   `1e-8`; moratorio con titular `81.1` ocultando el centavo) y se afirma que se atrapan. Si la
   auto-prueba falla, el badge lo dice: un verde sostenido por invariantes vacíos es el all-pass
   otra vez.

El motivo de que exista: cuatro veces seguidas, una regla nueva para evitar un engaño abrió la
puerta a otro, siempre igual — **una regla de *formato* se cumple *fabricando***. Por eso ningún
invariante verifica que un campo **esté**; verifican que la afirmación sea **derivable de la
fuente**, y el fallback de lo no derivable es siempre un "no lo sé" explícito (`[PEND]`, "sin
escala declarada", "sin cruce"), **nunca un valor por defecto**.

### 6.7 Las tres granularidades y el escalón

Cada motor de cálculo reporta el cuadre a **1e-8** (exactitud estricta), **1e-5** (precisión
intermedia) y **centavo** (tolerancia de negocio). El **escalón** entre niveles es más informativo
que cualquier número solo:

- `100 / 100 / 100` → mismo cálculo, bit a bit.
- bajo a 1e-8 y alto al centavo → residuo sub-centavo, granularidad del snapshot, **no** defecto.
- bajo también al centavo → diferencia **material** que investigar.

**Ojo:** esa lectura del escalón es la *habitual*, no una ley. En `CAT` es falsa —el escalón es
angosto porque `lc_loan_contract.cat` guarda dos decimales, no porque haya residuo que absorber—,
por eso un motor puede **declarar su lectura real** (`Motor.lectura_escalon`) y la plantilla
genérica dejó de afirmar el diagnóstico. Si ves una lectura de escalón, revisa si la declaró el
motor o la puso la plantilla.

### 6.8 Citar no es calcular

`origen_resultado` distingue tres cosas que un tablero descuidado mezclaría en una barra verde:

- `corrida_local` — el % lo calculó esta máquina, contra la BD, ahora.
- `dossier` — lo reporta el DOSSIER de una corrida previa del repo de validación. Se muestra
  **citado**, con su `n` y su fecha.
- `sin_cruce` — hay fórmula y autoprueba, no hay cruce contra datos. **Eso no es un pase.**

Y `cobertura` (`datos` / `volumen` / `config` / `completitud` / `sin_cruce`) dice de qué **clase**
es la evidencia. No es cosmético: un cruce a volumen leído como precisión aritmética fue
exactamente el defecto que destapó CAT.

---

## 7. Las pruebas

```bash
python -m pytest auditor_spa validador -q
```

440 pruebas. Las que conviene mirar si se desconfía del conjunto:

| archivo | qué protege |
|---|---|
| `validador/tests/test_no_all_pass.py` | que ningún camino devuelva "todo pasa"; catálogo y manifest sincronizados |
| `validador/tests/test_caso_trampa.py` | un caso con un defecto **sembrado** que las pruebas tienen que atrapar |
| `validador/tests/test_compare_matriz.py` | las celdas A/B/C, incluido universo vacío = "no prueba nada" |
| `validador/tests/test_guia_casos.py` | el §11 como invariantes ejecutables, no como documentación |
| `validador/tests/test_redondeo.py` | half-up explícito, cero `float` |
| `auditor_spa/tests/test_sanidad.py` | los 14 invariantes **y** que atrapen sus bugs históricos |
| `auditor_spa/tests/test_motores.py` | que el tablero no pueda presentar como verificado lo que no lo está |

El patrón: casi ninguna prueba verifica que algo *exista*; verifican que **atrape**. Cada una
construye el engaño y afirma que sale como violación. Una prueba que no puede fallar no prueba
nada — por eso `test_la_autoprueba_de_falsabilidad_puede_fallar` apaga un invariante a propósito
para comprobar que la auto-prueba sabe decir que **no**.

---

## 8. Añadir un caso nuevo

Lee primero **[`validador/guia/CONSTRUIR_UN_CASO.md`](validador/guia/CONSTRUIR_UN_CASO.md)**.
Resume lo que ya costó redescubrir cuatro veces: independencia de parámetros, convenciones
confirmadas (half-up, base de días), el playbook del sesgo y la **declaración de alcance**.

No es documentación decorativa: `test_guia_casos.py` falla si el caso nuevo ignora cualquiera de
las cuatro. `CAT-01` es el ejemplo más completo de alcance declarado — dice qué universo cubre,
qué estratos deja fuera **con su conteo**, y qué no puede dictaminar hasta que llegue SOL-015.

---

## 9. Los datos crudos (DuckDB / DBeaver)

La base con los universos extraídos:

```
validador/datos/validador.duckdb
```

En DBeaver: **Nueva conexión → DuckDB → Path** = esa ruta. Dos cosas o no funciona:

- **Ábrela en solo lectura**: DuckDB admite un solo escritor. En *Driver properties*,
  `duckdb.read_only` = `true`. Si no, `runner.py --con-bd` truena mientras DBeaver la tenga.
- **Versión del driver**: el archivo lo escribió DuckDB 1.5.5. Un driver más viejo da error de
  *storage version*; se sube en Driver Manager.

La evidencia por corrida **no** está en esa base: son parquet sueltos. Se leen desde la misma
conexión:

```sql
select regexp_extract(filename, '([A-Z0-9-]+_\d{4}-\d{2}-\d{2}_[0-9a-f]+)', 1) as corrida,
       count(*) as violaciones
from read_parquet('<ruta-del-repo>/validador/reportes/*/violaciones.parquet',
                  filename => true, union_by_name => true)
group by 1 order by 1;
```

Usa **barras normales** dentro del SQL: DuckDB trata `\` como escape. Las corridas con cero
violaciones no aparecen porque su parquet está vacío — eso es el resultado, no un archivo
faltante.

---

## 10. Qué NO sale de esta máquina

En `.gitignore` a propósito, y no por tamaño:

```
db_connections.yaml y cualquier derivado (.bak, .old, copias con fecha)
validador/datos/            la DuckDB con universos reales
validador/reportes/*/       la evidencia: universos y violaciones con datos de cliente
40_validaciones/_resultados/
auditor_spa/resultados/  ·  auditor_spa/spa/datos.js
```

Son la cadena probatoria y traen PII. Al remoto va el **conocimiento y el código** —lo que hace
auditable el trabajo—, no los datos fuente. El historial de git es permanente: lo que se sube una
vez ya no se puede desubir.

---

## 11. Dónde queda lo que se encuentra

| archivo | qué va ahí |
|---|---|
| `50_hallazgos/HALLAZGOS.md` | `H-###` confirmados: reproducidos, evaluados con A/B/C, clasificados y cuantificados |
| `50_hallazgos/CANDIDATOS_A_HALLAZGO.md` | observaciones firmes que aún no pasaron los cuatro pasos |
| `50_hallazgos/SOLICITUDES_DEL_AUDITOR.md` | `AUD-###`: lo que hay que preguntarle a Finsus |

`50_hallazgos/` **no viaja en el bundle**, por eso es el lugar correcto para lo que nace de este
lado. Las solicitudes se numeran `AUD-###` y no `SOL-###`: el número lo asigna el repo fuente, y
escribir en `40_validaciones/SOLICITUDES_FINSUS.md` no sirve — la siguiente sincronización del
bundle lo sobreescribe (ya pasó una vez).

**La regla de promoción** a `H-###`: (1) caso mínimo reproducido, (2) evaluado con A/B/C,
(3) clasificado, (4) cuantificado con evidencia propia. Sin los cuatro, se queda en candidato.

---

## 12. El sesgo de este documento

Todo lo anterior describe controles que **yo mismo** construí, así que léelos como afirmaciones a
verificar, no como garantías. Los tres puntos donde empezaría a picar si tuviera que auditar esto:

**1. El caso trampa.** Confirma que el defecto sembrado se atrapa.

```bash
python -m pytest validador/tests/test_caso_trampa.py -q
```

**2. Romper un JSON a mano.** Quítale la escala a un porcentaje y comprueba que el chequeo lo caza:

```bash
python -c "import json;p='auditor_spa/resultados/PLAZO.json';d=json.load(open(p,encoding='utf-8'));d['pct_escala']=None;json.dump(d,open(p,'w',encoding='utf-8'),indent=2,ensure_ascii=False)"
```

`python auditor_spa/backend/sanidad.py` debe pasar a **NO SANO** y nombrar la tarjeta
(`PLAZO: el titular 100.00% se muestra sin escala`). Se restaura con
`python auditor_spa/backend/runner.py`.

**3. Reejecutar el SQL a mano.** Abre el `consultas.sql` de una corrida, córrelo contra la base y
compara contra lo que reporta su `manifiesto.json`. Si esos dos números no coinciden, nada de lo
demás importa.

Las tres están verificadas al escribir este documento; el punto es que **tú** las corras, no que
te fíes de que yo las corrí.
