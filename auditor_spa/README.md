# Tablero del auditor independiente — motor C

SPA que ejecuta cada motor de cálculo contra la base, muestra el resultado con
transparencia total y un agente que lo explica con las fuentes del proyecto.

> **Verde no es aprobado.** Cada porcentaje sale de una validación que devuelve
> *las filas que violan la regla*. El valor del tablero está en los **no
> conformes bien explicados**, no en los verdes. El dictamen lo emite el humano.

---

## Correr

```bash
pip install -r ../requirements.txt
```

```bash
python backend/runner.py
```

Corre las **autopruebas de fórmula** (sin base de datos: cada oráculo debe
reproducir el ejemplo de su GTM) y escribe `resultados/<motor>.json` +
`spa/datos.js`.

Para cruzar contra la base — solo lectura, con tus credenciales de
`db_connections.yaml`:

```bash
python backend/runner.py --con-bd --motor PLAZO --cohorte-archivo cohorte.txt --param fecha_ini=2025-01-01 --param fecha_fin=2026-08-22 --param delimitador=live
```

Y para rearmar el tablero **sin volver a golpear la base** —útil cuando no hay
red, o cuando sólo cambió la presentación:

```bash
python backend/runner.py --desde-evidencia
```

Lee el universo de la evidencia ya guardada por el validador. No inventa nada:
son los datos de una corrida que ocurrió, y el JSON conserva el nombre del
directorio de evidencia. **No republica** evidencia de un caso cuya consulta se
retiró — pasó con `ISR-01`, cuyas 27 violaciones eran defecto de la consulta y
no del core.

Cada motor necesita **sus** parámetros, así que los cruces se corren de uno en
uno. Al regenerar el conjunto, un cruce ya calculado **se conserva**: borrar
evidencia por regenerar el índice sería perder cobertura sin darse cuenta.

## Ver

```bash
python backend/servidor.py
```

Abre `http://localhost:8777`. **Con el servidor, el botón "Ejecutar" funciona**:
dispara el motor contra la base y refresca la tarjeta al terminar.

También abre `spa/index.html` desde el disco, sin servidor — los datos van en
`spa/datos.js` porque el navegador bloquea `fetch()` sobre `file://`. En ese
modo el botón "Ejecutar" queda inactivo y lo dice; todo lo demás funciona.

### Apariencia

Selector en la barra superior, con tres modos que se guardan por navegador:

- **Auto** — sigue el `prefers-color-scheme` del sistema.
- **Linko** — los tokens reales del design system en `_ds/`: verde de marca
  `#02b101`, tinta `#09353b`, superficie `#f8faf8`, esquinas de 20 px y píldoras.
  Hay una prueba que compara los valores contra `tokens/colors.css`, así que si
  el design system cambia, obliga a re-sincronizar en vez de dejar una paleta
  parecida pero distinta.
- **Oscuro** — forzado, independiente del sistema.

Dos decisiones que vale la pena señalar:

**El verde de marca no se usa como veredicto.** `#02b101` es identidad; el verde
semántico de "conforme" es otro. Si fueran el mismo, la marca parecería un
dictamen — y hay una prueba que lo impide.

**La fuente no se importa.** `tokens/fonts.css` trae un `@import` de Google
Fonts y este SPA no carga nada remoto; se usa la pila de respaldo que el propio
token declara (Helvetica Neue / Arial).

Al cambiar de tema el scatter se re-dibuja: lee los colores del CSS en cada
pintado, así que sin re-pintar quedaría con la paleta anterior sobre el fondo
nuevo.

### Navegación

- **Home** — galería con las 16 tarjetas: estado, % y categoría.
- **☰** — casos agrupados por **Captación · Fiscal · Crédito ·
  Transaccional/Contable · Padrón**. Salta entre casos sin volver al home, y
  "ver todos" filtra la galería por categoría.
- **Pantalla individual** — fórmula, contra qué se valida, conteo, las tres
  granularidades, el scatter y la explicación de los no conformes.

### El botón "Ejecutar"

`POST /api/run/<motor>` responde de inmediato con `202` y un `job_id`; el
trabajo corre en un hilo aparte y el frontend hace poll a `GET /api/job/<id>`
hasta `terminado` o `error`. La UI nunca se bloquea: el botón se deshabilita,
aparece una barra de avance y al final el timestamp de la corrida.

