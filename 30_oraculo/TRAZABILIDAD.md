# Trazabilidad del Oráculo (Motor C)

Mapa `pieza de conocimiento → spec → función → test`. Cuando una pieza cambia de versión, todas
sus dependientes quedan marcadas como **"revisión requerida"** (CLAUDE.md §9.3, §6.2 paso 7).

Estado: **poblado** (2026-08-20) — los oráculos están portados al VALIDADOR
(`validador/oraculos/`) con batería de pruebas formal en `validador/tests/`.

| pieza (K-…) | versión pieza | spec (S-…) | función (src) | test | estado |
|-------------|---------------|------------|---------------|------|--------|
| K-FIS-002 | 3 | S-FIS-001 | `validador/oraculos/isr.py::isr_retenido` | `validador/tests/test_oraculo_isr.py` (5 casos de oro) | ✅ oráculo listo · validado 3,236/3,236 (spec por sincronizar a v3) |
| K-FIS-003 | 2 | (comparación) | `validador/oraculos/isr.py::isr_devengo_diario` | (sin corrida contra BD) | 🟡 código listo · caso `ISR-02` |
| K-FIS-004 | 1 | S-FIS-001 §Parámetros | `validador/oraculos/parametros_isr.py::valor_normativo` | `test_caso_trampa.py` (C-001) | ✅ **caso-trampa vivo**: detecta el rezago de UMA |
| K-DEV-001 | 2 | S-FIS-001 | `validador/engine/redondeo.py` (modos como parámetro) | `validador/tests/test_redondeo.py` | ✅ semántica de los 5 modos fijada por prueba |
| K-DEV-002 | **3** | (S-DEV-001 por escribir) | `validador/oraculos/rendimientos.py::rendimiento_vista`, `::saldo_promedio_rendimiento` | `test_oraculo_rendimientos.py` | **revisión requerida** (v2→v3) · falta spec · casos `REND-VISTA` 🟡 y `SALDO-PROM` ⛔ |
| K-DEV-003 | 1 | (S-DEV-002 por escribir) | `validador/oraculos/rendimientos.py::rendimiento_plazo` | `test_oraculo_rendimientos.py` · validado 775/775 | 🟡 código OK · falta spec formal |

> Los originales `entrega_finsus/oraculo_isr.py` y `entrega_finsus/oraculo_rendimientos.py`
> siguen en su lugar como parte del paquete de entrega. La aritmética portada es idéntica;
> lo que cambió es que los redondeos y los parámetros normativos ahora son **explícitos y
> por año de causación**, para no repetir el rezago de C-001.
>
> **Deduplicación (2026-08-20):** `oraculo_rendimientos.py` existía dos veces, byte-idéntico,
> en `entrega_finsus/` y en `comparadores/`. Se eliminó la copia de `comparadores/` (era
> huérfana: ningún script la importaba). La copia canónica es la de `entrega_finsus/`, que es
> la que cita `README_VALIDACION.md`. Dos copias de una regla son dos versiones esperando
> divergir; en una auditoría eso es un riesgo, no una comodidad.

## Dependencias rotas / revisión requerida
(ninguna) — nota: S-FIS-001 depende de parámetros normativos [PENDIENTE] (P-010); no ejecutar en
silencio (§9.3).

## Regla de independencia (§9.1)
El oráculo se implementa **desde las piezas de conocimiento**, nunca copiando la lógica de
openfin ni de `<CORE_NUEVO>`. Si para escribir una función se necesita mirar cómo lo hace un core,
falta una pieza → registrarla como `[PENDIENTE]`.
