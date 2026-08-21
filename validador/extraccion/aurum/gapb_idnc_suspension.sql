-- =============================================================================
-- AURUM · GAPB-IDNC — suspension de devengo en cartera vencida · SOLO LECTURA
-- BOUNDED: ventana [:fecha_ini, :fecha_fin) sobre information_date.
--
-- Identidad (K-REG-001 v3, CONFIRMADA en datos):
--   al pasar el credito a cartera vencida, `io_venc` cancela EXACTAMENTE el
--   interes ordinario devengado `io`, de modo que
--
--       io + io_venc = 0        (tolerancia 0.00)
--
--   es decir: el devengo se suspende y no sigue reconociendose en resultados
--   (Criterio B-4 CNBV / IFRS9, etapa 3 a los 90 dias).
--
-- Se restringe a las filas donde la suspension APLICA (io_venc distinto de
-- cero): en un credito vigente `io_venc` es cero y `io` no, y la identidad no
-- aplica. Meter los vigentes convertiria todo el universo en violaciones y
-- diria justo lo contrario de lo que pasa.
--
-- [PENDIENTE] Falta el barrido de poblacion completa y la contabilizacion a
-- cuentas de orden (NORTE §1 REG 2.1.7). Este caso prueba la MECANICA de la
-- suspension, no la contabilizacion.
-- =============================================================================
select
    s.contract_id::text                     as contrato,
    s.information_date::text                as fecha_informacion,
    coalesce(s.io, 0)::text                 as io,
    coalesce(s.io_venc, 0)::text            as io_venc,
    coalesce(s.iodnc, 0)::text              as iodnc,
    coalesce(s.capital_venc, 0)::text       as capital_venc
from aurumcore.lc_finantial_data_stage s
where s.information_date >= :fecha_ini
  and s.information_date <  :fecha_fin
  and coalesce(s.io_venc, 0) <> 0
order by s.information_date, s.contract_id;
