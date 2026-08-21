# Trazabilidad del Oráculo (Motor C)

Mapa `pieza de conocimiento → spec → función → test`. Cuando una pieza cambia de versión, todas
sus dependientes quedan marcadas como **"revisión requerida"** (CLAUDE.md §9.3, §6.2 paso 7).

Estado: **vacío** — no hay specs ni código todavía (arranque en frío).

| pieza (K-…) | versión pieza | spec (S-…) | función (src) | test | estado |
|-------------|---------------|------------|---------------|------|--------|
| K-FIS-002 | 3 | S-FIS-001 | `entrega_finsus/oraculo_isr.py` (5/5) | `oraculo_isr.py` autoprueba | ✅ oráculo listo · validado 3,236/3,236 (spec por sincronizar a v3) |
| K-DEV-001 | 2 | S-FIS-001 | `oraculo_rendimientos.py` (redondeos) | autoprueba | idem (redondeo) |
| K-DEV-002 | **2** | (S-DEV-001 por escribir) | `oraculo_rendimientos.py::rendimiento_vista`, `::saldo_promedio_rendimiento` (autoprueba) | autoprueba | **revisión requerida** (v1→v2: ejercicio migrado + hueco 31-ago) · falta spec |
| K-DEV-003 | 1 | (S-DEV-002 por escribir) | `oraculo_rendimientos.py::rendimiento_plazo` (3/3) | validado 775/775 | 🟡 código OK · falta spec formal |

## Dependencias rotas / revisión requerida
(ninguna) — nota: S-FIS-001 depende de parámetros normativos [PENDIENTE] (P-010); no ejecutar en
silencio (§9.3).

## Regla de independencia (§9.1)
El oráculo se implementa **desde las piezas de conocimiento**, nunca copiando la lógica de
openfin ni de `<CORE_NUEVO>`. Si para escribir una función se necesita mirar cómo lo hace un core,
falta una pieza → registrarla como `[PENDIENTE]`.
