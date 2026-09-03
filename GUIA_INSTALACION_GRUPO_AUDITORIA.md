# Guía de instalación y ejecución — grupo auditoría de Finsus

> Cómo instalar el oráculo (motor C), correr las validaciones y levantar el tablero. **En Windows.**
> Complementa `40_validaciones/MANUAL_USO_ORACULO_AUDITOR.md`, que cubre los comparadores;
> aquí va además lo que necesitan el **validador** y el **tablero**.
> Todo es **solo lectura**: el código rechaza cualquier SQL con verbos de escritura antes de conectar.

## 0. Antes que nada: usen el **Anaconda Prompt**

Menú Inicio → **Anaconda Prompt (anaconda3)**. No PowerShell, no la terminal de VS Code. Dos razones
concretas:

- **`conda activate` no funciona en PowerShell** hasta que alguien corra `conda init powershell` y
  reinicie la terminal. En el Anaconda Prompt funciona de entrada.
- **PowerShell 5.1 —el que trae Windows de fábrica— no entiende `&&`.** No es que falle a medias:
  es un error de sintaxis. Los comandos de esta guía están pensados para el Anaconda Prompt.

> Si de todos modos prefieren PowerShell, cada comando de esta guía va **en una sola línea**, sin
> `&&`, precisamente para que funcione en ambos. Donde haya diferencia, se indica.

## 1. ¿Anaconda sirve? Sí — con dos ajustes

Todas las dependencias están en `conda-forge`. Dos cosas cambian respecto a `pip`:

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
| `pytest auditor_spa validador 60_informe` | **490 pruebas, 0 fallos** |
| `sanity_check.py` (Finsus) | SANO + auto-prueba de falsabilidad OK |
| `sanidad.py` (tablero) | SANO, 0 violaciones en 15 invariantes |
| `cli.py --autopruebas` | todas pasan |
| `cli.py --listar` · `--explicar` · `--probar-conexion` | correctos |
| `cohorte.py --help` | correcto |
| `runner.py` | regenera los JSON y `datos.js` |
| `servidor.py` + `/api/sanidad` | el tablero sirve y responde SANO |

El desarrollo fue en 3.14, pero el código no usa nada posterior a 3.10.

> **Ojo con las rutas:** los comandos de esta guía se invocan **desde la raíz del repositorio** con
> rutas tipo `python validador\cli.py`, no entrando a cada carpeta. Se verificó que los scripts
> resuelven sus rutas internas solos, así que no hace falta `cd` a subcarpetas — lo cual evita el
> `cd X && comando`, que es justo lo que rompe en PowerShell.

## 2. Instalación

```
conda create -y -n auditor -c conda-forge python=3.11 polars duckdb pyarrow psycopg2 pyyaml pytest
```

Tarda varios minutos resolviendo — es normal, no está colgado.

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

### Alternativa sin Anaconda

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

En **PowerShell** la segunda línea es distinta: `.venv\Scripts\Activate.ps1` (y puede pedir
`Set-ExecutionPolicy -Scope Process RemoteSigned`).

## 3. Situarse en la carpeta

Todos los comandos siguientes asumen que están en la raíz del repositorio:

```
cd C:\ruta\donde\clonaron\finsus_core_migration_auditor
```

Si están en otra unidad (D:, por ejemplo), primero `D:` y luego el `cd`.

## 4. Credenciales (cada quien pone las suyas)

En el Anaconda Prompt o cmd:

```
copy validador\db_connections.example.yaml validador\db_connections.yaml
```

En PowerShell sería `Copy-Item` (aunque `copy` funciona ahí como alias).

Se edita con **credenciales de solo lectura**. El archivo está en `.gitignore` junto con cualquier
derivado (`.bak`, `.old`, copias con fecha): **nunca se versiona**.

```
python validador\cli.py --probar-conexion
```

Esto no sólo abre la conexión: **intenta escribir y verifica que el servidor lo rechace**. Si la
escritura pasa, el usuario no es de solo lectura y hay que parar ahí.

> Si no hay conexión, el comando termina con código distinto de cero. Es correcto, no está roto:
> así un script de arranque puede detectarlo.

> Si da *timeout*, es la ruta a la subred `10.10.0.0/16` — es tema de su IT, no del oráculo.
> Ver `40_validaciones/ACCESO_Y_RED.md`.

## 5. Verificar la instalación — sin tocar la base

Estos tres **no necesitan conexión** y son la mejor primera prueba:

```
python 40_validaciones\comparadores\sanity_check.py
```

Debe decir **SANO** y que la auto-prueba de falsabilidad atrapa los dos bugs históricos.

