-- ============================================================================================
-- CATÁLOGO ÚNICO DE CONSULTAS DE VALIDACIÓN — Finsus (openfin → AurumCore)
-- Tercero independiente · 2026-08-19 · TODAS son SOLO LECTURA (ningún INSERT/UPDATE/DDL).
--
-- CÓMO USAR:
--   • [OF] = correr contra la base openfin_aurum (t-1), esquema public.
--   • [AC] = correr contra la base aurumcore, esquema aurumcore.
--   • Parámetros con :nombre — sustituir por la cohorte/fechas al ejecutar.
--       :fecha_ini, :fecha_fin           ventana [ini, fin)
--       :cuentas                          lista de account_number Aurum ('100-2301-XXXX', ...)
--       :suc, :rol, :aso                  llave de cliente OpenFin (p.ej. 100, 10, 14083)
--       :isr_txn_type                     (ver §3.3; la firma verificada está en §3.4)
--   • Recomendado abrir la sesión con:  SET default_transaction_read_only = on; SET statement_timeout='300s';
--   • Complementa a los oráculos en Python (oraculo_isr.py, oraculo_rendimientos.py), que traen
--     sus propias consultas mínimas + el cálculo de referencia (motor C). Este archivo es el catálogo
--     completo de lo que se ejecutó, para que Finsus lo reproduzca ("que le muevan").
-- ============================================================================================


-- ============================================================================================
-- 0. VOLUMETRÍA — medidas antes de extraer (baratas, acotadas)
-- ============================================================================================

-- 0.1 [OF] Estimación de filas de isr_diario SIN full-scan (catálogo del sistema)
select 'openfin.isr_diario' as tabla,
       (select reltuples::bigint from pg_class where relname='isr_diario') as filas_estimadas;   -- ~171,829,856

-- 0.2 [OF] Rango de fechas del devengo diario
select min(fecha) as fecha_min, max(fecha) as fecha_max from isr_diario;                          -- 2025-09-03 → 2026-08-17

-- 0.3 [AC] Volumen de iv_payment_plan (rendimiento por período)
select count(*) as filas, count(distinct account_number) as cuentas,
       min(due_date) as fecha_min, max(due_date) as fecha_max
from aurumcore.iv_payment_plan;                                                                   -- ~36,705,512

-- 0.4 [AC] Volumen de lc_finantial_data_stage (staging IFRS9 / IDNC)
select count(*) as filas, count(distinct account_number) as cuentas,
       min(information_date) as fecha_min, max(information_date) as fecha_max
from aurumcore.lc_finantial_data_stage;                                                           -- ~2,651,935

-- 0.5 [AC] Volumen y rango de account_balance_tracking (saldo diario)
select count(*) as filas, count(distinct account_id) as cuentas,
       min(registration_date) as fmin, max(registration_date) as fmax
from aurumcore.account_balance_tracking;

-- 0.6 [AC] Esquemas fiscales con tasa ISR (cuántos y rango)
select count(*) as esquemas_isr, min(isr) as isr_min, max(isr) as isr_max
from aurumcore.account_tax where isr > 0;


-- ============================================================================================
-- 1. PARÁMETROS DEL ISR (P-010) — config del sistema
-- ============================================================================================

-- 1.1 [AC] system_configuration: días del año, exención (UMA × factor), etc.
select name, value, category, branch_id
from aurumcore.system_configuration
where lower(name) ~ 'tax|uma|exent|exempt|isr|reten'
order by name;
--   Esperado (ago-2026): tax.days.year=365 · yield.tax.exempt.uma.amount=5 · yield.tax.exempt.amount=206367.60 (stale, C-001)

-- 1.2 [AC] account_tax: tasa ISR aplicada (concepto 'ISR BASE' = 0.90 %, base_period_type=2)
select name, isr, iva, isr_concept, base_period_type, status
from aurumcore.account_tax where isr > 0 order by isr;

-- 1.3 [AC] cat_tax: catálogo de tasas (vacío en este entorno; la tasa real vive en account_tax)
select id, scheme_id, isr, iva, status, activation_date from aurumcore.cat_tax order by activation_date desc nulls last;


-- ============================================================================================
-- 2. MAPEO DE LLAVES (cliente / cuenta) entre cores
-- ============================================================================================

-- 2.1 [OF] Cliente OpenFin: (idsucursal,idrol,idasociado) -> kasociado (llave interna de isr_diario)
select idsucursal, idrol, idasociado, kasociado
from asociados where idsucursal=:suc and idrol=:rol and idasociado=:aso;

