-- =============================================================================
-- AURUM · PARAMETROS FISCALES CONFIGURADOS (caso ISR-03) · SOLO LECTURA
-- BOUNDED por naturaleza: son filas de configuracion, no datos de cliente.
-- No lleva cohorte ni PII.
--
-- Une las dos fuentes de configuracion fiscal en un formato comun
-- (parametro, valor) para que el oraculo normativo las contraste una por una:
--     system_configuration : exencion, dias del anio
--     cat_tax              : tasa ISR "de fabrica"
--
-- CASO-TRAMPA VIVO (C-001): se espera que `yield.tax.exempt.amount` traiga
-- 206,367.60 (5 x UMA 2025) mientras el core APLICA 213,973.20 (5 x UMA 2026).
-- Si esta consulta sale limpia contra la norma 2026, hay que revisar el
-- VALIDADOR antes que el core.
-- =============================================================================
select lower(sc.name)                as parametro,
       sc.value::text                as valor_configurado,
       'system_configuration'        as fuente,
       :anio_causacion::text         as anio_causacion
from aurumcore.system_configuration sc
where lower(sc.name) like '%exempt%'
   or lower(sc.name) like '%tax.days%'
   or lower(sc.name) like '%uma%'

union all

select 'cat_tax.isr'                 as parametro,
       ct.isr::text                  as valor_configurado,
       'cat_tax'                     as fuente,
       :anio_causacion::text         as anio_causacion
from aurumcore.cat_tax ct
where ct.status is null or upper(ct.status::text) not in ('INACTIVE', 'DISABLED')

order by parametro;
