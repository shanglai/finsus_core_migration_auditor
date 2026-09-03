# Guía del oráculo — instalar, correr y entender cada motor

> Para el **grupo auditoría de Finsus**, en **Windows**. Cubre la instalación, una primera ejecución
> completa, el tablero, y al final **cada motor con sus parámetros, formatos y un ejemplo copiable**.
> Complementa `40_validaciones/MANUAL_USO_ORACULO_AUDITOR.md`, que cubre los comparadores.
>
> Todo es **solo lectura**: el código rechaza cualquier SQL con verbos de escritura **antes** de abrir
> la conexión.

---

## 0. Antes que nada: usen el **prompt de conda**, no PowerShell

Menú Inicio → **Miniforge Prompt** (o **Anaconda Prompt** si ya tienen Anaconda). No PowerShell, no
la terminal de VS Code. Dos razones concretas:

- **`conda activate` no funciona en PowerShell** hasta que alguien corra `conda init powershell` y
  reinicie la terminal. En el prompt de conda funciona de entrada.
- **PowerShell 5.1 —el que trae Windows de fábrica— no entiende `&&`.** No falla a medias: es un
  error de sintaxis.

> Aun así, **cada comando de esta guía va en una sola línea, sin `&&`**, para que funcione igual en
> el prompt de conda, cmd y PowerShell. Donde haya diferencia, se indica.

## 1. Miniforge, Anaconda o pip — cuál usar

**Recomendado: Miniforge.** Es el instalador de la comunidad `conda-forge` (BSD-3), apunta a ese
canal por defecto y **no está sujeto a los términos comerciales de Anaconda Inc.** Se descarga de
`github.com/conda-forge/miniforge/releases`, no de anaconda.com ni de python.org.

**Anaconda también funciona** si ya lo tienen instalado y aprobado — el comando de instalación es el
mismo, porque lleva `-c conda-forge` explícito.

> **Por qué el canal importa.** La restricción de Anaconda Inc. es sobre su instalador y su canal
> `defaults` (`repo.anaconda.com`). `conda-forge` es un canal comunitario aparte. Se verificó en un
> entorno real: **los seis paquetes y el propio Python vinieron de `conda-forge`**, ninguno de
> `defaults`. Por eso el `-c conda-forge` va explícito aunque en Miniforge sea el default — así la
> procedencia queda escrita en el comando, que es lo que se puede auditar.

Dos cosas cambian respecto a `pip`:

**(a) El paquete se llama `psycopg2`, no `psycopg2-binary`.** En conda ya viene compilado; el
sufijo `-binary` sólo existe en PyPI.

**(b) No mezclen conda y pip para el mismo paquete.** Si algo se instala con `conda` y luego se
reinstala con `pip`, conda pierde el rastro y las actualizaciones posteriores rompen el entorno.
Regla práctica: **todo por conda**.

### Versión de Python: 3.11 o superior

**Verificado midiendo, no supuesto.** Se creó un entorno conda limpio con Python 3.11.16 en una
máquina Windows y ahí se corrió **cada comando de esta guía, tal como está escrito**:

| qué se probó | resultado |
|---|---|
| `pytest auditor_spa validador 60_informe` | **0 fallos** (el total de pruebas sube con cada entrega; lo que importa es que ninguna falle) |
| `sanity_check.py` (Finsus) | SANO + auto-prueba de falsabilidad OK |
| `sanidad.py` (tablero) | SANO, 0 violaciones en 15 invariantes |
| `cli.py --autopruebas` · `--listar` · `--explicar` · `--probar-conexion` | correctos |
| `cohorte.py --help` | correcto (ver la nota de abajo si no lo tienen) |
| `runner.py` | regenera los JSON y `datos.js` |
| `servidor.py` + `/api/sanidad` | el tablero sirve y responde SANO |

El desarrollo fue en 3.14, pero el código no usa nada posterior a 3.10.

> **Salvedad honesta:** esa verificación se hizo con el `conda` de **Anaconda**, apuntando a
> `conda-forge`. **No se probó el instalador de Miniforge**, porque no está disponible en el equipo
> donde se preparó esta guía. Lo que sí está verificado es lo que importa: los paquetes son **los
> mismos de `conda-forge`** que Miniforge instala, y el entorno resultante corre todo sin fallos.
> Si al validar Miniforge aparece cualquier diferencia, avisen y se corrige aquí.

