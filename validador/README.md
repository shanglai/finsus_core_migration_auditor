# VALIDADOR Independiente — motor C

Herramienta de auditoría del cálculo de AurumCore. Ejecuta, caso por caso, las
reglas de negocio y normativas **desde la fuente** (norma, documento oficial,
pieza de conocimiento) y devuelve **las filas que no cumplen**.

Tiene dos usos y son el mismo código:

1. **Pre-auditor interno.** Se corre de forma adversaria *antes* de mostrar
   cualquier hallazgo a Finsus. Un hallazgo que no sobrevive su propio
   validador no se reporta.
2. **Entregable a Finsus.** Finsus lo corre con **sus propios accesos**, elige
   caso y parámetros, **lee cada consulta antes de que toque la base**, y
   obtiene el mismo diagnóstico.

> **Lo que esta herramienta no hace: firmar.** No emite un semáforo verde. Emite
> violaciones, celdas de la matriz A/B/C, y un manifiesto de qué se corrió y qué
> no. **Un caso no corrido se marca NO-CORRIDO, jamás "OK".**

---

## Instalación

```bash
pip install -r validador/requirements.txt
```

## Credenciales

**De solo lectura, y nunca en el repositorio.**

```bash
cp validador/db_connections.example.yaml validador/db_connections.yaml
```

Se busca `db_connections.yaml` en dos lugares, en este orden:

1. `validador/db_connections.yaml`
2. `db_connections.yaml` en la raíz del repo — la convención que ya usaba
   `40_validaciones/comparadores/fase1_isr_runner.py`

Se aceptan **las dos formas** del archivo: con la llave `cores:` (la del
validador) y sin ella (la previa, con `aurum:` y `openfin:` al primer nivel).
Aceptar ambas evita el fallo más tonto posible: credenciales correctas y un
"no hay conexión configurada" por la sangría del archivo. También se admite un
DSN completo por ambiente: `AC_DSN` y `OF_DSN`.

La contraseña se toma preferentemente de una variable de ambiente
(`password_env`), no del archivo. Ambas rutas están en `.gitignore`, y hay una
prueba que falla si alguna vez quedan versionadas.

### Prueba de vuelo previa

```bash
python cli.py --probar-conexion
```

No corre ningún caso ni lee datos de clientes. Conecta en solo lectura y
responde: a qué base, con qué usuario, si es la réplica, y si el servidor
**rechaza** una escritura. Esto último lo comprueba de verdad —intenta crear
una tabla temporal y verifica que falle—, porque confiar en que la sesión es
de solo lectura sin comprobarlo es el tipo de supuesto que este proyecto no
acepta.

---

## Uso

```bash
python cli.py --listar
```

Catálogo por motor, con el estado de cada caso y si hoy tiene con qué correrse.

```bash
python cli.py --explicar ISR-01
```

Los cinco apartados del caso, generados desde su YAML: **(a)** qué afirma y de
qué pieza sale la regla · **(b)** de dónde salen los datos y con qué llaves se
cruzan · **(c)** parámetros y sus valores · **(d)** tolerancia · **(e)** qué
significa el resultado. Incluye los **supuestos** de modelado, si los tiene.

```bash
python cli.py --caso ISR-01 --dry-run \
  --cohorte-archivo mis_cuentas.txt \
  --param fecha_ini=2026-07-01 --param fecha_fin=2026-08-04
```

Imprime **el SQL exacto** que se enviaría, con la cohorte ya inyectada y los
parámetros resueltos. No se conecta a nada. Es el modo por omisión.

```bash
python cli.py --caso ISR-01 --confirmar \
  --cohorte-archivo mis_cuentas.txt \
  --param fecha_ini=2026-07-01 --param fecha_fin=2026-08-04
```

Corre contra la base. **`--confirmar` es obligatorio**: sin esa bandera nada
toca producción. Es la misma doble validación humana que ya usa
`fase1_isr_runner.py`.

