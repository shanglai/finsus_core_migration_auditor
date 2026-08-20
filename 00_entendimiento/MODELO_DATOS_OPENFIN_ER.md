# Modelo de datos de OpenFin — diagrama ER

Fuente: **F-011** (+ pantallas s009/s020). Notación entidad-relación (crow's foot).
Nombres **conceptuales** salvo `secuencia`, `fecha`, `hora` (vistos en s020); los físicos exactos y
los tipos llegan con el `describe` (P-004). El modelo de AurumCore es P-011.

```mermaid
erDiagram
    asociados ||--o{ acreedores : "llave cliente (1—N)"
    asociados ||--o{ deudores   : "llave cliente (1—N)"
    asociados ||..o| directorio : "datos personales (fuera de alcance)"
    acreedores ||--o{ detalle_auxiliar : "llave cuenta (1—N)"
    deudores   ||--o{ detalle_auxiliar : "llave cuenta · solo 5004 (1—N)"
    detalle_auxiliar ||--o| detalle_auxiliar_masdatos : "secuencia (1—1)"
    detalle_auxiliar_masdatos ||..o| AurumCore_o_middleware : "id_external · solo SPEI"

    asociados {
        id id_sucursal PK
        id id_role PK
        id id_asociado PK
        num estatus "1-2 onboarding, 3 activa, 4 cerrada, 5 cancelada"
    }
    acreedores {
        id id_sucursal FK
        id id_role FK
        id id_asociado FK
        id id_suc_aux PK
        id id_producto PK "2000s vista, 2300s inversiones"
        id id_auxiliar PK
        date fecha_apertura "fecha AP"
        date fecha_activacion
        date fecha_cancelacion
        num estatus "3 / 4 / 5"
        num saldo_inicial "0 en eje"
    }
    deudores {
        id id_sucursal FK
        id id_role FK
        id id_asociado FK
        id id_suc_aux PK
        id id_producto PK "5004 One Click (unico en Aurum)"
        id id_auxiliar PK
        num monto_entregado
        num tasa_io
        num plazo
        num dias_por_plazo
        num estatus
    }
    detalle_auxiliar {
        bigint secuencia PK "unico; vista en s020"
        id id_suc_aux FK
        id id_producto FK
        id id_auxiliar FK
        date fecha "vista en s020"
        time hora "vista en s020"
        num periodo
        num cargo
        num abono
        num saldo "final; NO hay saldo anterior"
        num monto_io "interes originado"
        num monto_imp "impuestos"
        txt referencia
        num folio_ticket "ordena estado de cuenta"
        id id_poliza
    }
    detalle_auxiliar_masdatos {
        bigint secuencia PK "FK 1:1 con detalle_auxiliar"
        txt id_external "llave cross-sistema (solo SPEI)"
        num tipo_transaccion "3 SPEI, 183 transf interna, 0 interna/manual"
        txt concepto
        txt referencia
        id id_asociado
        txt origen
    }
    directorio {
        txt datos_personales_corp "fuera de alcance"
    }
    AurumCore_o_middleware {
        txt transaction_id "= id_external (P-011: por confirmar)"
    }
```

## Cómo leer la cardinalidad
- `||--o{` = **uno a cero-o-muchos** (un cliente tiene N cuentas; una cuenta tiene N movimientos).
- `||--o|` = **uno a cero-o-uno** (cada movimiento tiene a lo más una fila de extensión, por `secuencia`).
- `||..o|` (línea punteada) = relación **no identificante / cross-sistema** (no es una FK dura):
  `id_external` amarra el movimiento con middleware/AurumCore, pero sólo está garantizado en SPEI.

## Notas
- Llave **cliente** = (`id_sucursal`, `id_role`, `id_asociado`); llave **cuenta** =
  (`id_suc_aux`, `id_producto`, `id_auxiliar`); `id_suc_aux` ≠ `id_sucursal`.
- `detalle_auxiliar` guarda **cargo/abono/saldo final** (sin saldo anterior ni saldo promedio → se
  reconstruyen, [[K-MOV-006]]).
- OpenFin registra **movimientos, no transacciones**; el `tipo_transaccion` vive en `_masdatos` ([[K-MOV-005]]).
- Detalle completo y apartados en [MODELO_DATOS_OPENFIN.md](MODELO_DATOS_OPENFIN.md). Sustento: [[K-DAT-002]] [[K-DAT-003]] [[K-DAT-004]] [[K-DAT-005]].
