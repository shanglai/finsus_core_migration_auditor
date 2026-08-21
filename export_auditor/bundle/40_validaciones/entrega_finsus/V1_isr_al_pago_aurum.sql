-- =============================================================================
-- V1 · ISR al pago posteado por AurumCore (para comparar contra el oraculo)  · SOLO LECTURA
-- Afirma: AurumCore retiene el ISR al momento del pago; ese monto = la regla (oraculo_isr.py).
-- Como usar: elige una cuenta de inversion de un cliente (:cuenta, formato '100-2301-XXXX').
--   El query trae la(s) retencion(es) de ISR del titular. Toma el saldo total del cliente y los
--   dias del periodo, y compara con  python oraculo_isr.py  (funcion isr_retenido).
-- Firma del asiento (verificada): transaction_type='INTERNAL TRANSFER', channel='Generic',
--   contraparte = cuenta de ISR (producto '0000'); isr_retenido = credit_amount.
-- =============================================================================
select pa.account_number                          as cuenta_cliente,
       ah.external_id                             as titular_id_interno,
       td.created                                 as fecha_pago,
       td.credit_amount                           as isr_retenido_aurum,
       pe.account_number                          as cuenta_isr_contraparte
from aurumcore.transaction_detail td
join aurumcore.transaction   t  on t.transaction_id = td.transaction_id
join aurumcore.account       pa on pa.account_id    = t.payer_account_id
join aurumcore.account       pe on pe.account_id    = t.payee_account_id
join aurumcore.accountholder ah on ah.accountholder_id = pa.accountholder_id
where td.transaction_type    = 'INTERNAL TRANSFER'
  and td.transaction_channel = 'Generic'
  and split_part(pe.account_number, '-', 2) = '0000'
  and pa.accountholder_id = (select accountholder_id from aurumcore.account where account_number = :cuenta)
order by td.created;
