-- =============================================================================
-- AURUM · CONTABLE-B1 — doble partida diaria · SOLO LECTURA
-- BOUNDED: agrega en el servidor a UNA fila por dia dentro de [:fecha_ini, :fecha_fin).
--
-- Modelo (REFERENCIA_TABLAS_POR_CASO §CONTABLE-B1 · PLAN_CONTABLE_BC.md):
--   AurumCore no guarda poliza ni balanza como tabla; el asiento vive en
--   transaction_detail, con `debit_amount` NEGATIVO y `credit_amount` POSITIVO.
--   Cada fila es un asiento balanceado, asi que la doble partida del dia es
--   literalmente una suma que se cancela:
--
--       SUM(debit_amount) + SUM(credit_amount) = 0     (tolerancia 0.00)
--
-- Es origin-agnostico a proposito: la doble partida debe cuadrar para TODO lo
-- que el core postea, sea migrado o vivo. Filtrar por origin aqui escondaria
-- justo el asiento descuadrado que se busca.
--
-- Se agrega en SQL y no en Python porque el detalle diario son millones de
-- filas: traerlas para sumarlas seria un volcado, no una extraccion acotada.
-- El conteo de movimientos viaja para que un dia vacio se distinga de un dia
-- que cuadra (universo vacio NO es un pase).
-- =============================================================================
select
    td.created::date::text                  as fecha,
    count(*)::text                          as n_movimientos,
    coalesce(sum(td.debit_amount), 0)::text  as suma_debit,
    coalesce(sum(td.credit_amount), 0)::text as suma_credit
from aurumcore.transaction_detail td
where td.created >= :fecha_ini
  and td.created <  :fecha_fin
group by td.created::date
order by td.created::date;
