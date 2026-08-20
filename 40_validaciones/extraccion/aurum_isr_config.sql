-- AURUM · Parámetros de ISR desde system_configuration (cierra P-010, lado config). SOLO LECTURA.
-- No lleva datos de cliente. Sustento: K-FIS-002 (F-009: tax.days.year, uma, exención).
select name, value, category, branch_id
from aurumcore.system_configuration
where lower(name) like '%tax%'
   or lower(name) like '%isr%'
   or lower(name) like '%uma%'
   or lower(name) like '%yield%exempt%'
   or lower(name) like '%exempt%'
order by category, name;
