-- OPENFIN (t-1, base openfin_aurum, esquema public) · Inversiones (acreedores, productos plazo).
-- SOLO LECTURA. Columnas confirmadas por \d+ acreedores. Params: cohorte_of(id_sucursal,id_role,id_asociado).
-- Sustento: K-DAT-002 v3, K-DAT-003, K-DAT-004.
select
    a.idsucursal, a.idrol, a.idasociado,           -- llave cliente
    a.idsucaux, a.idproducto, a.idauxiliar,        -- llave cuenta
    a.idproducto      as producto,                 -- 2301/2302/2307/2308
    a.estatus,                                     -- 1..5 (3 activa, 4 cerrada, 5 cancelada)
    a.fechaape        as fecha_apertura,
    a.fechaactivacion,
    a.fechacancelacion as fecha_cierre,
    a.montocontrato   as capital,                  -- monto invertido (capital de la inversión)
    a.saldoinicial,
    a.saldo,
    a.tasa,
    a.plazo, a.diasxplazo,
    a.retxaplicar     as isr_por_aplicar           -- retención ISR pendiente
from public.acreedores a
join cohorte_of c
  on c.id_sucursal = a.idsucursal and c.id_role = a.idrol and c.id_asociado = a.idasociado
where a.idproducto in (2301, 2302, 2307, 2308)
  and a.estatus in (3, 4);
