# Paquete de validación ISR + motores — para reproducción por Finsus

**Emisor:** tercero independiente (validación de migración openfin → AurumCore)
**Fecha:** 2026-08-19 · **Alcance:** ISR sobre rendimientos (inversiones) + gaps de motores B y C
**Propósito:** que **Finsus reproduzca y valide** nuestros hallazgos con sus propios accesos —
"que le muevan". Todo es **solo lectura**, parametrizado, y no contiene datos de clientes nuestros.

---

## 0. Qué prueba este paquete (resumen)

| # | Afirmación (nuestro hallazgo) | Cómo se prueba aquí | Resultado esperado |
|---|-------------------------------|---------------------|--------------------|
| V1 | AurumCore retiene el ISR **al pago** y ese monto **= la regla** | `V1_isr_al_pago_aurum.sql` + `oraculo_isr.py` | C (oráculo) = ISR posteado, ±$0.01 |
| V2 | El "descuadre OF vs AC" es **MODELO** (devengo OF vs pago AC), no defecto | `V2_isr_devengo_openfin.sql` | el devengo diario de OpenFin sigue la regla (≈100% de días) |
| P-010 | Los **parámetros** del ISR coinciden con la **norma 2026** | `oraculo_isr.py` (usa los valores de ley) + doc | ver §4 (citas normativas) |
| V3 | Gap B (suspensión de devengo / IDNC) **EXISTE** en Aurum | `V3_gapB_idnc.sql` | `con_iodnc` >> 0, `suma_iodnc` < 0 |
| V4 | Gap C (cuota **Prosofipo**) **FALTA** en Aurum | `V4_gapC_prosofipo.sql` | 0 en las tres líneas |
| V5 | Rendimiento de **plazo fijo** (2.1.2) = AurumCore al centavo | `V5_rendimiento_plazo.sql` + `oraculo_rendimientos.py` | C = `iv_payment_plan.interest_amount` (validado 775/775) |
| Escala | El 100% del set de desviación ISR es MODELO | `../comparadores/fase1_isr_desviacion.py` | 3,236/3,236 MODELO |

**Oráculos incluidos (autoprobables sin BD):** `oraculo_isr.py` (ISR, 5/5) y `oraculo_rendimientos.py`
(rendimiento vista/plazo + saldo promedio, 3/3 contra los ejemplos del doc). Corran `python <archivo>.py`.

**Catálogo completo de consultas:** `consultas_validacion.sql` — **un solo archivo** con TODAS las consultas
ejecutadas (solo lectura), de volumetría (§0) → parámetros/P-010 (§1) → mapeo de llaves (§2) → extracción y
comparación de ISR (§3) → rendimiento plazo (§4) → gap B/IDNC (§5) → gap C/Prosofipo (§6). Marca [OF]/[AC] por
base y usa parámetros `:nombre`. Los `Vn_*.sql` de arriba son la versión "pulida por hallazgo"; este es el
catálogo integral para reproducir todo.

---

## 1. Prerequisitos

- Acceso **de solo lectura** a `aurumcore` y (para V2) a `openfin_aurum` (t-1).
- **Python 3.11+** para el oráculo (usa `decimal.Decimal`, sin dependencias externas).
- Para correr los `.sql` desde Python: `psycopg2`. También pueden correrse tal cual en DBeaver/psql.
- **No se requiere escribir nada.** Ningún script hace `INSERT/UPDATE/DDL`. Recomendado: abrir la sesión
  con `SET default_transaction_read_only = on;`.

---

## 2. El oráculo de ISR (`oraculo_isr.py`)

Implementa la regla **exactamente** como el doc oficial de AurumCore (proporción **÷ saldo total**,
truncamientos Trunc20/Trunc5, redondeo final a 2) y con los **parámetros de la norma 2026**.

**Autoprueba (sin base):**
```bash
python oraculo_isr.py
```
Reproduce casos conocidos (46.37 / 4.81 / 0.05 del caso de oro; 765.75 de un cliente de 1 inversión;
13.38 del ejemplo del doc con la proporción corregida). Debe dar **5/5 dentro de ±0.01**.

**Con sus datos:** `isr_retenido(saldo_total_cliente, saldo_cuenta, dias_periodo)` devuelve el ISR de
esa cuenta. Comparar contra lo que trae `V1`.

---

## 3. Validación V1 — C = ISR al pago de AurumCore

