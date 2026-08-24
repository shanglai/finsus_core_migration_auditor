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

Cada motor necesita **sus** parámetros, así que los cruces se corren de uno en
uno. Al regenerar el conjunto, un cruce ya calculado **se conserva**: borrar
evidencia por regenerar el índice sería perder cobertura sin darse cuenta.

## Ver

Abre `spa/index.html`. Funciona **desde el disco, sin servidor**: los datos van
en `spa/datos.js`, porque el navegador bloquea `fetch()` sobre `file://`. Si
prefieres servirlo:

```bash
python -m http.server 8777 --directory spa
```

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

## Seguridad

Solo lectura contra la base. Sin credenciales ni PII al frontend: los JSON
llevan agregados y una muestra con identificadores truncados a 24 caracteres.
`datos.js` y `resultados/` están en `.gitignore` porque contienen filas de
clientes reales.