> **Ojo con las rutas:** los comandos se invocan **desde la raíz del repositorio** con rutas tipo
> `python validador\cli.py`, no entrando a cada carpeta. Se verificó que los scripts resuelven sus
> rutas internas solos — y eso es lo que permite evitar el `cd X && comando` que rompe en PowerShell.

## 2. Instalación

Mismo comando en Miniforge y en Anaconda:

```
conda create -y -n auditor -c conda-forge python=3.11 polars duckdb pyarrow psycopg2 pyyaml pytest
```

Tarda varios minutos resolviendo — es normal, no está colgado. En Miniforge pueden usar `mamba` en
lugar de `conda` para que resuelva más rápido; el resto es idéntico.

```
conda activate auditor
```

Versiones con las que se verificó: polars 1.44.1 · duckdb 1.5.5 · pyarrow 25.0.0 · psycopg2 2.9.12 ·
pyyaml 6.0.3 · pytest 9.1.1.

Para qué sirve cada uno, porque importa entenderlo al auditar:

| paquete | para qué | ¿toca el dinero? |
|---|---|---|
| `polars`, `duckdb` | **mover y cruzar** datos: joins, set-diff, conteos | **no** |
| `pyarrow` | puente entre Polars y DuckDB. **No es opcional** — sin él, cargar un DataFrame al warehouse falla a media corrida | no |
| `psycopg2` | conexión a los cores, en solo lectura | no |
| `pyyaml` | catálogo de casos | no |
| `pytest` | las autopruebas | no |

**Todo cálculo monetario va en `decimal.Decimal`, de la librería estándar.** Ninguna de estas
librerías recalcula dinero: sólo mueven filas. Es deliberado — un `float` en una ruta de dinero es
un error silencioso.

### Sin conda — sólo si ya tienen un Python aprobado

Esta ruta **no incluye instalar Python**: asume que ya hay un intérprete 3.11+ autorizado en el
equipo. Descargarlo de python.org puede estar restringido por política de seguridad, y esa decisión
no la resuelve esta guía.

En el **Símbolo del sistema (cmd)**, una línea por vez:

```
python -m venv .venv
```
```
.venv\Scripts\activate.bat
```
```
pip install -r requirements.txt
```

En **PowerShell** la segunda línea es `.venv\Scripts\Activate.ps1` (y puede pedir
`Set-ExecutionPolicy -Scope Process RemoteSigned`).

### Sobre Spyder

**Spyder es un IDE, no una distribución de Python:** necesita un intérprete debajo y no sustituye a
Miniforge. Puede editar y correr este código sin problema —es Python plano, sin notebooks—, pero el
entregable son herramientas de línea de comandos y un servidor local, así que lo natural es
**Spyder como editor apuntando al entorno de Miniforge**, y los comandos de esta guía en el prompt
de conda. Ojo con `servidor.py`: bloquea la consola mientras corre.

### Licencias — para TI/CISO

| componente | licencia |
|---|---|
| Python (CPython) | **Python-2.0** (PSF) |
| polars · duckdb · PyYAML · pytest | **MIT** |
| pyarrow / libarrow | **Apache-2.0** |
| psycopg2 | **LGPL-3.0-or-later** |
| instalador Miniforge | **BSD-3-Clause** |

Todas permisivas salvo `psycopg2`, que es **LGPL**: se usa **sin modificar, como librería
importada**, en herramienta interna que no se redistribuye. Es el único punto que conviene señalar
explícitamente. Ningún paquete proviene del canal `defaults` de Anaconda.

---

# Primera ejecución — de cero a un resultado

Siete pasos. Los cuatro primeros **no tocan la base**.

## Paso 1 · Situarse en la carpeta

```
cd C:\ruta\donde\clonaron\finsus_core_migration_auditor
```

Si están en otra unidad (D:, por ejemplo), primero `D:` y luego el `cd`.

## Paso 2 · Comprobar que las fórmulas reproducen el documento

```
python validador\cli.py --autopruebas
```

Cada oráculo se contrasta contra los ejemplos del documento oficial. Si algo falla aquí, no tiene
caso seguir: el problema es la instalación, no los datos.

