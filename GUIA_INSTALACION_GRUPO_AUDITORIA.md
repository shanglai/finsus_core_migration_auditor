# Guía de instalación y ejecución — grupo auditoría de Finsus

> Cómo instalar el oráculo (motor C), correr las validaciones y levantar el tablero.
> Complementa `40_validaciones/MANUAL_USO_ORACULO_AUDITOR.md`, que cubre los comparadores;
> aquí va además lo que necesitan el **validador** y el **tablero**.
> Todo es **solo lectura**: el código rechaza cualquier SQL con verbos de escritura antes de conectar.

## 1. ¿Anaconda sirve? Sí — con dos ajustes

Todas las dependencias están en `conda-forge`. Dos cosas que sí cambian respecto a `pip`:

**(a) El paquete se llama `psycopg2`, no `psycopg2-binary`.** En conda ya viene compilado; el sufijo
`-binary` sólo existe en PyPI. Instalarlo con el nombre de pip dentro de un entorno conda funciona,
pero es la fuente clásica de conflictos.

**(b) No mezclen conda y pip para el mismo paquete.** Si algo se instala con `conda` y luego se
reinstala con `pip`, conda pierde el rastro y las actualizaciones posteriores rompen el entorno.
Regla práctica: **todo por conda**, y sólo lo que no exista ahí por pip, al final.

### Versión de Python

**3.11 o superior.** El desarrollo fue en 3.14, pero el código no usa nada posterior a 3.10 —
sin `match`, sin `except*`, sin PEP 695— y 21 de 24 módulos declaran
`from __future__ import annotations`, que es lo que permite las anotaciones modernas en versiones
anteriores.

## 2. Instalación con Anaconda

```bash
conda create -y -n auditor -c conda-forge python=3.11 polars duckdb pyarrow psycopg2 pyyaml pytest
```

```bash
conda activate auditor
```

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

```bash
python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
```

## 3. Credenciales (cada quien pone las suyas)

```bash
cp validador/db_connections.example.yaml validador/db_connections.yaml
```

Se edita con **credenciales de solo lectura**. El archivo está en `.gitignore` junto con cualquier
derivado (`.bak`, `.old`, copias con fecha): **nunca se versiona**.

```bash
cd validador && python cli.py --probar-conexion
```

Esto no sólo abre la conexión: **intenta escribir y verifica que el servidor lo rechace**. Si la
escritura pasa, el usuario no es de solo lectura y hay que parar ahí.

> Si da *timeout*, es la ruta a la subred `10.10.0.0/16` — es tema de su IT, no del oráculo.
> Ver `40_validaciones/ACCESO_Y_RED.md`.

## 4. Verificar que todo quedó bien — sin tocar la base

Estos tres comandos **no necesitan conexión** y son la mejor primera prueba:

```bash
python 40_validaciones/comparadores/sanity_check.py
```

Debe decir **SANO** y que la auto-prueba de falsabilidad atrapa los dos bugs históricos.

```bash
cd validador && python cli.py --autopruebas
```

Las fórmulas se validan contra los ejemplos del documento oficial. Debe salir N/N.

```bash
python -m pytest auditor_spa validador 60_informe -q
```

## 5. Correr una validación

Primero, **ver el plan sin tocar nada** (es el modo por defecto):

```bash
cd validador && python cli.py --listar
```

```bash
cd validador && python cli.py --caso REND-VISTA --explicar
```

`--explicar` muestra la identidad, la tolerancia, los supuestos y **qué deja fuera el caso**. Para
ejecutar de verdad hay que decirlo explícitamente con `--confirmar`:

```bash
cd validador && python cli.py --caso REND-VISTA --confirmar --param fecha_cierre=2026-08-31 --param fecha_pago=2026-09-01 --param limite=400000
```

Algunos casos piden una **cohorte** (lista de cuentas). Se genera con su procedencia dentro:

```bash
cd validador && python cohorte.py --producto 2301 --desde 2026-09-01 --hasta 2026-09-02 --delimitador live --criterio censo --salida cuentas.txt
```

```bash
cd validador && python cli.py --caso REND-PLAZO --confirmar --cohorte-archivo cuentas.txt --param fecha_ini=2026-09-01 --param fecha_fin=2026-09-02 --param delimitador=live
```

### Dónde queda la evidencia

Cada corrida escribe `validador/reportes/<CASO>_<fecha>_<hash>/`:

| archivo | qué es |
|---|---|
| `violaciones.parquet` | **las filas que rompen la regla** — el producto |
| `universo.parquet` | todo lo que se comparó |
| `consultas.sql` | el SQL **exacto** que se envió al servidor |
| `manifiesto.json` | parámetros, snapshot, hash, tolerancia, supuestos |

Con `consultas.sql` y `manifiesto.json` pueden **reejecutar la consulta a mano** y comparar contra
lo que el manifiesto reporta. Si esos dos números no coinciden, nada de lo demás importa — es la
comprobación que recomendamos hacer primero.

## 6. Levantar el tablero

```bash
cd auditor_spa/backend && python runner.py
```

Eso genera los JSON por motor. Después:

```bash
cd auditor_spa/backend && python servidor.py --puerto 8777
```

Y se abre **http://localhost:8777**.

**Sin servidor también funciona:** `runner.py` deja `auditor_spa/spa/datos.js` empaquetado, así que
`auditor_spa/spa/index.html` se abre directo desde el disco con doble clic. Pierden el botón
"Ejecutar" (que necesita el backend), no la información.

En el menú hamburguesa hay dos vistas pensadas para ustedes:

- **Criterios de auditoría** — los 13 criterios de F-032 con enlace al motor o documento que atiende cada uno.
- **Glosario de estados** — qué significa cada etiqueta, renderizado del documento del bundle.

### Antes de creerle al tablero

```bash
cd auditor_spa/backend && python sanidad.py
```

Devuelve las tarjetas que violan cada uno de los 15 invariantes. **SANO = 0 en todos**; no hay
"casi sano". Si sale algo, imprime cuál y por qué.

## 7. Si algo falla

| síntoma | causa probable |
|---|---|
| `ModuleNotFoundError: pyarrow` a media corrida | falta `pyarrow`; no es opcional aunque nada lo importe directo |
| `timeout` al conectar | ruta a `10.10.0.0/16` — su IT, no el oráculo |
| `ExtraccionNoAcotada` | la consulta devolvió más de 500,000 filas. **Aborta en vez de truncar**, a propósito: truncar en silencio reportaría cobertura que no se midió |
| `faltan parametros requeridos` | el caso pide `--param`; `--explicar` los lista |
| el tablero muestra datos viejos | puede haber otro `servidor.py` vivo en el mismo puerto. Windows deja que dos procesos escuchen el 8777 y contesta cualquiera |

---

**Verde no es dictamen.** Cada validación devuelve las filas que violan la regla; cero filas
significa cero violaciones **en ese universo**, no que el motor esté bien fuera de él. El dictamen
lo emite el humano.
