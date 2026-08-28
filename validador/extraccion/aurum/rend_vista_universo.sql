-- =============================================================================
-- AURUM · REND-VISTA — universo del interes de cuenta vista · SOLO LECTURA
-- BOUNDED: un solo evento de capitalizacion (:fecha_cap) + cohorte opcional.
--
-- B = el interes que AurumCore posteo: `transaction_detail` con referencia
--     'Capitaliza Interes DD/MM/AAAA' y source = target (autocapitalizacion).
--
-- Insumos de C, desde `aurumcore.finsus_account_history` (la ruta que abrio la
-- respuesta de Finsus del 2026-08-24, y que quita la dependencia del cierre
-- del 31-ago):
--     interes = SPM x dt x tasa / 36000        (base 360)
--
-- `dt` = dias efectivamente DEVENGADOS, y ahi esta el matiz que decide el
-- resultado. La regla que dio Finsus: se cuenta inclusivo en ambos extremos y
-- EL DIA DE FONDEO NO CUENTA. Para una cuenta abierta dentro del mes eso es
--     dt = (dia del ultimo dia del mes) - (dia de activacion)
-- y para una cuenta que ya venia de antes, el mes completo.
--
-- Medido sobre el posteo real del 31-jul-2026 (muestra de 1,500 cuentas):
--     dt = 31 fijo                    89.5%
--     dt = regla de Finsus            91.9%   <- la que implementa este query
--     sin NINGUN dt entero que cuadre  7.2%
-- Ese 7.2% NO se puede atribuir al motor: es el SPM. Finsus advierte que el
-- SPM de RENDIMIENTO se guarda en la poliza de intereses y PUEDE DIFERIR del
-- `average_balance_amount` que aqui se lee, que es el de CONSULTA. Mientras la
-- poliza no este disponible, ese residuo es data-sourcing, no defecto.
--
-- [PENDIENTE] La convencion exacta de `dt` sigue sin documento formal; la de
-- aqui es la que Finsus describio verbalmente el 2026-08-24.
-- =============================================================================
-- El LIMIT se aplica a los POSTEOS antes de tocar finsus_account_history:
-- esa tabla son 105M filas y unir primero para recortar despues agota el
-- statement_timeout (comprobado). Acotar antes del join es la diferencia
-- entre una extraccion y un volcado.
with post as (
    select t.payer_account_id  as account_id,
           td.credit_amount    as interes,
           td.created::date    as fecha
    from aurumcore.transaction_detail td
    join aurumcore.transaction t on t.transaction_id = td.transaction_id
                                and t.payer_account_id = t.payee_account_id   -- autocapitalizacion
    where td.alfanumeric_reference like 'Capitaliza Interes%%'
      -- Rango en vez de `created::date = ...`: castear la columna anula el
      -- indice y la consulta agota el timeout (comprobado en la corrida).
      and td.created >= :fecha_cap::date
      and td.created <  :fecha_cap::date + 1
    limit :limite
)
select
    a.account_number                              as cuenta,
    p.fecha::text                                 as fecha_capitalizacion,
    p.interes::text                               as interes_posteado,
    h.average_balance_amount::text                as saldo_promedio,
    h.interest_rate::text                         as tasa,
    a.activation_date::text                       as fecha_activacion,
    -- dt: el dia de fondeo no cuenta; extremos inclusivos
    (case
        when a.activation_date::date > date_trunc('month', p.fecha)::date
        then extract(day from (date_trunc('month', p.fecha)
                               + interval '1 month - 1 day'))::int
             - extract(day from a.activation_date)::int
        else extract(day from (date_trunc('month', p.fecha)
                               + interval '1 month - 1 day'))::int
     end)::text                                   as dias_devengados
from post p
join aurumcore.account a on a.account_id = p.account_id
join aurumcore.finsus_account_history h
                         on h.account_id = p.account_id
                        and h.record_date >= :fecha_cap::date
                        and h.record_date <  :fecha_cap::date + 1
where h.average_balance_amount is not null
  and h.interest_rate is not null
order by a.account_number;
