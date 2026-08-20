-- AURUM · Saldo diario y acumulado (base del saldo promedio → ISR y rendimiento vista). SOLO LECTURA.
-- Params: cohorte(accountholder_number), :fecha_ini, :fecha_fin. Sustento: K-DEV-002, K-FIS-002.
select
    b.account_id,
    b.registration_date,
    b.initial_balance,
    b.final_balance,
    b.accumulated_balance_total,
    b.days_number_partial_accumulation,
    b.accumulated_balance_partial
from aurumcore.account_balance_tracking b
join aurumcore.account a on a.account_id = b.account_id
join aurumcore.accountholder ah on ah.accountholder_id = a.accountholder_id
join cohorte c on c.accountholder_number = ah.accountholder_number
where b.registration_date >= :fecha_ini
  and b.registration_date <  :fecha_fin;
