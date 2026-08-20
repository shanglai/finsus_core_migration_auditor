-- =============================================================================
-- AURUM · ISR AL PAGO (motor B)  ·  SOLO LECTURA
-- Firma VERIFICADA en la semilla (2026-08-18): el ISR se asienta como
--   transaction_type = 'INTERNAL TRANSFER', transaction_channel = 'Generic',
--   debito en la cuenta vista del cliente, CREDITO a la cuenta de ISR (producto 0000,
--   p.ej. 100-0000-438220). isr_retenido = credit_amount.
-- Casos comprobados: 1-10-370 -> 765.75 ; 100-10-677746 -> 137.04 ; exentos sin fila.
-- Cohorte por account_number -> accountholder. Parametros: :fecha_ini, :fecha_fin.
-- =============================================================================
select pa.accountholder_id,
       pa.account_number              as account_cliente,   -- cuenta vista debitada
       td.created                     as fecha_pago,
       td.credit_amount               as isr_retenido_ac,    -- ISR retenido (positivo)
       pe.account_number              as cuenta_isr,         -- contrapartida (ISR, producto 0000)
       td.alfanumeric_reference,
       td.transaction_id
from aurumcore.transaction_detail td
join aurumcore.transaction t  on t.transaction_id = td.transaction_id
join aurumcore.account pa     on pa.account_id = t.payer_account_id
join aurumcore.account pe     on pe.account_id = t.payee_account_id
where td.transaction_type    = 'INTERNAL TRANSFER'
  and td.transaction_channel = 'Generic'
  and split_part(pe.account_number, '-', 2) = '0000'          -- contrapartida = cuenta de ISR
  and pa.accountholder_id in (
        select a2.accountholder_id from aurumcore.account a2
        join cohorte_acc c on c.account_number = a2.account_number)
  and td.created >= :fecha_ini and td.created < :fecha_fin
order by pa.accountholder_id, td.created;
