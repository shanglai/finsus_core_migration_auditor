# Esquema de un caso del catálogo

El catálogo es **la fuente de verdad de QUÉ se valida**. Un caso = un archivo
`<ID>.yaml` en este directorio. El motor (`engine/`) no contiene ninguna regla de
negocio: sólo ejecuta lo que el caso declara. Agregar un requisito = agregar un
YAML (§7 del prompt constructor), no tocar el motor.

`engine/catalogo.py` valida este esquema al cargar. Un YAML que no lo cumple
**aborta la corrida**; no se ejecuta a medias.

---

## Campos

| campo | obligatorio | qué es |
|---|---|---|
| `id` | sí | Identificador `ABC-01`. Único en el catálogo. |
| `titulo` | sí | Qué afirma el caso, en una línea. |
| `motor` | sí | `FIS · DEV · MOV · REG · CTB · COL · PRC · MIG` |
| `dominio` | sí | Dominio de conocimiento (normalmente igual al motor). |
| `regla_ref` | sí | Lista de piezas que lo sustentan (`K-*`, `S-*`, `F-*`, `P-*`, `C-*`). Si una sube de versión, el caso queda "revisión requerida". |
| `severidad` | sí | `1` bloquea go-live · `2` bloquea ciclo · `3` documentar. |
| `tolerancia` | sí | Ver abajo. |
| `parametros` | no | Lo que el CLI pide/permite sobreescribir. |
| `extraccion` | sí | `core → ruta del .sql` (relativa a la raíz del repo) o `PENDIENTE`. |
| `oraculo` | sí | `oraculos/mod.py::funcion` o `PENDIENTE`. |
| `universo` | no | Cómo se arma lo que el oráculo recalcula. Ver abajo. |
| `comparacion` | sí | Llaves y columnas del cruce. Ver abajo. |
| `identidad` | sí | La afirmación, en prosa. Es lo que viola quien aparece en `violaciones.parquet`. |
| `matriz_esperada` | sí | Qué celda A/B/C se espera y por qué. |
| `estado` | sí | `VALIDADO · PARCIAL · PENDIENTE · BLOQUEADO · HALLAZGO` |
| `cobertura_nota` | no | Qué se ha corrido realmente y con qué muestra. |
| `bloqueo` | no | Qué insumo falta, si el caso no se puede correr. |
| `supuestos` | no | Decisiones de modelado no verificadas. **Viajan a la evidencia de cada corrida.** |
| `estado_origen` | no | Lo que el documento fuente afirmaba, para rastrear divergencias. |

### `tolerancia`

```yaml
tolerancia:
  tipo: contable          # contable | redondeo
  max_evento: "0.00"      # CADENA, no número: un float aquí contamina la ruta del dinero
  prueba_sesgo: false
  alfa_sesgo: "0.01"
```

Reglas que el validador de esquema impone y **no se negocian en caliente** (§1.7):

- `tipo: contable` ⇒ `max_evento` debe ser exactamente `"0.00"`.
- `tipo: redondeo` ⇒ `prueba_sesgo` debe ser `true`. Una tolerancia de un centavo
  sin prueba de signo deja pasar el sesgo sistemático, que es severidad 1.
- Todo monto se declara como **cadena entrecomillada**.

### `comparacion`

```yaml
comparacion:
  tipo: igualdad_montos   # igualdad_montos | existencia | doble_partida
  llaves: [cuenta, periodo]
  columna_a: isr_openfin  # opcional: si falta, la matriz corre "sin A"
  columna_b: isr_posteado # el core bajo prueba
  columna_c: isr_oraculo  # el oráculo
  fuente_b: aurum         # de qué core sale B (default aurum)
  fuente_a: openfin       # de qué core sale A (default openfin)
```

`fuente_b` existe porque hay casos donde el motor bajo prueba **no** es AurumCore
(ISR-02 prueba el devengo de OpenFin contra la norma).

### `universo`

Lo que el oráculo recalcula, fila por fila. Dos formas:

```yaml
universo:
  fuente: aurum           # la tabla del core tal cual
```
```yaml
universo:
  sql: |                  # DuckDB sobre las tablas ya cargadas: <caso>_<core>
    SELECT id_cliente, fecha, saldo_base_of AS saldo_base
    FROM isr_02_openfin
```

Los casos de `tipo: existencia` no llevan universo ni oráculo: la identidad es
el set-diff, y para eso bastan las dos consultas.

---

## Plantilla

```yaml
id: ISR-01
titulo: Retencion de ISR al pago = regla normativa
motor: FIS
dominio: FIS
regla_ref: [K-FIS-002, K-FIS-004, S-FIS-001]
severidad: 1
tolerancia: {tipo: redondeo, max_evento: "0.01", prueba_sesgo: true}
parametros:
  - {nombre: cohorte, tipo: lista_cuentas, requerido: true}
  - {nombre: uma_anual, tipo: decimal, default: "42794.64", nota: "por anio de causacion"}
extraccion:
  aurum: validador/extraccion/aurum/isr_al_pago_universo.sql
  openfin: PENDIENTE
oraculo: oraculos/isr.py::fila_isr_retenido
universo: {fuente: aurum}
comparacion:
  tipo: igualdad_montos
  llaves: [accountholder_id, cuenta_inversion, periodo]
  columna_b: isr_posteado
  columna_c: isr_oraculo
identidad: "C(fila) == B(isr_posteado) +/- tolerancia"
matriz_esperada: "A != B posible (modelo); B == C obligatorio"
estado: VALIDADO
cobertura_nota: "set desviacion 3,236/3,236 = MODELO; B==C +/-0.01"
```

---

## Invariantes que el cargador impone

1. **`estado: VALIDADO` exige que el caso sea ejecutable.** Declarar validado un
   caso sin oráculo o sin consulta es firmar en falso; el cargador lo rechaza.
2. **Los montos son cadenas.** Un `0.01` sin comillas es un float de YAML.
3. **Identidad contable ⇒ tolerancia 0.00.**
4. **Devengo ⇒ prueba de sesgo obligatoria.**
5. **Las rutas de `extraccion` deben existir** (o decir `PENDIENTE` explícitamente).
   No hay rutas rotas silenciosas.

> `estado` describe lo que se sabe de la **validación** (según `NORTE_VALIDACION.md`).
> Si este validador la ha corrido o no es otra cosa, y vive en `reportes/cobertura.md`.
> No confundirlas: un caso `VALIDADO` que este tooling nunca corrió aparece como
> **NO-CORRIDO** en cobertura, y así debe leerse.
