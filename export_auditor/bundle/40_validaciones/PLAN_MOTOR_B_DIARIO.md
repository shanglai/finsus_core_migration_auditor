# Plan / Spec — Motor B: validador de la transaccional diaria (Aurum vs OpenFin)

> Corriente 2 del entregable (NORTE §0). Objetivo: un **tercero independiente** que cruce, **día a día**, la
> transaccionalidad de OpenFin (A) y AurumCore (B), normalizando las diferencias de diseño y **clasificando**
> cada descuadre en causuísticas explicables. **No** es OF-vs-AU a ciegas: el árbitro sigue siendo la
> coherencia de cada core consigo mismo y contra el oráculo (charter §9, K-PRC-001).
>
> Estado: **DESBLOQUEADO** (2026-08-19) — foundation de datos establecida con **nuestros propios accesos**.
> Fuentes: F-021/F-022 (encomienda), F-024 (queries de Finsus, referencia), extracción BD 2026-08-19.

## 1. Acceso — qué alcanzamos y qué no
- ✅ **AurumCore** (`aurumcore`, host .53): `transaction`, `transaction_detail`, `cat_finsus_transaction`, `account`, `accountholder`.
- ✅ **OpenFin** (`openfin_aurum`/`public`, host .164.25): `vista_movimientos_cargos`, `vista_movimientos_abonos`, `cat_tx_cuadre`, `detalle_auxiliar`, `catalogo_tipo_transaccion`, tablas SPEI (`fs_datospeiin/out`, `datahub_speineto`).
- ❌ **NO** alcanzamos `openfin_migracion`/`openfin_m` ni las vistas `aurum_transaction_*` que Finsus pre-armó
  (host/base/usuario distintos, `aurumcoreuser`). Bien por independencia (§9.1): **reconstruimos el mapeo**.
  Acción opcional: pedir lectura a `openfin_migracion` para **benchmarkear** esas vistas (no usarlas como verdad).

## 2. Modelo de datos de cada lado (grano transaccional)
**OpenFin — dos piernas + catálogo:**
- `vista_movimientos_cargos` / `vista_movimientos_abonos`: movimientos tipados por `tipo_transaccion`; llave de
  cuenta `idsucaux-idproducto-idauxiliar` (= `acreedores.cuenta`, K-DAT-003), `fecha`, `hora`, monto, `referencia`.
- `cat_tx_cuadre` (catálogo de cuadre): `tipo_transaccion → descripcion`, `tipo` (1=pierna cargo / 2=pierna abono),
  `cuenta_contable_cargo`, `cuenta_contable_abono`. Ej.: tipo 1 "transferencia interna entre clientes"
  (ambas piernas cuenta de cliente); tipo 3/4 "SPEI" (una pierna interbancaria `1102…`).

**AurumCore — operación atómica + catálogo:**
- `transaction` (cabecera: `payer_account_id`, `payee_account_id`, `gross_amount`, `type`, `channel`, `state`,
  `created`) y `transaction_detail` (piernas: `source_address`/`target_address` → `account`, `credit/debit_amount`).
  **1 fila = 1 operación atómica** (K-MOV-001).
- `cat_finsus_transaction` (410 filas / 348 tipos): `transaction_type → cta_charge, cta_deposit` (dos filas por
  tipo = doble partida). Es el "**catálogo de Ines**" del lado Aurum, gemelo de `cat_tx_cuadre`.

## 3. El crosswalk (la bisagra 2:1 / 1:1)
- **Misma numeración de tipo** en ambos catálogos (`cat_tx_cuadre.tipo_transaccion` ↔
  `cat_finsus_transaction.transaction_type`) y **mismas descripciones** → el crosswalk OF↔AU es **directo por el
  número de tipo**. (Confirmar cobertura: OF tiene 314 tipos [1..314], AU 348 [1..5100, incluye 5xxx crédito].)
