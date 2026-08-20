-- =============================================================================
-- AURUM · SALDO DIARIO por cuenta (base para el oraculo C)  ·  SOLO LECTURA
-- Fuente real: account_balance_tracking. Se traen TODAS las cuentas (vista+plazo)
-- de los titulares del cohorte, para poder sumar el saldo total del cliente
-- (base ISR = max(0, total - exencion)). Independencia: son SALDOS (hechos), no el
-- calculo de ISR de ningun core (§9.1). Sustento: PLAN_FASE1_ISR.md A6.
-- La llave de cliente '100-10-X' se reconstruye local via account_number (parquet).
-- Parametros: :fecha_ini, :fecha_fin. Cohorte: cohorte_acc(account_number).
-- =============================================================================
select acc.accountholder_id,
       acc.account_number,
       split_part(acc.account_number, '-', 2)      as producto,   -- 2000s vista / 2300s inversion
       t.registration_date                          as fecha,
       t.initial_balance,
       t.final_balance,
       t.accumulated_balance_total,
       t.accumulated_balance_partial,
       t.days_number_partial_accumulation
from aurumcore.account_balance_tracking t
join aurumcore.account acc on acc.account_id = t.account_id
where acc.accountholder_id in (
        select a2.accountholder_id from aurumcore.account a2
        join cohorte_acc c on c.account_number = a2.account_number)
  and t.registration_date >= :fecha_ini and t.registration_date < :fecha_fin
order by acc.accountholder_id, acc.account_number, t.registration_date;
