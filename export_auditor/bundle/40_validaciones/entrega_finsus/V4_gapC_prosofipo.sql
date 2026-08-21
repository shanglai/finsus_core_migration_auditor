-- =============================================================================
-- V4 · Gap C (cuota Prosofipo / fondo de proteccion de depositos) — FALTA  · SOLO LECTURA
-- Afirma: AurumCore NO tiene motor para calcular/provisionar la cuota mensual al Fondo de Proteccion
--   (Prosofipo) que toda SOFIPO debe pagar (LACP Art. 104 Bis). No hay tabla, config ni campo.
-- Como usar: correr tal cual. Se espera 0 en las tres lineas (salvo 'protection_percentage' de
--   GARANTIAS de credito, que es otra cosa y por eso se excluye).
-- =============================================================================
select 'system_configuration'                        as fuente,
       count(*)                                       as coincidencias
from aurumcore.system_configuration
where lower(name) ~ 'prosofipo|fondo|protec|ipab|cuota|seguro.*dep'

union all
select 'tablas',
       count(*)
from information_schema.tables
where table_schema = 'aurumcore'
  and lower(table_name) ~ 'prosofipo|fondo|protec|ipab|insur'

union all
select 'columnas (excl. garantias de credito)',
       count(*)
from information_schema.columns
where table_schema = 'aurumcore'
  and lower(column_name) ~ 'prosofipo|fondo|protec|ipab'
  and table_name !~ 'guarantee';

-- Nota: 'Calculo de Seguros Asociados' (punto 2.1.11) es seguro de CREDITOS (del acreditado),
-- distinto del seguro de DEPOSITOS (Prosofipo). No cubre este gap.
