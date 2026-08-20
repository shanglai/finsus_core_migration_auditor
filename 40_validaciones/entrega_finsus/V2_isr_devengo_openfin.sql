-- =============================================================================
-- V2 · OpenFin: el ISR DEVENGADO diario sigue la regla  · SOLO LECTURA (base openfin_aurum / t-1)
-- Afirma: el "ISR de OpenFin" es un DEVENGO/provision diario (isr_diario), y ese devengo diario
--   coincide con la regla. Por eso el "descuadre OF vs AC" del arbol es MODELO (provision-devengo
--   de OpenFin vs retencion-al-pago de AurumCore), NO un defecto de calculo.
-- Como usar: elige un cliente por su llave (:suc, :rol, :aso), p.ej. 100 / 10 / 14083.
--   Compara isr_openfin contra isr_regla_2026 (o _2025 en la ventana de transicion de feb).
-- Regla: isr_dia = (0.9/100/365) x max(0, saldo - exencion). Exencion 2026 = 213,973.20 ; 2025 = 206,367.60.
-- =============================================================================
select d.fecha,
       d.saldo,
       d.isr                                                            as isr_openfin,
       round((0.009/365.0) * greatest(0, d.saldo - 213973.20), 2)       as isr_regla_2026,
       round((0.009/365.0) * greatest(0, d.saldo - 206367.60), 2)       as isr_regla_2025_transicion,
       d.isr - round((0.009/365.0) * greatest(0, d.saldo - 213973.20), 2) as dif_vs_2026
from isr_diario d
join asociados a on a.kasociado = d.kasociado
where a.idsucursal = :suc and a.idrol = :rol and a.idasociado = :aso
order by d.fecha;

-- Resumen (misma logica): fraccion de dias que coinciden con la regla (aceptando UMA 2026 o 2025)
select count(*)                                                                as dias,
       count(*) filter (
         where abs(d.isr - round((0.009/365.0)*greatest(0,d.saldo-213973.20),2)) <= 0.02
            or abs(d.isr - round((0.009/365.0)*greatest(0,d.saldo-206367.60),2)) <= 0.02
       )                                                                       as dias_que_siguen_la_regla
from isr_diario d
join asociados a on a.kasociado = d.kasociado
where a.idsucursal = :suc and a.idrol = :rol and a.idasociado = :aso;
