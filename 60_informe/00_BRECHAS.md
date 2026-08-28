# Brechas del informe detallado — lo que sigue pendiente

> Todo lo que este informe NO puede afirmar todavia, con **como se cierra**. Un pendiente sin instruccion de cierre se vuelve permanente.

## 1. Denominadores sin medir (15 de 19 puntos)

Es la pregunta central de la auditoria [00:32:35]. Cada uno trae la consulta que lo cierra; todas son de solo lectura y de agregacion (no leen datos de cliente).

### V-01 · Rendimiento plazo fijo — motor vivo (origin IS NULL)

Comparado **530,195** periodos (157,999 cuentas), de un total **no declarado** segun B (AurumCore).

Se declaro 'todas las origin IS NULL', o sea el subconjunto ES el universo de su clase. Falta la cifra de control: cuantos periodos hay EN TOTAL (origin null + no null) para expresar que fraccion del libro representa.

```sql
select count(*) total, count(*) filter (where a.origin is null) origin_null from aurumcore.iv_payment_plan p join aurumcore.account a on a.account_id = p.account_id
```

### V-02 · Rendimiento plazo fijo — migrado (origin = FINSUS)

Comparado **3,748** periodos (300 cuentas), de un total **no declarado** segun B (AurumCore).

AQUI SI HAY MUESTREO: 300 cuentas de un total no declarado.

```sql
select count(*) from aurumcore.iv_payment_plan p join aurumcore.account a on a.account_id = p.account_id where a.origin = 'FINSUS'
```

### V-04 · Rendimiento vista — oraculo independiente

Comparado **20,000** pagos de rendimiento vista, de un total **no declarado** segun B (AurumCore).

El limite de 20,000 es una COTA DE LA EXTRACCION (`limite` del caso), no el universo. Hay que declarar cuantos pagos hubo ese dia para expresar la representatividad.

```sql
select count(*) from aurumcore.yield_dto y where y.iv_payment_plan_id is null and y.process_date = :fecha_pago
```

### V-05 · Saldo promedio (SPM) — barrido de logs

Comparado **90** filas (27 cuentas), de un total **no declarado** segun logs del core.

27 cuentas de un padron de vista completo — la cobertura es minima y se declara.

```sql
no hay consulta: el dato no esta en la base, esta en la traza de log
```

### V-06 · GAT inversion (nominal / real)

Comparado **126,465** inversiones (term 7), de un total **no declarado** segun B (AurumCore).

126,465 corresponde al plazo 7; faltan los volumenes de los demas plazos.

```sql
select count(*) from aurumcore.iv_payment_plan  -- y por plazo
```

### V-07/08 · ISR inversiones — join A/B/C completo y desviacion clasificada

Comparado **18,599** inversiones (14,913 clientes), de un total **no declarado** segun interseccion A ∩ B.

18,599 es el tamano de la INTERSECCION. Falta declarar cuantas inversiones hay en cada core para saber cuantas quedaron fuera del cruce. Es la cifra que convierte '18,599' en una representatividad.

```sql
contar inversiones en A y en B por separado, y el tamano del anti-join en ambas direcciones
```

### V-09/10/11 · ISR — reconciliacion al pago, devengo diario e insumo de saldo base

Comparado **728** dias-cliente (V-10); 2 pagos (V-09); 65 filas (V-11), de un total **no declarado** segun A (openfin).

728 dias-cliente sobre 4 clientes. Es una SEMILLA de reconciliacion, no una muestra representativa, y se debe leer como tal.

```sql
select count(*) from openfin.isr_diario where fecha between ...
```

### V-12 · ISR-vivo nativo (post-cutover)

Comparado **[PEND]** pagos, de un total **no declarado** segun B (AurumCore).

```sql
pendiente de definir el universo una vez exista el insumo
```

### V-15 · Credito — conteo de DIAS de devengo

Comparado **3** contratos (traza de log), de un total **no declarado** segun log del core.

3 contratos es una TRAZA DE CONFIRMACION, no una muestra.

```sql
contar cuantos contratos aparecen en la traza CreditAmortizationChargeServiceImpl
```

### V-16 · Credito — IVA sobre interes