1. Elegir una cuenta de inversión de un cliente (`:cuenta`, p.ej. `100-2301-XXXX`).
2. Correr `V1_isr_al_pago_aurum.sql` → trae el/los ISR posteado(s) del titular.
3. Obtener el **saldo total del cliente** (Σ vista saldo promedio + Σ plazo capital) y los **días del
   periodo** de esa inversión, y llamar `isr_retenido(...)` en el oráculo.
4. **Esperado:** el resultado del oráculo coincide con el ISR posteado (±$0.01).

---

## 4. P-010 — parámetros del ISR vs la norma (verificado)

| parámetro | valor 2026 | fundamento normativo |
|-----------|-----------|----------------------|
| UMA anual | 42,794.64 | INEGI, DOF 9-ene-2026, **vigente 1-feb-2026** |
| Tasa de retención | **0.90%** (subió de 0.50%) | **LIF 2026 Art. 24** (remite LISR Art. 54/135), sobre el capital, pago provisional |
| Exención | **5 × UMA** = 213,973.20 sobre saldo promedio diario | **LISR Art. 93 fr. XX** (beneficio SOFIPO) |
| Días del año | 365 | `tax.days.year` |

> Nota operativa: la UMA cambia cada 1-feb. Verificamos un **rezago de ~9 días en feb-2026** (se aplicó la
> UMA 2025 hasta ~el 11-feb) → sobre-retención menor y acotada. Recomendación: parametrizar por año de causación.

---

## 5. Validación V2 — el descuadre OF↔AC es modelo, no defecto

1. Elegir un cliente por su llave (`:suc`, `:rol`, `:aso`).
2. Correr `V2_isr_devengo_openfin.sql` (contra `openfin_aurum`).
3. **Esperado:** `isr_openfin` (devengo diario) ≈ `isr_regla_2026` casi todos los días (el residuo cae
   en la ventana de transición de la UMA de feb, donde aplica `isr_regla_2025_transicion`). El segundo
   query da la **fracción de días que siguen la regla** (≈ 1.0).
4. **Interpretación:** OpenFin **devenga** el ISR día a día (provisión); AurumCore lo **retiene al pago**.
   El "OF ≠ AC" del árbol compara provisión-devengo contra retención-al-pago → magnitudes distintas, no defecto.
   Para el set completo, ver `../comparadores/fase1_isr_desviacion.py` (3,236/3,236 = MODELO).

---

## 6. Validación V3 — Gap B (IDNC) existe

Correr `V3_gapB_idnc.sql`. **Esperado:** `con_iodnc` en el orden de millones (IODNC poblado), `suma_iodnc`
negativa (contra-cuenta que saca el interés de resultados). Conclusión: la suspensión de devengo / IDNC
**existe** (módulo IFRS9/staging). **Pendiente 2.1.7:** validar que la *lógica* sea correcta (umbral 90 días,
montos, contabilización a cuentas de orden, reserva 100%) — requiere el doc del Módulo IFRS 9.

## 7. Validación V4 — Gap C (Prosofipo) falta

Correr `V4_gapC_prosofipo.sql`. **Esperado:** 0 en las tres líneas → AurumCore **no** tiene motor para la
cuota Prosofipo (LACP Art. 104 Bis). Es un **motor faltante real** (se provisiona manual/externo → riesgo).

---

## 8. Cómo leer los resultados (matriz A/B/C del ejercicio)

- **A = openfin** (referencia histórica) · **B = AurumCore** (sistema bajo prueba) · **C = oráculo** (regla/norma).
- Si **C = B** → AurumCore calcula bien. Si **C = A ≠ B** → revisar AurumCore. Si **A ≠ B pero ambos siguen
  la regla en su propio modelo** (V2) → es diferencia de **modelo/momento**, no defecto.

## 9. Notas

- Todo **solo lectura**; los `.sql` no modifican nada. Los parámetros (`:cuenta`, `:suc/:rol/:aso`) los
  pone quien ejecuta, contra su propia base.
- El oráculo es **independiente** (implementa la norma, no copia el código de ningún core).
- Dudas / afinación: los dos residuos abiertos son **H-J** (config go-forward de OpenFin 1.45% ≠ ley 0.90%)
  y el tratamiento de **personas morales** (LISR Art. 54 las excluye de retención; el doc de Aurum pone
  exención $0). Ambos a confirmar.
