---
id: K-DAT-005
titulo: Fuente de la verdad por dato entre sistemas (core/middleware/backend/analyzer)
dominio: DAT
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-15
actualizado: 2026-08-15
fuentes:
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85__s009__00-00-52.jpg
    ubicacion: "screenshot · deck slide 3 (AS-IS ecosistema, asteriscos)"
  - ref: 20_fuentes/v2t/finsus_assessment_02_20260814/finsus-assessment-02-20260814-a86e0f85.md
    ubicacion: "@00:03:38, @00:33:27"
    hablante: "SPEAKER_04 (experto OpenFin/Citi, inferido)"
relaciones:
  refina: [K-ARQ-001]
  depende_de: []
  contradice: []
  usado_por: [00_entendimiento/MODELO_DATOS_OPENFIN.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] La información vive en todo el ecosistema, con una **fuente de la verdad por dato**
(asterisco en el slide 3, corroborado narrativamente):
- **Core (OpenFin):** TASAS, CAT/GAT, Datos de Producto, Datos Fiscales, **Saldos**, **Movimientos**, Cuentas Contables, PLD, Listas.
- **Middleware:** Nivel de Cuenta, Límite Transaccional, Valor de la UDI, **Tipo de Operación**.
- **Backend:** Datos de Cliente, Datos personales, Datos de Contacto (y TDD/TDC).
- **Analyzer:** Clave SIEC (CVE SIEC), PLD y KYC, Scoring y Buró, Datos del producto (PM/PFAE/PYME), Dictamen Legal.
  → fuente: F-011 s009 (deck) + @00:03:38.

## Detalle
- El **saldo** es siempre fuente-de-verdad de **OpenFin** (de ahí salen los reportes regulatorios);
  middleware/backend son réplicas que pueden descuadrarse. → @00:33:27.
- El **tipo de operación** es fuente-de-verdad del middleware — por eso Aurum lo reconstruye desde
  ahí/logs (K-MOV-005).
- Es el mismo deck que F-002 (proyecto "Cliente Único"); aquí se lee la slide 3 con los asteriscos.

## Implicaciones para la validación
- Para cada dato a comparar hay que ir a **su** fuente de verdad, no asumir que "todo está en el core".
- Refuerza que el oráculo tome el saldo de OpenFin como referencia A (no del middleware/backend).

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-15 | Creada desde F-011 (deck s009). | F-011 |