**El botón sólo aparece activo si el caso se puede correr hoy.** Esa bandera la
calcula el backend contra el catálogo del validador, no la deduce el frontend:
un caso puede existir y aun así no ser ejecutable — `ISR-01` tiene su consulta
retirada, `DIARIO-B` espera el catálogo de normalización. Ofrecer un botón que
el backend va a rechazar sería prometer una corrida que no puede pasar.

### Cuando no hay porcentaje (§3.2)

Un `%` ausente **no es cobertura ausente**. El backend calcula un campo
`cobertura` — `datos` · `config` · `sin_cruce` — y la tarjeta elige su texto por
ese campo, **no** por si hay porcentaje ni inspeccionando los chips: es una
afirmación sobre la evidencia, no una decisión de presentación.

- **`config`** — el oráculo reproduce la tabla de configuración del propio core.
  La tarjeta muestra la evidencia (`lc_reserve_ifrs 37/37 · lc_risk_stage`), no
  un guion, y explica que una configuración no es una cohorte: por eso no hay %,
  y por eso es **más fuerte** que uno.
- **`sin_cruce`** — lo dice sin adornos: *"Eso no es un pase."*
- El botón apagado trae `motivo_no_ejecutable`, redactado por el backend. Nunca
  un botón muerto sin explicación.

### Las tres granularidades

Cada motor de cálculo muestra su cuadre a **1e-8** (exactitud aritmética
estricta), **1e-5** (precisión intermedia) y **centavo** (tolerancia de
negocio), con `comparadores/tolerancias.py`.

**El escalón entre niveles es lo diagnóstico**, más que cualquier número solo:
100/100/100 es cuadre exacto; bajo a 1e-8 pero alto al centavo significa
residuo sub-centavo del snapshot y **no defecto**; bajo también al centavo es
diferencia material que hay que investigar. La tarjeta escribe esa lectura, no
sólo las barras.

Y al centavo no basta: sobre el residuo fuera de 1e-8 corre una **prueba de
signo**. Si las diferencias se cargan a un lado es **sesgo sistemático,
severidad 1** aunque cada una sea de un centavo. Verde al centavo *con* sesgo
no es aprobado.

Los motores de identidad (**Contable**, **Motor B**) no muestran las tres
barras: declaran su tolerancia propia (`0.00 exacto`, `A ≥ B`) y por qué. No
comparan dos importes calculados, así que un escalón de precisión ahí no
significaría nada.

---

## Qué muestra cada tarjeta

| elemento | qué dice |
|---|---|
| **Badge de estado** | validado · parcial · bloqueado · sin cruce |
| **Badge de origen** | **de dónde salió el número** — ver abajo |
| **Barra de %** | match sobre el universo comparado |
| **Fórmula** | tal como está en el documento, en monoespaciado |
| **Chips "valida contra"** | `config` (el valor está en una tabla de Aurum: la más fuerte) · `norma` · `doc` (+página) · `inferencia` (a rayas: **por confirmar**) |
| **Conteo** | comparadas · conformes · no conformes · tolerancia · conformes omitidos del gráfico |
| **Scatter** | ver abajo |
| **No conformes** | por qué no cuadran, clasificados |
| **Explicar** | abre el agente con ese motor |

### El badge de origen es lo que sostiene la honestidad

- **Calculado aquí** — el porcentaje lo computó esta máquina, contra la base, en
  la corrida indicada. Trae evidencia.
- **Citado del dossier** — lo reporta el `DOSSIER_MOTORES_ORACULO_C.md` de una
  corrida previa hecha en el repo de validación. **Este tablero no lo
  recalculó.**
- **Sin cruce** — hay fórmula y autoprueba, no hay cruce contra datos. No es un
  pase.

Pintar los tres en una sola barra verde sería exactamente el "todo pasa" que
este producto existe para evitar. Se pueden filtrar por origen.

### El scatter

Eje X la magnitud del caso, eje Y `delta = C − B`. Los conformes se agrupan en
cero, en verde tenue; **los no conformes saltan en rojo y se dibujan encima**
para que nunca queden tapados. La banda verde es la tolerancia.

