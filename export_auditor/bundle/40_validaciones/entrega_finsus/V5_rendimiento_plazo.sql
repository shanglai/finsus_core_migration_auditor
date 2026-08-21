-- =============================================================================
-- V5 · Rendimiento de inversiones a plazo fijo (2.1.2)  · SOLO LECTURA
-- Afirma: el oraculo reproduce `iv_payment_plan.interest_amount` de AurumCore al centavo,
--   periodo a periodo, con la formula del doc (Ceil10/Ceil10/RoundHalfEven2, base 360).
--   Validado: 775/775 periodos (40 cuentas) = 100%.
-- Como usar: elige una inversion (:cuenta, '100-2301-XXXX'). El query trae su plan de pagos con
--   los dias de cada periodo. Luego en Python:
--     from oraculo_rendimientos import rendimiento_plazo
--     # tasa: si no la tienes a la mano, se despeja del periodo 1:
--     #   tasa = rend_1 * base / (capital * dias_1) * 100     (base = 360)
--     rendimiento_plazo(capital, tasa, dias_periodo, base)  ->  debe = rend_aurum
-- =============================================================================
select p.account_number,
       p.payment_number,
       p.start_date,
       p.due_date,
       (p.due_date - p.start_date)   as dias_periodo,
       p.interest_amount             as rend_aurum,
       a.iv_initial_amount           as capital
from aurumcore.iv_payment_plan p
join aurumcore.account a on a.account_number = p.account_number
where p.account_number = :cuenta
  and p.interest_amount > 0
order by p.payment_number;

-- Nota: base de dias (360 comercial / 365-366 natural) y "tiempo exacto vs aproximado" se definen por
-- producto (doc "Cálculo de Intereses de Créditos" §1). En la muestra validada todas fueron 360 + dias
-- reales de calendario. La tasa vive en el esquema del producto (pendiente de fijar el join exacto;
-- entre tanto se despeja del periodo 1 y se verifica que reproduce TODOS los periodos).