```bash
python cli.py --cobertura      # regenera reportes/cobertura.md
python cli.py --autopruebas    # la batería completa, sin base de datos
```

---

## Qué produce una corrida

`reportes/<caso>_<fecha>_<hash>/`

| archivo | qué es |
|---|---|
| `violaciones.parquet` | **El producto.** Las filas que no cumplen la identidad, cada una con su `motivo`. |
| `violaciones_muestra.csv` | Las primeras 1,000, para leerlas sin herramientas. |
| `universo.parquet` | Todas las filas evaluadas, con su celda de la matriz A/B/C. |
| `consultas.sql` | Las consultas **exactas** que se ejecutaron. |
| `manifiesto.json` | Caso, parámetros, snapshot, versión de la regla, sha256 del oráculo, resultado, supuestos. |

El `hash` del directorio sale de (caso, parámetros, consultas, versión del
oráculo, tolerancia) — **no de la hora**. Misma entrada, mismo hash, misma
carpeta: re-correr es idempotente, y dos personas con los mismos insumos
producen la misma evidencia.

---

## Cómo está armado

```
validador/
├── catalogo/     CAPA 1 · QUÉ se valida — un YAML por caso, más manifest.yaml
├── engine/       CAPA 2 · motor determinista (extract · warehouse · compare · sesgo · evidencia)
├── oraculos/     motor C · funciones Decimal, una por regla
├── extraccion/   SQL propio del validador (el ya validado se apunta donde vive)
├── reportes/     CAPA 3 · evidencia por corrida + cobertura.md
└── tests/        autopruebas de los oráculos y los invariantes anti-all-pass
```

**El motor no contiene ninguna regla de negocio.** Agregar un requisito es
agregar un YAML (ver `catalogo/_schema.md`), no tocar `engine/`.

Las consultas ya validadas (`40_validaciones/extraccion/*.sql`,
`entrega_finsus/V1..V5.sql`) **no se copiaron aquí**: el catálogo las apunta
donde viven. Dos copias de una consulta significan que nadie sabe cuál se
corrió, y eso rompe la cadena probatoria.

---

## Las reglas que el código impone

**Solo lectura.** El SQL se rechaza si contiene verbos de escritura o DDL
*antes* de conectar; la sesión abre con `default_transaction_read_only = on` y
`readonly=True`; la transacción cierra con `ROLLBACK` siempre. Aun así, el
usuario de base **debe** ser un rol de solo lectura: son capas, no sustitutos.

**Cero float en la ruta del dinero.** Todo cálculo monetario va en
`decimal.Decimal`. Los montos viajan como texto desde la extracción hasta el
oráculo. Una columna monetaria en float **aborta la corrida**; no se convierte.
Polars y DuckDB mueven y cruzan datos — no recalculan dinero.

**Extracción acotada.** Se lee con cursor del servidor pidiendo una fila más
que el límite. Si llega, la corrida **aborta** en vez de truncar. Una muestra
truncada se lee después como universo completo.

**Redondeo explícito.** `Trunc20 · Trunc5 · Ceil10 · RoundHalfEven2 · Round2`
son parámetro por caso, nunca un default global. Donde la fuente es ambigua
(S-FIS-001 no desambigua half_even vs half_up para el ISR), el modo es
parámetro para que la elección quede en el manifiesto de la corrida en vez de
esconderse en el código.

**Independencia.** El oráculo implementa la norma o el documento oficial, nunca
la lógica de un core. Si para calcular hiciera falta mirar cómo lo hace
OpenFin o AurumCore, falta una pieza de conocimiento: el caso se marca
`PENDIENTE` y **no se inventa la regla**. Por eso ocho de los trece casos hoy
no corren — les falta un insumo documental, no código.

---

## Las cinco defensas anti-all-pass

Están en `tests/test_no_all_pass.py` y `tests/test_caso_trampa.py` como
invariantes ejecutables. Si alguien afloja una, la batería se rompe.

