-- AURUM · Inversiones (plazo fijo) del cohorte. SOLO LECTURA. Columnas nombradas.
-- Params: tabla temporal cohorte(accountholder_number). Periodo opcional por activation_date/iv_closing_date.
-- Sustento: K-DAT-006, K-DEV-003, K-FIS-002.
select
    ah.accountholder_number,
    ah.person_type,                                   -- física/moral (rama ISR)
    a.account_id,
    a.account_number,
    split_part(a.account_number, '-', 2) as producto, -- 2301/2302/2307/2308
    a.account_type,
    a.iv_account_state,
    a.iv_initial_amount            as capital,
    a.activation_date,
    a.iv_closing_date,
    a.term,
    a.iv_reinvestment_cycle_number,
    a.average_balance_amount,
    ay.interest_rate               as tasa,
    ay.days_in_year,                                  -- 360/365 (base de días)
    ay.isr_exempt
from aurumcore.account a
join aurumcore.accountholder ah on ah.accountholder_id = a.accountholder_id
join cohorte c on c.accountholder_number = ah.accountholder_number
left join aurumcore.account_yield ay
       on ay.yield_scheme_id = a.yield_scheme_id
      and ay."enable" = 1 and ay.status = 1
where a.account_type = 'INVESTMENT_ACCOUNT'
  and a.activation_date <  :fecha_fin
  and (a.iv_closing_date is null or a.iv_closing_date >= :fecha_ini);
