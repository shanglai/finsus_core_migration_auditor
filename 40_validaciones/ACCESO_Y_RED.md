# Acceso y red — requisitos para correr el oráculo

> El oráculo corre **solo lectura** contra las bases. Para ejecutar los cruces se necesita **ruta de red** a los hosts
> y un **usuario de solo lectura**. Linko · corte 2026-08-28.
>
> **A quién aplica:**
> - **Auditor interno** (nuestro entorno de validación): **ya tiene acceso VPN**; la conexión es **intermitente**
>   (timeouts esporádicos a `aurum`/`openfin`). Cuando falla, es **transitorio** — reintentar; los comparadores
>   pesados son reanudables (`--skip-hechos`). No requiere provisión nueva.
> - **Grupo auditoría de Finsus** (si quieren correr el oráculo ellos mismos): **sí requieren provisión** — ruta a la
>   subred y un usuario read-only. Es a ellos a quienes aplica la sección 2.

## 1. Hosts y puertos (destino)
| Servicio | Host | Puerto | Uso | Necesario para |
|---|---|---|---|---|
| **AurumCore** (motor B) | `10.10.160.53` | 5432 (PostgreSQL) | consultas read-only al core destino | la mayoría de los cruces (crédito, IFRS, GAT, vista, contable) |
| **OpenFin** (motor A, t-1) | `10.10.164.25` | 5432 (PostgreSQL) | réplica t-1 del core histórico | cruces A vs B (Motor B diario, ISR inversiones) |
| **Logs del core** | `10.10.160.34` | SSH (22) | traza operativa (rolling logs) | SPM de rendimiento, ISR-vivo, días de crédito |

Todos en la subred **`10.10.0.0/16`**. **El síntoma actual del auditor (timeout en `aurum` y `openfin`) es falta de
ruta a esa subred por la VPN.**

## 2. Lo que IT debe habilitar
1. **Ruta VPN a `10.10.0.0/16`** desde la máquina del auditor (o al menos a los 3 hosts de arriba).
2. **Usuario de solo lectura** en AurumCore y OpenFin (PostgreSQL): permiso `SELECT` sobre el esquema `aurumcore`
   (y el equivalente en openfin). **No** se requiere escritura. El oráculo además fuerza `SET default_transaction_read_only`.
3. (Opcional, para los motores que dependen de logs) acceso **SSH de solo lectura** al host de logs.

## 3. Configuración del lado del auditor
El oráculo lee `db_connections.yaml` en la raíz (**gitignored**; formato en `db_connections.example.yaml`). Cada quien
pone **sus propias credenciales**:
```yaml
aurum:
  host: 10.10.160.53
  port: 5432
  dbname: aurumcore
  user: <usuario_readonly_del_auditor>
  password: <...>
  sslmode: prefer
openfin:
  host: 10.10.164.25
  port: 5432
  dbname: <bd_openfin_t1>
  user: <usuario_readonly>
  password: <...>
```
Para logs, `other_connections.yaml` con el acceso SSH. **Nunca se versionan credenciales.**

## 4. Cómo verificar que la ruta ya funciona
```bash
# ¿hay ruta al host? (no necesita credenciales)
python -c "import socket; socket.create_connection(('10.10.160.53',5432),timeout=8); print('AURUM alcanzable')"
python -c "import socket; socket.create_connection(('10.10.164.25',5432),timeout=8); print('OPENFIN alcanzable')"
```
Si esto **conecta**, la ruta está; si da **timeout**, sigue faltando la ruta (tema de IT/VPN, no del oráculo).
Después, con credenciales, correr una autoprueba sin BD (`python 40_validaciones/comparadores/oraculo_credito.py`) y
luego un cruce completo (`python 40_validaciones/comparadores/validate_plazo_origin.py --limite 300`).

## 5. Notas
- **Esquema:** las tablas están en el esquema **`aurumcore`** (no `public`) — calificar `aurumcore.<tabla>`.
- **T-1 planchado:** la réplica t-1 de openfin puede **resetear permisos** al replancharse; si el acceso deja de
  funcionar, **revalidar el grant** (no es un problema del oráculo).
- **VPN intermitente:** si la conexión cae a media corrida, los comparadores pesados son reanudables
  (p.ej. `barrido_average_balance.py --skip-hechos`).