## Paso 3 · Comprobar que el tablero no se contradice

```
python 40_validaciones\comparadores\sanity_check.py
```
```
python auditor_spa\backend\sanidad.py
```

Ambos deben decir **SANO**. El primero además confirma que la auto-prueba de falsabilidad **atrapa
los dos bugs históricos** — un chequeo que no atrapa su propio error no prueba nada.

## Paso 4 · La suite completa

```
python -m pytest auditor_spa validador 60_informe -q
```

## Paso 5 · Credenciales

```
copy validador\db_connections.example.yaml validador\db_connections.yaml
```

Se edita con **credenciales de solo lectura**. El archivo está en `.gitignore` junto con cualquier
derivado (`.bak`, `.old`, copias con fecha): **nunca se versiona**.

```
python validador\cli.py --probar-conexion
```

Esto no sólo abre la conexión: **intenta escribir y verifica que el servidor lo rechace**. Si la
escritura pasa, el usuario no es de solo lectura y hay que parar ahí.

> Si no hay conexión, el comando termina con código distinto de cero. Es correcto, no está roto.
> Si da *timeout*, es la ruta a la subred `10.10.0.0/16` — tema de su IT. Ver
> `40_validaciones/ACCESO_Y_RED.md`.

## Paso 6 · La primera validación de verdad

Empiecen por **`CONTABLE-B1`**: es el caso más simple —dos parámetros, sin cohorte— y su regla es
una identidad exacta, así que el resultado no admite interpretación.

Primero, ver el plan **sin tocar nada** (es el modo por defecto):

```
python validador\cli.py --caso CONTABLE-B1 --explicar
```

Eso muestra la identidad, la tolerancia, los supuestos y **qué deja fuera el caso**. Para ejecutar
hay que decirlo con `--confirmar`:

```
python validador\cli.py --caso CONTABLE-B1 --confirmar --param fecha_ini=2026-08-10 --param fecha_fin=2026-08-17
```

**Qué esperar.** Un resumen con `universo · violaciones · matriz A/B/C · sesgo · evidencia`, y una
carpeta nueva bajo `validador\reportes\`. Para este caso, lo correcto es **0 violaciones**: la doble
partida no admite holgura.

## Paso 7 · Verificar la corrida contra su propia evidencia

Cada corrida escribe `validador\reportes\<CASO>_<fecha>_<hash>\`:

| archivo | qué es |
|---|---|
| `violaciones.parquet` | **las filas que rompen la regla** — el producto |
| `universo.parquet` | todo lo que se comparó |
| `consultas.sql` | el SQL **exacto** que se envió al servidor |
| `manifiesto.json` | parámetros, snapshot, hash, tolerancia, supuestos |

**La comprobación que recomendamos hacer primero:** abrir `consultas.sql`, ejecutarlo a mano contra
la base, y comparar el conteo contra lo que reporta `manifiesto.json`. Si esos dos números no
coinciden, nada de lo demás importa.

Los `.parquet` se abren con DBeaver vía DuckDB. En el SQL usen **barras normales** (`/`) aunque
estén en Windows: DuckDB trata `\` como escape.

---

# El tablero

```
python auditor_spa\backend\runner.py
```

Genera los JSON por motor. Después:

```
python auditor_spa\backend\servidor.py --puerto 8777
```

Y se abre **http://localhost:8777**. La ventana queda ocupada mientras el servidor corre; `Ctrl+C`
lo detiene.

En el menú hamburguesa hay dos vistas pensadas para ustedes:

- **Criterios de auditoría** — los 13 criterios de F-032 con enlace al motor o documento que atiende cada uno.
- **Glosario de estados** — qué significa cada etiqueta, renderizado del documento del bundle.

### ¿El tablero necesita las dependencias? Casi no

El **front no tiene ninguna dependencia externa**: son dos archivos, `index.html` y `datos.js`, sin
CDN, sin librerías, sin red. El único `<script src=>` apunta a `datos.js`, que está al lado.

El **servidor tampoco necesita las pesadas**: usa `http.server` de la librería estándar, y los
imports de `polars`/`duckdb`/`psycopg2` están diferidos dentro de las funciones que los usan.
**Verificado**: levanta y sirve `/`, `/api/motores`, `/api/sanidad` y `/datos.js` con un Python
**sin polars, sin duckdb y sin psycopg2**.

**Sin servidor también funciona:** `auditor_spa\spa\index.html` se abre con doble clic. El tablero
lee siempre de `datos.js` —no del API—, así que se ve completo. Lo único que se pierde es el botón
"Ejecutar".

> **Pero `datos.js` hay que generarlo.** No viene en el repositorio, y es a propósito: contiene
> **11,527 números de cuenta completos** (en los puntos del scatter, el detalle de no conformes y la
> muestra de cohorte). Se genera con `runner.py` en la máquina de cada quien —y **eso sí** necesita
> las dependencias y el acceso—. No se manda por correo ni se sube a ningún repositorio.

---

# Los motores — parámetros, formatos y ejemplos

El catálogo tiene **18 casos**; **9 son ejecutables** hoy. Los otros 9 declaran su bloqueo, y
`--listar` los muestra con su motivo:

```
python validador\cli.py --listar
```

## Cómo se pasan los parámetros

| tipo | formato | cómo se pasa |
|---|---|---|
| `fecha` | `AAAA-MM-DD` | `--param fecha_ini=2026-08-10` |
| `entero` | dígitos | `--param limite=20000` |
| `decimal` | punto decimal, sin separador de miles | `--param dias_anio=360` |
| `texto` | palabra del vocabulario del caso | `--param delimitador=live` |
| `lista_cuentas` | archivo, un `account_number` por línea | `--cohorte-archivo cuentas.txt` |
| `lista_llaves_of` | archivo, tres números por línea (`1-10-370` o `1,10,370`) | `--cohorte-of-archivo llaves.txt` |

En los dos archivos de cohorte, **las líneas que empiezan con `#` se ignoran** — por eso el
generador escribe ahí la procedencia de la muestra.