-- 2.2 [OF] Cuenta OpenFin: (idsucaux,idproducto,idauxiliar) -> kauxiliar (llave de isr_diario_aux_log); + tasa/saldo
select idsucaux, idproducto, idauxiliar, kauxiliar, saldo, montocontrato, tasa, fechaape, fechacancelacion, estatus
from acreedores where idsucaux=:suc and idproducto=2301 and idauxiliar=:aso;   -- ejemplo producto 2301 (inversión)

-- 2.3 [AC] Cliente/cuenta AurumCore: la llave '100-10-X' NO existe (accountholder.external_id es entero interno).
--          Se ancla por account.account_number ('100-2301-X') -> accountholder_id -> todas las cuentas del titular.
select acc.account_number, acc.accountholder_id, ah.external_id
from aurumcore.account acc
join aurumcore.accountholder ah on ah.accountholder_id = acc.accountholder_id
where acc.account_number = any(:cuentas);


-- ============================================================================================
-- 3. ISR — EXTRACCIÓN Y COMPARACIÓN (A = openfin · B = AurumCore · C = oráculo)
-- ============================================================================================

-- 3.1 [OF] A — ISR DEVENGADO diario por cliente (provisión). Trae saldo (base del día) e isr.
select a.idsucursal, a.idrol, a.idasociado, d.kasociado, d.fecha, d.saldo as saldo_base_of, d.isr as isr_dia_of
from isr_diario d
join asociados a on a.kasociado = d.kasociado
where a.idsucursal=:suc and a.idrol=:rol and a.idasociado=:aso
  and d.fecha >= :fecha_ini and d.fecha < :fecha_fin
order by d.fecha;

-- 3.2 [OF] A — Provisión acumulada por INVERSIÓN (Σ del devengo diario, nivel cuenta). = el 'isr_of' del árbol.
select l.kauxiliar, round(sum(l.isr_diario),2) as provision_total, min(l.fecha) fmin, max(l.fecha) fmax
from isr_diario_aux_log l
where l.kauxiliar = :kauxiliar
group by l.kauxiliar;

-- 3.3 [AC] DESCUBRIMIENTO del asiento de ISR al pago (por si cambia): perfil por tipo sobre cuentas semilla
select td.transaction_type, td.transaction_channel, t.type, t.origin,
       count(*) n, min(td.credit_amount) cmin, max(td.credit_amount) cmax
from aurumcore.transaction_detail td
join aurumcore.transaction t on t.transaction_id = td.transaction_id
join aurumcore.account acc   on acc.account_id in (t.payer_account_id, t.payee_account_id)
where acc.account_number = any(:cuentas)
  and td.created >= :fecha_ini and td.created < :fecha_fin
group by 1,2,3,4 order by n desc;
--   Hallazgo: el ISR es transaction_type='INTERNAL TRANSFER' + channel='Generic', contraparte cuenta ISR (producto '0000').

-- 3.4 [AC] B — ISR AL PAGO (retención real), firma verificada. isr = credit_amount; débito en la vista del cliente.
select pa.accountholder_id, pa.account_number as cuenta_cliente, td.created as fecha_pago,
       td.credit_amount as isr_retenido_ac, pe.account_number as cuenta_isr, td.transaction_id
from aurumcore.transaction_detail td
join aurumcore.transaction   t  on t.transaction_id = td.transaction_id
join aurumcore.account       pa on pa.account_id = t.payer_account_id
join aurumcore.account       pe on pe.account_id = t.payee_account_id
where td.transaction_type    = 'INTERNAL TRANSFER'
  and td.transaction_channel = 'Generic'
  and split_part(pe.account_number,'-',2) = '0000'
  and pa.accountholder_id = (select accountholder_id from aurumcore.account where account_number = any(:cuentas))
  and td.created >= :fecha_ini and td.created < :fecha_fin
order by pa.accountholder_id, td.created;

-- 3.5 [AC] SALDO BASE para el oráculo C — saldo diario por cuenta (todas las cuentas del titular)
select acc.accountholder_id, acc.account_number, split_part(acc.account_number,'-',2) as producto,
       t.registration_date as fecha, t.final_balance, t.accumulated_balance_total, t.accumulated_balance_partial
from aurumcore.account_balance_tracking t
join aurumcore.account acc on acc.account_id = t.account_id
where acc.accountholder_id in (
        select a2.accountholder_id from aurumcore.account a2 where a2.account_number = any(:cuentas))
  and t.registration_date >= :fecha_ini and t.registration_date < :fecha_fin
order by acc.accountholder_id, acc.account_number, t.registration_date;

