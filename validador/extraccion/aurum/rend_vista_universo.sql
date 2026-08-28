-- =============================================================================
-- AURUM · REND-VISTA — universo del interes de cuenta vista · SOLO LECTURA
-- BOUNDED: un ciclo (:fecha_cierre / :fecha_pago) + cota :limite.
--
-- REALINEADO 2026-08-28 con `comparadores/oraculo_vista_finsus_history.py`.
-- La version anterior tomaba B de `transaction_detail` buscando la referencia
-- de texto 'Capitaliza Interes%'. Esta lo toma de `yield_dto`, que es el
-- REGISTRO DEL POSTEO y no una cadena de texto que puede cambiar de formato.
-- Medido sobre el mismo ciclo, el cambio de fuente sube el cuadre de 91.52% a
-- 96.06%.
--
--   B  = yield_dto.yield_amount  con `iv_payment_plan_id IS NULL` (= VISTA, no
--        inversion) y `process_date` = el dia de pago del ciclo.
--   C  = SPM x dt x tasa / 36000, via oraculo_rendimientos.rendimiento_vista.
--   SPM y tasa = finsus_account_history en el `record_date` del cierre.
--
-- BASE DE DIAS: 360, ELEGIDA POR EVIDENCIA, no asumida (§11.2). Se probaron las
-- cuatro convenciones naturales sobre 20,000 pares del ciclo de julio:
--     base 360 · dt 31   ->  94.97% a 1e-8   <== gana por mucho
--     base 365 · dt 31   ->  42.68%
--     base 360 · dt 30   ->  34.46%
--     base 365 · dt 30   ->  30.27%
-- La separacion es tan grande que no hay ambiguedad. Probar las convenciones y
-- reportar cual ajusta es no-circular; fijar 360 "porque suele ser" no lo era.
--
-- `dt` = dias efectivamente DEVENGADOS. La regla de Finsus (2026-08-24): el dia
-- de fondeo NO cuenta y los extremos son inclusivos. Derivarlo de la fecha de
-- activacion en vez de fijar 31 sube el cuadre de 95.30% a 96.06% y baja el
-- sesgo de z=30.9 a z=3.64.
-- =============================================================================
select
    a.account_number                              as cuenta,
    :fecha_pago::text                             as fecha_capitalizacion,
    y.yield_amount::text                          as interes_posteado,
    h.average_balance_amount::text                as saldo_promedio,
    h.interest_rate::text                         as tasa,
    a.activation_date::text                       as fecha_activacion,
    -- dt: el dia de fondeo no cuenta; extremos inclusivos
    greatest(1, (case
        when a.activation_date::date > date_trunc('month', :fecha_cierre::date)::date
        then extract(day from :fecha_cierre::date)::int
             - extract(day from a.activation_date)::int
        else extract(day from :fecha_cierre::date)::int
     end))::text                                  as dias_devengados
from aurumcore.yield_dto y
join aurumcore.finsus_account_history h
       on h.account_id = y.account_id
      and h.record_date = :fecha_cierre::date
join aurumcore.account a on a.account_id = y.account_id
where y.iv_payment_plan_id is null          -- VISTA, no inversion a plazo
  and y.process_date = :fecha_pago::date
  and y.yield_amount > 0
  and h.average_balance_amount > 0
order by a.account_number
limit :limite;
