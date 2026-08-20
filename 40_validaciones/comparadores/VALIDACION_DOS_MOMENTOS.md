# Validación de dos momentos — separar sincronía de hallazgo real

Diseño (Fase 1) para la idea de comparar a **dos puntos en el tiempo**: uno **ingenuo** (reproduce el
descuadre) y uno **equivalente** (donde la mayoría cuadra), y quedarnos con los **outliers** reales.

## Objetivo
La mayoría de los descuadres del árbol son de **sincronía**, no de cálculo (K-TMP-001, K-MIG-002).
Esta validación los aísla: lo que sigue descuadrando **tras alinear el tiempo** es el hallazgo real.

## Parámetros
- `:clientes` — cohorte (tabla `cohorte`/`cohorte_of`).
- `:corte_of`, `:corte_ac` — el instante de corte **por core** (pueden diferir: OpenFin cierra vista
  ~18:00, Aurum a medianoche; los nocturnos ~06:00). Permite alinear "peras con peras".
- `:momento` ∈ {`ingenuo`, `equivalente`}:
  - **ingenuo:** un instante fijo común (p.ej. 23:59 del día) → antes de que ambos completen procesos → **reproduce el descuadre**.
  - **equivalente:** cada core a su corte lógico (`:corte_of`/`:corte_ac`), tras correr el mismo proceso → **la mayoría cuadra**.

## Método
1. Correr el comparador A↔B↔C a `:momento = ingenuo` → **N descuadres** (línea base del problema).
2. Correr a `:momento = equivalente` → **M descuadres** (esperado M ≪ N).
3. **Outliers = filas que violan en AMBOS momentos** → no son sincronía → a clasificar/RCA.
4. Cada outlier se etiqueta por **causa residual**: `SINCRONIA` (desaparece al alinear) ·
   `MODELO` (ISR diario vs al-pago, atomicidad) · `REDONDEO` · `DEFECTO`.

## Fuentes por dominio (para los dos cortes)
- **Saldo/cuentas:** `account_balance_tracking`(AC, diario) / `etl_saldo_prom_mensual`(OF) por fecha;
  o `detalle_auxiliar.saldo`(OF) vs `transaction_detail.*_after_balance`(AC) al corte.
- **ISR:** ⚠ además del tiempo, **normalizar el modelo**: Σ `isr_diario`(OF) del periodo vs ISR al
  pago (AC). Sin esto, el ISR **no cuadra aunque alinees el tiempo** (A15-ISR-DIARIO).
- **Transacciones:** `transaction.created`(AC) vs `detalle_auxiliar.fecha/hora`(OF) con **tolerancia
  de desfase** (p.ej. ±N min): las que casan dentro de la tolerancia = sincronía.

## Salida
| momento | descuadres | % explicado por sincronía |
|---------|-----------:|---------------------------|
| ingenuo | N | — |
| equivalente | M | (N−M)/N |

Y el conjunto **outliers (M)** con su `causa residual` → alimenta el ledger de hallazgos.

## Lo que esta validación NO hace (importante)
Alinear el tiempo **no** disuelve: (a) la diferencia de **modelo del ISR** (diario vs al-pago) — eso
se normaliza aparte; (b) el **sesgo de redondeo** del rendimiento (OpenFin trunca). Esos persisten y
**son** hallazgos. El diseño los separa explícitamente en `causa residual`.

## Estado
Constructo de **Fase 1**: requiere extraer a dos cortes (o usar las tablas diarias `isr_diario` /
`account_balance_tracking`). Se implementa con los `.sql` de `extraccion/` parametrizados por corte.