Tres reglas que evitan la mayoría de los tropiezos:

- **Las fechas `_fin` y `--hasta` son EXCLUSIVAS.** Para un solo día, pongan el día siguiente.
- **Sin `--confirmar` no se conecta.** El modo por defecto enseña el plan y el SQL sin tocar nada.
- **`--explicar` lista los parámetros requeridos** de cualquier caso, con su nota.

---

## Captación

### `REND-PLAZO` — rendimiento de inversión a plazo fijo

Reproduce el interés periodo a periodo. Tolerancia `0.01` por evento, con prueba de sesgo.
Llave de comparación: `(cuenta, periodo)`.

| parámetro | tipo | |
|---|---|---|
| `cohorte` | lista_cuentas | **requerido** — vía `--cohorte-archivo` |
| `fecha_ini` / `fecha_fin` | fecha | **requeridos** — sobre `payment_date`, `fin` exclusiva |
| `delimitador` | texto | **requerido** — `live` o `migrado` |
| `dias_anio` | decimal | `360` |
| `tasa` | decimal | si se omite, **se despeja del periodo 1** |

**`delimitador` son dos experimentos distintos y no se mezclan:** `live` (`origin is null`) valida
lo que AurumCore generó y confirma **C = B**; `migrado` (`origin = 'FINSUS'`) valida lo ingestado de
OpenFin y confirma **C = A**.

Primero la cohorte:

```
python validador\cohorte.py --producto 2301 --desde 2026-09-01 --hasta 2026-09-02 --delimitador live --criterio censo --salida cuentas.txt
```

> **Si su copia no trae `validador\cohorte.py`**, es un añadido posterior al paquete que
> recibieron; se los pasamos aparte. Mientras tanto el caso corre igual con un archivo hecho a
> mano: un `account_number` por línea, y las líneas que empiezan con `#` se ignoran.
>
> ```
> # cohorte armada a mano — declarar aqui como se eligio
> 100-2301-0000123
> 100-2301-0000456
> ```
>
> Lo que aporta el generador no es el archivo sino **la procedencia**: escribe dentro cuántas
> cuentas había disponibles, cuántas se tomaron, qué fracción representa y con qué criterio. Si lo
> arman a mano, **anoten eso en los comentarios** — es la pregunta que la auditoría hace primero.

```
python validador\cli.py --caso REND-PLAZO --confirmar --cohorte-archivo cuentas.txt --param fecha_ini=2026-09-01 --param fecha_fin=2026-09-02 --param delimitador=live
```

