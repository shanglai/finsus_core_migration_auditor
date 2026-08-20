-- =============================================================================
-- AURUM · UNIVERSO del caso REND-PLAZO — un renglon por periodo del plan de pagos
-- SOLO LECTURA · BOUNDED: cohorte_acc (cuentas) + ventana [:fecha_ini, :fecha_fin)
--
-- Escala V5_rendimiento_plazo.sql (que corre una cuenta a la vez, :cuenta) a una
-- cohorte. Es exactamente el "escalar muestra" que NORTE_VALIDACION pide para
-- este caso: la regla ya reproduce 775/775 periodos en 40 cuentas.
--
-- B = iv_payment_plan.interest_amount (lo que AurumCore tiene en el cronograma)
-- Insumos de C: capital, dias del periodo, tasa y base de dias.
--
-- [SUPUESTO] La tasa vive en el esquema del producto y el join exacto sigue sin
--   fijarse (nota de V5). Mientras tanto se pasa como PARAMETRO `tasa` desde el
--   CLI, o se despeja del primer periodo:
--       tasa = rend_1 * base_dias / (capital * dias_1) * 100
--   Despejarla del periodo 1 y verificar que reproduce TODOS los demas es una
--   prueba fuerte (775/775), pero no sustituye leer la tasa de su tabla: si la
--   tasa configurada estuviera mal, el despeje la absorbe y el caso pasaria.
--   Ese hueco esta declarado en `supuestos:` del YAML.
-- =============================================================================
select
    pp.account_number                        as cuenta,
    pp.payment_number                        as periodo,
    pp.start_date::text                      as fecha_inicio,
    pp.due_date::text                        as fecha_vencimiento,
    (pp.due_date - pp.start_date)::text      as dias_periodo,
    a.iv_initial_amount::text                as capital,
    pp.interest_amount::text                 as rend_posteado,
    null::text                               as tasa
from aurumcore.iv_payment_plan pp
join aurumcore.account a on a.account_id = pp.account_id
join cohorte_acc c       on c.account_number = pp.account_number
where pp.interest_amount > 0
  and pp.due_date >= :fecha_ini
  and pp.due_date <  :fecha_fin
order by pp.account_number, pp.payment_number;
