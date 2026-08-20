-- =============================================================================
-- AURUM · Rendimiento y bandera de exencion ISR por cuenta  ·  SOLO LECTURA
-- Fuente real: account_yield (F-014). Acotado a cohorte.
-- Sustento: exencion 5xUMA (K-FIS-002) — aqui se ve isr_exempt/base dias por cuenta.
-- Parametros: cohorte(accountholder_number).
-- =============================================================================
select ah.external_id            as id_cliente,      -- [?] confirmar external_id = 100-10-X
       acc.account_number,
       ay.id                     as account_yield_id,
       ay.interest_rate,
       ay.days_in_year,
       ay.isr_exempt,
       ay.payment_periodicity,
       ay.status
from aurumcore.account_yield ay
join aurumcore.account acc        on acc.account_scheme_id = ay.yield_scheme_id  -- [?] confirmar join real cuenta<->yield
join aurumcore.accountholder ah   on ah.accountholder_id = acc.accountholder_id
join cohorte co                   on co.accountholder_number = ah.external_id
order by ah.external_id, acc.account_number;

-- [?] El vinculo account<->account_yield puede ser account.account_scheme_id ->
--     account_yield.yield_scheme_id, o via account_scheme. Se confirma en P2 con
--     un EXPLAIN + muestra de 1 cuenta semilla antes del extracto amplio.