- **Clasificación 2:1 vs 1:1** (K-MOV-001 v2) derivable del catálogo:
  - **Peer-to-peer (2:1):** ambas piernas son cuentas **de cliente** (patrón captación, no interbancaria). En OF
    = 1 cargo + 1 abono (dos filas) → en AU = 1 `transaction`. Ej.: tipo 1.
  - **Unidireccional (1:1):** una pierna es **externa/interbancaria** (`1102…`) o de servicios. SPEI-out = solo
    cargo; SPEI-in = solo abono → 1:1 con AU. Ej.: tipos 3/4/5.

## 4. Diseño de la reconciliación (identidad y normalización)
Para una **fecha** dada, por **cuenta**:
1. **Normalizar OF:** unir `vista_movimientos_cargos` + `_abonos`; para tipos **peer-to-peer**, colapsar el par
   cargo+abono (misma referencia/tipo/instante, cuentas opuestas) en **1 operación lógica**; los unidireccionales
   quedan 1 fila.
2. **Aurum:** tomar `transaction` (payer/payee/gross/tipo) como grano atómico equivalente.
3. **Emparejar** OF-normalizado ↔ AU por (cuenta, monto, tipo-crosswalk, ventana de tiempo). **Ventana amplia**:
   AU paga a medianoche, OF a las 18:00 → **6 h de corrimiento**; comparar contra **T-1/T-2 ya saldado**, no el
   mismo instante (F-021 @01:08).
4. **Invariantes (devuelven violaciones, §10):**
   - **Neteo por cuenta-día = 0** tras normalización (Σ cargos−abonos OF = Σ neto AU), tolerancia contable 0.00.
   - **Igualdad de conjunto de operaciones** OF↔AU (con la regla 2:1/1:1); las que no casan → residual.
5. **Clasificar residuales** en causuística (semilla de F-024 + K-MOV):
   `SOLO_EN_OF` · `SOLO_EN_AU` · `MONTO_DISTINTO` · `HORARIO_6H` (cruzó medianoche) · `NO_ATOMICO` (cargo+reverso
   OF sin registro AU, K-MOV-001) · `PRODUCTO_NUEVO_NO_CONECTADO` (One Click, F-021 @00:28) · `EXPLICABLE_OTRO`.

## 5. Pendientes de descubrimiento (acotados, antes de codificar)
1. **Confirmar el emparejamiento de piernas** en `vista_movimientos_cargos/abonos`: ¿qué campo liga el cargo y el
   abono de una misma transferencia interna? (¿`secuencia`, `idpoliza`, `referencia`?). Determina el colapso 2:1.
2. **Construir y congelar el crosswalk** `cat_tx_cuadre` ↔ `cat_finsus_transaction` por tipo; marcar los tipos
   sin correspondencia (314 vs 348) y los 5xxx (crédito).
3. **Regla de clasificación cliente-vs-externo** para 2:1/1:1: formalizar el patrón de cuenta contable
   (`1102…`=interbancaria, `2101/2401…`=cliente) desde `cat_tx_cuadre`.
4. **Evaluar `cat_tx_cuadre`** (y, si nos dan acceso, las vistas `aurum_transaction_*` de `openfin_m`) como
   **benchmark** — nunca como verdad.

## 6. Entregable
- Comparador `40_validaciones/comparadores/motor_b_diario.py` (solo lectura, réplica): entra una fecha, sale el
  set de violaciones + el **reporte de causuística** (conteo, monto, % por clase).
- Se integra al "diario" de Sergio/INCO como el **tercero independiente** (P-016).

## 6.bis PRIMERA CORRIDA (2026-08-19, fecha de datos 2026-08-14)
Comparador `comparadores/motor_b_diario.py` (solo lectura). Salida: `_resultados/motor_b_diario_2026-08-14.txt`.

**Resultado headline — el modelo funciona:**
> OpenFin ops normalizadas = **28,996**  vs  Aurum transaccional-cliente = **29,530**  → **delta −534 (−1.8%)**.

