---
id: K-TMP-001
titulo: Ventanas de proceso y asincronía nocturna entre OpenFin y Aurum
dominio: TMP
estado: CONFIRMADO
confianza: alta
version: 2
creado: 2026-08-14
actualizado: 2026-08-15
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:19:05-00:21:01"
    hablante: "SPEAKER_05"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:33:09 y @00:38:38"
    hablante: "SPEAKER_10 (Néstor, inferido) / SPEAKER_04"
  - ref: 20_fuentes/v2t/finsus_assessment_20260814_01/finsus-assessment-20260814-01-6452c817.md
    ubicacion: "@00:44:08 y @00:48:22"
    hablante: "SPEAKER_04"
relaciones:
  refina: []
  depende_de: [K-ARQ-002]
  contradice: []
  usado_por: []
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Varios procesos de cálculo corren en **momentos distintos en cada core**, lo que
genera descuadres de saldo por **sincronía**, no por cálculo.
  → fuente: F-001 @00:19:05, @00:33:09

## Detalle (calendario declarado en la sesión)
- [CONFIRMADO] **Operaciones asíncronas nocturnas** (de madrugada): pago de rendimientos de
  cuentas plazo, retornos de inversión, reinversiones automáticas, domiciliaciones. Un robot
  nocturno compara "OpenFin hizo estas / Aurum hizo estas por estos montos". → @00:19:05.
- [CONFIRMADO] **OpenFin paga rendimientos de plazo ~18:30 (6:30pm)**; **Aurum los paga en la
  noche**. Entre esas horas hay descuadre de saldo disponible. → @00:33:09, @00:38:38.
- [CONFIRMADO] **Rendimientos a cuentas VISTA: el primer día del mes**, a todas las cuentas vista.
  → @00:44:08.
- [CONFIRMADO] **Rendimientos a cuentas PLAZO: de lunes a viernes** (los fines de semana no se
  pagan rendimientos, salvo la vista del primer día del mes). → @00:48:22.
- [CONFIRMADO] **Robot de conciliación cada 4 horas**: onboardings, nuevas entrantes, SPEI in/out
  en ambos cores (pendiente de reactivar). → @00:19:05.
- [CONFIRMADO] (F-011) OpenFin **cierra vista ~18:00** y Aurum a medianoche → ~6 h de descuadre en
  el saldo promedio. El **corte transaccional** se puede tomar a las 00:00+1 min (día anterior
  completo); los nocturnos ya corrieron ~06:00. → F-011 @01:18:29, @01:17:29, @01:18:02.

## Implicaciones para la validación
- El comparador A vs B **debe conciliar en ventanas de tiempo con delta** y hacer roll-forward
  (ver K-PRC-001), no comparar snapshots instantáneos.
- El oráculo (C) debe modelar el **momento** de cada proceso (fecha valor vs fecha de aplicación).
- Foco caliente: coincide con candidato PAR-338 (días inhábiles en inversiones) y PAR-121 (fecha
  valor de movimientos manuales).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-14 | Creada desde F-001. | F-001 |
| 2 | 2026-08-15 | Se añade cierre de vista ~18:00 y corte transaccional 00:00. | F-011 |
