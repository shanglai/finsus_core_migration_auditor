# S-FIS-001 — Retención de ISR sobre pago de rendimientos (captación)

Estado: BORRADOR · Creado: 2026-08-14 · Dominio: FIS
Sustento: [[K-FIS-002]] [[K-DEV-001]] [[K-DEV-002]] [[K-DEV-003]] · Relacionado: [[K-FIS-001]]

## Regla
[CONFIRMADO] Al **momento del pago de rendimientos**, se retiene ISR sobre la **parte expuesta**
del saldo total del cliente, prorrateada por cuenta.
  → sustento: K-FIS-002 (F-009 §6, verificado con F-010)

```
saldo_total_cliente = Σ vista(saldo_promedio_mensual) + Σ plazo(capital_inicial)
                      (cuentas con bandera exento aportan 0)
base_exenta         = uma * multiplicador_uma      # personas morales: 0
parte_expuesta      = max(saldo_total_cliente - base_exenta, 0)
isr_diario_cliente  = (tasa_anual / dias_anio) * parte_expuesta      # trunc 20 dec
isr_cuenta          = dias_transcurridos * (monto_cuenta / saldo_total_cliente) * isr_diario_cliente
isr_cuenta_final    = round(isr_cuenta, 2)                            # ver Precisión
```
> ⚠ **[C-002]** El denominador de la proporción es el **saldo_total_cliente** (p.ej. 311,136.07 en el
> caso de oro), **NO** la parte_expuesta/base_gravable (97,162.87). Verificado contra la BD real
> (1-10-370 → 765.75 con ÷saldo_total; ÷base_gravable daría 2,670.41). La spec oficial F-016 escribe
> `÷ base_gravable` — ver contradicción C-002; **C usa ÷saldo_total** hasta que Finsus lo resuelva.

## Definiciones
- `saldo_promedio_mensual(vista)`: [PENDIENTE] definición exacta (media de saldos de cierre) → K-DEV-002, P-006.
- `capital_inicial(plazo)`: [CONFIRMADO] `account.iv_initial_amount` → K-DEV-003.
- `dias_transcurridos`: [CONFIRMADO] días del periodo del plan de pago → K-DEV-003.
- `proporcion_cuenta`: [CONFIRMADO] monto_cuenta / **saldo_total_cliente** (el total, no la parte
  expuesta) → K-FIS-002 (F-010 col G), verificado en BD. Ver C-002.

## Parámetros — CONFIRMADOS contra la norma 2026 (P-010 CERRADA, ver [[K-FIS-004]])
| parámetro | valor (2026) | estado | origen normativo |
|-----------|--------------|--------|------------------|
| `tasa_anual` | 0.009 (0.9%) | **CONFIRMADO vs norma** | **LIF 2026 Art. 24** (remite LISR 54/135); subió de 0.50% (2025) |
| `multiplicador_uma` | 5.0 | **CONFIRMADO vs norma** | LISR **Art. 93 fr. XX** (5×UMA sobre saldo promedio diario; beneficio SOFIPO) |
| `base_exenta` (=uma×5) | **213,973.20** | **CONFIRMADO vs norma + BD** | 5 × 42,794.64. Config `exempt.amount=206,367.60` es stale (C-001) |
| `uma` | 42,794.64 | **CONFIRMADO vs INEGI** | UMA anual 2026 (INEGI, DOF 9-ene-2026, vigente 1-feb-2026) |
| `dias_anio` | 365 | CONFIRMADO config+doc | `tax.days.year`; tasa anual prorrateada |

> **P-010 CERRADA (2026-08-19):** los parámetros ya están verificados contra la norma ([[K-FIS-004]]).
> Recordatorio operativo: la UMA cambia cada 1-feb (2026: 42,794.64; 2025: 41,273.52) y la tasa se fija
> anual en la LIF — el oráculo debe **parametrizar por año de causación** para no repetir el rezago de
> C-001 (feb-2026). Personas morales: LISR Art. 54 excluye retención — ver nota en K-FIS-004.

## Precisión y redondeo (K-DEV-001, F-016 §6 confirma la estructura)
- `decimal.Decimal` en todo, **cero float**.
- `tasa_diaria = tasa/(100×días_año)`: **Trunc20**. `isr_diario_cliente = base_gravable × tasa_diaria`: **Trunc5**.
- `proporción = saldo_cuenta/saldo_total`: **Trunc20**. `isr_diario × días_periodo`: **Trunc20**.
- `isr_cuenta_final`: **Round2** (F-016). [PENDIENTE menor] modo exacto (half_even vs half_up): F-016 no
  lo desambigua; el rendimiento plazo usa half_even. Confirmar con un caso de centavo límite en BD.

## Caso de prueba de oro (de F-010, cliente 100-10-233102, cierre 2026-08-02)
- uma=42,794.64 · mult=5 · base_exenta=213,973.20
- **saldo_total_cliente = 311,136.07** · parte_expuesta = 311,136.07 − 213,973.20 = 97,162.87 · tasa=0.009 · 365 días
- isr_diario_cliente = 2.395796795
- Inversión 100-2301-9645234: 120 días · prop 0.161289432 (= 50,182.96 / **311,136.07**) → **ISR 46.37**
- Inversión 100-2301-10240706: 7 días · prop 0.286611 → **ISR 4.81**
- Inversión 100-2301-10118775: 30 días · prop 0.000651 → **ISR 0.05**
- **Caso BD real (2026-08-18):** 1-10-370, 1 inv 300,000, 361 días, saldo_total=300,000 → C=765.76 = B(765.75).
Estos deben reproducirse al centavo en `tests/test_fis_isr.py`.

## Casos borde a cubrir
saldo_total ≤ exención (no retiene) · persona moral (exención 0) · cuenta exenta (aporta 0) ·
inversión con 0 días transcurridos · cambio de UMA/tasa en el periodo · múltiples cuentas del cliente.

## Lo que esta spec NO cubre
- El ISR de OpenFin (se calcula igual desde la norma y se contrasta; K-FIS-001).
- La retención durante devengamiento (F-009: el ISR NO aplica en devengo, sólo al pago).
- CFDI/constancias.

## Dependencias / trazabilidad
Al implementar: registrar en `TRAZABILIDAD.md` el mapa K-FIS-002 → S-FIS-001 → `src/fiscal.py::isr_pago_rendimiento` → `tests/test_fis_isr.py`.
Si K-FIS-002 o K-DEV-001 cambian de versión → esta spec queda "revisión requerida".
