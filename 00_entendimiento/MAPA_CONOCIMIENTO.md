# Mapa de Conocimiento

Índice de todas las piezas de conocimiento (`10_conocimiento/`) y su grafo de relaciones.

## Índice de piezas (33)
| id | dominio | título | estado | confianza | v |
|----|---------|--------|--------|-----------|---|
| K-ARQ-001 | ARQ | Inventario de sistemas del ecosistema Finsus | CONFIRMADO | media | 1 |
| K-ARQ-002 | ARQ | Arquitectura del paralelo (gateway Citi, OpenFin primario, switch) | CONFIRMADO | alta | 1 |
| K-ORG-001 | ORG | Core destino = AurumCore | CONFIRMADO | alta | 1 |
| K-ORG-002 | ORG | Responsables del paralelo por dominio | CONFIRMADO | alta | 1 |
| K-ORG-003 | ORG | Participantes sesión F-001 + mapeo inferido de hablantes | INFERIDO | media | 1 |
| K-MIG-001 | MIG | Espacio Paralelo AurumCore en Jira PAR (331 folios) | CONFIRMADO | alta | 1 |
| K-MIG-002 | MIG | Día cero (2-ago) e ingestas; riesgo dato ingestado | CONFIRMADO | alta | 1 |
| K-MIG-003 | MIG | "Finalizada" ≠ cierre evidenciado (20.8%) | CONFIRMADO | alta | 1 |
| K-MIG-004 | MIG | Alcance: universos, queries, balanza + detalle | CONFIRMADO | alta | 1 |
| K-DAT-001 | DAT | Estructura/linaje del export Jira PAR | CONFIRMADO | alta | 1 |
| K-DAT-002 | DAT | Tablas núcleo de OpenFin + ambiente (PostgreSQL, T-1 vs prod) | CONFIRMADO | alta | 1 |
| K-DAT-003 | DAT | Llaves de OpenFin (cliente, cuenta, secuencia, id_external) | CONFIRMADO | alta | 1 |
| K-DAT-004 | DAT | Productos (id_producto) y estatus de cuenta | CONFIRMADO | alta | 1 |
| K-DAT-005 | DAT | Fuente de la verdad por dato (core/middleware/backend/analyzer) | CONFIRMADO | alta | 1 |
| K-DAT-006 | DAT | Modelo de datos y queries de AurumCore (esquema aurumcore) | CONFIRMADO | alta | 1 |
| K-CAP-001 | CAP | Árbol cuentas vista: universos y causas (BUG API, 201, tasa 2019) | CONFIRMADO | alta | 1 |
| K-COL-001 | COL | Árbol crédito One Click 5004: cuadra 100% salvo 68 por redondeo | CONFIRMADO | alta | 1 |
| K-FIS-003 | FIS | Árbol inversiones: Diff ISR es el mayor gap (≈27%) | CONFIRMADO | alta | 1 |
| K-MIG-005 | MIG | Árbol de decantación día cero: metodología y estado global | CONFIRMADO | alta | 1 |
| K-MOV-007 | MOV | Árbol transacciones (2-ago): universos y causas | CONFIRMADO | alta | 1 |
| K-TMP-001 | TMP | Ventanas de proceso y asincronía nocturna | CONFIRMADO | alta | 2 |
| K-DEV-001 | DEV | Redondeo/truncamiento AurumCore (trunc 20/5, modos por cálculo) | CONFIRMADO | alta | 2 |
| K-DEV-002 | DEV | Rendimiento cuentas a la vista | CONFIRMADO | alta | 1 |
| K-DEV-003 | DEV | Rendimiento plazo fijo (capital inicial) | CONFIRMADO | alta | 1 |
| K-MOV-001 | MOV | OpenFin no-atómico vs Aurum atómico | CONFIRMADO | alta | 1 |
| K-MOV-002 | MOV | SPEI OUT: OpenFin no valida CLABE; Aurum sí | CONFIRMADO | alta | 1 |
| K-MOV-003 | MOV | Pérdida de trazabilidad 1:1 por IDs de reinversión | CONFIRMADO | alta | 1 |
| K-MOV-004 | MOV | Tipos de transacción AurumCore observados (parcial) | CONFIRMADO | media | 1 |
| K-MOV-005 | MOV | OpenFin registra movimientos (no transacciones); tipos 3/183/0 | CONFIRMADO | alta | 1 |
| K-MOV-006 | MOV | Lo que OpenFin no guarda y se reconstruye (saldo anterior/promedio) | CONFIRMADO | alta | 1 |
| K-FIS-001 | FIS | ISR mal calculado históricamente en OpenFin | CONFIRMADO | alta | 1 |
| K-FIS-002 | FIS | Regla de retención de ISR AurumCore (con caso de oro) | CONFIRMADO | alta | 1 |
| K-PRC-001 | PRC | Filosofía: explicado 100%, no cuadrado; tercero; neteo=0 | CONFIRMADO | alta | 1 |

## Cobertura por dominio (§8 del CLAUDE.md)
| dominio | piezas | completitud | nota |
|---------|--------|-------------|------|
| CAP | 1 | 30% | vista/plazo vía DEV + árbol cuentas (causas); falta config de productos/tasas |
| COL | 1 | 30% | One Click cuadra 100% (árbol); falta devengamiento crédito |
| MOV | 7 | 55% | atomicidad, CLABE, tipos 3/183/0, reconstrucción, árbol tx; catálogo completo [PENDIENTE] |
| TMP | 1 | 35% | ventanas/asincronía + cortes (vista 18h, transaccional 00h); husos/inhábiles [PENDIENTE] |
| DEV | 3 | 55% | redondeo + rendimiento vista + plazo; falta def. saldo promedio, tasas, One Click |
| CTB | 0 | 5% | id_poliza existe en detalle_auxiliar; matriz tipo_mov→cuenta [PENDIENTE] |
| FIS | 3 | 60% | ISR: regla + defecto histórico + árbol diff (mayor gap); falta verificación normativa (P-010) |
| REG | 0 | 5% | OpenFin = fuente de reportes regulatorios (K-DAT-005); reportes específicos [PENDIENTE] |
| DAT | 6 | 65% | modelo OpenFin (con nombres físicos) + modelo Aurum (K-DAT-006); falta `describe` formal y cols de transaction |
| ARQ | 2 | 40% | ecosistema + paralelo |
| PRC | 1 | 25% | filosofía/método de validación |
| MIG | 5 | 50% | paralelo, día cero, evidencia, alcance, árbol de decantación real |
| ORG | 3 | 30% | core, responsables, participantes |

## Grafo de relaciones
- K-ARQ-002 refina K-ARQ-001
- K-MIG-003/004 refinan K-MIG-001 · K-MOV-004 refina K-MIG-004
- K-ORG-002 depende_de K-MIG-001 · K-ORG-003 refina K-ORG-002
- K-TMP-001 depende_de K-ARQ-002 · K-MOV-003 depende_de K-ARQ-002
- K-MOV-002 depende_de K-MOV-001
- K-DEV-002 depende_de K-DEV-001, K-TMP-001 · K-DEV-003 depende_de K-DEV-001
- K-FIS-002 depende_de K-DEV-001/002/003 · relacionada con K-FIS-001
- **Sustentan spec:** K-FIS-002, K-DEV-001 → S-FIS-001