- OF: 36,106 piernas → 28,996 ops tras normalizar 2:1/1:1; monto $528M.
- AU: 96,235 `transaction_detail`, de los cuales **core-interno** (YIELD PAYMENT/TAX, CAPITAL RETURN, INTERNAL
  INVESTMENT TRANSFER = rendimiento/ISR/inversión, **no vienen de canal**) = 66,705; **cliente** = 29,530.
- Excluir el core-interno de Aurum es lo que hace el cruce "peras con peras" (K-MIG-002). El **−1.8%** es la
  causuística a explicar (abajo). Que dé ~2% al primer intento **valida la reconstrucción del mapeo**.

**Causuística surgida (a refinar, no defectos aún):**
1. **NULL `tipo_transaccion`:** 3,506 cargos ($89.3M), 0 abonos — movimientos OF sin tipo. Investigar qué son.
2. **Clasificación PEER/UNI cruda:** el prefijo `21/24` marcó como PEER varios que son **unidireccionales**
   (245 PURCHASE TDD POMELO 1001/0; 314 RETENCIÓN RECOMPENSAS 671/0; 238 NO CLASIFICADO 443/0). La regla
   cliente-vs-externo debe afinarse: `2401…` (comisiones/recompensas/TDD Pomelo) **no** es pierna de cliente
   para emparejar. → mejora directa del clasificador.
3. **Desbalance genuino en PEER reales:** tipo 1 (transf interna) 466/439 = **27 piernas sin par** — contraparte
   fuera del universo vista o cruzó medianoche (`HORARIO_6H`). Es la causuística legítima.
4. **Tipos sin catálogo:** 403/404/409/410 (OF >314) no están en `cat_tx_cuadre`.

**Siguientes pasos (afinar, ya no desbloquear):**
- Reclasificar PEER/UNI con la taxonomía fina de cuenta contable (2401 = no-par).
- Emparejar cargo↔abono por `secuencia N/N+1` (+ monto + referencia) para el conteo exacto de ops PEER.
- Construir el **crosswalk tipo-numérico OF ↔ tipo-texto AU** (`transaction_detail`) para bajar del volumen al
  **match por tipo** y luego instancia-a-instancia.
- Explicar los NULL y los tipos sin catálogo.

## 6.ter Afinación (pasos 1-2-3, 2026-08-19)

**Paso 1 — clasificador refinado (catálogo).** El prefijo de cuenta NO sirve (el catálogo usa cuentas
**puente `2401`** entre las piernas cliente `2101`). Regla nueva: **PEER (2:1) iff el tipo tiene pierna
cargo (tipo=1) y abono (tipo=2) con la MISMA descripción**; si difieren (SPEI "saliente"≠"entrante") = dos
operaciones unidireccionales → UNI. Resultado: **21 PEER / 293 UNI**. La causuística PEER-imbalance bajó de
12 a **3 genuinos** (tipo 1, 177, 182). El cruce de volumen se mantuvo (**−1.7%**), confirmando que la
clasificación afecta la etiqueta, no tanto el conteo.

**Paso 2 — pareo cargo↔abono: no hay llave fiable en las vistas.** `secuencia N/N+1` empareja solo 33%,
`fecha_hora_creacion+monto` 7%, `idpoliza` 30%. Es exactamente lo que las vistas `openfin_m.aurum_transaction_*`
de Finsus resuelven (y no tenemos). **Para el conteo no se necesita** (basta la clasificación de tipo); el
match instancia irá **OF-op ↔ AU-tx directo** (cuenta+monto+categoría+ventana), no por pareo interno de OF.

**Paso 3 — crosswalk por CATEGORÍA** (más robusto que 314 tipos). Categorización **por pierna** (un tipo
reúsa el número para ambas direcciones: SPEI saliente=cargo, entrante=abono). Aurum contabiliza el **SPEI-in
como DEPOSIT**. Resultado 14-ago:

