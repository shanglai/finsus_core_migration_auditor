"""
Ensamblador del paquete para el repo del AUDITOR independiente.

Copia (snapshot) los archivos-fuente de este repo a export_auditor/bundle/ preservando estructura,
y regenera BUNDLE_MANIFEST.md con hash + fecha de cada archivo para detectar cambios entre exports.

Regla dura: NUNCA incluir credenciales, PII ni resultados.
  - Excluye db_connections.yaml, landing/, **/_resultados/, *.csv de datos, *.parquet.

Uso:  python export_auditor/ensamblar.py
Luego: copiar export_auditor/bundle/ al repo del auditor.
"""
import sys, hashlib, shutil
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[1]
OUT = RAIZ / "export_auditor" / "bundle"

# Lista blanca de lo que va al auditor (rutas relativas a la raiz del repo).
INCLUYE = [
    # --- El prompt de construccion (el auditor se CONSTRUYE con esto) ---
    "40_validaciones/PROMPT_CONSTRUCTOR_VALIDADOR.md",
    # --- Fuente unica / catalogo de casos (decision C) ---
    "40_validaciones/NORTE_VALIDACION.md",
    # --- Oraculos (motor C, Decimal) ---
    "40_validaciones/entrega_finsus/oraculo_isr.py",
    "40_validaciones/comparadores/oraculo_rendimientos.py",
    "40_validaciones/comparadores/oraculo_credito.py",
    "40_validaciones/comparadores/oraculo_gat.py",
    "40_validaciones/comparadores/oraculo_ifrs9.py",
    "40_validaciones/comparadores/oraculo_amortizacion.py",
    "40_validaciones/comparadores/oraculo_cat.py",
    # --- Comparadores ---
    "40_validaciones/comparadores/motor_b_diario.py",
    "40_validaciones/comparadores/contable_bc.py",
    "40_validaciones/comparadores/cuentahabientes_wso2.py",
    "40_validaciones/comparadores/validate_plazo_origin.py",
    "40_validaciones/comparadores/isr_live_nativo.py",
    "40_validaciones/comparadores/fase1_isr_desviacion.py",
    "40_validaciones/comparadores/fase1_isr_comparador.py",
    "40_validaciones/comparadores/fase1_isr_runner.py",
    # --- Extractores de logs (SOL-003; read-only SSH) ---
    "40_validaciones/comparadores/log_extractor.py",
    "40_validaciones/comparadores/barrido_average_balance.py",
    "40_validaciones/comparadores/tolerancias.py",
    "40_validaciones/comparadores/oraculo_vista_finsus_history.py",
    "40_validaciones/comparadores/sanity_check.py",
    # --- SQL (extraccion + validaciones) ---
    "40_validaciones/entrega_finsus/V1_isr_al_pago_aurum.sql",
    "40_validaciones/entrega_finsus/V2_isr_devengo_openfin.sql",
    "40_validaciones/entrega_finsus/V3_gapB_idnc.sql",
    "40_validaciones/entrega_finsus/V4_gapC_prosofipo.sql",
    "40_validaciones/entrega_finsus/V5_rendimiento_plazo.sql",
    "40_validaciones/entrega_finsus/consultas_validacion.sql",
    "40_validaciones/extraccion/wso2_cuentahabientes.sql",
    # --- Indice maestro + comparacion C vs doc + dossier de motores (para el agente conversacional) ---
    "40_validaciones/INDICE_PRODUCTOS_PROCESOS.md",
    "40_validaciones/COMPARACION_C_vs_DOC.md",
    "40_validaciones/DOSSIER_MOTORES_ORACULO_C.md",
    "40_validaciones/PROMPT_AUDITOR_SPA.md",
    "40_validaciones/MATRIZ_TOLERANCIAS.md",
    "40_validaciones/NORTE_SANIDAD.md",
    "40_validaciones/CASO_CAT-01_estratificado.md",
    "40_validaciones/INFORME_DETALLADO_AUDITORIA/00_INDICE.md",
    "40_validaciones/INFORME_DETALLADO_AUDITORIA/01_CAPTACION_FISCAL.md",
    "40_validaciones/INFORME_DETALLADO_AUDITORIA/02_CREDITO.md",
    "40_validaciones/INFORME_DETALLADO_AUDITORIA/03_CONTABLE_PADRON.md",
    # --- Paquete de datos para auditoria (universo, fechas, detalle desde DuckDB) ---
    "40_validaciones/PAQUETE_AUDITOR_DATOS/00_INDICE.md",
    "40_validaciones/PAQUETE_AUDITOR_DATOS/01_TABLA_MAESTRA_VALIDACIONES.md",
    "40_validaciones/PAQUETE_AUDITOR_DATOS/02_FICHAS_POR_VALIDACION.md",
    "40_validaciones/PAQUETE_AUDITOR_DATOS/03_INVENTARIO_DUCKDB.md",
    # --- Para auditoria: manuales + guia + estado + respuesta Finsus ---
    "40_validaciones/GUIA_AUDITORIA.md",
    "40_validaciones/GLOSARIO_ESTADOS_TABLERO.md",
    "40_validaciones/ACCESO_Y_RED.md",
    "40_validaciones/MANUAL_DEFINICIONES.md",
    "40_validaciones/MANUAL_USO_ORACULO_AUDITOR.md",
    "40_validaciones/ESTADO_RESUMEN.md",
    "40_validaciones/RESPUESTA_FINSUS_2026-08-24.md",
    # --- Planes / especificaciones / referencias ---
    "40_validaciones/entrega_finsus/README_VALIDACION.md",
    "40_validaciones/entrega_finsus/DOSSIER_VALIDACION.md",
    "40_validaciones/extraccion/REFERENCIA_queries_diario_finsus.md",
    "40_validaciones/PLAN_MOTOR_B_DIARIO.md",
    "40_validaciones/PLAN_CONTABLE_BC.md",
    "40_validaciones/PLAN_FASE1_ISR.md",
    "40_validaciones/REFERENCIA_TABLAS_POR_CASO.md",
    "40_validaciones/SOLICITUDES_FINSUS.md",
    "export_auditor/00_START_HERE.md",
    "export_auditor/PROMPT_ARRANQUE_AUDITOR.md",
    "export_auditor/PROMPT_SYNC_AUDITOR.md",
    "export_auditor/PROMPT_SYNC_2026-08-28.md",
    "export_auditor/PROMPT_SYNC_2026-08-31.md",
    "30_oraculo/ESPECIFICACIONES/S-FIS-001.md",
    "30_oraculo/TRAZABILIDAD.md",
    # Config de ejemplo (SIN credenciales reales)
    "db_connections.example.yaml",
]
# Carpetas completas (con filtro de exclusion)
INCLUYE_DIRS = [
    "10_conocimiento",   # las reglas (piezas K) que citan los casos
]
PROHIBIDO = ("db_connections.yaml", "_resultados", "/landing/")
PROHIBIDO_EXT = (".parquet",)


