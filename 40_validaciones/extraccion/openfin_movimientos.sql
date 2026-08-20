-- OPENFIN (public) · Movimientos del cohorte por periodo: detalle_auxiliar ⋈ detalle_auxiliar_masdatos.
-- SOLO LECTURA. Columnas confirmadas por \d+. Params: cohorte_of(...), :fecha_ini, :fecha_fin.
-- Acotar SIEMPRE por fecha (índice idx_da_fecha(fecha,hora)); detalle_auxiliar pesa ~65 GB. Sustento: K-DAT-002/003, K-MOV-005/006.
select
    da.secuencia,
    da.idsucaux, da.idproducto, da.idauxiliar,     -- llave cuenta
    da.fecha, da.hora, da.periodo,
    da.cargo, da.abono, da.saldo,                  -- saldo = saldo FINAL (no hay saldo anterior)
    da.montoio, da.montoim, da.montoimp, da.montocomision,
    da.tipomov,                                    -- 0..5 (clasificación interna del movimiento)
    da.idsucpol, da.tipopol, da.idpoliza,          -- póliza contable
    da.referencia, da.folio_ticket,
    dam.tipo_transaccion,                          -- 3 SPEI / 183 transf interna / 0 interna
    dam.id_external,                               -- llave cross-sistema (garantizada en SPEI)
    dam.transaction_id, dam.concepto, dam.origen
from public.detalle_auxiliar da
left join public.detalle_auxiliar_masdatos dam on dam.secuencia = da.secuencia
join public.acreedores a
  on a.idsucaux = da.idsucaux and a.idproducto = da.idproducto and a.idauxiliar = da.idauxiliar
join cohorte_of c
  on c.id_sucursal = a.idsucursal and c.id_role = a.idrol and c.id_asociado = a.idasociado
where da.fecha >= :fecha_ini
  and da.fecha <  :fecha_fin;
