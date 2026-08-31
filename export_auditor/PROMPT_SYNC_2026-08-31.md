# PROMPT — Sincronización del auditor interno con el export 2026-08-31

Eres el **auditor interno** (nuestro Claude Code): construyes/mantienes el SPA/tablero, los motores y la suite de
sanidad del oráculo (motor C). Llegó un **export nuevo**. Este prompt te dice **qué cambió desde el sync del 28-ago** y
**qué ajustar**. No rehagas lo que ya tienes; **reconcilia** y corre las verificaciones al final.

Terminología (respétala): **auditor interno = tú**. **Grupo auditoría de Finsus** = los auditores de Finsus (personas,
sin ruta a la subred). Cuando un documento hable de "el auditor" construyendo/corriendo, eres tú.

Regla rectora: cada afirmación verifica **la verdad de la fuente** (derivable), no el formato; el fallback de "no
derivable" es un "no lo sé" explícito (`[PEND]`), **nunca un default**. Fuente: `40_validaciones/NORTE_SANIDAD.md`.

## 0. Empieza por aquí
Lee **`export_auditor/00_START_HERE.md`** — es el nuevo punto de entrada del bundle (ruta rápida + mapa de documentos +
orden por rol). Alinea la navegación del tablero con ese mapa.

## 1. Delta desde el sync anterior (28-ago) — qué ajustar
1. **`GLOSARIO_ESTADOS_TABLERO.md` (NUEVO).** Es la "tablita de significados" que Linko prometió al grupo auditoría.
   **Alinea las etiquetas/leyenda/tooltips del tablero exactamente a este glosario:** Estado (validado/**parcial**=falta
   ampliar alcance, no match parcial/bloqueado/sin cruce) · Origen (calculado aquí / citado) · Cobertura
   (datos/volumen/config/completitud) · Escala (1e-8/1e-5/**centavo=titular**) · Sesgo · Alcance. Si tu diccionario
   difiere, adopta el del glosario.
2. **`NORTE_SANIDAD.md` — INV-E5 (alcance declarado) ahora es canónico.** Confirma que tu suite lo tiene (tú lo
   agregaste): cada card debe declarar qué se valida, qué NO, universo y representatividad; falla si hay
   representatividad **inventada** sobre universo `[PEND]` (mismo criterio que INV-H3). Mantén la auto-prueba de
   falsabilidad.
3. **`ACCESO_Y_RED.md` — reencuadrado.** El **auditor interno (tú) SÍ tiene acceso VPN**; los timeouts son
   **intermitentes/transitorios** → reintenta (los comparadores pesados son reanudables, `--skip-hechos`). **No
   reportes "sin ruta a 10.10.0.0/16" como bloqueo permanente.** La sección de provisión de red aplica al **grupo
   auditoría de Finsus**, no a ti.
4. **`INFORME_DETALLADO_AUDITORIA/00_INDICE.md` §4 — AUD-004 (conciliaciones abiertas).** Refléjalo en las cards:
   - `lc_loan_contract`: 31,867 (Linko @2026-08-28) vs 31,866 (tú) = **1 contrato = deriva de tabla viva**. Se cierra
     **declarando la hora de cada medición**, no alineando en silencio. Muestra la hora junto al universo.
   - **VISTA — referencia:** tu corrida fue **agosto sobre cota 20,000 → 96.62% centavo**; el informe cita **julio
     censo 83,094 → 94.76% a 1e-8 / 95.03% centavo**. Ciclos/universos distintos: **ni se contradicen ni se promedian.**
     La card muestra ambas con su etiqueta; referencia vigente = julio censo; se unifica con el cierre del 31-ago.

## 2. Cierre del 31-ago (mañana, ciclo vivo de agosto)
Después de la corrida del cierre (VISTA censo completo de agosto, base 360·dt31; ver `40_validaciones/PLAN_CIERRE_31AGO.md`):
- La card de VISTA pasa de "citado julio / preview agosto-20k" a **una sola cifra: agosto censo, calculado aquí**.
- `MATRIZ_TOLERANCIAS` sale de `[PEND]` para VISTA → cifra de agosto (cierra INV-C3 y el AUD-004 de VISTA).
- SPM (V-05) e ISR-vivo (V-12) salen de 🔒 según lo que arroje la traza de logs. Actualiza sus cards y el badge de sanidad.

## 3. Qué NO cambiar
- No promuevas a "calculado aquí" nada sin corrida con datos. No subas el CAT global 11.6% (los 25,026 constantes son
  data-sourcing). No inventes bases de E1/E2 ni umbral de pago sostenido (siguen `[PEND]` por documento).

## 4. Verificación
- `python 40_validaciones/comparadores/sanity_check.py` → **STATUS GLOBAL: SANO** + auto-prueba OK (atrapa CAT y MOR).
- Autopruebas de fórmula N/N. Cada card: escala en todo % · titular al centavo · alcance + representatividad · badge de
  sanidad · botón "Ejecutar" honesto (solo con feed+caso).

## 5. Reporta de vuelta
Qué ajustaste (por punto), qué quedó pendiente y por qué, y el status de sanidad final. Si algo del alcance o de la
representatividad del informe no te cuadra, **levántalo** (AUD-###) — declarar la discrepancia, no alinearla en silencio.