### `REND-VISTA` — interés de cuenta a la vista

Llave: `(cuenta, fecha_capitalizacion)`. Tolerancia `0.01` con prueba de sesgo.

| parámetro | tipo | |
|---|---|---|
| `fecha_cierre` | fecha | **requerido** — `record_date` de donde salen SPM y tasa |
| `fecha_pago` | fecha | **requerido** — `process_date` del pago |
| `limite` | entero | `5000` — cota operativa; súbanla para censo |
| `dias_anio` | decimal | `360` |
| `tasa` | decimal | normalmente viene por fila |

**Las dos fechas van desfasadas un día** y el orden importa: el ciclo cierra el 31 y paga el 1. Si
ponen la misma fecha en ambas, el join no encuentra historia y el universo sale **vacío**.

```
python validador\cli.py --caso REND-VISTA --confirmar --param fecha_cierre=2026-08-31 --param fecha_pago=2026-09-01 --param limite=400000
```

## Fiscal

### `ISR-03` — parámetros fiscales configurados vs la norma

El más barato de correr: **un solo parámetro y sin cohorte**. Compara la configuración del core
contra la ley del año de causación, con tolerancia **`0.00` exacta**.

| parámetro | tipo | |
|---|---|---|
| `anio_causacion` | entero | **requerido** |

```
python validador\cli.py --caso ISR-03 --confirmar --param anio_causacion=2026
```

### `ISR-02` — descuadre OpenFin vs AurumCore = diferencia de modelo

Necesita una cohorte de **llaves de OpenFin**, no de cuentas. Tolerancia `0.02`.

| parámetro | tipo | |
|---|---|---|
| `cohorte_of` | lista_llaves_of | **requerido** — vía `--cohorte-of-archivo` |
| `fecha_ini` / `fecha_fin` | fecha | **requeridos** |
| `anio_causacion` | entero | `2026` |
| `uma_anual` | decimal | `42794.64` |
| `tasa_anual` | decimal | `0.9` |
| `multiplicador_uma` | decimal | `5` |
| `dias_anio` | decimal | `365` — ojo: ISR es 365, no 360 |
| `modo_final` | texto | `Round2` |

El archivo de llaves lleva una por línea:

```
1-10-370
1-10-233102
```

```
python validador\cli.py --caso ISR-02 --confirmar --cohorte-of-archivo llaves.txt --param fecha_ini=2026-02-03 --param fecha_fin=2026-08-04
```

> Los parámetros normativos (`uma_anual`, `tasa_anual`, `multiplicador_uma`) traen el valor de la
> **ley**, no el del core. Cambiarlos para que cuadre sería ajustar la regla al dato.

## Crédito y regulatorio

### `CAT-01` — Costo Anual Total, estrato per-contrato

Llave: `contrato`. Tolerancia `0.01` **puntos porcentuales**, con prueba de sesgo.

| parámetro | tipo | |
|---|---|---|
| `umbral_constante` | entero | `100` — cuántos contratos deben compartir un mismo `cat` para tratarlo como constante copiada |
| `limite` | entero | `20000` |

Corre sin argumentos: los dos tienen default.

```
python validador\cli.py --caso CAT-01 --confirmar
```

**Bajar `umbral_constante` amplía el universo** hacia contratos cuyo `cat` comparten pocos; subirlo
lo restringe a los claramente per-contrato.

> Bloqueo abierto (**SOL-015**): falta la convención de días. El residuo **no se atribuye a
> AurumCore** hasta cerrarlo.

### `IFRS9-E3` — reserva de capital en etapa 3

Llave: `stage_id`. Tolerancia `0.01` con prueba de sesgo.

| parámetro | tipo | |
|---|---|---|
| `fecha_ini` / `fecha_fin` | fecha | **requeridos** — sobre `information_date`, `fin` exclusiva |
| `limite` | entero | `20000` |

```
python validador\cli.py --caso IFRS9-E3 --confirmar --param fecha_ini=2026-08-01 --param fecha_fin=2026-09-01
```

**Alcance deliberadamente estrecho:** sólo etapa 3, consumo, zona no marginada. Los porcentajes de C
salen de las Tablas del GTM, **no** de `lc_reserve_ifrs` — leerlos del core probaría que es
consistente consigo mismo, no que aplica la norma.

