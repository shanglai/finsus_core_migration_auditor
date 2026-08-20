-- =============================================================================
-- OPENFIN · ISR DIARIO (motor A, dia-por-dia a nivel cliente)  ·  SOLO LECTURA
-- Fuente real: isr_diario(fecha, kasociado, saldo, isr) — F-015 (openfin_columnas).
-- Mapea kasociado -> cliente 100-10-X via asociados. Acotado a cohorte + ventana.
-- Sustento: A15-ISR-DIARIO, K-DAT-002, PLAN_FASE1_ISR.md A4.
-- Parametros: :fecha_ini, :fecha_fin. Cohorte: cohorte_of(id_sucursal,id_role,id_asociado).
-- =============================================================================
select a.idsucursal            as id_sucursal,
       a.idrol                 as id_role,
       a.idasociado            as id_asociado,
       (a.idsucursal::text || '-' || a.idrol::text || '-' || a.idasociado::text) as id_cliente,
       d.kasociado,
       d.fecha,
       d.saldo                 as saldo_base_of,   -- base que usa OpenFin ese dia
       d.isr                   as isr_dia_of       -- ISR diario que OpenFin acumula
from isr_diario d
join asociados a  on a.kasociado = d.kasociado
join cohorte_of c on c.id_sucursal = a.idsucursal
                 and c.id_role      = a.idrol
                 and c.id_asociado  = a.idasociado
where d.fecha >= :fecha_ini and d.fecha < :fecha_fin
order by a.idsucursal, a.idrol, a.idasociado, d.fecha;

-- NOTA: para el detalle por CUENTA (no por cliente) existe isr_diario_aux_log
-- (kauxiliar, fecha, isr_diario) — 42 GB. Solo si se requiere prorrateo por inversion.
