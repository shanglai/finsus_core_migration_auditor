-- =============================================================================
-- AURUM · REND-PLAZO — universo del rendimiento de plazo fijo · SOLO LECTURA
-- BOUNDED: cohorte_acc (cuentas) + ventana + delimitador de origen.
--
-- Escala V5_rendimiento_plazo.sql (una cuenta a la vez) y adopta el metodo de
-- comparadores/validate_plazo_origin.py, que separa los DOS experimentos del
-- NORTE en vez de mezclarlos:
--
--   :delimitador = 'migrado'  ->  origin = 'FINSUS'   (ingestado de OpenFin)
--                                 el oraculo confirma  C = A   (97.8%)
--   :delimitador = 'live'     ->  origin IS NULL      (generado por AurumCore)
--                                 el oraculo confirma  C = B   (99.7%)
--
-- Por que aqui `origin is null` SI es delimitador limpio, cuando la nota
-- general dice que no lo es: `iv_payment_plan` solo trae FINSUS o null — no
-- tiene tags de canal (DIMO, FINSUS_CREDIT...), que son los que le dan
-- semantica mixta a `transaction.origin`. La regla por tabla viene del prompt
-- de arranque §3. Para transaccional/completitud el delimitador robusto sigue
-- siendo `created >= cutover`.
-- [PENDIENTE · SOL-004] Taxonomia de `origin` sin confirmar por Finsus.
--
-- La TASA no esta limpia en el modelo (`account_yield.interest_rate` = 0 para
-- inversion), asi que se despeja del periodo 1. Se devuelven los insumos del
-- periodo 1 y el despeje se hace en Decimal, en el oraculo: dividir aqui
-- metaria la tasa a la ruta del dinero por aritmetica de servidor.
-- =============================================================================
with base as (
    select
        pp.account_number,
        pp.payment_number,
        pp.origin,
        (pp.due_date - pp.start_date)                          as dias_periodo,
        pp.interest_amount,
        a.iv_initial_amount                                     as capital,
        first_value(pp.interest_amount) over w                  as rend_periodo_1,
        first_value(pp.due_date - pp.start_date) over w         as dias_periodo_1
    from aurumcore.iv_payment_plan pp
    join aurumcore.account a on a.account_id = pp.account_id
    join cohorte_acc c       on c.account_number = pp.account_number
    where pp.interest_paid = true
      and pp.interest_amount > 0
      and pp.payment_date >= :fecha_ini
      and pp.payment_date <  :fecha_fin
      and (
            (:delimitador = 'migrado' and pp.origin = 'FINSUS')
         or (:delimitador = 'live'    and pp.origin is null)
          )
    window w as (partition by pp.account_number order by pp.payment_number
                 rows between unbounded preceding and unbounded following)
)
select
    account_number              as cuenta,
    payment_number::text        as periodo,
    coalesce(origin, '(null)')  as origen,
    dias_periodo::text          as dias_periodo,
    capital::text               as capital,
    interest_amount::text       as rend_posteado,
    rend_periodo_1::text        as rend_periodo_1,
    dias_periodo_1::text        as dias_periodo_1
from base
order by account_number, payment_number;
