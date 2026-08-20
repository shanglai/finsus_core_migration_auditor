-- AURUM · Plan de rendimiento por periodo (para recalcular multiperiodo). SOLO LECTURA.
-- Params: cohorte(accountholder_number), :fecha_ini, :fecha_fin. Sustento: K-DEV-003.
select
    p.plan_id,
    p.account_id,
    p.account_number,
    p.start_date,
    p.due_date,
    p.payment_date,
    p.payment_number,
    p.interest_amount,                 -- rendimiento del periodo (B)
    p.interest_paid,
    p.is_full,
    p.parcial
from aurumcore.iv_payment_plan p
join aurumcore.account a on a.account_id = p.account_id
join aurumcore.accountholder ah on ah.accountholder_id = a.accountholder_id
join cohorte c on c.accountholder_number = ah.accountholder_number
where p.payment_date >= :fecha_ini
  and p.payment_date <  :fecha_fin;
