# Glosario

> Para la **notación** (K-*, P-*, F-*, dominios, §N, marcas) y el catálogo indexado de cada
> instancia, ver `DICCIONARIO.md`. Este glosario guarda los **términos de negocio con su cita** a
> fuente.

Términos, siglas y nombres propios del proyecto. Cada entrada, si viene de una fuente, se cita.

| término | significado | fuente | estado |
|---------|-------------|--------|--------|
| openfin / OpenFin | Core bancario **actual** ("Motor A"), referencia histórica; **no es la verdad** (CLAUDE.md §1). | CLAUDE.md, F-002/F-003/F-008 | confirmado |
| AurumCore / Aurum | Core bancario **destino** ("Motor B", `<CORE_NUEVO>`). Migración OpenFin → AurumCore. | F-002, F-003, F-008 (K-ORG-001) | confirmado |
| Motor A / B / C | A = OpenFin; B = AurumCore; C = oráculo independiente (CLAUDE.md §1). | CLAUDE.md | referencia del charter |
| oráculo (Motor C) | Cálculo independiente desde norma/contrato; árbitro de discrepancias. | CLAUDE.md §1, §9 | referencia del charter |
| Espacio Paralelo AurumCore | Operación en paralelo openfin↔Aurum cuyas incidencias se registran en Jira. | F-008, F-003 (K-MIG-001) | confirmado |
| Jira PAR / proyecto PAR | Proyecto Jira ("Paralelo AurumCore"), 331 folios; URLs `finsus-digital.atlassian.net/browse/PAR-###`. | F-003, F-004, F-008 | confirmado |
| Cliente Único | Proyecto para volver "Cliente Único" la fuente central de datos (Fase 0/1). | F-002 (K-ARQ-001) | confirmado |
| Analyzer | Componente del ecosistema (integración/datos). | F-002 | confirmado (diagrama, conf. media) |
| Middleware / Gateway | Capa de integración entre cores y satélites. | F-002 (K-ARQ-001) | confirmado (diagrama) |
| Simetrik | Sistema de conciliación del ecosistema. | F-002 | confirmado (diagrama) |
| Pomelo | Card Manager (TDD/TDC) del ecosistema. | F-002 | confirmado (diagrama) |
| Dynamics | ERP del ecosistema. | F-002 | confirmado (diagrama) |
| AODB / F1 / WebBanking / FinsusApp | Sistemas satélite del ecosistema Finsus. | F-002 | confirmado (diagrama) |
| Un Click | Producto/línea de crédito (p.ej. PAR-318, PAR-351). | F-008 | confirmado (nombre; reglas [PENDIENTE]) |
| SPEI | Sistema de pagos electrónicos interbancarios; dominio de folios PAR. | F-008 | referencia |
| TDD / TDC | Tarjeta de débito / crédito; dominio de folios PAR. | F-008 | referencia |
| ISR | Impuesto Sobre la Renta (retención en inversiones); dominio FIS. | F-008, CLAUDE.md | referencia |
| SIC | Sociedad de Información Crediticia (saldos reportados); dominio REG. | CLAUDE.md | referencia del charter |
| SOFIPO | Sociedad Financiera Popular. Tipo de entidad **supuesto** (S-004). | CLAUDE.md §0 | supuesto |
| CNBV | Comisión Nacional Bancaria y de Valores. | CLAUDE.md §0 | referencia del charter |
| v2t | video-to-text: conferencia diarizada con screenshots. | CLAUDE.md §4 | referencia del charter |
| BRONZE/SILVER/GOLD | Capas de la plataforma de datos "Cliente Único". | F-002 | confirmado (diagrama) |
| gateway (Citi) | Capa que recibe las operaciones de los canales y las **deriva a ambos cores** en el paralelo. Construida por el equipo de Citi. | F-001 @00:05:30 (K-ARQ-002) | confirmado |
| core primario / autorizador | En el paralelo, el core que autoriza y define el saldo del cliente = **OpenFin** (hasta el switch ~1-oct). | F-001 (K-ARQ-002) | confirmado |
| día cero | Corte donde se ingestan movimientos y saldos para que ambos cores **nazcan cuadrados** (fue el 2-ago-2026). | F-001 @00:40:10 (K-MIG-002) | confirmado |
| ingesta | Traspaso de datos OpenFin→Aurum (DB→DB con transformación) para recuadrar; on-demand. | F-001 (K-MIG-002) | confirmado |
| operación atómica | Aurum registra la operación como una unidad; OpenFin hace cargo+abono(+reversa). | F-001 @00:23:54 (K-MOV-001) | confirmado |
| One Click | Crédito amarrado a cuentas plazo, con domiciliación a cuentas vista; altera saldos/movimientos de captación. | F-001 @00:12:11 (K-MIG-004) | confirmado |
| CLABE / "algoritmo de Luna" | Validación de estructura de cuenta CLABE (dígito verificador) que Aurum aplica en SPEI OUT y OpenFin no. Grafía "de Luna" por confirmar (¿Luhn?). | F-001 @00:07:32 (K-MOV-002) | confirmado (algoritmo [PENDIENTE]) |
| balanza / detalle de movimientos | Las dos "salidas": balanza = agregado contable; detalle = auxiliares que la alimentan. | F-001 @00:13:03 (K-MIG-004) | confirmado |
| explicado vs cuadrado | Premisa: no se busca cuadre 100% sino diferencias explicadas 100%. | F-001 @00:08:32 (K-PRC-001) | confirmado |
| STP | Sistema de pagos (procesa SPEI OUT; regresa operaciones con CLABE inválida). | F-001 | referencia |
| Read AI / Fireflies.ai | Notetakers automáticos presentes en la sesión F-001. | F-001 (screenshots) | confirmado |
| ISR | Impuesto Sobre la Renta; retención sobre rendimientos, aplicada al momento del pago (no en devengo). | F-009 §6 (K-FIS-002) | confirmado (regla); parámetros por verificar |
| UMA | Unidad de Medida y Actualización; base de la exención de ISR (5×UMA). Valor en F-010: $42,794.64. | F-010 (K-FIS-002) | confirmado (valor por verificar) |
| base exenta / expuesta | Exenta = 5×UMA (moral: 0); expuesta = saldo total − exenta; sobre la expuesta se calcula ISR. | F-009/F-010 (K-FIS-002) | confirmado |
| saldo promedio mensual | Base de cálculo del rendimiento de cuentas a la vista. Definición exacta [PENDIENTE]. | F-009 §5.1 (K-DEV-002) | confirmado (def. pendiente) |
| iv_initial_amount / iv_account_state | Campos AurumCore: capital de apertura y estado de la inversión a plazo. | F-009 §5.2 (K-DEV-003) | confirmado |
| misceláneo del producto | Configuración por producto (días del año, tasa) usada en el cálculo de plazo. | F-009 §5.2 | confirmado |
| ISR AurumCore | Tipo de transacción de retención (Salida) que postea AurumCore al pagar rendimientos. | F-010 (K-MOV-004) | confirmado |
| asociados (tabla) | Tabla de OpenFin con todos los clientes. Llave cliente = id_sucursal+id_role+id_asociado. | F-011 (K-DAT-002/003) | confirmado |
| acreedores / deudores (tablas) | Cuentas de captación (acreedores) y de crédito (deudores) en OpenFin; misma estructura. | F-011 (K-DAT-002) | confirmado |
| detalle_auxiliar / _masdatos | Tabla de movimientos (cargo/abono/saldo final) y su extensión, unidas por `secuencia`. | F-011 s020 (K-DAT-002/003) | confirmado |
| secuencia | Llave primaria de detalle_auxiliar; une con detalle_auxiliar_masdatos. | F-011 s020 (K-DAT-003) | confirmado |
| id_external | Llave única cross-sistema (OpenFin↔middleware↔Aurum); garantizada sólo en SPEI. | F-011 (K-DAT-003) | confirmado |
| tipo de transacción (3/183/0) | 3=SPEI, 183=transferencia interna, 0=operación interna/manual. ~63 tipos activos. | F-011 (K-MOV-005) | confirmado |
| id_producto (2000s/2300s/5004) | 2000s=vista, 2300s=inversiones, 5004=crédito One Click (único crédito en Aurum). | F-011 (K-DAT-004) | confirmado |
| estatus de cuenta (3/4/5) | 3=activa, 4=cerrada, 5=cancelada; 1/2=onboarding. Sólo 3 transacciona. | F-011 (K-DAT-004) | confirmado |
| T-1 | Ambiente espejo de OpenFin; NO fuente de verdad (tuvo secuencias duplicadas). Producción manda. | F-011 (K-DAT-002) | confirmado |
| SQuirreL SQL Client | Cliente SQL usado para consultar OpenFin (PostgreSQL). | F-011 s020 | confirmado |
| directorio (tabla) | Tabla de OpenFin con datos personales/corp del cliente (fuera de alcance de validación). | F-011 | confirmado |
