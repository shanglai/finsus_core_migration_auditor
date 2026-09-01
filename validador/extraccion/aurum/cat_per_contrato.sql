-- =============================================================================
-- CAT-01 · Universo ESTRATIFICADO del Costo Anual Total  ·  SOLO LECTURA
--
-- Especificacion: 40_validaciones/CASO_CAT-01_estratificado.md
--
-- El punto del caso esta en el WHERE, no en el SELECT. `lc_loan_contract.cat`
-- es un campo MIXTO: en la mayoria de los contratos guarda una CONSTANTE
-- copiada, no la salida de un motor. Medido el 2026-08-28: `cat = 27.10` cubre
-- 15,300 contratos que abarcan 521 plazos y 3,930 montos distintos, y un CAT es
-- funcion del monto y del plazo. Comparar el oraculo contra esa constante no
-- prueba nada del motor; por eso el universo se acota al estrato donde el campo
-- SI varia por contrato.
--
-- [1] universo per-contrato (lo que el oraculo recalcula)
-- [2] conteo de los cuatro estratos (para reportar lo que queda fuera y por que)
-- =============================================================================

-- [1] ------------------------------------------------------------------------
with constantes as (
  -- Un valor de `cat` compartido por muchos contratos no puede ser un CAT
  -- per-contrato. El umbral es un parametro del caso, no una constante magica.
  select cat
  from aurumcore.lc_loan_contract
  where cat is not null
  group by cat
  having count(*) >= :umbral_constante
),
base as (
  select c.id, c.contract_number, c.amortization_type, c.loan_amount,
         c.activation_date, c.cat as cat_almacenado, c.account_id
  from aurumcore.lc_loan_contract c
  left join constantes k on k.cat = c.cat
  where c.cat is not null
    and c.cat <> 0                    -- `cat = 0` es A28-CAT-CERO, no un cuadre
    and k.cat is null                 -- fuera las constantes copiadas
    and c.activation_date is not null -- sin t=0 no hay flujo que descontar
),
comision as (
  -- La comision de APERTURA CONFIGURADA (concept = 1; concept = 2 son seguros,
  -- que van en el pago y no en la disposicion). Se toma la fila, NO la suma:
  -- sumar varias filas de configuracion inflaba la comision al doble.
  -- Queda como RESPALDO: manda el cargo realmente aplicado, de abajo.
  select account_id,
         max(percentage_amount) as comision_pct,
         max(fixed_amount)      as comision_fija,
         max(financed)          as comision_financiada
  from aurumcore.lc_account_commission
  where concept = 1
    and account_id in (select account_id from base)
  group by account_id
),
cargo as (
  -- La comision REALMENTE COBRADA. Medido el 2026-09-01: la configuracion no
  -- siempre es lo que se aplico, y el cargo efectivo reproduce el CAT guardado
  -- en mas casos (36.81% contra 33.51% en la cohorte de un pago).
  --
  -- El cargo vive con `charge_type = 'MISC'` (concepto MISCELANEOS), no
  -- 'COMMISSION' — ese literal no existe en la tabla. Lo que identifica a la
  -- comision es la REFERENCIA a `lc_account_commission_id`, asi que se filtra
  -- por ahi y no por el nombre del tipo.
  --
  -- Se SUMAN todos los cargos de comision (usar solo el primero baja a 29.82%)
  -- y se EXCLUYE el IVA: sumar `tax_amount` reproduce el CAT en CERO casos, lo
  -- que confirma la regla de la Circular 21/2009.
  select g.lc_contract_id,
         sum(g.amount) as comision_cobrada,
         count(*)      as n_cargos_comision
  from aurumcore.lc_loan_charge g
  where g.lc_account_commission_id is not null
    and g.lc_contract_id in (select id from base)
  group by g.lc_contract_id
),
pagos as (
  -- Pago para CAT = capital + interes ordinario + seguros + otros, SIN IVA
  -- (`interest_tax_amount`, `tax_insurances` y `tax_misc` quedan fuera por la
  -- Circular 21/2009). Los dias corren desde la ACTIVACION del contrato.
  select a.lc_contract_id,
         array_agg((a.capital_amount + a.interest_amount
                    + coalesce(a.insurances, 0) + coalesce(a.misc, 0))::float8
                   order by a.demandable_date)                        as pago_sin_iva,
         array_agg((a.demandable_date::date - b.activation_date)::int
                   order by a.demandable_date)                        as dias,
         count(*)                                                     as n_pagos
  from aurumcore.lc_loan_amortization a
  join base b on b.id = a.lc_contract_id
  group by a.lc_contract_id
)
select b.contract_number                        as contrato,
       b.amortization_type                      as tipo_amortizacion,
       b.loan_amount                            as monto,
       b.cat_almacenado,
       coalesce(m.comision_pct, 0)              as comision_pct,
       coalesce(m.comision_fija, 0)             as comision_fija,
       coalesce(m.comision_financiada, 0)       as comision_financiada,
       g.comision_cobrada                       as comision_cobrada,
       coalesce(g.n_cargos_comision, 0)         as n_cargos_comision,
       p.pago_sin_iva,
       p.dias,
       p.n_pagos
from base b
join pagos p    on p.lc_contract_id = b.id
left join comision m on m.account_id = b.account_id
left join cargo   g  on g.lc_contract_id = b.id
order by b.contract_number
limit :limite;

-- [2] Los cuatro estratos ------------------------------------------------------
-- Se extraen para PODER REPORTAR lo que el caso deja fuera. Un universo acotado
-- sin el conteo de lo excluido se lee como cobertura total.
with constantes as (
  select cat from aurumcore.lc_loan_contract
  where cat is not null group by cat having count(*) >= :umbral_constante
)
select case when c.cat is null            then 'sin_cat'
            when c.cat = 0                then 'cat_cero'
            when k.cat is not null        then 'constante_copiada'
            when c.activation_date is null then 'sin_activacion'
            else 'per_contrato' end                      as estrato,
       count(*)                                          as contratos,
       count(*) filter (where c.status = 'ACTIVE')       as activos
from aurumcore.lc_loan_contract c
left join constantes k on k.cat = c.cat
group by 1
order by 2 desc;
