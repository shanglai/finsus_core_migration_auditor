---
id: K-REG-002
titulo: Cuota al Fondo de Protección (Prosofipo) — Gap C de Finsus CONFIRMADO (motor faltante)
dominio: REG
estado: CONFIRMADO
confianza: alta
version: 3
creado: 2026-08-19
actualizado: 2026-08-19
fuentes:
  - ref: F-020 GAP_Analysis_Motores.pdf (Finsus) — Gap C
    ubicacion: "Motor de Cuotas de Seguro de Depósitos (IPAB/Prosofipo)"
  - ref: Ley de Ahorro y Crédito Popular (LACP)
    ubicacion: "Art. 104 (Comité Técnico) y Art. 104 Bis (cálculo de cuotas ordinarias mensuales) · https://www.diputados.gob.mx/LeyesBiblio/pdf/LACP.pdf"
  - ref: Fondo de Protección de Sociedades Financieras Populares (Prosofipo)
    ubicacion: "https://www.prosofipo.mx/ ; DOF 23-03-2017 (reglas del Fondo)"
  - ref: BD AurumCore (aurumcore) — búsqueda de módulo Prosofipo (solo lectura, 2026-08-19)
    ubicacion: "system_configuration=0, tablas=0, columnas=0 (solo protection_percentage de garantías de crédito)"
relaciones:
  refina: []
  depende_de: []
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] El **Gap C de Finsus** es un **motor faltante REAL**: AurumCore **no calcula ni provisiona la
cuota al Fondo de Protección (Prosofipo)** que toda SOFIPO debe pagar. No hay motor, tabla, configuración ni
campo para ello en el core. A diferencia del Gap B (que sí existía en el modelo), aquí genuinamente falta.

