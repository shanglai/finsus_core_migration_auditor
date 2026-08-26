# Estado — resumen ejecutivo (rumbo Dictamen 7-sep)

> Finsus · openfin (A) → AurumCore (B) · árbitro: oráculo independiente C · corte 2026-08-23.

## Súper resumen

**Terminamos de construir TODOS los motores de cálculo y están validados hasta donde el dato alcanza — 0 desviaciones de cálculo abiertas.**

De **21 puntos de validación**:

- **13/21 en verde** (validados, 0 desviaciones): rendimiento plazo (100% en 530K periodos) · ISR retención (C=B) · crédito ordinario (96.8%) · moratorio (81.1%) · días · IVA (99%) · GAT inversión · IFRS 9 etapas+% (= config real de Aurum, 37/37) · amortización · CAT (fórmula 3/3) · Motor B (completitud) · contable doble partida ($0.00) · cuentahabientes WSO2.
  → **Falta el Manual de Cálculos (SOL-015)** para cerrar al 100% per-contrato **3 de esos motores**: aplicación de reserva IFRS 9, GAT/CAT per-contrato, y modo de redondeo. (No muestran desviación en lo validado; el Manual da los parámetros finos que el GTM no trae.)
- **3/21 se cierran el 31-ago** (cuando corran los cálculos de cierre de mes): rendimiento vista, saldo promedio, ISR-vivo. Sus oráculos ya están construidos y validados vs doc; solo esperan la corrida (bloqueo de tiempo, no de defecto).
- **4/21 gaps rojos** (naturaleza distinta): OpenFin → defecto en moratorios One Click (#6) · Aurum → suspensión de devengo / IDNC · Aurum → cuota Prosofipo (se hace por fuera de Aurum) · Documentación → mapeo `tipo_movimiento → cuenta contable` (por pedir).
- **1/21 middleware** — falta acceso **y** definición de alcance para iniciar la validación.

---

## Detalle de los 21 puntos

### ✅ 13 en verde — validados, 0 desviaciones
| # | Motor / validación | Resultado | Contra qué se validó |
|---|---|---|---|
| 1 | Rendimiento plazo fijo | 100% · 0 viol. en 530,195 periodos | doc |
| 2 | ISR retención (histórico) | C = B = 765.75; parámetros = ley 2026 | doc + norma + config |
| 3 | Crédito ordinario | 96.8% exacto a 1e-8; 0/4,091 tasa | doc |
| 4 | Crédito moratorio | 81.1% exacto a 1e-8 | doc |
| 5 | Crédito conteo de días | log = período de amortización | doc + log |
| 6 | Crédito IVA sobre interés | 99.0% exacto (16%) | doc + datos |
| 7 | GAT inversión | oráculo reproduce exacto `nominal_cgat` | doc + datos |
| 8 | IFRS 9 etapas + % reserva | **C = config real de Aurum** (37/37) | config |
| 9 | Amortización francesa | interés Actual/360 exacto; identidad 99.9% | doc + datos |
| 10 | CAT (One Click + Francesa) | fórmula 3/3 vs doc; caso real exacto | doc |
| 11 | Motor B — completitud A vs B | +0.1% a +2.1% (OF≥AU) = sin faltante | inferencia |
| 12 | Contable — doble partida | balanza = $0.00 (0/7 días) | identidad |
| 13 | Cuentahabientes WSO2 | Aurum→WSO2 completo | datos |

**Falta el Manual (SOL-015) para llevar al 100% per-contrato:** ① aplicación de reserva IFRS 9 (base "capital/intereses exigibles" + tabla de PI); ② GAT/CAT per-contrato (tramos de tasa + semántica del campo `cat`); ③ modo de redondeo (residuo sub-centavo).

### 📅 3 se cierran el 31-ago (corrida de cierre de mes)
| # | Validación | Estado |
|---|---|---|
| 14 | Rendimiento vista (capitalización mensual) | oráculo listo; espera la corrida del día 1° |
| 15 | Saldo promedio de rendimiento | solo se genera en la corrida (logs) |
| 16 | ISR-vivo nativo | necesita el saldo base punto-en-tiempo |

### 🔴 4 gaps rojos
| # | Gap | Naturaleza / acción |
|---|---|---|
| 17 | Moratorios One Click (#6) | **defecto histórico de OpenFin** (Aurum cobra bien) → decisión de Comité |
| 18 | Suspensión de devengo / IDNC | **gap de motor de Aurum** (CNBV C-16) → regulatorio |
| 19 | Cuota Prosofipo | **se hace por fuera de Aurum** (LACP 104 Bis) → formalizar |
| 20 | Mapeo `tipo_movimiento → cuenta contable` | **gap de documentación** (matriz "por incorporar") → pedir catálogo |

### 🔌 1 middleware
| # | Punto | Estado |
|---|---|---|
| 21 | Middleware | sin acceso **y** sin alcance definido → conexión + definición de qué valida C |

---

**Los dos desbloqueos que cierran casi todo lo abierto:** ① el **Manual de Cálculos (SOL-015)** y ② el **cierre del 31-ago**.
Regla de honestidad: cada "verde" se sostiene en una validación que devuelve **las filas que violan la regla**; los no-conformes se explican, nunca se ocultan.

---

## Actualización 2026-08-24 — respondió Finsus (respuesta parcial; doc completo en preparación)
Ver `RESPUESTA_FINSUS_2026-08-24.md`. **Resuelve la dirección de los 5 cierres** y **el punto 5 puede destrabar 2 de los 3 del 31-ago sin esperar:**
- **PD/IFRS 9:** el Core **no calcula PD** — usa **% directo CNBV** (nuestro enfoque, ya validado 37/37). Entregan las 9 tablas (falta validar comercio/reestructurado).
- **Reserva de intereses:** base definida (EPRC; en E3 el interés vencido es **informativo**). Pendiente las fórmulas exactas.
- **Tramos de tasa de inversión:** existen en 2 estructuras; arman la tabla consolidada. La tasa puede venir **del canal** (explica el residuo per-contrato de GAT/CAT).
- **Redondeo:** **half-up, por evento** (cada devengo se redondea antes de acumular). Explica el residuo sub-centavo.
- **Saldo promedio:** **se guarda en la póliza de intereses con `dt`** (base 360, `SPM×dt×tasa/36000`, al centavo). → **acción inmediata (VPN datos):** localizar la póliza y reconstruir; podría mover vista/saldo promedio antes del 31-ago (la corrida VIVA sí sigue en 31-ago).
