# Crosswalk OF ↔ AU (tipos de transacción) — SOL-004 / criterio #6

> Mapeo del **tipo de transacción de openfin (numérico) ↔ AurumCore (texto)** para habilitar el cruce **instancia-a-
> instancia** de Motor B (hoy solo por volumen). Cierra SOL-004 y mueve el **criterio #6** de ◔ a ✅. Linko · 2026-08-31.
> **Estado: spec listo; el join con datos queda [PENDIENTE — VPN]** (se corre en la madrugada 31-ago→01-sep).

## 1. Fuentes (verificadas en el código, no inventadas)
- **OF:** `public.cat_tx_cuadre` — **314 tipos**, columnas `tipo_transaccion`, `tipo` (1=cargo / 2=abono),
  `descripcion`, **`cuenta_contable_cargo`**, **`cuenta_contable_abono`**. Clasificados **PEER (2:1)** (aparece con
  pierna cargo y abono bajo el mismo `tipo_transaccion`) vs **UNI (1:1)** (unidireccional, p.ej. SPEI saliente ≠
  entrante). Ver `motor_b_diario.py::clasifica_catalogo`.
- **AU:** `aurumcore.cat_finsus_transaction` (puente candidato) + `aurumcore.tbl_transactiontype` (tipos-texto) +
  taxonomía de [[K-MOV-002]] (STP · SPEI IN/OUT · Pomelo PURCHASE/WITHDRAWAL/REVERSAL_PAYMENT/REFUND/PAYMENT ·
  Authorizer · P2P · Portal Admin).

## 2. Hipótesis a confirmar
`motor_b_diario.py` (cabecera) documenta *"OF `cat_tx_cuadre` ↔ AU `cat_finsus_transaction`, **misma numeración de
tipo**"*. → **Hipótesis:** el `tipo_transaccion` de OF y el identificador numérico de `cat_finsus_transaction`
**coinciden**, y `cat_finsus_transaction` lleva el **texto** (PURCHASE, SPEI…) que usa `transaction_detail` en AU.
Si se confirma, el crosswalk es directo por número; si no, se mapea por **semántica** (descripción OF ↔ texto AU).

## 3. Queries (listas para correr; solo lectura)
```sql
-- (a) OF: catálogo completo (314 tipos) con clasificación y contable
select tipo_transaccion, tipo, descripcion, cuenta_contable_cargo, cuenta_contable_abono
from public.cat_tx_cuadre
order by tipo_transaccion, tipo;

-- (b) AU: catálogo puente + tipos-texto
select * from aurumcore.cat_finsus_transaction;      -- ¿numero ↔ texto?
select * from aurumcore.tbl_transactiontype;

-- (c) Cruce por numeración (prueba de la hipótesis)
select o.tipo_transaccion, o.descripcion as of_descr,
       a.*                                          -- columnas de cat_finsus_transaction
from public.cat_tx_cuadre o
full outer join aurumcore.cat_finsus_transaction a
  on a.<id_numerico> = o.tipo_transaccion            -- confirmar el nombre de la columna
order by o.tipo_transaccion;
-- Métrica: cuántos de los 314 OF empatan 1-a-1 con un texto AU; los que no, se resuelven por semántica.
```

## 4. Resultado (corrido 2026-08-31, VPN)
- **OF `cat_tx_cuadre`:** 314 tipos (1-314). **AU `cat_finsus_transaction`:** 348 tipos-número (1-5100).
- **Crosswalk por número CONFIRMADO:** **313 de 314 tipos OF empatan por número con AU** (1 solo-OF, 35 solo-AU, en su
  mayoría números altos > 314). La hipótesis de **"misma numeración"** se sostiene. → **SOL-004 (bridge de tipos)
  cerrado**; Motor B ya puede ir **instancia-a-instancia por tipo** (pendiente correr el cruce de instancias reales).
  **Criterio #6 pasa de ◔ a ✅ en el bridge de tipos.**
- **Estructura de AU `cat_finsus_transaction`:** `transaction_type` (núm) · `cta_charge` · `cta_deposit` ·
  `cta_descripcion` (a veces `SPEIOUT_MORALES`/`SPEIIN_MORALES` = variantes física/moral). **AurumCore SÍ tiene un
  mapeo config `tipo → cuentas`** (esto reencuadra D2, ver §5).

## 5. D2 (mapeo contable) — reencuadrado, no cerrado
Dos hallazgos, con matiz:
1. **AurumCore SÍ tiene el mapeo `tipo → cuenta` en config** (`cat_finsus_transaction`), con variantes por naturaleza
   (moral/física). Eso **corrige el D2** original ("no hay contra qué corroborar"): **la fuente config existe** — como
   IFRS, se puede validar C = config del propio core.
2. **PERO las cuentas OF y AU NO coinciden 1-a-1** (idénticas=0, intersección=0 en los 313 comunes): OF usa formato de
   **mayor** (`2101020111102`); AU `cat_finsus_transaction` usa **códigos producto/internos** (`100-2000-400014` / `2002`).
   Son **niveles distintos** de plan de cuentas. → Falta el mapeo **AU-interno → mayor** para cerrar D2; el catálogo OF
   (mayor, por el crosswalk de número confirmado) es una **referencia** de qué debería postear cada tipo, no un igual directo.

Ejemplos (tipo · OF descr · OF ctas mayor · AU ctas producto/interno):
| # | OF descripción | OF (mayor) | AU (cat_finsus_transaction) |
|---|---|---|---|
| 1 | transferencia interna entre clientes | 2101020111102 / 2401150111126 | 100-2000-400014 / 2002 |
| 3 | transferencia saliente SPEI | 1102010112103 / 2101020111102 | 100-2000-400000 / 2002 / 2015 (MORALES) |
| 5 | compra en TPV / pago servicios | 2101010111101 / 2401150111127 | 100-0000-405766 / 100-2000-405601 |

## 6. Estado y siguientes pasos — actualizado 2026-09-01 (probe de records)
**Matiz importante tras revisar los registros:** el bridge de número (313/314) es entre los **catálogos config/
contables** (OF `cat_tx_cuadre` ↔ AU `cat_finsus_transaction`), **NO** entre los **registros transaccionales**. Los
records de AU usan **tipo-TEXTO** (`transaction_detail.transaction_type`: YIELD PAYMENT, EXTERNAL TRANSFER, DEPOSIT,
DEBIT CARD CHARGE…). `transaction_detail.numeric_reference` **no es** el tipo (son fechas/referencias; 113/2857 empatan
por coincidencia). → Para el **cruce de records** OF↔AU falta el **mapeo semántico OF-descripción ↔ AU-texto**.
- [x] Bridge de **catálogos config por número: 313/314** (SOL-004 nivel catálogo).
- [ ] **Mapeo semántico OF-descr ↔ AU-`transaction_type` (texto)** para el cruce por tipo de los **records** (Motor B).
- **D2 avanza fuerte:** `transaction_detail` trae **`source/target_accounting_account` (mayor) por posteo** → la matriz
  AU `tipo-texto → cuenta contable` **es derivable de los posteos reales**, y valida [[K-CTB-001]]. **Cierra el "no hay
  fuente" de D2** a nivel posteo (criterio #5/#7). Siguiente: agregar por `transaction_type` las cuentas mayor y cotejar.
- [ ] Documentar los 35 tipos solo-AU / 1 solo-OF (catálogo).