## Lo que exige la norma (verificado)
[CONFIRMADO] Toda SOFIPO está obligada al **Fondo de Protección** ("Fondo de Protección de Sociedades
Financieras Populares y Protección a sus Ahorradores", Prosofipo), constituido bajo la **LACP**:
- **Cobertura:** hasta **25,000 UDIs** (~$213,000) por ahorrador por SOFIPO (vista y plazo).
- **Financiamiento:** con **cuotas que pagan las propias SOFIPOs** (no se cobra prima al ahorrador).
- **Cuotas ordinarias mensuales:** su cálculo sigue los lineamientos del **Comité Técnico** conforme al
  **Art. 104 Bis** de la LACP (Comité Técnico referido en Art. 104, fr. V). Base ligada a los depósitos captados.

## Lo que muestra AurumCore (el motor falta) — evidencia
[CONFIRMADO] Búsqueda en el modelo de datos y en la BD en vivo (2026-08-19), solo lectura:
- Diccionario (`aurum_columnas.csv`/`aurum_tablas.csv`): **0 coincidencias** de prosofipo/fondo/protección/cuota/ipab.
- BD `aurumcore`: `system_configuration` con esos términos = **0 filas**; tablas = **0**; columnas = **0** de
  prosofipo/fondo/protección/ipab. Únicas coincidencias: `loan_guarantee.protection_percentage` e
  `ifrs9_loan_guarantee.protection_percentage` → son **garantías de crédito** (colateral), NO el fondo de
  protección de depósitos. Concepto distinto.

→ El core **no incluye** el cálculo/provisión de la cuota Prosofipo en sus motores de captación. Coincide con
el gap analysis de Finsus.

## Disposición de Finsus (F-021, sesión 2026-08-19) — CONFIRMADA
[CONFIRMADO] Ante nuestra pregunta de si la cuota Prosofipo se calcula "por fuera o de manera adicional",
Finsus (Jorge, negocio) respondió: **"hoy lo hacen por fuera, eso es un hecho; y visualizan que va a seguir
siendo por fuera"** (proceso manual / hasta la contabilidad). → fuente: F-021 @00:18:13 y @00:41:23.
- Es decir: **no es un defecto que AurumCore vaya a corregir**; es un **proceso externo aceptado y consciente**.
  El hallazgo se mantiene, pero su clasificación práctica es **DIFERENCIA_DISENO_AUTORIZADA** (motor deliberadamente
  fuera del core), no un defecto a resolver en la migración.
- **Riesgo residual que NO desaparece:** al ser manual/externo, persiste el riesgo de error/omisión y de
  descuadre contable-regulatorio. Recomendación de tercero: que el proceso externo esté **documentado, con
  control y conciliación**, y que el Comité lo registre formalmente como excepción (charter §11).

## Respuesta oficial de AurumCore (F-023, §3) — distingue COBERTURA-841 de CUOTA
[CONFIRMADO] AurumCore responde a la observación así (importante leerlo con precisión):
- **La observación (gap) misma admite:** *"...requiere calcular y provisionar mensualmente la **cuota** del
  fondo... AurumCore no incluye este cálculo dentro de sus motores de captación."* → coincide con esta pieza.
- **La respuesta NO habla de la cuota, habla de la cobertura:** AurumCore calcula *"el **monto y porcentaje
  cubierto** por el Fondo de Protección"* **al generar el reporte 841** (R04-0841), con el monto de cobertura
  configurado en **System Configuration**. Explícito: *"Estos valores **no se calculan ni se almacenan diaria
  o mensualmente por cliente**; se determinan al momento de generar el 841."*

[INFERIDO] Son **dos cosas distintas**: (a) **cobertura reportada** por ahorrador en el 841 (hasta 25,000 UDIs
— esto AurumCore **sí** lo calcula, a tiempo de reporte); (b) **cuota mensual** que la SOFIPO paga al Fondo
(la provisión-gasto) — **esto sigue faltando** en el core. Por tanto la respuesta de AurumCore **NO refuta**
el Gap C; lo **confirma** para la cuota y sólo aporta que la cobertura-841 sí existe.

[PENDIENTE] **Re-verificar** en BD la variable de cobertura en `system_configuration`: nuestra búsqueda v1
dio 0 para prosofipo/fondo/ipab, pero AurumCore dice que el monto de cobertura está en System Configuration
→ probablemente bajo otro nombre (p.ej. "cobertura", "25000 UDIS", "monto_proteccion"). NO es contradicción
de la cuota; es afinar la búsqueda de la **cobertura**. No resolver hasta re-verificar.

## Implicaciones para la validación
- **Gap C CONFIRMADO como motor faltante REAL** (la **cuota** mensual; la cobertura-841 sí existe), con
  **disposición aceptada** de mantener la cuota
  por fuera. Es un hueco **funcional/regulatorio**, más serio que una diferencia de cálculo: la provisión
  mensual de la cuota Prosofipo es obligación de ley (LACP).
- **Riesgo:** si el core no lo calcula, la cuota se provisiona **manual/externo** (Excel/Dynamics) → riesgo de
  error u omisión, y descuadre contable/regulatorio. Evaluar si es **bloqueante de go-live** o si hay un
  proceso manual aceptable y documentado (decisión de Comité — charter §11).
- **[PENDIENTE] Precisar** con Finsus/Prosofipo la fórmula vigente de la cuota ordinaria (base exacta sobre
  depósitos, tasa/al millar, periodicidad de entero) para dimensionar el motor faltante y su impacto.
- **Nota de alcance:** el punto de validación 2.1.11 "Cálculo de Seguros Asociados" (doc Motor Crédito) es
  **seguro de CRÉDITOS** (del acreditado), distinto del seguro de DEPÓSITOS (Prosofipo). No lo cubre.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-19 | Creada: norma (LACP Art. 104 Bis) verificada + BD sin módulo Prosofipo → Gap C confirmado como motor faltante real. | F-020, LACP, BD |
| 2 | 2026-08-19 | Disposición de Finsus: se calcula por fuera y seguirá por fuera → clasif. práctica DIFERENCIA_DISENO_AUTORIZADA; riesgo residual (documentar/conciliar). | F-021 |
| 3 | 2026-08-19 | Respuesta AurumCore (F-023): distingue cobertura-841 (sí calcula a tiempo de reporte) de la cuota (sigue faltando); re-verificar variable de cobertura en System Configuration. Gap C de la cuota se mantiene. | F-023 |
