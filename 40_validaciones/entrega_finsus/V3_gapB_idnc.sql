-- =============================================================================
-- V3 · Gap B (suspension de devengo / IDNC en cartera vencida) — EXISTE  · SOLO LECTURA
-- Afirma: contrario al gap analysis, AurumCore SI implementa el IODNC/IMDNC (intereses devengados
--   no cobrados) y la clasificacion por etapa. El mecanismo vive en el modulo IFRS9/staging
--   (lc_finantial_data_stage), no en el doc del motor de intereses.
-- Norma (CNBV SOFIPO, IFRS9): al pasar a Etapa 3 (>=90 dias) no se reconoce en resultados el devengo
--   sobre cartera vencida; el IDNC va a cuentas de orden, reserva 100% (Criterio B-4).
-- Como usar: correr tal cual (no lleva parametros). Se espera con_iodnc >> 0 y suma_iodnc < 0.
-- =============================================================================
select count(*)                                              as filas,
       count(*) filter (where coalesce(iodnc, 0) <> 0)       as con_iodnc,          -- Int. Ordinario Devengado No Cobrado
       count(*) filter (where coalesce(imdnc_eco_ab,0) <> 0
                          or coalesce(imdnc_eco_ca,0) <> 0)  as con_imdnc,          -- Int. Moratorio Devengado No Cobrado
       count(*) filter (where coalesce(capital_venc, 0) <> 0) as con_capital_venc,
       round(sum(coalesce(iodnc, 0)), 2)                     as suma_iodnc,          -- contra-cuenta (saca interes de resultados)
       round(sum(coalesce(io, 0)),    2)                     as suma_io_resultados
from aurumcore.lc_finantial_data_stage;

-- Catalogo de etapas (clasificacion por dias de atraso / severidad)
select stage, min_days_in_stage, days_in_stage
from aurumcore.cat_severity_no_coverage
group by stage, min_days_in_stage, days_in_stage
order by stage, min_days_in_stage;

-- [PENDIENTE 2.1.7] Que EXISTA no prueba que sea CORRECTO. Falta validar contra el Modulo IFRS 9:
--   umbral de 90 dias, montos IODNC/IMDNC, contabilizacion a cuentas de orden y reserva al 100%.