Controles: **solo no conformes** · **escala log** (para CAT y GAT, con outliers
extremos) · **tolerancia editable**, que recolorea en vivo — sirve para ver
cuánto margen hay realmente entre "cuadra" y "cuadra por poco".

Hover muestra id, B, C, delta y motivo. Click abre el agente con ese punto.

**Muestreo honesto:** si hay demasiados puntos se muestrean los conformes, pero
**los no conformes van siempre completos** y la tarjeta rotula cuántos
conformes se omitieron. La cobertura no se esconde.

### Clasificación de los no conformes

Distinguirlos es el trabajo del auditor: reportar linaje como defecto es tan
grave como ocultar un defecto.

| clase | significado |
|---|---|
| `defecto` | el motor calcula distinto de la regla. **Es hallazgo.** |
| `linaje` | el dato de contraste discrepa entre tablas; el motor no está en duda |
| `data-sourcing` | falta el insumo punto-en-tiempo para comparar de forma justa |
| `bloqueo` | no hay corrida todavía (tiempo o log faltante) |
| `redondeo` | diferencia sub-centavo por modo de redondeo no desambiguado |

---

## El agente

Responde con **secciones reales** del dossier, el NORTE, el índice, la
comparación, las solicitudes y las piezas K — y **siempre cita de cuál sale**,
con documento y línea.

Si la pregunta no tiene respaldo en el corpus, **lo dice** y remite al `SOL-*`
correspondiente en vez de improvisar. Un tablero de auditoría que inventa una
explicación vale menos que uno que calla.

Es recuperación sobre el corpus, no un modelo. Cablearlo a uno es directo
(`responder()` en `index.html`), pero la regla de no inventar tendría que
sobrevivir al cambio.

---

## Los feeds de log

El runner **no hace SSH ni extrae logs**. Los feeds los produce otro proceso
(`log_extractor.py`, `barrido_average_balance.py`) y llegan como CSV a
`40_validaciones/_resultados/`. El tablero marca qué motores dependen de logs y
la fecha del feed. **Sin feed, el motor queda bloqueado** — no se sustituye por
una aproximación presentada como validación.

---

## Estructura

```
auditor_spa/
├── backend/
│   ├── motores.py    tabla declarativa de los 16 motores (espejo del DOSSIER)
│   ├── runner.py     ejecuta y escribe los JSON + datos.js
│   └── dossier.py    corta los documentos en secciones citables para el agente
├── resultados/       JSON por motor + indice.json + conocimiento.json (regenerables)
├── spa/
│   ├── index.html    el tablero (autocontenido, sin CDN)
│   └── datos.js      los datos empaquetados (regenerable)
└── README.md
```

`motores.py` **no calcula nada**: declara qué afirma cada motor, con qué
fórmula, contra qué se valida y con qué fuente. Los cálculos viven en los
oráculos de `40_validaciones/`, que ya existían y no se duplicaron.

## Antes de construir un caso nuevo

Lee **[`validador/guia/CONSTRUIR_UN_CASO.md`](../validador/guia/CONSTRUIR_UN_CASO.md)**
(§11 del brief). Resume lo que ya costó redescubrir:

1. **Independencia** — los parámetros de C salen de la fuente, no de la config
   del core que estás probando. Si tienes que leer un parámetro del core,
   detente o decláralo.
2. **Convenciones confirmadas** — half-up por evento; base de días por producto,
   confirmada del esquema y no asumida; `Decimal` con modo explícito.
3. **Playbook del sesgo** — antes de gritar severidad 1: ¿redondeaste como el
   core? ¿es precisión de la base? Sólo si sobrevive a ambas es candidato a
   defecto. Ha pasado tres veces y las tres el sesgo era del método.
4. **Alcance declarado** — escribe lo que dejas fuera y por qué.

No es sólo documentación: `validador/tests/test_guia_casos.py` falla si un caso
nuevo ignora cualquiera de las cuatro.

## Seguridad

Solo lectura contra la base. Sin credenciales ni PII al frontend: los JSON
llevan agregados y una muestra con identificadores truncados a 24 caracteres.
`datos.js` y `resultados/` están en `.gitignore` porque contienen filas de
clientes reales.