### `GAPB-IDNC` — suspensión de devengo en cartera vencida

Identidad de suma cero sobre `stage_id`, tolerancia **`0.00` exacta**.

| parámetro | tipo | |
|---|---|---|
| `fecha_ini` / `fecha_fin` | fecha | **requeridos** |

```
python validador\cli.py --caso GAPB-IDNC --confirmar --param fecha_ini=2026-07-01 --param fecha_fin=2026-08-19
```

> **Contradicción abierta (AUD-001).** La identidad declarada `io + io_venc = 0` **no se reproduce**,
> y no se ajustó por cuenta propia: se levantó la mano. Si lo corren, esperen violaciones — son el
> hallazgo, no un fallo de la herramienta.

## Transaccional y contable

### `CONTABLE-B1` — doble partida diaria

Identidad de suma cero por `fecha`. Tolerancia **`0.00` exacta, sin excepción**: no es un cálculo
con redondeo.

| parámetro | tipo | |
|---|---|---|
| `fecha_ini` / `fecha_fin` | fecha | **requeridos**, `fin` exclusiva |

```
python validador\cli.py --caso CONTABLE-B1 --confirmar --param fecha_ini=2026-08-10 --param fecha_fin=2026-08-17
```

### `COMPLETITUD` — existencia OpenFin vs AurumCore

Cruce de conjuntos sobre `id_inversion`: verifica que **no falte** nada en B. Admite cohorte por
cualquiera de los dos lados, o ninguna.

| parámetro | tipo | |
|---|---|---|
| `fecha_ini` / `fecha_fin` | fecha | **requeridos** |
| `cohorte` | lista_cuentas | opcional |
| `cohorte_of` | lista_llaves_of | opcional |

```
python validador\cli.py --caso COMPLETITUD --confirmar --param fecha_ini=2026-08-01 --param fecha_fin=2026-08-19
```

---

## Cómo leer cualquier resultado

```
estado: SIN-VIOLACIONES | VIOLACIONES | SESGO | ERROR
universo: N filas · violaciones: M
matriz A/B/C: B=C (sin A)=... · B!=C (sin A)=... · sin C=...
sesgo: no detectado (p=...) | DETECTADO (p=..., +x/-y)
```

- **`sin C`** = el oráculo **no pudo** calcular esa fila. Cuenta como violación, no se descarta:
  descartar lo que no se pudo medir subiría el porcentaje **por no haberlo medido**.
- **`SESGO` no es un defecto todavía.** El orden para diagnosticarlo es (1) ¿se redondeó half-up
  como el core?, (2) ¿es precisión de la base?, (3) sólo si sobrevive a ambas es candidato a defecto
  del core. Ha pasado cuatro veces y las cuatro era del método.
- **Cero violaciones = cero violaciones *en ese universo*.** No dice nada fuera de él.

---

## Si algo falla

| síntoma | causa |
|---|---|
| `conda activate` no hace nada / "not recognized" | están en PowerShell sin `conda init powershell`. Usen el **Miniforge Prompt** (o Anaconda Prompt) |
| `El token '&&' no es un separador válido` | PowerShell 5.1 no soporta `&&`. Un comando por línea |
| `'cp' no se reconoce` | es cmd, no PowerShell: usen `copy` |
| `ModuleNotFoundError: pyarrow` a media corrida | falta `pyarrow`; no es opcional aunque nada lo importe directo |
| `timeout` al conectar | ruta a `10.10.0.0/16` — su IT, no el oráculo |
| `ExtraccionNoAcotada` | la consulta pasó de 500,000 filas. **Aborta en vez de truncar**, a propósito |
| `faltan parametros requeridos` | el caso pide `--param`; `--explicar` los lista |
| universo vacío en `REND-VISTA` | `fecha_cierre` y `fecha_pago` deben ir desfasadas un día |
| el tablero muestra datos viejos | puede haber otro `servidor.py` vivo en el mismo puerto |

Para cerrar servidores colgados, en PowerShell:

```
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*servidor.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

---

**Verde no es dictamen.** Cada validación devuelve las filas que violan la regla; cero filas
significa cero violaciones **en ese universo**, no que el motor esté bien fuera de él. El dictamen
lo emite el humano.