1. **Violaciones como salida.** Ningún comparador devuelve un booleano ni un
   total. Devuelve el conjunto de filas que violan la identidad, cada una con
   su motivo. "Cero violaciones" es un resultado, no un valor por omisión.
2. **Matriz A/B/C, celda por celda.** `A=B=C` OK · `A=B≠C` ambos cores mal
   contra la norma (severidad máxima) · `A≠B=C` defecto de OpenFin ya corregido
   · `A=C≠B` defecto de AurumCore · `A≠B≠C` regla mal especificada. Se reporta
   la celda, no un semáforo. La ausencia de motor A se **etiqueta**, nunca se
   cuenta como coincidencia.
3. **Manifiesto de cobertura.** `reportes/cobertura.md` lista **los trece
   casos**, no solo los corridos, y dice **NO-CORRIDO NO ES PASO** en su
   encabezado. Un universo vacío se reporta como "no prueba nada", no como
   limpio.
4. **Prueba de signo obligatoria en devengo.** Un caso con tolerancia de
   redondeo **no puede** declararse sin `prueba_sesgo: true` — el cargador del
   catálogo lo rechaza. Sesgo estadístico ⇒ **severidad 1**, aunque cada
   diferencia sea de un centavo.
5. **Regresión permanente.** Cada hallazgo confirmado se vuelve un invariante
   nuevo en `tests/`. La red solo crece.

**Y casos-trampa.** `tests/test_caso_trampa.py` siembra discrepancias
*conocidas* y verifica que la herramienta las detecte:

- **C-001** — rezago de UMA: el core tiene configurado 5 × UMA 2025
  (206,367.60) mientras la norma 2026 exige 213,973.20. `ISR-03` está diseñado
  para exhibirlo. **Si esa corrida sale limpia, el defecto está en el
  VALIDADOR, no en el core.**
- **C-002** — si el oráculo dividiera entre la base gravable en vez del saldo
  total, el caso de oro reventaría.
- **Sesgo** — 400 diferencias de +0.01: cada evento respeta la tolerancia, el
  agregado está mal por $4.00. Sin la prueba de signo esto es un "cero
  violaciones" impecable.

---

## Estado actual

`python cli.py --cobertura` da la foto exacta. Al 2026-08-20:

- **5 de 13 casos** tienen hoy con qué correr: `ISR-01`, `ISR-02`, `ISR-03`,
  `REND-PLAZO`, `COMPLETITUD`.
- **0 de 13** han sido corridos **por esta herramienta**. Los que el
  `NORTE_VALIDACION.md` marca como validados lo fueron con los comparadores
  anteriores; hasta que esta herramienta los corra aparecen **NO-CORRIDO**, y
  así deben leerse.
- Los 8 restantes esperan un insumo, no código. El detalle, con su motivo, está
  en la segunda tabla de `cobertura.md`.

`COMPLETITUD` es el único ejecutable de punta a punta sin insumos faltantes
—no necesita oráculo, la identidad es el set-diff— y por eso es el mejor primer
caso para probar el pipeline contra la base.

---

## Cómo crece el catálogo

1. **Requisito nuevo** → pieza `K-*` en `10_conocimiento/` → **YAML** en
   `catalogo/` con su `regla_ref`, extracción, oráculo, identidad y tolerancia
   → alta en `manifest.yaml`.
2. **Regla que cambia** → sube la versión de la pieza `K-*` → los casos que la
   citan quedan *revisión requerida* → ajustar oráculo/identidad → re-correr →
   actualizar cobertura.
3. **Hallazgo confirmado** → invariante de regresión permanente en `tests/`.
4. Mantener sincronizados `NORTE_VALIDACION.md`, `manifest.yaml` y
   `cobertura.md`. `--cobertura` verifica la sincronía YAML↔manifest y reporta
   discrepancias; la sincronía contra el NORTE es manual.
