# Mensaje para Finsus/Aurum — confirmación de esquema fuente (para enviar por David/Linko)

> No enviado por Claude. Revísalo y envíalo tú (grupo de líderes o correo a los dueños de datos de
> AurumCore: Mario, Cristhian, etc.). Es una confirmación técnica, no un señalamiento.

---

**Tema:** Confirmación del esquema fuente para la conciliación (AurumCore)

Equipo, gracias por el acceso a la base de AurumCore. Empezando a mapear el modelo detectamos un
punto que queremos confirmar con ustedes, para leer la **fuente correcta** y no conciliar contra una
tabla equivocada:

La base tiene **dos esquemas — `aurumcore` y `public`— con tablas del mismo nombre pero estructura
distinta**. Ejemplos:
- `public.account` tiene 4 columnas; los queries de referencia leen `aurumcore.account` (con
  `account_number`, `accountholder_id`, `account_type`, `iv_initial_amount`, etc.).
- `public.transaction_detail` no tiene fecha; `aurumcore.transaction_detail` sí (`created`).
- `public.investment` maneja los montos en `double precision` (float).

Entendemos que **la fuente de verdad es el esquema `aurumcore`** (es el que usan sus queries) y que
debemos **calificar siempre `aurumcore.`**. ¿Nos lo confirman? En concreto:

1. ¿Confirmamos que la conciliación se lee de **`aurumcore.*`** y que `public` **no** debe usarse como fuente?
2. ¿Qué es el esquema **`public`** — reporte/derivado, staging de migración, o remanente? ¿Lo ignoramos?
3. Donde hay nombres duplicados (`account`, `accountholder`, `transaction_detail`, `investment`,
   `payment_plan`), ¿cuál es la **tabla vigente**?
4. ¿Confirman el modelo de transacciones: **`aurumcore.transaction`** (cabecera, con `created`,
   payer/payee) + **`transaction_detail`**; que **`external_id`** es la llave para cruzar con OpenFin
   y **`parent_transaction_id`** para reversos?
5. ¿Los catálogos **`tbl_transactiontype`** (tipos) y **`cat_accounting_transaction` /
   `cat_finsus_transaction`** (mapeo a cuenta contable) son los vigentes?
6. Duda de precisión: ¿los montos vigentes están en **`numeric`** (no `double precision`/float)? Lo
   preguntamos porque `public.investment` usa float y eso podría introducir diferencias de redondeo.

Con esto amarramos nuestras consultas contra la fuente correcta. Gracias.
