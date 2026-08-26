# Manual de Uso del Oráculo — Auditor

**Linko · Tercero independiente** · Cómo instalar, ejecutar e interpretar el oráculo (motor C)
Versión 1.0 · 2026-08-24 · Para: Auditoría Interna de Finsus

> Complemento operativo del *Manual de Definiciones*. Aquí se explica **cómo correr** el oráculo, **qué se recibe**
> y **cómo interpretarlo**. El oráculo está en `decimal.Decimal` (aritmética exacta, cero `float`) y accede a la base
> **solo en lectura**.

---

## 1. Qué es y qué NO es

- **Es:** un conjunto de módulos Python (los *oráculos*) que implementan las fórmulas oficiales/normativas, y unos
  *comparadores* que ejecutan el cruce contra AurumCore y **devuelven las filas que violan la regla**.
- **No es:** un sistema que modifique datos. Todo acceso es **read-only** (`SET default_transaction_read_only`).

Dos formas de correrlo:
- **Autoprueba (sin base de datos):** valida que las fórmulas del oráculo reproducen los ejemplos del doc. **No
  requiere credenciales.** Ideal para que Auditoría verifique el motor de forma aislada.
- **Cruce completo (con base de datos read-only):** ejecuta la validación sobre el universo real y reporta el
  % de match y los no-conformes.

---

## 2. Requisitos

- **Python 3.11+**.
- Paquetes: `psycopg2` (o `psycopg2-binary`), `pyyaml`. Para leer logs del core: `paramiko`. (Todo el cálculo usa
  `decimal` de la librería estándar.)
- Acceso **de solo lectura** a la base AurumCore (para los cruces completos). Las autopruebas NO lo requieren.

```bash
pip install psycopg2-binary pyyaml paramiko
```

---

## 3. Instalación

1. Copiar el **bundle** que entrega Linko (`export_auditor/bundle/`) al repositorio del auditor. Contiene los
   oráculos, los comparadores, los documentos (Manual de Definiciones, Dossier, Comparación, Índice) y este manual.
   **No incluye credenciales, PII ni resultados** (por diseño).
2. Verificar la estructura:
   ```
   40_validaciones/comparadores/   → oráculos y comparadores (oraculo_*.py, validate_*, motor_b_diario.py, ...)
   40_validaciones/entrega_finsus/ → oraculo_isr.py, oraculo_rendimientos.py, SQL
   40_validaciones/*.md            → Manual de Definiciones, Dossier, Comparación, Índice, este manual
   ```

---

## 4. Configuración de accesos (el auditor pone SUS credenciales)

El oráculo lee la conexión de `db_connections.yaml` en la raíz (**gitignored**; el formato está en
`db_connections.example.yaml`). El auditor crea el suyo con **sus propias credenciales de solo lectura**:

```yaml
aurum:
  host: 10.10.160.53
  port: 5432
  dbname: aurumcore
  user: <usuario_readonly_del_auditor>
  password: <...>
  sslmode: prefer
```

Para leer logs del core (opcional, para validaciones que dependen de trazas), `other_connections.yaml` con el acceso
SSH read-only. **Nunca** se versionan credenciales ni se envían al frontend.

---

## 5. Qué se ejecuta — catálogo de comandos

### 5.1 Autopruebas de fórmula (sin base de datos)
Verifican que el oráculo reproduce los ejemplos del doc. Salida esperada: `N/N OK`.
```bash
python 40_validaciones/comparadores/oraculo_credito.py        # ordinario/moratorio/IVA  → 3/3 OK
python 40_validaciones/comparadores/oraculo_rendimientos.py   # vista/plazo/saldo prom.  → 3/3 dentro de ±0.01
python 40_validaciones/comparadores/oraculo_gat.py            # GAT nominal/real         → 2/2 OK
python 40_validaciones/comparadores/oraculo_ifrs9.py          # etapas + % + reserva     → 14/14 OK
python 40_validaciones/comparadores/oraculo_amortizacion.py   # cuota/interés/invariantes→ 6/6 OK
python 40_validaciones/comparadores/oraculo_cat.py            # CAT One Click/Francesa   → 3/3 vs doc
```