Comparado **54,716** filas con IVA, de un total **no declarado** segun B (AurumCore).

54,716 filas CON IVA; falta el total de filas para expresar la fraccion.

```sql
select count(*) from aurumcore.lc_loan_amortization -- total de filas, con y sin IVA
```

### V-17 · Credito — AMORTIZACION (tabla francesa)

Comparado **794** contratos, de un total **no declarado** segun B (AurumCore).

794 contratos. La auditoria lo senalo en la sesion [00:29:23]: 'el tema de amortizacion solo son 700 casos'. Falta el denominador.

```sql
select count(distinct lc_contract_id) from aurumcore.lc_loan_amortization  -- y cuantos son FRENCH
```

### V-19 · IFRS 9 — etapas y porcentaje de reserva

Comparado **20,000** filas de staging en etapa 3, de un total **no declarado** segun B (AurumCore).

El 20,000 es la COTA de la extraccion, no el universo. Ademas hay un segundo denominador, el de la config: 37 de 37 celdas de lc_reserve_ifrs, que ese SI es completo.

```sql
select count(*) from aurumcore.lc_finantial_data_stage where capital_mora_days >= 90 and information_date between ...
```

### V-20 · Motor B diario — completitud A vs B

Comparado **6** dias (21K-29K operaciones por dia), de un total **no declarado** segun A (openfin) y B (AurumCore).

6 dias de una ventana post-cutover cuyo largo total no se declaro.

```sql
contar dias disponibles post-cutover en ambos cores
```

### V-21/22 · Contable — doble partida diaria y detalle transaccional

Comparado **7** dias (17K-220K asientos por dia), de un total **no declarado** segun B (AurumCore).

7 dias consecutivos. El detalle transaccional del 08-14 son 96,235 movimientos, el dia completo.

```sql
select count(distinct date_trunc('day', ...)) from aurumcore.transaction_detail  -- dias disponibles post-cutover
```

### V-23 · Cuentahabientes — WSO2 vs padron Aurum

Comparado **20** huerfanos Aurum -> WSO2, de un total **no declarado** segun B (AurumCore) — padron completo.

Los 20 huerfanos son el RESULTADO, no el universo. El universo es el padron completo y no se declaro. En la otra direccion: 181,850 telefonos de WSO2 que no estan en Aurum, y 295 altas incompletas.

```sql
select count(*) from aurumcore.accountholder
```


## 2. Universos sin conciliar (5)

Un universo que solo se cuenta a si mismo confirma consistencia interna, no completitud.

- **V-01** Rendimiento plazo fijo — motor vivo (origin IS NULL)
- **V-02** Rendimiento plazo fijo — migrado (origin = FINSUS)
- **V-04** Rendimiento vista — oraculo independiente
- **V-09/10/11** ISR — reconciliacion al pago, devengo diario e insumo de saldo base
- **V-17** Credito — AMORTIZACION (tabla francesa)


## 3. Puntos bloqueados por insumo (2)

### V-05 · Saldo promedio (SPM) — barrido de logs

**Bloquea:** El SPM de rendimiento solo existe en logs; el barrido capturo 27 cuentas.

**Se necesita:** QUE: la traza completa `Calculating with average balance` del cierre mensual, o la poliza de intereses con el SPM y los dias efectivamente usados por cuenta. CUANDO: el cierre del 31-ago es la primera oportunidad de capturarla completa.

### V-12 · ISR-vivo nativo (post-cutover)

**Bloquea:** Falta el SALDO BASE PUNTO-EN-TIEMPO del cliente al momento del pago. Los saldos actuales solo dan una aproximacion, y comparar contra una aproximacion produce diferencias que no dicen nada del motor.

**Se necesita:** QUE: el saldo base gravable del cliente EN EL INSTANTE del pago (point-in-time), no el saldo actual. Puede venir de la traza de calculo del core o de una tabla de snapshot por evento de pago. CUANDO: en cuanto exista la traza; el cierre del 31-ago es la primera ventana.



---

*Estas brechas son del informe, no del core. Ninguna de ellas es una desviacion de calculo: son cosas que todavia no se han medido o declarado.*
