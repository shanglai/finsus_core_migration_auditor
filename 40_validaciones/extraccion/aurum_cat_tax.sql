-- =============================================================================
-- AURUM · Configuracion fiscal ISR (cierra P-010, lado config)  ·  SOLO LECTURA
-- No lleva datos de cliente. Fuentes reales: cat_tax, account_tax (F-014).
-- Sustento: K-FIS-002, S-FIS-001, PLAN_FASE1_ISR.md A2.
-- =============================================================================

-- [1] Catalogo de tasas (la tasa ISR "de fabrica", p.ej. 0.009) ---------------
select id, scheme_id, isr, iva, status, activation_date, last_updated
from aurumcore.cat_tax
order by activation_date desc nulls last;

-- [2] Esquemas fiscales por cuenta (concepto, periodo base, tasa aplicada) -----
select id, name, tax_scheme_id, isr, iva, isr_concept, iva_concept,
       base_period_type, enable, status
from aurumcore.account_tax
order by name;
