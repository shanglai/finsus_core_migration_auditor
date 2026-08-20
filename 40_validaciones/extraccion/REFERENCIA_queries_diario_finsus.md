# Referencia — queries de día cero / diario de Finsus (F-024)

> **Estatus: REFERENCIA, NO fuente de verdad** (instrucción del usuario, y charter §9.1: el oráculo se
> construye desde las piezas de conocimiento, **no copiando** la lógica de ningún core ni de estos scripts).
> Se usan para **ubicar datos, llaves, filtros y escenarios**, y para diseñar el **Motor B (diario)** y la
> **prueba de día cero** — nunca como definición de la regla correcta.
>
> Fuente: `datos/queries_finsus/queries seguimiento diario.docx` (F-024, gitignored). Autoría: Finsus/Aurum.
> **Credenciales:** el .docx original trae **contraseñas en claro** (dblink). Aquí van **redactadas**; no
> reproducir credenciales en el repo. Ver aviso en bitácora 2026-08-19.

## Endpoints que usa Finsus (redactados) — difieren de los nuestros
| rol | host | base | usuario | esquema | nota |
|---|---|---|---|---|---|
| OpenFin (monitoreo prod) | 172.17.100.14 | openfin_s | monitoreo_ops | public (`acreedores`, `asociados`) | distinto de nuestro t-1 |
| OpenFin (migración) | 10.10.164.25 | openfin_migracion | aurumcoreuser | **openfin_m** | vía `dblink` desde Aurum |
| AurumCore | 10.10.160.27 | aurumcore | zbx_monitor | aurumcore | distinto de nuestro `.53` |
| Identidad (usuarios) | 10.10.160.27 | wso2_identity_shared_db | wso2isuser | — | username/MSISDN (cuentahabientes) |

> Patrón: corren **desde Aurum** y jalan OpenFin por `public.dblink(...)`. El esquema **`openfin_m`** tiene
> **vistas pre-armadas** que mapean transacciones OpenFin a forma Aurum: `aurum_transaction_final_complete`,
> `aurum_transaction_credit_complete_live`, `lc_loan_contract_live`. Útiles como pista; **verificar**, no confiar.

## Reportes / escenarios (día cero + diario)
1. **Captación** — universo de cuentas por producto; OF `acreedores` vs AU `account`+`accountholder`. Filtro OF
   `estatus IN (1,3,4,5)`, `idproducto IN (...)`; **excluye sucursal `201`** (fondeadora — coincide con K-MIG-004).
2. **Créditos descuadre** (3 escenarios):
   - Créditos **LIQUIDADOS en Aurum pero ACTIVOS en OpenFin**.
   - **NO liquidados en Aurum** por **abonos anticipados mal calculados**.
   - **NO liquidados en Aurum** por **descuadre de saldos y ordenamiento distinto de cobro**.
   Compara `aurumcore.lc_loan_contract`+`lc_loan_amortization` vs `openfin_m.lc_loan_contract` (producto `5004`).
3. **Cuentahabientes** — escenarios: username/MSISDN nulos; estatus no activo; activos sin roles; **OpenFin no en
   Aurum**; **Aurum no en OpenFin**. Usa WSO2 (identidad) + `accountholder`.
4. **Inversiones** — saldos/vencimientos; `iv_payment_plan`, `inversiones_vencimiento`.
5. **Saldos** (AU y cruce) — `account`, `stored_value`, `productos_contables`, `cat_accounting_*`.
6. **General** — conteos agregados diarios OF vs AU (clientes totales/nuevos, vista cantidad/monto, etc.).

## Llaves y mapeos que confirman lo nuestro
- OF `acreedores`: `idsucursal-idrol-idasociado` = **usuario**; `idsucaux-idproducto-idauxiliar` = **cuenta**
  (concuerda con K-DAT-003).
- AU: `account.account_number` `SPLIT_PART('-',2)` = **producto**; `account_number → accountholder` (K-DAT-006, K-DEV-002).
- **Exclusión `sucursal/idsucursal = 201`** en ambos (fondeadora) — consistente con K-MIG-004.
- Producto crédito de ejemplo: `5004`. Productos captación: lista parametrizada `PRODUCTOS`.

## Qué reutilizar para el Motor B (diario) y día cero
- El **catálogo de escenarios** de descuadre (arriba) es un buen punto de partida para las **casuísticas**
  de diferencia (crédito y cuentahabientes) — pero cada uno debe re-derivarse y validarse con nuestro oráculo.
- Las vistas `openfin_m.aurum_transaction_*` prometen el **mapeo transaccional OF→AU** (incluye el 2:1
  cuenta-a-cuenta / 1:1 unidireccional de K-MOV-001 v2) — **evaluar** si lo resuelven bien o si hay que
  reconstruirlo desde el catálogo de ~400 (P-016).
- Usar la **réplica** (no T-1) para producción de estas corridas (memoria acceso-bd).

## Cautelas (por qué "no es la verdad")
- Son scripts operativos de Finsus/Aurum: reflejan **cómo Finsus decide comparar**, no la regla normativa.
  Nuestro rol es el **tercero**: el cruce válido es contra el **oráculo**, no OF-vs-AU a ciegas (NORTE §0).
- Filtros y umbrales (estatus 1/3/4/5, producto 5004, orden de cobro) son **decisiones suyas** a verificar.
- No hay garantía de que las vistas `aurum_transaction_*` estén completas o correctas — es justo lo que hay
  que validar (P-016).
