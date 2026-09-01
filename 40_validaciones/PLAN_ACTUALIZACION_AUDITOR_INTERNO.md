# Plan — Cerrar una versión del auditor interno, incorporando las observaciones de auditoría

> **Objetivo:** congelar una **versión entregable** del auditor interno (SPA/tablero + motores) que responda a las
> observaciones de Auditoría Interna de Finsus (Criterios de Hallazgos Bloqueantes F-032 + peticiones de las reuniones
> F-030/F-031), rumbo al **Dictamen del 7-sep**. Linko · corte 2026-08-31.
> Terminología: **auditor interno** = nuestro Claude Code (construye el motor/tablero); **grupo auditoría** = Finsus.

## 1. Insumos de este lado (Linko), que se congelan
- **Informe Detallado de Auditoría** (`INFORME_DETALLADO_AUDITORIA/`) — alcance, periodo, universo, representatividad, santo y seña por punto (+ AUD-004).
- **Crosswalk Criterios Bloqueantes ↔ cobertura** (`CROSSWALK_CRITERIOS_BLOQUEANTES.md` + Word) — el marco del Dictamen.
- **Corrida de la madrugada (31-ago→01-sep):** VISTA censo agosto + `dt` por cuenta + SPM + ISR-vivo (saca de 🔒 a los motores de alcance crítico). Ver `PLAN_CIERRE_31AGO.md`.
- **CAT-01** (estrato per-contrato) y, si se logra, **crosswalk OF↔AU** (SOL-004, criterio #6).
- **Bundle 119 archivos:** NORTE_SANIDAD + sanity_check, glosario, acceso/red, K-MOV-002, manuales, dossier, matriz.

## 2. Qué debe incorporar el motor del auditor interno (mapeado a cada observación)
| Observación de auditoría | Ajuste en el motor/tablero | Dónde ya está el brief |
|---|---|---|
| **Umbral $0.99 MXN** (F-032, criterio raíz) | Cada card marca **explícitamente el umbral de negocio $0.99** además del centavo/1e-8, para que se lea "por debajo del bloqueante". | nuevo — agregar a §3 del PROMPT_AUDITOR_SPA |
| **#2 sesgo (errores sistemáticos)** | Card con sesgo muestra la descomposición (redondeo → precisión de base → residual) y la lectura "método, no core". | §11 (playbook del sesgo) |
| **#3 reproducibilidad** | Badge "reproducible por el auditor" + health-check; el manual + bundle permiten recálculo independiente. Depende del **acceso del grupo auditoría**. | ACCESO_Y_RED.md · MANUAL_USO |
| **#8 pruebas no ejecutadas** | Los 🔒 dicen "insumo externo faltante" (no falla); tras el 31-ago, VISTA/SPM/ISR-vivo → ejecutado. | §3.2/§12 |
| **Alcance + representatividad** (F-031, Polo) | Cada card: universo total, % y **qué se valida / qué NO** (INV-E5). | §3.3 · INV-E5 · informe detallado |
| **Glosario de estados** (F-031) | Leyenda/tooltips del tablero = `GLOSARIO_ESTADOS_TABLERO.md` exacto. | glosario |
| **Sanidad** (nuestra) | Invariantes H/E/C/T + badge global SANO + auto-prueba de falsabilidad. | NORTE_SANIDAD · sanity_check.py · §12 |
| **Hallazgos levantados** (A28-CAT-CERO, D2, morales, IDNC/Prosofipo) | Mostrarlos como **observaciones/hallazgos**, no como bloqueantes de cálculo; con su clasificación y dueño. | crosswalk · P-021/023/024 |
| **K-MOV-002 / SOL-004** | Si se logra el crosswalk OF↔AU, Motor B pasa de volumen a **instancia-a-instancia**. | K-MOV-002 · COMPARACION D1 |

## 3. Secuencia
- **Fase 0 — Congelar el corte de datos (hoy / madrugada).** Correr 31-ago (VISTA/SPM/ISR-vivo) + CAT-01 + OF↔AU si la
  VPN lo permite. **Declarar el corte:** fecha, universo y hora de cada medición (cierra el patrón AUD-004). Guardar
  resultados en `_resultados/`.
- **Fase 1 — Sync al auditor interno.** Pasarle el bundle + `PROMPT_SYNC_2026-08-31.md` + crosswalk + informe detallado.
  Que reconcilie: alcance/representatividad, glosario, sanidad (INV-E5), AUD-004, **umbral $0.99**.
- **Fase 2 — Actualización del motor.** El auditor interno actualiza cifras (VISTA agosto), estados (🔒→ejecutado),
  agrega el **badge de umbral $0.99** y el **badge de reproducibilidad**, alinea la leyenda al glosario, y cablea los
  hallazgos levantados como observaciones.
- **Fase 3 — Verificación.** `sanity_check.py` → SANO + auto-prueba OK; autopruebas de fórmula N/N; health-check verde;
  cada card cumple el checklist de §4.
- **Fase 4 — Congelar la versión.** Etiquetar la versión (fecha + corte de datos), regenerar el bundle, generar el
  paquete de entrega + un prompt de sync corto, y dejar constancia del **corte común** (lo que la auditoría pidió).

## 4. Definition of Done (listo para entregar)
- [ ] `sanity_check.py` = **SANO** + auto-prueba atrapa los bugs históricos.
- [ ] Autopruebas de fórmula N/N; health-check verde.
- [ ] Todo motor de alcance crítico **ejecutado** o etiquetado **insumo externo faltante** con su razón y fecha de desbloqueo.
- [ ] Cada card: escala · procedencia · alcance · representatividad · **umbral $0.99** · badge de sanidad · botón honesto.
- [ ] Crosswalk criterios ↔ cobertura **sin bloqueante de cálculo abierto**; hallazgos levantados con dueño.
- [ ] **Versión congelada** con corte declarado (fecha/universo/hora) — reproducible por el grupo auditoría.

## 5. Reparto
- **Linko (este Claude Code):** corridas 31-ago, informe detallado, crosswalk, K-MOV-002, OF↔AU, prompts de sync.
- **Auditor interno (otro Claude Code):** actualiza tablero/motor, corre sanity, congela la versión.
- **Grupo auditoría Finsus:** provisión de acceso (ACCESO_Y_RED), reproduce, comenta.

## 5b. Secuencia POSTERIOR a la completitud (acordada 2026-09-01)
Una vez completos los pendientes de datos (tríada 8/5/2, D2, y los que apliquen):
1. **Validar resultados** — que cada cifra tenga sustento y método correcto; **cero `[PEND]`** donde ya sea computable.
2. **Documentos al 100%** — sobre todo los de **auditoría de Finsus**: el **Crosswalk de Criterios Bloqueantes** y el
   **Informe Detallado (documento exhaustivo)** actualizados con todas las cifras y estados.
3. **Generar el bundle** y el **prompt** para el auditor interno.
4. **El material para el auditor interno debe MOSTRAR dónde se atienden las observaciones del equipo de auditoría de
   Finsus** (mapeo observación → dónde/cómo se atiende). El `CROSSWALK_CRITERIOS_BLOQUEANTES` es la base; el tablero y
   el prompt deben hacerlo explícito y navegable.
5. **Explicabilidad ante todo:** todo residuo/no-conforme se explica (cohorte, causa, convención), nunca se fuerza un
   número global. Patrón: estratificar (como CAT e IVA por tasa), no promediar.

**Regla de oro (no negociable):** un resultado nuevo **no reemplaza** uno en firme sin **preguntar al usuario primero**,
mostrando **qué sustituye y por qué**. Matches no obvios / inferidos → se marcan, no se asumen. Doble-check antes de correr.
Siempre propagar la **tríada 8/5/2 decimales** (no solo donde el cuadre es parcial). Respetar el NORTE_SANIDAD y los
métodos/cálculos provistos.

## 6. Riesgos / dependencias
- **VPN intermitente** y **logs que rotan** (captura del 31-ago es lo más urgente).
- **SOL-015** (convención de días del CAT) acota el dictamen del residuo de CAT-01.
- **Acceso del grupo auditoría** (criterio #3) — ruta a la subred + usuario read-only.
- **Definiciones de Finsus** (D2 mapeo contable, personas morales) — no son de cálculo nuestro.