| categoría | OF ops | AU cliente | delta |
|---|---|---|---|
| DEPOSITO | 7,936 | 8,126 | **−2.3%** |
| SPEI_EXTERNA | 10,288 | 9,999 | **+2.9%** |
| TARJETA | 1,605 | 1,576 | **+1.8%** |
| TRANSFER_INTERNA | 7,117 | 9,798 | −27.4% → explicado por los NULL |
| RECOMPENSAS | 1,344 | 0 | OF-only (AU no lo contabiliza como tx cliente) |
| SERVICIOS | 565 | 0 | AU los manda como SPEI/EXTERNAL |

**Causuística nombrada:** (a) **NULL "api_dimmer" 3,506/$89.3M** — movimientos que la **vista de Finsus dejó
sin tipo**; son las transferencias internas que faltan (cierran el gap de TRANSFER_INTERNA). (b) RECOMPENSAS
OF-only. (c) SERVICIOS mapea a EXTERNAL en Aurum. → **Tres categorías (depósito, SPEI, tarjeta) reconcilian a
~3%**; los residuales están explicados, no son defectos.

## 6.quater Queries de Sergio (F-027) + el desbloqueo de `origin` (2026-08-20)

Sergio compartió los queries "live" de captación y pago a créditos (validados vs esquema real). Aportan:
- **Grano AurumCore = `transaction`** (payer/payee, gross_amount) — **confirma nuestro grano** de Motor B.
- **Universo captación** = todas las tx del periodo **excluyendo** dispersiones y pagos de crédito (vía
  `lc_loan_contract.account_id/subaccount_id/subaccount_2nd_id` y `lc_loan_dispersion`, productos 5004/1101).
- **Universo pago-crédito** = AurumCore vía `lc_loan_charge` (VNT/MORA, status 1/3) → `origin_transaction_id` →
  `transaction`, productos (UUIDs normal/black/white); OpenFin vía `detalle_auxiliar`+`deudores`, producto 5004,
  `pago = abono+montoio+montoim+montoimp`.
- **OpenFin lo mapean con `openfin_m.aurum_transaction_final_complete`** (vista pre-armada) — NO la tenemos
  (refuerza pedir `openfin_migracion`, P-016). Nosotros lo reconstruimos (auditable).

**DESBLOQUEO — filtro `origin` (P-013 resuelta) · AÑADIDO A LA METODOLOGÍA:** `transaction.origin IS NULL` =
**generado por AurumCore (live)**; los valores con nombre = **migrado/ingestado**. Se **incorpora `origin is null`
a Motor B y a todos los comparadores A/B** (compara SOLO lo que AurumCore calculó, no lo ingestado — cierra el
riesgo #1, K-MIG-002), **en consonancia con los queries enviados por Sergio (F-027)** que aplican el mismo filtro.
`origin` vive en `transaction` (no en `transaction_detail`) → join. Nota fija en el código de `motor_b_diario.py`.

**Resultado con el filtro (14-ago):** el cruce de volumen pasó de **−1.7% a +0.0%** (OF ops_norm **29,029** vs AU
cliente **29,020**, delta **+9**). El residual eran ~502 `INTERNAL TRANSFER` **migrados** que el filtro excluye.
Por categoría siguen las imperfecciones de mapeo (TRANSFER_INTERNA −23% por los NULL api_dimmer del lado OF), pero
el **total reconcilia casi al punto**.

## 7. Relación con conocimiento
Sustento: [[K-MOV-001]] v2 (2:1/1:1), [[K-DAT-003]] (llaves OF), [[K-DAT-006]] (Aurum), [[K-CTB-001]] (amarre),
[[K-PRC-001]] (validar contra sí mismo), [[K-MIG-002]] (migrado vs generado). Fuente de referencia: F-024.
Pregunta madre: [[P-016]].
