-- =============================================================================
-- AURUM · IFRS9-E3 — reserva de capital en etapa 3 · SOLO LECTURA
-- BOUNDED: ventana [:fecha_ini, :fecha_fin) + cota :limite.
--
-- Identidad: en etapa 3 (>= 90 dias de mora), la reserva de capital es el
-- capital vencido por el porcentaje que corresponde a los dias de mora:
--
--     reserva_cap = |capital_venc| x pct(dias_mora)
--
-- El % de C NO se lee de aqui: sale de las Tablas 1/2/3 del GTM-IFRS9, en
-- `oraculo_ifrs9`. Leerlo de `lc_reserve_ifrs` y compararlo contra el mismo
-- core seria circular. Que los dos coincidan 37/37 es un RESULTADO, no el
-- metodo.
--
-- Medido antes de escribir el caso (400 filas de agosto, E3 con capital
-- vencido): la razon |reserva / capital_venc| sale exactamente 75%, 90% o
-- 100% segun el tramo de mora, que es la tabla de consumo no marginado.
--
-- Signos: el staging guarda `capital_venc` y `reserva_cap_result` en negativo
-- (son contra-cuentas) y `reserva_cap_activo` en positivo. Se compara contra
-- el activo, en positivo, para no reportar el 100% de violaciones por una
-- convencion de presentacion.
--
-- ALCANCE: solo E3, consumo, zona no marginada. E1/E2 amortizando y
-- `reserva_int` quedan fuera a proposito — su base depende del spec que sigue
-- pendiente, y aproximarla seria presentar una estimacion como validacion.
-- =============================================================================
select
    s.stage_id::text                              as stage_id,
    s.lc_contract_id::text                        as contrato,
    s.information_date::text                      as fecha_informacion,
    s.mora_days::text                             as dias_mora,
    abs(coalesce(s.capital_venc, 0))::text        as capital_venc,
    abs(coalesce(s.reserva_cap_activo, 0))::text  as reserva_posteada,
    'NON_MARGINAL'                                as zona
from aurumcore.lc_finantial_data_stage s
where s.information_date >= :fecha_ini
  and s.information_date <  :fecha_fin
  and coalesce(s.mora_days, 0) >= 90
  and coalesce(s.capital_venc, 0) <> 0
  and coalesce(s.reserva_cap_activo, 0) <> 0
order by s.information_date, s.lc_contract_id
limit :limite;