-- 3.6 [OF] CHEQUEO 'A vs regla' en SQL puro — ¿el devengo diario de OpenFin sigue la regla?
--          (acepta UMA 2026=213,973.20 o 2025=206,367.60 por el rezago de transición de feb)
select count(*) as dias,
       count(*) filter (
         where abs(d.isr - round((0.009/365.0)*greatest(0, d.saldo-213973.20),2)) <= 0.02
            or abs(d.isr - round((0.009/365.0)*greatest(0, d.saldo-206367.60),2)) <= 0.02
       ) as dias_que_siguen_la_regla
from isr_diario d
join asociados a on a.kasociado = d.kasociado
where a.idsucursal=:suc and a.idrol=:rol and a.idasociado=:aso
  and d.fecha >= :fecha_ini and d.fecha < :fecha_fin;


-- ============================================================================================
-- 4. RENDIMIENTO — plazo fijo (2.1.2)
-- ============================================================================================

-- 4.1 [AC] Plan de pagos + capital + días de cada período (comparar contra oraculo_rendimientos.rendimiento_plazo)
select p.account_number, p.payment_number, p.start_date, p.due_date,
       (p.due_date - p.start_date) as dias_periodo, p.interest_amount as rend_aurum,
       a.iv_initial_amount as capital
from aurumcore.iv_payment_plan p
join aurumcore.account a on a.account_number = p.account_number
where p.account_number = :cuenta and p.interest_amount > 0
order by p.payment_number;
--   Validado: 40 cuentas / 775 períodos = 100% al centavo (base 360). Tasa: por fijar el join de esquema;
--   entre tanto se despeja del período 1: tasa = rend_1 * 360 / (capital * dias_1) * 100.


-- ============================================================================================
-- 5. GAP B — Suspensión de devengo / IDNC (REFUTADO: existe)
-- ============================================================================================

-- 5.1 [AC] Evidencia de que el IODNC/IMDNC existe y opera
select count(*) as filas,
       count(*) filter (where coalesce(iodnc,0)<>0)                                   as con_iodnc,
       count(*) filter (where coalesce(imdnc_eco_ab,0)<>0 or coalesce(imdnc_eco_ca,0)<>0) as con_imdnc,
       count(*) filter (where coalesce(capital_venc,0)<>0)                            as con_capital_venc,
       round(sum(coalesce(iodnc,0)),2) as suma_iodnc,       -- contra-cuenta (saca interés de resultados)
       round(sum(coalesce(io,0)),2)    as suma_io
from aurumcore.lc_finantial_data_stage;                     -- con_iodnc ≈ 2,339,027 ; suma_iodnc ≈ -4,564,129,742.71

-- 5.2 [AC] Catálogo de etapas / severidad (clasificación por días de atraso)
select stage, min_days_in_stage, days_in_stage
from aurumcore.cat_severity_no_coverage
group by stage, min_days_in_stage, days_in_stage order by stage, min_days_in_stage;


-- ============================================================================================
-- 6. GAP C — Cuota Prosofipo / fondo de protección (CONFIRMADO: falta)
-- ============================================================================================

-- 6.1 [AC] Búsqueda del módulo Prosofipo (se espera 0 en las tres líneas)
select 'system_configuration' as fuente,
       count(*) as coincidencias
from aurumcore.system_configuration where lower(name) ~ 'prosofipo|fondo|protec|ipab|cuota|seguro.*dep'
union all
select 'tablas', count(*)
from information_schema.tables where table_schema='aurumcore' and lower(table_name) ~ 'prosofipo|fondo|protec|ipab|insur'
union all
select 'columnas (excl. garantias de credito)', count(*)
from information_schema.columns where table_schema='aurumcore'
  and lower(column_name) ~ 'prosofipo|fondo|protec|ipab' and table_name !~ 'guarantee';
--   Único match: loan_guarantee.protection_percentage = garantías de CRÉDITO (colateral), NO fondo de depósitos.


-- ============================================================================================
-- FIN. Resumen de hallazgos que estas consultas sustentan:
--   • ISR: AurumCore retiene al pago = la regla (C=B). El 'descuadre' OF≠AC es MODELO (provisión-devengo
--     vs retención-al-pago). Set de desviación material 3,236/3,236 = MODELO. Defecto real de cálculo = $0.
--   • Parámetros vs norma (P-010): UMA 42,794.64 (INEGI) · tasa 0.90% (LIF 2026 Art.24) · exención 5×UMA
--     (LISR Art.93 fr.XX) · 365 días. Todos ✔.
--   • Rendimiento plazo (2.1.2): oráculo = iv_payment_plan al centavo (775/775).
--   • Gap B (IDNC): existe (refutado como motor faltante). Gap C (Prosofipo): falta (confirmado).
-- ============================================================================================