def sha16(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def prohibido(rel: str) -> bool:
    r = "/" + rel.replace("\\", "/") + "/"
    return any(x in r for x in PROHIBIDO) or rel.endswith(PROHIBIDO_EXT)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    copiados = []

    def copiar(rel):
        src = RAIZ / rel
        if not src.exists():
            print(f"  [FALTA] {rel}"); return
        if prohibido(rel):
            print(f"  [OMITE-PROHIBIDO] {rel}"); return
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copiados.append((rel, sha16(src)))

    for rel in INCLUYE:
        copiar(rel)
    for d in INCLUYE_DIRS:
        for src in sorted((RAIZ / d).rglob("*")):
            if src.is_file():
                copiar(str(src.relative_to(RAIZ)).replace("\\", "/"))

    # Manifiesto del bundle (para detectar cambios entre exports)
    man = OUT / "BUNDLE_MANIFEST.md"
    lines = ["# BUNDLE del auditor — inventario\n",
             f"Archivos: {len(copiados)}\n",
             "\n| archivo | sha256(16) |\n|---|---|\n"]
    for rel, h in sorted(copiados):
        lines.append(f"| {rel} | `{h}` |\n")
    man.write_text("".join(lines), encoding="utf-8")

    print(f"\nBundle armado en {OUT} — {len(copiados)} archivos.")
    print("Siguiente: copiar export_auditor/bundle/ al repo del auditor.")
    print("Recordatorio: el bundle NO lleva credenciales, PII ni resultados.")


if __name__ == "__main__":
    main()
