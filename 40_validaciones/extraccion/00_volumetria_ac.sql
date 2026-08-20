-- =============================================================================
-- VOLUMETRIA AurumCore  ·  MEDIDAS  ·  SOLO LECTURA
-- Cohorte anclada por account_number -> accountholder -> todas sus cuentas
-- (la llave '100-10-X' NO existe en Aurum; ver bitacora 2026-08-18).
-- Parametros: :fecha_ini, :fecha_fin. Cohorte: cohorte_acc(account_number) (la inyecta el runner).
-- =============================================================================

-- [AC-1] account_balance_tracking del universo de cuentas de los titulares del cohorte
select count(*)                              as filas,
       count(distinct t.account_id)          as cuentas,
       count(distinct acc.accountholder_id)  as titulares,
       min(t.registration_date)              as fecha_min,
       max(t.registration_date)              as fecha_max
from aurumcore.account_balance_tracking t
join aurumcore.account acc on acc.account_id = t.account_id
where acc.accountholder_id in (
        select a2.accountholder_id from aurumcore.account a2
        join cohorte_acc c on c.account_number = a2.account_number)
  and t.registration_date >= :fecha_ini and t.registration_date < :fecha_fin;

-- [AC-2] account_tax: esquemas con tasa ISR (cat_tax esta vacia en este entorno)
select count(*) as esquemas_isr, min(isr) as isr_min, max(isr) as isr_max
from aurumcore.account_tax
where isr > 0;