```
python auditor_spa\backend\sanidad.py
```

Los 15 invariantes del tablero. **SANO = 0 en todos**; no hay "casi sano".

```
python -m pytest auditor_spa validador 60_informe -q
```

## 6. Correr una validación

Primero, **ver el plan sin tocar nada** (es el modo por defecto):

```
python validador\cli.py --listar
```
```
python validador\cli.py --caso REND-VISTA --explicar
```

`--explicar` muestra la identidad, la tolerancia, los supuestos y **qué deja fuera el caso**. Para
ejecutar de verdad hay que decirlo con `--confirmar`:

```
python validador\cli.py --caso REND-VISTA --confirmar --param fecha_cierre=2026-08-31 --param fecha_pago=2026-09-01 --param limite=400000
```

Algunos casos piden una **cohorte** (lista de cuentas). Se genera con su procedencia dentro:

```
python validador\cohorte.py --producto 2301 --desde 2026-09-01 --hasta 2026-09-02 --delimitador live --criterio censo --salida cuentas.txt
```
```
python validador\cli.py --caso REND-PLAZO --confirmar --cohorte-archivo cuentas.txt --param fecha_ini=2026-09-01 --param fecha_fin=2026-09-02 --param delimitador=live
```

> `--hasta` y `fecha_fin` son **exclusivas**: para un solo día, el día siguiente.

### Dónde queda la evidencia

Cada corrida escribe `validador\reportes\<CASO>_<fecha>_<hash>\`:

| archivo | qué es |
|---|---|
| `violaciones.parquet` | **las filas que rompen la regla** — el producto |
| `universo.parquet` | todo lo que se comparó |
| `consultas.sql` | el SQL **exacto** que se envió al servidor |
| `manifiesto.json` | parámetros, snapshot, hash, tolerancia, supuestos |

Con `consultas.sql` y `manifiesto.json` pueden **reejecutar la consulta a mano** y comparar contra
lo que el manifiesto reporta. Si esos dos números no coinciden, nada de lo demás importa — es la
comprobación que recomendamos hacer primero.

Los `.parquet` se abren con DBeaver vía DuckDB. En el SQL usen **barras normales** (`/`) aunque
estén en Windows: DuckDB trata `\` como escape.

## 7. Levantar el tablero

```
python auditor_spa\backend\runner.py
```

Eso genera los JSON por motor. Después:

```
python auditor_spa\backend\servidor.py --puerto 8777
```

Y se abre **http://localhost:8777**. La ventana queda ocupada mientras el servidor corre; para
detenerlo, `Ctrl+C`.

**Sin servidor también funciona:** `runner.py` deja `auditor_spa\spa\datos.js` empaquetado, así que
`auditor_spa\spa\index.html` se abre con doble clic. Pierden el botón "Ejecutar" (que necesita el
backend), no la información.

En el menú hamburguesa hay dos vistas pensadas para ustedes:

- **Criterios de auditoría** — los 13 criterios de F-032 con enlace al motor o documento que atiende cada uno.
- **Glosario de estados** — qué significa cada etiqueta, renderizado del documento del bundle.

## 8. Si algo falla

| síntoma | causa |
|---|---|
| `conda activate` no hace nada / "not recognized" | están en PowerShell sin `conda init powershell`. Usen el **Anaconda Prompt** |
| `El token '&&' no es un separador válido` | PowerShell 5.1 no soporta `&&`. Un comando por línea, o usen el Anaconda Prompt |
| `'cp' no se reconoce` | es cmd, no PowerShell: usen `copy` |
| `ModuleNotFoundError: pyarrow` a media corrida | falta `pyarrow`; no es opcional aunque nada lo importe directo |
| `timeout` al conectar | ruta a `10.10.0.0/16` — su IT, no el oráculo |
| `ExtraccionNoAcotada` | la consulta pasó de 500,000 filas. **Aborta en vez de truncar**, a propósito: truncar en silencio reportaría cobertura que no se midió |
| `faltan parametros requeridos` | el caso pide `--param`; `--explicar` los lista |
| el tablero muestra datos viejos | puede haber otro `servidor.py` vivo en el mismo puerto. Windows deja que dos procesos escuchen el 8777 y contesta cualquiera. Ver abajo |

Para cerrar servidores colgados, en PowerShell:

```
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*servidor.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

---

**Verde no es dictamen.** Cada validación devuelve las filas que violan la regla; cero filas
significa cero violaciones **en ese universo**, no que el motor esté bien fuera de él. El dictamen
lo emite el humano.
