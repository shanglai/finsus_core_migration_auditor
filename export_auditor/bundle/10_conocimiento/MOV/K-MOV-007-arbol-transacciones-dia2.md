---
id: K-MOV-007
titulo: Árbol de transacciones (2-ago) — universo comparable y causas de diferencia
dominio: MOV
estado: CONFIRMADO
confianza: alta
version: 1
creado: 2026-08-16
actualizado: 2026-08-16
fuentes:
  - ref: 20_fuentes/datos/analisis_arboles_20260803/Árboles - Día Cero.xlsx
    ubicacion: "hoja Árboles (Transacciones 2-ago), RCA-CAUSA (24-49), Asignaciones (~970 pares)"
relaciones:
  refina: [K-MIG-005]
  depende_de: [K-MOV-001, K-MOV-002, K-MOV-005]
  contradice: []
  usado_por: [00_entendimiento/ANALISIS_ARBOLES.md]
impacto_validacion: alto
---
## Enunciado
[CONFIRMADO] Para las transacciones del **2-ago**, **32,539 están en común** (por cliente+cuenta+
id transacción); 524 únicas de AurumCore y 182 únicas de OpenFin. Las diferencias se explican por
casuísticas de diseño y algunos defectos puntuales.
  → fuente: F-013

## Cifras
- TOTAL AC 33,063 · TOTAL OF 32,721 · En común 32,539 · Único AC 524 · Único OF 182.
- **Único OF por tipo:** tipo 1 = 97 · tipo 3 (SPEI) = 46 · tipo 183 = 32 · tipo 186 = 2 · tipo 314 = 5.

## Causas (RCA — a verificar por C)
**Únicas OF (OpenFin las tiene, Aurum no):**
- Origen = destino en la misma cuenta (Aurum no lo permite): tipo 1 = 6; reversos tipo 183 = 13.
- Cuentas TERMINATED/inactivas que en Aurum no transaccionan: tipo 183 = 18, tipo 186 = 2.
- **SPEI OUT a CLABE/tarjeta inválida** (tipo 3 = 19) → confirma K-MOV-002 (Aurum valida y detiene).
- SPEI a/desde satélites que no llegaron (fondos, cuenta inexistente): varios.
- Transacciones internas de crédito (pagos a capital que Aurum registra distinto): tipo 1 = 52 + 26.
- Monto 0 (proceso interno con par en Aurum): tipo 1 = 13.

**Únicas AC (Aurum las tiene, OpenFin no) — transacciones internas de la plataforma:**
- VIRTUAL1→VIRTUAL2 de créditos (prelación/pólizas): 126 · comisiones crédito: 105 + 99 ·
  pago crédito 2002→5004: 35 · dispersiones: 99 + 2 · recompensas $0: 10 · consulta saldo Pomelo $0: 48.

## Implicaciones para la validación
- La mayoría son **`DIFERENCIA_DISENO_AUTORIZADA`** (atomicidad K-MOV-001, CLABE K-MOV-002, internas
  de cada core). Confirma que **el conteo de transacciones difiere legítimamente**.
- **Candidatos a hallazgo (reales):** SPEI que no llegan a satélites (dinero real), cuentas
  TERMINATED que deberían poder transaccionar, cuentas contables con espacio en blanco (no rastrean).
- La hoja **Asignaciones** (~970 pares de cuenta contable origen→destino) es el mapa fino: cada par
  tiene su % de cuadre y su remediación → base directa del comparador por tipo de transacción.

## Historial
| v | Fecha | Cambio | Fuente |
|---|-------|--------|--------|
| 1 | 2026-08-16 | Creada desde F-013. | F-013 |
