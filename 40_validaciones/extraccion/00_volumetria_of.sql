-- =============================================================================
-- VOLUMETRIA OpenFin (isr_diario)  ·  MEDIDAS  ·  SOLO LECTURA
-- Correr contra openfin_aurum (t-1). Sustento: PLAN_FASE1_ISR.md A1.
-- Parametros: :fecha_ini, :fecha_fin. Cohorte: cohorte_of(id_sucursal,id_role,id_asociado).
-- =============================================================================

-- [OF-1] Estimacion BARATA de filas de isr_diario (sin full-scan)
select 'openfin.isr_diario' as tabla,
       (select reltuples::bigint from pg_class where relname = 'isr_diario') as filas_estimadas;

-- [OF-2] Rango de fechas del ledger diario (usa indice sobre fecha)
select min(fecha) as fecha_min, max(fecha) as fecha_max
from isr_diario;

-- [OF-3] Medida ACOTADA a cohorte + ventana (bounded; no full-scan)
select count(*)                       as filas,
       count(distinct d.kasociado)    as clientes,
       min(d.fecha)                   as fecha_min,
       max(d.fecha)                   as fecha_max,
       sum(d.isr)                     as isr_total,
       sum(case when d.isr = 0 then 1 else 0 end) as dias_isr_cero,
       count(*) filter (where d.saldo is null)    as saldo_nulos
from isr_diario d
join asociados a  on a.kasociado = d.kasociado
join cohorte_of c on c.id_sucursal = a.idsucursal
                 and c.id_role      = a.idrol
                 and c.id_asociado  = a.idasociado
where d.fecha >= :fecha_ini and d.fecha < :fecha_fin;
