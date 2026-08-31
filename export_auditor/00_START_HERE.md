# START HERE — Bundle del Oráculo (motor C) · Linko

> Punto de entrada único del paquete. El oráculo es el **árbitro independiente (motor C)**: implementa las reglas
> **desde la norma/contrato**, no desde el código de ningún core, y compara contra AurumCore (B) / openfin (A).
> **Todo es solo lectura.** `decimal.Decimal`, cero `float`. Corte 2026-08-28.

## 1. Ruta rápida (5 pasos)
```bash
# 1) Requisitos
pip install psycopg2-binary pyyaml paramiko

# 2) Accesos (TUS credenciales read-only; ver ACCESO_Y_RED.md y db_connections.example.yaml)
cp db_connections.example.yaml db_connections.yaml   # editar con host/usuario/password

# 3) Autoprueba SIN base (valida que las fórmulas reproducen el doc)
python 40_validaciones/comparadores/oraculo_credito.py        # 3/3 OK
python 40_validaciones/comparadores/tolerancias.py            # 4/4 OK

# 4) Status de sanidad del tablero (debe decir SANO)
python 40_validaciones/comparadores/sanity_check.py

# 5) Un cruce completo (con base read-only)
python 40_validaciones/comparadores/validate_plazo_origin.py --limite 300
```
Detalle paso a paso: `40_validaciones/MANUAL_USO_ORACULO_AUDITOR.md`.

## 2. Mapa de documentos (dónde vive cada cosa)
**Arranque / operación**
- `export_auditor/00_START_HERE.md` — este archivo.
- `export_auditor/PROMPT_ARRANQUE_AUDITOR.md` · `PROMPT_SYNC_2026-08-28.md` — arranque y sincronización del auditor interno.
- `40_validaciones/MANUAL_USO_ORACULO_AUDITOR.md` — instalar, correr, interpretar (incluye §5.4 parámetros/universos).
- `40_validaciones/ACCESO_Y_RED.md` — hosts/puertos/rutas + usuario read-only.

**Qué significan las cosas**
- `40_validaciones/MANUAL_DEFINICIONES.md` — conceptos, criterios y fórmulas.
- `40_validaciones/GLOSARIO_ESTADOS_TABLERO.md` — qué significa cada etiqueta (validado/parcial/bloqueado/sin cruce · datos/volumen/config/completitud · 1e-8/1e-5/centavo · sesgo · alcance).
- `40_validaciones/DOSSIER_MOTORES_ORACULO_C.md` — el "cerebro": ficha por motor (para el agente conversacional).

**Qué se validó, con qué universo y precisión**
- `40_validaciones/INFORME_DETALLADO_AUDITORIA/` — **alcance, periodo, universo, representatividad y santo y seña por punto**.
- `40_validaciones/PAQUETE_AUDITOR_DATOS/` — universo/fechas/cronología de ejecución (más alto nivel).
- `40_validaciones/COMPARACION_C_vs_DOC.md` — lo evaluado vs la documentación oficial (con foco en desviaciones).
- `40_validaciones/MATRIZ_TOLERANCIAS.md` — % de cuadre por motor a 1e-8/1e-5/centavo + prueba de sesgo.
- `40_validaciones/INDICE_PRODUCTOS_PROCESOS.md` — índice maestro de motores/procesos.

**Sanidad (el tablero se audita a sí mismo)**
- `40_validaciones/NORTE_SANIDAD.md` — invariantes falsables (H/E/C/T) + status global.
- `40_validaciones/comparadores/sanity_check.py` — corre los invariantes; imprime SANO/NO SANO + auto-prueba.

**Casos y construcción del tablero**
- `40_validaciones/PROMPT_AUDITOR_SPA.md` — brief del SPA (§3.2/3.3 despliegue · §11 guía de casos · §12 sanidad).
- `40_validaciones/CASO_CAT-01_estratificado.md` — caso ejecutable con alcance declarado (patrón).

**Motores (código)** — `40_validaciones/comparadores/*.py` y `40_validaciones/entrega_finsus/` (oráculos + comparadores).

## 3. Orden de lectura sugerido
- **Auditor interno (construye/corre):** este README → `MANUAL_USO` → `NORTE_SANIDAD` + `PROMPT_AUDITOR_SPA` →
  `INFORME_DETALLADO_AUDITORIA` → los `comparadores/*.py`.
- **Grupo auditoría de Finsus (revisa):** este README → `MANUAL_DEFINICIONES` + `GLOSARIO_ESTADOS_TABLERO` →
  `INFORME_DETALLADO_AUDITORIA` (alcance y representatividad) → `COMPARACION_C_vs_DOC` (desviaciones). Para correrlo
  ellos mismos: `ACCESO_Y_RED.md`.

## 4. Principios que gobiernan todo
- **Cada validación devuelve las filas que violan la regla** (0 filas = pasa). El foco está en los **no-conformes** y su explicación.
- **Verde ≠ dictamen:** el dictamen técnico lo emite el humano contra el Manual de Cálculos Oficiales.
- **Nunca se inventa:** lo no computado va `[PEND]`, nunca un default. Ninguna cifra sin **escala** y sin **procedencia**.
- **No se modifica dato:** read-only estricto; credenciales nunca se versionan.

## 5. Verificación de "todo bien"
`sanity_check.py` → **SANO** · las autopruebas de fórmula pasan (N/N) · cada card lleva escala + procedencia + alcance +
representatividad + badge de sanidad. Si algo no cuadra, **se levanta** (AUD-###), no se alinea en silencio.
