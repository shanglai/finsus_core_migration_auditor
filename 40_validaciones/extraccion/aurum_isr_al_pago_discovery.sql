-- =============================================================================
-- AURUM · DESCUBRIR como se asienta el ISR al pago  ·  SOLO LECTURA
-- transaction_detail NO tiene columna isr -> el ISR se asienta como transaccion
-- (debit_amount). IDENTIFICA el transaction_type del ISR sobre las cuentas de los
-- titulares del cohorte (ISR conocido de la semilla: 46.37 / 4.81 / 0.05, etc.).
-- Parametros: :fecha_ini, :fecha_fin. Cohorte: cohorte_acc(account_number).
-- =============================================================================

-- [1] Perfil por tipo de transaccion (que mueve importes tipo retencion)
select td.transaction_type,
       td.transaction_channel,
       t.type            as txn_type,
       t.origin,
       count(*)          as n,
       min(td.debit_amount)  as debito_min,
       max(td.debit_amount)  as debito_max,
       round(sum(td.debit_amount), 2) as debito_sum
from aurumcore.transaction_detail td
join aurumcore.transaction t on t.transaction_id = td.transaction_id
join aurumcore.account acc   on acc.account_id in (t.payer_account_id, t.payee_account_id)
where acc.accountholder_id in (
        select a2.accountholder_id from aurumcore.account a2
        join cohorte_acc c on c.account_number = a2.account_number)
  and td.created >= :fecha_ini and td.created < :fecha_fin
group by 1,2,3,4
order by n desc;

-- [2] Detalle de importes chicos (ver el 46.37 / 4.81 / 0.05 y fijar el tipo exacto)
select acc.account_number,
       td.created,
       td.transaction_type,
       td.transaction_channel,
       td.debit_amount,
       td.credit_amount,
       t.type as txn_type
from aurumcore.transaction_detail td
join aurumcore.transaction t on t.transaction_id = td.transaction_id
join aurumcore.account acc   on acc.account_id in (t.payer_account_id, t.payee_account_id)
where acc.accountholder_id in (
        select a2.accountholder_id from aurumcore.account a2
        join cohorte_acc c on c.account_number = a2.account_number)
  and td.created >= :fecha_ini and td.created < :fecha_fin
  and td.debit_amount between 0.01 and 2000
order by acc.account_number, td.created;
