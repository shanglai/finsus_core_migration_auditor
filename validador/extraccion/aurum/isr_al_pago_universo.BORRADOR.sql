-- =============================================================================
-- AURUM · UNIVERSO del caso ISR-01 — un renglon por evento de retencion de ISR
-- SOLO LECTURA · BOUNDED: cohorte_acc (cuentas) + ventana [:fecha_ini, :fecha_fin)
--
-- Para que el oraculo pueda recalcular la retencion necesita, por evento:
--     saldo_total_cliente · saldo_cuenta · dias_periodo
-- que no viven en una sola tabla. Esta consulta los junta.
--
-- Origen de cada pieza (todas son HECHOS de la BD, no calculos de ningun core:
-- charter §9.1 — el oraculo no copia logica, solo consume saldos y fechas):
--   B (lo que el core postea)  : transaction_detail, firma verificada en
--                                40_validaciones/extraccion/aurum_isr_al_pago.sql
--   saldo_cuenta / dias_periodo: iv_payment_plan + account.iv_initial_amount
--   saldo_total_cliente        : account_balance_tracking, suma de las cuentas
--                                del titular a la fecha de corte
--
-- [SUPUESTO 1] El evento de ISR se aparea con el periodo del plan de pagos por
--   (titular, cuenta de inversion, fecha de pago). Si un titular tuviera dos
--   pagos el mismo dia por la misma inversion, el apareo seria ambiguo: la
--   consulta los deja como filas separadas y el comparador las marcara.
-- [SUPUESTO 2] `saldo_total_cliente` se toma al dia habil del pago. S-FIS-001
--   no fija si es el saldo del dia del pago o el del cierre anterior.
--   Mientras P-006 no cierre, esto es una decision de modelado declarada, no
--   un hecho verificado — viaja en `supuestos:` del YAML y queda en la
--   evidencia de cada corrida.
--
-- Los montos salen como ::text a proposito: la ruta del dinero va en Decimal.
-- =============================================================================
select
    ah.accountholder_id::text                    as accountholder_id,
    inv.account_number                           as cuenta_inversion,
    pp.payment_number                            as periodo,
    td.created::date::text                       as fecha_pago,
    -- B · lo que AurumCore postea
    td.credit_amount::text                       as isr_posteado,
    -- insumos del oraculo (C)
    inv.iv_initial_amount::text                  as saldo_cuenta,
    (pp.due_date - pp.start_date)::text          as dias_periodo,
    coalesce(st.saldo_total, 0)::text            as saldo_total_cliente,
    false                                        as persona_moral,
    pe.account_number                            as cuenta_isr_contraparte,
    -- Delimitador "Aurum vivo" = `created >= cutover` (la ventana de este
    -- query). `origin` viaja SOLO para transparencia del desglose, no como
    -- filtro: su semantica es mixta y sigue sin confirmarse (SOL-004 / P-013).
    coalesce(t.origin, '(null)')                 as origen
from aurumcore.transaction_detail td
join aurumcore.transaction   t   on t.transaction_id  = td.transaction_id
join aurumcore.account       pa  on pa.account_id     = t.payer_account_id
join aurumcore.account       pe  on pe.account_id     = t.payee_account_id
join aurumcore.accountholder ah  on ah.accountholder_id = pa.accountholder_id
-- La inversion se identifica por la REFERENCIA del asiento
-- ('Pago de rendimientos-100-2301-XXXX'), que es el metodo de
-- isr_live_nativo.py. Las dos alternativas que se probaron el 2026-08-21
-- estaban mal y quedan documentadas para que nadie las repita:
--   * unir por accountholder: producto cartesiano entre TODAS las inversiones
--     del cliente y su plan de pagos -> agotaba el statement_timeout;
--   * unir contra la cohorte con ON TRUE: FABRICA filas (cada evento de ISR
--     se apareaba con las 3 cuentas de la cohorte, 3 eventos -> 27 filas).
-- El prefijo de la referencia NO es estable: se observaron '-100-2301-X',
-- 'Pago de rendimientos-100-2301-X' y 'Pago de rendimientos 10-100-2301-X'.
-- Lo estable es el SUFIJO con forma de numero de cuenta, asi que se extrae por
-- patron en vez de por posicion de split_part.
join aurumcore.account       inv on inv.account_number = substring(td.alfanumeric_reference from '[0-9]+-[0-9]+-[0-9]+$')
                                and inv.product_type_key = 'INVESTMENT_ACCOUNT'
join aurumcore.iv_payment_plan pp on pp.account_id = inv.account_id
                                and pp.payment_date::date = td.created::date
left join (
        -- saldo total del titular por dia: suma de TODAS sus cuentas
        select a2.accountholder_id,
               abt.registration_date::date as fecha,
               sum(abt.final_balance)      as saldo_total
        from aurumcore.account_balance_tracking abt
        join aurumcore.account a2 on a2.account_id = abt.account_id
        where a2.accountholder_id in (
                select a3.accountholder_id from aurumcore.account a3
                join cohorte_acc c on c.account_number = a3.account_number)
          and abt.registration_date >= :fecha_ini
          and abt.registration_date <  :fecha_fin
        group by a2.accountholder_id, abt.registration_date::date
     ) st on st.accountholder_id = ah.accountholder_id
         and st.fecha = td.created::date
where td.transaction_type    = 'INTERNAL TRANSFER'
  and td.transaction_channel = 'Generic'
  and split_part(pe.account_number, '-', 2) = '0000'      -- contrapartida = cuenta de ISR
  and pa.accountholder_id in (
        select a4.accountholder_id from aurumcore.account a4
        join cohorte_acc c2 on c2.account_number = a4.account_number)
  and td.created >= :fecha_ini
  and td.created <  :fecha_fin
order by ah.accountholder_id, inv.account_number, pp.payment_number;