### 5.2 Cruces completos (con base de datos read-only)
Ejecutan la validación sobre el universo real y reportan match + no-conformes.
```bash
python 40_validaciones/comparadores/validate_plazo_origin.py --limite 0   # plazo: 100% en 530,195 periodos
python 40_validaciones/comparadores/motor_b_diario.py                     # completitud A vs B (diario)
python 40_validaciones/comparadores/contable_bc.py                        # doble partida / amarre
python 40_validaciones/comparadores/cuentahabientes_wso2.py               # identidad ↔ padrón
python 40_validaciones/comparadores/isr_live_nativo.py                    # ISR-vivo (parcial; ver Definiciones)
```
Los cruces de **crédito** (ordinario/moratorio/IVA) e **IFRS 9** se corren con los oráculos anteriores sobre el feed
de provisiones del core (extraído de logs a CSV con `log_extractor.py`) y las tablas `lc_finantial_data`/
`lc_loan_amortization` — el detalle metodológico está en `COMPARACION_C_vs_DOC.md` y `DOSSIER_MOTORES_ORACULO_C.md`.

### 5.3 Extracción de logs (opcional, read-only)
```bash
python 40_validaciones/comparadores/log_extractor.py --patron dias --servicio core-rendimientos   # días de crédito
python 40_validaciones/comparadores/barrido_average_balance.py                                     # saldo base
```

---

## 6. Qué se recibe (la salida) y cómo leerla

Cada comparador imprime, sobre su **universo**:
- **el tamaño del universo** (cuántos casos se compararon),
- **el % de match** (cuántos cuadran dentro de la tolerancia),
- **los no-conformes** (los que NO cuadran) con su delta y un motivo,
- para las identidades contables, **las filas que violan** (0 = PASS).

Ejemplo (plazo):
```
plazo A=B=C por origin: 157,999 cuentas / 530,195 periodos
  100.00% (0 violaciones)
```
Ejemplo (crédito ordinario):
```
INTEREST rows=4091 · tasa feed=DB 4091/4091 (0 mismatch)
EXACTO(1e-8)=96.8% · fuera=... (motivo: linaje/gap de reserva)
```

---

## 7. Cómo interpretar (criterios de PASS)

| Ves esto | Significa |
|---|---|
| `0 violaciones` / `$0.00` | **PASS** exacto (identidad o universo completo). |
| `EXACTO(1e-8) = 96.8%` | 96.8% cuadra a **8 decimales** (sin redondear) — criterio más estricto que "al centavo". |
| `≤$0.01 = 99%` | 99% cuadra **al centavo** (tolerancia de devengo). |
| `0/N mismatch de tasa` | la tasa que usa el core = la contratada (0 discrepancias). |
| `C = B` | el oráculo = lo posteado por AurumCore. |
| un **no-conforme** | se **clasifica y explica** — ver la clase (defecto / linaje / gap de datos / bloqueo / redondeo). |

**Regla de interpretación:** un motor está **validado** si sus no-conformes **no** son "Defecto de AurumCore" (es
decir, son dato, tiempo o cobertura). El detalle de cada no-conforme está en `DOSSIER_MOTORES_ORACULO_C.md` y
`COMPARACION_C_vs_DOC.md`. **Verde ≠ dictamen.**

---

## 8. El tablero (SPA) — visualización

Para una vista gráfica (progreso, % de match, fórmulas, **scatterplot con foco en los no-conformes** y un agente
conversacional que explica cada motor), Linko entrega el brief de construcción en `PROMPT_AUDITOR_SPA.md`. El SPA
corre los oráculos (backend), produce un JSON por motor y lo renderiza; **los logs se traen con un proceso aparte**
(no hace SSH en vivo). El "cerebro" del agente conversacional es `DOSSIER_MOTORES_ORACULO_C.md`.

---

## 9. Seguridad y buenas prácticas

1. **Solo lectura** en la base (el código fuerza `readonly`).
2. **`decimal.Decimal`** en todo cálculo monetario (cero `float`).
3. **Nunca** versionar credenciales (`db_connections.yaml`/`other_connections.yaml` son gitignored) ni exponer PII
   en la salida (agregados + muestras con ids truncados).
4. Cada resultado se sostiene en una prueba que **devuelve las filas que violan la regla**; los no-conformes se
   **explican**, nunca se ocultan.

---

*Soporte: Linko (tercero independiente). Este manual acompaña al Manual de Definiciones y al bundle del auditor.*
