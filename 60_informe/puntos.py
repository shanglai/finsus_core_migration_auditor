# -*- coding: utf-8 -*-
"""Registro declarativo de los puntos de validacion — informe DETALLADO.

POR QUE EXISTE. En la sesion del 2026-08-28 con el equipo de auditoria, tres
preguntas quedaron sin contestar en el informe de alto nivel:

  [00:26:55] "Cual fue el universo? Y si ese universo lo conciliaste contra
              algo? Que tan representativas fueron las pruebas? Que porcentaje
              del universo se esta abarcando?"
  [00:27:52] "4,091 contratos, de cuantos? Y segun quien? Aurum, OpenFin, o la
              conciliacion entre los dos?"
  [00:32:35] "Dos cuestiones fundamentales: uno, LA METODOLOGIA con la que
              determinaron cuantos y POR QUE. Dos, CUANTO REPRESENTAN esos
              items respecto del universo."
  [00:49:04] "Se puede ver que es lo que se esta tomando? ... saber los
              universos y ver a que esta enfocada la prueba."
  [00:52:11] (bloqueados) "Vamos a poder ver que es lo que le hace falta."

Este modulo declara, punto por punto, lo que contesta esas preguntas. El
generador (`generar.py`) lo convierte en un .md por punto.

REGLA DEL MODULO — la que impide que esto se vuelva relleno:
Un punto NO puede declarar `n` (lo que se comparo) sin declarar tambien su
DENOMINADOR, o marcarlo `[PEND]` **con la consulta que lo mediria**. Un
porcentaje de representatividad que nadie puede reproducir es peor que un hueco
declarado. `tests/test_informe.py` lo verifica.

DE DONDE SALE CADA COSA:
  * los puntos V-01..V-23 y sus cifras: `40_validaciones/PAQUETE_AUDITOR_DATOS/`
    (tabla maestra + fichas), que es lo que el equipo de auditoria ya tiene.
  * el racional, el santo y seña y el fuera-de-alcance de los casos que ESTE
    validador corrio: sus YAML en `validador/catalogo/` y el manifiesto de la
    corrida.
  * lo que no se sabe: `[PEND]` con la pregunta concreta, nunca una redaccion
    que suene a respuesta.
"""

from __future__ import annotations

from dataclasses import dataclass, field

PEND = "[PEND]"

# --- Vocabulario -------------------------------------------------------------

CORES = {
    "A": "openfin (replica t-1) — historico, NO es la verdad",
    "B": "AurumCore — el core bajo prueba",
    "C": "oraculo independiente — motor C",
}


@dataclass
class Denominador:
    """De cuantos, segun quien, y como se reproduce la cifra.

    `total` puede ser `[PEND]`, pero entonces `consulta` es obligatoria: sin la
    consulta, el hueco no se puede cerrar y se vuelve permanente.
    """
    total: str                 # el universo completo disponible, o PEND
    segun: str                 # "B (AurumCore)" | "A (openfin)" | "feed" | ...
    consulta: str = ""         # SQL/artefacto que lo mide — obligatorio si PEND
    nota: str = ""

    @property
    def pendiente(self) -> bool:
        return self.total == PEND

    def pct(self, n: str) -> str:
        """Representatividad. Solo si ambos son numeros limpios."""
        try:
            a = float(str(n).replace(",", ""))
            b = float(str(self.total).replace(",", ""))
        except ValueError:
            return PEND
        return f"{a / b * 100:.2f}%" if b else PEND


@dataclass
class Punto:
    id: str                       # V-01 ...
    titulo: str
    familia: str                  # Captacion | Fiscal | Credito | Transaccional/Contable | Padron
    motores: str                  # "C vs B", "A vs B", "A/B/C", "C vs config B"
    # --- alcance
    que_se_valida: str
    que_NO_se_valida: list[str]
    # --- periodo
    ventana_datos: str
    corte: str
    ejecutado: str                # timestamp de la corrida (mtime del artefacto)
    # --- universo
    n_comparado: str              # lo que efectivamente se comparo
    unidad: str                   # "periodos", "contratos", "provisiones", ...
    denominador: Denominador
    conciliacion: str             # contra que se concilio el universo, o PEND
    # --- racional
    racional_subconjunto: str     # POR QUE ese recorte y no otro
    # --- santo y sena
    tablas: list[str]
    filtros: list[str]            # los predicados EXACTOS que definen el universo
    llave: str
    formula: str
    tolerancia: str
    oraculo: str
    sql: str = ""                 # ruta del SQL reproducible, si existe
    # --- resultado
    resultado: str = ""
    granularidades: str = ""      # 1e-8 / 1e-5 / centavo
    sesgo: str = ""
    no_conformes: str = ""
    clase_no_conforme: str = ""
    # --- limites
    no_concluye: list[str] = field(default_factory=list)
    bloqueo: str = ""
    insumo_requerido: str = ""    # QUE se necesita y CUANDO, para los bloqueados
    solicitudes: tuple[str, ...] = ()
    # --- evidencia
    evidencia: list[str] = field(default_factory=list)
    reproducir: str = ""
    caso_validador: str = ""      # si este repo lo tiene como caso ejecutable

    @property
    def representatividad(self) -> str:
        return self.denominador.pct(self.n_comparado)


# =============================================================================
# A · CAPTACION / INVERSION
# =============================================================================

PUNTOS: list[Punto] = [

Punto(
    id="V-01", familia="Captacion", motores="C vs B",
    titulo="Rendimiento plazo fijo — motor vivo (origin IS NULL)",
    que_se_valida=(
        "El interes de inversion a plazo que GENERA AurumCore despues del cutover, "
        "reproducido periodo por periodo por el oraculo independiente."),
    que_NO_se_valida=[
        "Las inversiones MIGRADAS desde openfin (`origin = 'FINSUS'`) — son V-02, y "
        "tienen otro comportamiento: su tasa de originacion difiere de la despejada.",
        "La decision de negocio de que tasa aplicar; solo se valida que la ARITMETICA "
        "reproduzca la tasa efectivamente pactada en el plan de pagos.",
        "El pago/abono del rendimiento al cliente (eso es transaccional, V-20/V-21).",
    ],
    ventana_datos="periodos del plan de pago vigentes al corte",
    corte="2026-08-20", ejecutado="2026-08-21 17:00",
    n_comparado="530,195", unidad="periodos (157,999 cuentas)",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta=("select count(*) total, count(*) filter (where a.origin is null) origin_null "
                  "from aurumcore.iv_payment_plan p "
                  "join aurumcore.account a on a.account_id = p.account_id"),
        nota=("Se declaro 'todas las origin IS NULL', o sea el subconjunto ES el universo "
              "de su clase. Falta la cifra de control: cuantos periodos hay EN TOTAL "
              "(origin null + no null) para expresar que fraccion del libro representa.")),
    conciliacion=(
        "PEND — no se concilio contra un conteo independiente. La cifra de 530,195 sale "
        "de la misma extraccion que se valido, asi que confirma consistencia interna, no "
        "completitud del universo."),
    racional_subconjunto=(
        "NO es una muestra: es el universo COMPLETO de su clase. El recorte `origin is null` "
        "no busca reducir volumen sino AISLAR el motor bajo prueba — separa lo que AurumCore "
        "calculo de lo que heredo de openfin en la migracion. Mezclarlos daria un porcentaje "
        "que no dice nada de ningun motor. El delimitador `origin` tiene semantica mixta "
        "segun la tabla: aqui es limpio porque `iv_payment_plan` no lleva etiquetas de canal."),
    tablas=["aurumcore.iv_payment_plan", "aurumcore.account"],
    filtros=["a.origin is null  -- generado por AurumCore, no migrado"],
    llave="(account_id, numero de periodo)",
    formula="RoundHalfEven2( Ceil10( Ceil10((Capital x Tasa)/100) / DiasAnio ) x DiasPeriodo ), base 360",
    tolerancia="0.01 por evento, con prueba de signo",
    oraculo="oraculos/rendimientos.py::fila_rendimiento_plazo",
    sql="validador/extraccion/aurum/rend_plazo_universo.sql",
    resultado="100.00% — 0 violaciones sobre 530,195 periodos",
    granularidades="1e-8 100.00% · 1e-5 100.00% · centavo 100.00%",
    sesgo="no detectado (no hay residuo que probar)",
    no_conformes="ninguno",
    no_concluye=[
        "El 100% es sobre el universo `origin is null` al corte 2026-08-20. NO dice nada "
        "de las inversiones migradas ni de periodos posteriores al corte.",
        "La tasa se DESPEJA del periodo 1 y se reproduce en los demas. Eso valida "
        "consistencia interna del plan; NO valida que la tasa pactada sea la correcta "
        "contra el contrato del cliente.",
    ],
    evidencia=["PLAZO_LIVE_ESCALA_2026-08-20.txt",
               "validador/reportes/REND-PLAZO_2026-08-28_*/"],
    reproducir="cd validador && python cli.py --caso REND-PLAZO --confirmar",
    caso_validador="REND-PLAZO",
),

Punto(
    id="V-02", familia="Captacion", motores="C vs B",
    titulo="Rendimiento plazo fijo — migrado (origin = FINSUS)",
    que_se_valida="El mismo motor de V-01 sobre inversiones INGESTADAS desde openfin.",
    que_NO_se_valida=[
        "La correccion de la migracion en si (si el saldo migrado era el correcto).",
        "Las inversiones nativas — esas son V-01.",
    ],
    ventana_datos="periodos del plan de pago de inversiones migradas",
    corte="2026-08-20", ejecutado="2026-08-21 17:00",
    n_comparado="3,748", unidad="periodos (300 cuentas)",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta=("select count(*) from aurumcore.iv_payment_plan p "
                  "join aurumcore.account a on a.account_id = p.account_id "
                  "where a.origin = 'FINSUS'"),
        nota="AQUI SI HAY MUESTREO: 300 cuentas de un total no declarado."),
    conciliacion="PEND",
    racional_subconjunto=(
        "ESTE PUNTO SI ES UNA MUESTRA y su metodo de seleccion NO esta declarado. "
        "Es la brecha mas grande del informe frente a lo que pidio la auditoria "
        "[00:32:35]: hace falta decir COMO se eligieron esas 300 cuentas (aleatorio? "
        "primeras por id? por volumen?) y que fraccion del universo migrado representan. "
        "Mientras no se declare, el 97.79% NO es extrapolable al padron migrado."),
    tablas=["aurumcore.iv_payment_plan", "aurumcore.account"],
    filtros=["a.origin = 'FINSUS'", "muestra de 300 cuentas — criterio [PEND]"],
    llave="(account_id, numero de periodo)",
    formula="la misma de V-01",
    tolerancia="0.01 por evento",
    oraculo="oraculos/rendimientos.py::fila_rendimiento_plazo",
    resultado="97.79% (3,665 cuadran, 83 no)",
    granularidades=PEND,
    sesgo=PEND,
    no_conformes=(
        "83 periodos. Ejemplos: cta 00003b5f-18b p8 B=376.46 / C=426.66; p9 B=401.56 / "
        "C=351.36; cta 0001a2ba-8cd p0 B=122.49 / C=237.33."),
    clase_no_conforme="linaje (migracion)",
    no_concluye=[
        "El patron observado —tasa/base de originacion distinta a la despejada del "
        "periodo 1— es una HIPOTESIS consistente con los datos, no una conclusion "
        "verificada contra el contrato original.",
        "Sin el metodo de muestreo declarado, el porcentaje no se extrapola.",
    ],
    evidencia=["PLAZO_origin_migrado_vs_live_2026-08-20.txt"],
    reproducir=PEND,
),

Punto(
    id="V-03", familia="Captacion", motores="feed vs B",
    titulo="Rendimiento vista — integridad de posteo (feed ↔ DB)",
    que_se_valida=(
        "Que cada pago de rendimiento que el core escribe en su feed operativo "
        "(`yield-trans`) EXISTA en la base con la misma cuenta y el mismo monto. "
        "Es integridad de POSTEO, no correccion del CALCULO."),
    que_NO_se_valida=[
        "El calculo del rendimiento — eso es V-04, con oraculo independiente.",
        "Los pagos de la DB que NO aparecen en el feed: el feed capturado es de UN pod, "
        "asi que la direccion contraria (DB ⊆ feed) no se afirma y no se puede afirmar.",
    ],
    ventana_datos="2026-08-18 (dia completo en DB; feed parcial de un pod)",
    corte="2026-08-18", ejecutado="2026-08-23",
    n_comparado="30,769", unidad="pagos capturados en el feed",
    denominador=Denominador(
        total="38,921", segun="B (AurumCore) — pagos del dia completo en DB",
        nota=("El feed capturo 30,769 de los 38,921 pagos del dia porque se leyo UN pod. "
              "La direccion validada es feed ⊆ DB al 100%.")),
    conciliacion=(
        "SI se concilio: 38,921 pagos · $5,751,013.03 en la DB del dia, productos "
        "2301/2307/2308. El feed es subconjunto propio y coincide 30,769/30,769."),
    racional_subconjunto=(
        "El recorte no se eligio: lo impone la captura. El feed se lee de los logs de UN "
        "pod del core, y el core corre en varios. Se valida la direccion que el dato "
        "SOPORTA (todo lo que el feed dice esta en la DB) y se declara que la contraria "
        "no se puede afirmar con esta captura."),
    tablas=["feed yield-trans (CSV pre-extraido)", "aurumcore transaccional del dia"],
    filtros=["fecha = 2026-08-18", "productos 2301 / 2307 / 2308"],
    llave="payee_account_id + monto",
    formula="n/a — es cruce de existencia, no de calculo",
    tolerancia="existencia exacta",
    oraculo="cruce de conjuntos",
    resultado="feed ⊆ DB = 30,769 / 30,769 = 100.00%",
    no_conformes="ninguno en la direccion validada",
    no_concluye=[
        "NO prueba que el core haya posteado todos los pagos que debia: prueba que lo "
        "que el feed reporta esta en la base. La completitud absoluta requiere el feed "
        "de todos los pods.",
    ],
    evidencia=["yield_feed_2026-08-18.csv", "RESULTADO_rendimiento_feed_2026-08-23.md"],
),

Punto(
    id="V-04", familia="Captacion", motores="C vs B",
    titulo="Rendimiento vista — oraculo independiente",
    que_se_valida=(
        "El interes de cuenta a la vista calculado de forma independiente "
        "(SPM x tasa x dias / base) contra lo que AurumCore posteo."),
    que_NO_se_valida=[
        "El SPM de RENDIMIENTO en si: se reconstruye de `finsus_account_history`, no se "
        "lee del insumo real que uso el core (ese vive en la poliza de intereses, SOL-003).",
        "El primer cierre mensual de vista post-cutover — se observa el 31-ago.",
    ],
    ventana_datos="cierre de agosto 2026 sobre `yield_dto` + `finsus_account_history`",
    corte="2026-08-28", ejecutado="2026-08-28",
    n_comparado="20,000", unidad="pagos de rendimiento vista",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta=("select count(*) from aurumcore.yield_dto y "
                  "where y.iv_payment_plan_id is null and y.process_date = :fecha_pago"),
        nota=("El limite de 20,000 es una COTA DE LA EXTRACCION (`limite` del caso), no "
              "el universo. Hay que declarar cuantos pagos hubo ese dia para expresar la "
              "representatividad.")),
    conciliacion="PEND",
    racional_subconjunto=(
        "El tope de 20,000 filas es deliberado y su motivo esta declarado: no degradar "
        "AurumCore, que es PRODUCCION [transcripcion 00:28:23 y 00:30:42]. La herramienta "
        "NO muestrea por diseño —puede correr el universo completo— y el limite se sube "
        "en cuanto se acuerde la ventana de ejecucion. Es una restriccion operativa "
        "declarada, no una decision estadistica."),
    tablas=["aurumcore.yield_dto", "aurumcore.finsus_account_history", "aurumcore.account"],
    filtros=["y.iv_payment_plan_id is null  -- VISTA, no inversion",
             "y.process_date = :fecha_pago",
             "h.record_date = :fecha_cierre"],
    llave="account_id",
    formula="Rendimiento = Round2( Trunc20( Trunc20((SPM x Tasa)/100) / DiasAnio ) x DiasPeriodo )",
    tolerancia="0.01 por evento, con prueba de signo",
    oraculo="oraculos/rendimientos.py::fila_rendimiento_vista",
    sql="validador/extraccion/aurum/rend_vista_universo.sql",
    resultado="96.62% al centavo (19,325 / 20,000)",
    granularidades="1e-8 96.37% · 1e-5 96.37% · centavo 96.62%",
    sesgo="ver corrida — el residuo se concentra en cuentas con proxy de fecha de activacion",
    no_conformes=(
        "675 al centavo. De ellos 398 son diferencias SUB-PESO. Solo 8 superan $100, y las "
        "8 tienen el mismo patron: la fecha de activacion usada como proxy sobrecuenta dias "
        "(fondeo != activacion)."),
    clase_no_conforme="data-sourcing",
    no_concluye=[
        "El residuo NO se puede atribuir a AurumCore hasta tener el SPM real y el `dt` de "
        "la poliza de intereses (SOL-003). El oraculo reconstruye el SPM, y una diferencia "
        "contra un insumo reconstruido no acusa al motor.",
    ],
    solicitudes=("SOL-003",),
    evidencia=["validador/reportes/REND-VISTA_2026-08-28_*/"],
    reproducir="cd validador && python cli.py --caso REND-VISTA --confirmar",
    caso_validador="REND-VISTA",
),

Punto(
    id="V-05", familia="Captacion", motores="insumo",
    titulo="Saldo promedio (SPM) — barrido de logs",
    que_se_valida="Nada todavia: es el INSUMO que necesita V-04, no una validacion.",
    que_NO_se_valida=["Todo. El punto existe para declarar un bloqueo, no un resultado."],
    ventana_datos="2026-08-06 → 2026-08-23",
    corte="2026-08-23", ejecutado="2026-08-23",
    n_comparado="90", unidad="filas (27 cuentas)",
    denominador=Denominador(
        total=PEND, segun="logs del core",
        consulta="no hay consulta: el dato no esta en la base, esta en la traza de log",
        nota="27 cuentas de un padron de vista completo — la cobertura es minima y se declara."),
    conciliacion="no aplica — es un barrido parcial de trazas",
    racional_subconjunto=(
        "No hubo eleccion de subconjunto: es lo que el barrido de logs alcanzo a capturar. "
        "El SPM de RENDIMIENTO es distinto del SPM de consulta (`account.average_balance_amount`) "
        "y solo existe en la traza `Calculating with average balance`."),
    tablas=["logs del core (no hay tabla)"],
    filtros=["traza 'Calculating with average balance'"],
    llave="account_id + fecha",
    formula="n/a", tolerancia="n/a", oraculo="n/a",
    resultado="insumo incompleto — no cierra",
    bloqueo="El SPM de rendimiento solo existe en logs; el barrido capturo 27 cuentas.",
    insumo_requerido=(
        "QUE: la traza completa `Calculating with average balance` del cierre mensual, o "
        "la poliza de intereses con el SPM y los dias efectivamente usados por cuenta. "
        "CUANDO: el cierre del 31-ago es la primera oportunidad de capturarla completa."),
    solicitudes=("SOL-003",),
    evidencia=["average_balance_sweep_core-rendimientos.csv",
               "saldo_promedio_feed_2026-08-18.csv"],
),

Punto(
    id="V-06", familia="Captacion", motores="C vs B",
    titulo="GAT inversion (nominal / real)",
    que_se_valida=(
        "Que `nominal_cgat` sea funcion pura de (tasa, plazo, 360) y que el oraculo la "
        "reproduzca exacto. Es una prueba NO-CIRCULAR: la funcion se deriva de la "
        "definicion, no se ajusta a los datos."),
    que_NO_se_valida=[
        "El GAT REAL (descontada la inflacion) contra cada contrato: falta la tabla de "
        "tramos de tasa (data-sourcing, no calculo).",
        "El cruce 1-a-1 a volumen sobre todo el padron de inversiones.",
    ],
    ventana_datos="inversiones vigentes al corte", corte="2026-08-20", ejecutado="2026-08-20",
    n_comparado="126,465", unidad="inversiones (term 7)",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta="select count(*) from aurumcore.iv_payment_plan  -- y por plazo",
        nota="126,465 corresponde al plazo 7; faltan los volumenes de los demas plazos."),
    conciliacion="volumenes por plazo declarados en COMPARACION_C_vs_DOC.md A4",
    racional_subconjunto=(
        "Se eligio el plazo 7 por ser el de mayor volumen, lo que da la prueba mas dura "
        "de la funcion pura con el menor riesgo de sesgo por plazo raro. La validacion NO "
        "depende del volumen: si `nominal_cgat` es funcion pura, reproducirla exacto en "
        "126,465 casos ya lo demuestra."),
    tablas=["aurumcore.iv_payment_plan", "cat_financial_variables.INFLATIONMXN"],
    filtros=["term = 7"],
    llave="id de inversion",
    formula="GAT nominal = f(tasa, plazo, 360) — funcion pura",
    tolerancia="exacto",
    oraculo="comparadores/oraculo_gat.py",
    resultado="reproduce EXACTO (prueba no-circular)",
    no_conformes="ninguno en el alcance cubierto",
    no_concluye=["El GAT real y el cruce per-contrato quedan fuera; ver SOL-015."],
    solicitudes=("SOL-015",),
    evidencia=["COMPARACION_C_vs_DOC.md A4"],
),

# =============================================================================
# B · FISCAL — ISR
# =============================================================================

Punto(
    id="V-07/08", familia="Fiscal", motores="A/B/C",
    titulo="ISR inversiones — join A/B/C completo y desviacion clasificada",
    que_se_valida=(
        "El ISR retenido sobre inversiones, comparando los TRES motores sobre el universo "
        "de inversiones que existen en ambos cores. Es el unico punto con motor A completo."),
    que_NO_se_valida=[
        "El ISR de cuentas a la VISTA — ese es V-12 y esta bloqueado.",
        "Las inversiones que existen en UN solo core: el join las excluye por construccion, "
        "y ese diferencial NO se cuantifico aqui.",
    ],
    ventana_datos="apertura 2024-08-01 → 2026-07-27",
    corte="2026-08-03", ejecutado="2026-08-17 22:22",
    n_comparado="18,599", unidad="inversiones (14,913 clientes)",
    denominador=Denominador(
        total=PEND, segun="interseccion A ∩ B",
        consulta=("contar inversiones en A y en B por separado, y el tamano del "
                  "anti-join en ambas direcciones"),
        nota=("18,599 es el tamano de la INTERSECCION. Falta declarar cuantas inversiones "
              "hay en cada core para saber cuantas quedaron fuera del cruce. Es la cifra "
              "que convierte '18,599' en una representatividad.")),
    conciliacion=(
        "Parcial: 18,599 ids distintos en cada lado del join (1-a-1 limpio, sin "
        "duplicacion). No se concilio contra el total de cada core."),
    racional_subconjunto=(
        "El universo lo define la INTERSECCION, no una muestra: solo se puede comparar "
        "A contra B donde la inversion existe en los dos. El recorte es estructural."),
    tablas=["openfin (ISR diario)", "aurumcore (ISR al pago)", "oraculo C"],
    filtros=["inversiones presentes en ambos cores", "corte 2026-08-03"],
    llave="id_inversion (crosswalk A↔B)",
    formula="ISR = base gravable x 0.9% anual / 365 (LISR); exencion 5 x UMA",
    tolerancia="clasificacion de desviacion, no umbral fijo",
    oraculo="comparadores/oraculo_isr.py",
    resultado=(
        "Descuadre bruto 0.006%. Tras clasificar 3,236 filas (2,774 clientes), el 100% es "
        "DIFERENCIA DE MODELO — openfin devenga ISR diario, AurumCore retiene al pago — "
        "o sea $0.00 de defecto de calculo real."),
    no_conformes="3,236 filas, todas clasificadas como diferencia de modelo",
    clase_no_conforme="diferencia de diseno autorizada",
    no_concluye=[
        "'Diferencia de modelo' explica el descuadre pero NO lo cierra contablemente: los "
        "dos modelos convergen al vencimiento, y esa convergencia no se verifico aqui.",
    ],
    evidencia=["_isr_join_full.parquet", "f1_desviacion_clasificada.parquet"],
),

Punto(
    id="V-09/10/11", familia="Fiscal", motores="A/B/C",
    titulo="ISR — reconciliacion al pago, devengo diario e insumo de saldo base",
    que_se_valida=(
        "V-09: que la retencion al pago de un caso reconciliado cuadre C=B. "
        "V-10: que openfin y el oraculo apliquen el MISMO motor de devengo diario. "
        "V-11: el saldo base como insumo."),
    que_NO_se_valida=[
        "El cruce MASIVO per-contrato de ISR al pago: requiere el Manual (SOL-015).",
        "Los parametros fiscales del core contra la norma — eso es su propio caso (ISR-03).",
    ],
    ventana_datos="V-10: 2026-02-03 → 2026-08-03 · V-11: 2025-10-16 → 2026-08-03",
    corte="2026-08-03", ejecutado="2026-08-18",
    n_comparado="728", unidad="dias-cliente (V-10); 2 pagos (V-09); 65 filas (V-11)",
    denominador=Denominador(
        total=PEND, segun="A (openfin)",
        consulta="select count(*) from openfin.isr_diario where fecha between ...",
        nota=("728 dias-cliente sobre 4 clientes. Es una SEMILLA de reconciliacion, no una "
              "muestra representativa, y se debe leer como tal.")),
    conciliacion="PEND",
    racional_subconjunto=(
        "SEMILLA DELIBERADA, no muestra. El objetivo no es estimar una tasa de acierto "
        "sino DEMOSTRAR LA MECANICA: si openfin y C coinciden dia a dia en 728 dias-cliente "
        "con Σ|dif| = 5.87 (puro redondeo), es el mismo motor. Ese hecho no depende del "
        "tamano. Lo que SI depende del tamano —cuantos clientes tienen desviacion— es lo "
        "que mide V-07/08, no este punto."),
    tablas=["openfin.isr_diario", "aurumcore (ISR al pago)", "aurumcore.system_configuration"],
    filtros=["4 clientes semilla", "2026-02-03 → 2026-08-03"],
    llave="cliente + dia",
    formula="ISR diario = saldo base x tasa / 365, half-up por evento",
    tolerancia="0.01",
    oraculo="oraculos/isr.py",
    resultado=(
        "V-09: C = B (Aurum 765.75 / C 765.76, diferencia de redondeo). "
        "V-10: Σ|dif| = 5.87 en 728 dias-cliente — mismo motor. "
        "V-11: insumo, 65 filas / 4 titulares / 16 cuentas."),
    no_conformes="solo redondeo",
    clase_no_conforme="redondeo",
    no_concluye=[
        "Cuatro clientes NO permiten afirmar nada sobre el padron. El punto demuestra la "
        "MECANICA, no la cobertura.",
    ],
    solicitudes=("SOL-015",),
    evidencia=["REPORTE_FASE1_ISR.md", "f1_a_vs_c_diario_SEMILLA.parquet"],
    caso_validador="ISR-03",
),

Punto(
    id="V-12", familia="Fiscal", motores="C vs B",
    titulo="ISR-vivo nativo (post-cutover)",
    que_se_valida="El ISR que AurumCore calcula por si mismo despues del cutover.",
    que_NO_se_valida=["Todo: el punto esta BLOQUEADO por falta de insumo."],
    ventana_datos="post-cutover", corte="2026-08-20", ejecutado="2026-08-20",
    n_comparado="[PEND]", unidad="pagos",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta="pendiente de definir el universo una vez exista el insumo"),
    conciliacion="no aplica",
    racional_subconjunto=(
        "No hay subconjunto elegido: el ~13% de match reportado NO es un resultado de "
        "validacion sino la evidencia de que falta el insumo. Publicarlo como porcentaje "
        "de acierto seria enganoso."),
    tablas=["aurumcore (ISR al pago)"],
    filtros=["cutover ISR 2026-08-02 en adelante"],
    llave="cuenta + pago",
    formula="la misma de V-09/10",
    tolerancia="0.01",
    oraculo="oraculos/isr.py",
    resultado="~13% — NO es un resultado de validacion; es la senal del bloqueo",
    bloqueo=(
        "Falta el SALDO BASE PUNTO-EN-TIEMPO del cliente al momento del pago. Los saldos "
        "actuales solo dan una aproximacion, y comparar contra una aproximacion produce "
        "diferencias que no dicen nada del motor."),
    insumo_requerido=(
        "QUE: el saldo base gravable del cliente EN EL INSTANTE del pago (point-in-time), "
        "no el saldo actual. Puede venir de la traza de calculo del core o de una tabla de "
        "snapshot por evento de pago. "
        "CUANDO: en cuanto exista la traza; el cierre del 31-ago es la primera ventana."),
    solicitudes=("SOL-003", "SOL-015"),
    evidencia=["ISR_LIVE_NATIVO_2026-08-20.txt"],
),

# =============================================================================
# C · CREDITO
# =============================================================================

Punto(
    id="V-13", familia="Credito", motores="C vs B",
    titulo="Credito — interes ORDINARIO",
    que_se_valida=(
        "La provision DIARIA de interes ordinario que el core escribe en su feed "
        "operativo (credits-closing), contra el oraculo capital x (tasa/100) / 360."),
    que_NO_se_valida=[
        "El interes MORATORIO — es V-14, con otra base (capital_venc) y otra tasa.",
        "Los contratos sin provision ese dia: el universo lo define el feed del 2026-08-20, "
        "no el padron de credito.",
        "Que la tasa pactada sea la correcta contra el contrato; solo que la tasa del feed "
        "coincida con la de la DB (0 mismatch en 4,091).",
    ],
    ventana_datos="feed operativo del 2026-08-20 (un dia de provision)",
    corte="2026-08-20", ejecutado="2026-08-23",
    n_comparado="4,091", unidad="provisiones de interes ordinario",
    denominador=Denominador(
        total="5,365", segun="feed credits-closing del 2026-08-20",
        nota=("ESTA ES LA RESPUESTA A LA PREGUNTA DE LA SESION [00:27:52] '4,091 contratos, "
              "de cuantos?': de las 5,365 provisiones del feed de ese dia — 4,091 ordinario "
              "+ 1,274 moratorio —, repartidas en 4,945 contract_id distintos. El "
              "denominador es el FEED DEL DIA, no el padron de credito. Cuantos contratos "
              "de credito hay en total en AurumCore sigue [PEND] y es lo que convierte "
              "esto en representatividad del libro.")),
    conciliacion=(
        "SI, en dos ejes: (1) tasa del feed contra tasa de la DB, 4,091/4,091 sin mismatch; "
        "(2) 5,365 provisiones = 4,091 ordinario + 1,274 moratorio, sin residuo."),
    racional_subconjunto=(
        "El universo lo define el EVENTO, no una muestra: la provision diaria es el acto "
        "de calculo que se quiere auditar, y el feed de un dia contiene todos los contratos "
        "que devengaron ese dia. Se eligio un solo dia porque el feed lo produce un proceso "
        "de extraccion de logs aparte, no una consulta a la base. Ampliar a varios dias "
        "depende de que ese proceso corra mas dias, no del validador."),
    tablas=["feed credits-closing (CSV)", "aurumcore.lc_finantial_data",
            "aurumcore.lc_loan_contract"],
    filtros=["feed del 2026-08-20", "tipo = ordinario", "base 360 (calendar_type 1)"],
    llave="contract_id + fecha de provision",
    formula="interes_dia = capital x (tasa/100) / 360",
    tolerancia="1e-8 para el exacto; 0.01 para el de negocio",
    oraculo="comparadores/oraculo_credito.py",
    resultado="96.8% exacto a 1e-8 (3,472 / 3,585 con capital); 97.0% al centavo",
    granularidades="1e-8 96.80% · 1e-5 [PEND] · centavo [PEND, >=96.8]",
    sesgo="no detectado",
    no_conformes=(
        "El residual son 108 provisiones con capital = 0 en el staging y 506 sin snapshot "
        "al 2026-08-20. Es la tabla de capital PUNTO-EN-TIEMPO la que falta, no el motor."),
    clase_no_conforme="data-sourcing (patron P-019)",
    no_concluye=[
        "Un dia de provision NO permite afirmar nada sobre el comportamiento del motor a "
        "lo largo del mes o del ciclo de vida del credito.",
        "El denominador es el feed, no el padron: la representatividad respecto del libro "
        "de credito sigue sin declararse.",
    ],
    evidencia=["credito_provision_feed_2026-08-20.csv", "RESULTADO_credito_vivo_2026-08-23.md"],
),

Punto(
    id="V-14", familia="Credito", motores="C vs B",
    titulo="Credito — interes MORATORIO",
    que_se_valida=("capital_venc x (tasaMor/100) / 360, dias = 1, contra "
                   "lc_finantial_data.capital_venc."),
    que_NO_se_valida=[
        "El interes ordinario (V-13).",
        "La correccion de la CLASIFICACION en mora: se toma el capital_venc que el core "
        "declara; que ese capital DEBA estar vencido es otra pregunta.",
    ],
    ventana_datos="feed operativo del 2026-08-20",
    corte="2026-08-20", ejecutado="2026-08-23",
    n_comparado="1,274", unidad="provisiones de moratorio (692 con capital_venc)",
    denominador=Denominador(
        total="5,365", segun="feed credits-closing del 2026-08-20",
        nota=("1,274 de 5,365 provisiones del feed. De esas 1,274, solo 692 traen "
              "capital_venc distinto de cero — el resto no tiene base sobre la cual "
              "calcular, y el porcentaje se expresa sobre las 692.")),
    conciliacion=("tasa feed = tasa DB en el 100%; ratio feed x 360 / (tasa/100) = "
                  "capital_venc en 666/692"),
    racional_subconjunto=(
        "Mismo criterio que V-13: el universo es el evento del dia. El sub-recorte a 692 no "
        "es una eleccion sino una consecuencia — comparar contra un capital_venc de cero "
        "no prueba nada, y contarlas como no conformes acusaria al motor de un dato que no "
        "existe. Las 582 restantes se declaran, no se esconden."),
    tablas=["feed credits-closing (CSV)", "aurumcore.lc_finantial_data"],
    filtros=["feed del 2026-08-20", "tipo = moratorio", "capital_venc <> 0 para el cuadre"],
    llave="contract_id + fecha",
    formula="interes_mora = capital_venc x (tasaMor/100) / 360, dias = 1",
    tolerancia="1e-8 exacto; 0.01 de negocio",
    oraculo="comparadores/oraculo_credito.py",
    resultado="81.1% a 1e-8 (561/692); 95.7% al centavo (662/692)",
    granularidades="1e-8 81.10% · 1e-5 [PEND] · centavo 95.70%",
    sesgo="no detectado",
    no_conformes=(
        "30 son placeholders (capital_venc = 10,000,000) o creditos liquidados. El resto "
        "del residuo es SUB-CENTAVO: granularidad del snapshot de capital_venc, que es "
        "mas volatil intra-periodo. P-020 cerrada — la asimetria de 2.7% era artefacto de "
        "comparar el moratorio redondeado contra el feed sin redondear."),
    clase_no_conforme="data-sourcing (patron P-019)",
    no_concluye=[
        "El escalon 81.1% -> 95.7% es el diagnostico de que el residuo es sub-centavo. NO "
        "prueba que el core y el oraculo usen exactamente el mismo capital_venc.",
    ],
    evidencia=["RESULTADO_credito_vivo_2026-08-23.md"],
),

Punto(
    id="V-15", familia="Credito", motores="mecanica",
    titulo="Credito — conteo de DIAS de devengo",
    que_se_valida=(
        "Que los dias de provision correspondan a los dias del PERIODO DE AMORTIZACION, "
        "no a los dias transcurridos."),
    que_NO_se_valida=["El monto del interes — eso es V-13/V-14. Aqui solo la convencion "
                      "de dias."],
    ventana_datos="traza de log del 2026-08-23", corte="2026-08-23", ejecutado="2026-08-23",
    n_comparado="3", unidad="contratos (traza de log)",
    denominador=Denominador(
        total=PEND, segun="log del core",
        consulta=("contar cuantos contratos aparecen en la traza "
                  "CreditAmortizationChargeServiceImpl"),
        nota="3 contratos es una TRAZA DE CONFIRMACION, no una muestra."),
    conciliacion="no aplica",
    racional_subconjunto=(
        "Es una pregunta BINARIA sobre la convencion del motor: topa al periodo o cuenta "
        "transcurridos? Tres trazas que muestran el mismo comportamiento la contestan; "
        "trescientas no la contestarian mejor. Lo que un n de 3 NO puede decir es si hay "
        "contratos donde la convencion sea otra."),
    tablas=["log CreditAmortizationChargeServiceImpl.java:844"],
    filtros=["traza Days N"],
    llave="contrato",
    formula="dias = dias del periodo de amortizacion",
    tolerancia="exacto",
    oraculo="lectura de traza",
    resultado=("confirmado — Aurum topa al periodo. Explica el ~5% de residual historico "
               "del oraculo ordinario."),
    no_concluye=["Con n=3 no se puede descartar que haya productos con otra convencion."],
    evidencia=["credito_dias_log_2026-08-23.csv"],
),

Punto(
    id="V-16", familia="Credito", motores="C vs B",
    titulo="Credito — IVA sobre interes",
    que_se_valida="Que interest_tax_amount = interes x 16%.",
    que_NO_se_valida=["Que la tasa de 16% sea la aplicable a cada cliente (exenciones, "
                      "zona fronteriza)."],
    ventana_datos="corte de credito", corte="2026-08-20", ejecutado="2026-08-20",
    n_comparado="54,716", unidad="filas con IVA",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta=("select count(*) from aurumcore.lc_loan_amortization "
                  "-- total de filas, con y sin IVA"),
        nota="54,716 filas CON IVA; falta el total de filas para expresar la fraccion."),
    conciliacion="tasa implicita 16.0% en el 95% de las filas",
    racional_subconjunto=(
        "El recorte filas-con-IVA es estructural: una fila sin IVA no tiene nada que "
        "validar. No hubo muestreo — se tomaron todas."),
    tablas=["aurumcore.lc_loan_amortization"],
    filtros=["interest_tax_amount is not null and <> 0"],
    llave="fila de amortizacion",
    formula="IVA = interes x 0.16",
    tolerancia="1e-8",
    oraculo="comparadores/oraculo_credito.py",
    resultado="99.0% exacto",
    granularidades="1e-8 99.00% · 1e-5 [PEND] · centavo [PEND, >=99]",
    no_conformes="el ~5% restante es redondeo en montos chicos",
    clase_no_conforme="redondeo",
    evidencia=["COMPARACION_C_vs_DOC.md C3b"],
),

Punto(
    id="V-17", familia="Credito", motores="C vs B",
    titulo="Credito — AMORTIZACION (tabla francesa)",
    que_se_valida=(
        "Que la tabla de amortizacion cumpla la identidad de fila (capital + interes = "
        "cuota) y que el interes siga Actual/360."),
    que_NO_se_valida=[
        "Las amortizaciones AMERICANA, ITALIANA y ALEMANA: no tienen formula en el doc.",
        "El rollforward en contratos con pagos aplicados: capital_remaining_amount es un "
        "campo VIVO que se actualiza, asi que solo se puede validar en contratos FRESCOS.",
    ],
    ventana_datos="corte de credito", corte="2026-08-20", ejecutado="2026-08-20",
    n_comparado="794", unidad="contratos",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta=("select count(distinct lc_contract_id) from "
                  "aurumcore.lc_loan_amortization  -- y cuantos son FRENCH"),
        nota=("794 contratos. La auditoria lo senalo en la sesion [00:29:23]: 'el tema de "
              "amortizacion solo son 700 casos'. Falta el denominador.")),
    conciliacion=PEND,
    racional_subconjunto=(
        "Los 794 son los contratos FRESCOS (sin pagos aplicados) de amortizacion francesa. "
        "El recorte es metodologico, no de volumen: en un contrato con pagos, "
        "capital_remaining_amount ya se movio, asi que compararlo contra la tabla original "
        "produciria diferencias que no son del motor de amortizacion sino del paso del "
        "tiempo. Validar donde la comparacion es JUSTA y declarar el resto es preferible a "
        "un porcentaje mas grande y sin significado."),
    tablas=["aurumcore.lc_loan_amortization", "aurumcore.lc_loan_contract"],
    filtros=["amortization_type = FRENCH", "contratos frescos (sin pagos aplicados)"],
    llave="lc_contract_id + numero de periodo",
    formula="Francesa: cuota constante; interes = saldo x tasa/360 x dias (Actual/360)",
    tolerancia="0.01",
    oraculo="comparadores/oraculo_amortizacion.py",
    resultado=("identidad de fila 99.9%; interes Actual/360 EXACTO (P1 158.33, P3 112.37)"),
    granularidades="1e-8 [PEND] · 1e-5 [PEND] · centavo 99.90%",
    no_conformes=(
        "En contratos frescos, el rollforward / suma de capital / cuota constante da 91.7%. "
        "La cuota sale ~0.1% off por el ajuste Actual/360 contra la anualidad."),
    clase_no_conforme="data-sourcing",
    no_concluye=[
        "El 99.9% es IDENTIDAD DE FILA, no reconstruccion de la tabla completa desde cero. "
        "Son dos afirmaciones distintas y la segunda da 91.7%.",
    ],
    solicitudes=("SOL-015",),
    evidencia=["COMPARACION_C_vs_DOC.md C5"],
),

Punto(
    id="V-18", familia="Credito", motores="C vs doc / C vs B",
    titulo="Credito — CAT (Costo Anual Total)",
    que_se_valida=(
        "Que el oraculo reproduzca el CAT de la Circular 21/2009: contra los ejemplos del "
        "doc (3/3) y contra el cat que el core guarda, en el ESTRATO donde ese campo es "
        "un CAT per-contrato."),
    que_NO_se_valida=[
        "Los 25,026 contratos donde cat guarda una CONSTANTE copiada: comparar el oraculo "
        "contra una constante no mide el motor. Se reportan aparte con su conteo.",
        "Los 2,576 contratos con cat = 0 — es el hallazgo A28-CAT-CERO, no un cuadre.",
        "El CAT de amortizacion italiana y alemana.",
    ],
    ventana_datos="padron de credito al corte", corte="2026-08-28", ejecutado="2026-08-28",
    n_comparado="4,225", unidad="contratos del estrato per-contrato",
    denominador=Denominador(
        total="31,866", segun="B (AurumCore) — lc_loan_contract completo",
        nota=("MEDIDO, no estimado. La particion completa: constante copiada 25,026 "
              "(78.5%); varia por contrato 4,220 (13.2%); cat = 0 2,576 (8.1%); sin cat "
              "44 (0.1%).")),
    conciliacion=(
        "SI: los cuatro estratos suman 31,866 sin residuo. cat = 27.10 cubre 15,300 "
        "contratos que abarcan 521 plazos y 3,930 montos distintos — la prueba de que ahi "
        "el campo no es un calculo."),
    racional_subconjunto=(
        "El recorte NO busca subir el porcentaje: busca que el porcentaje SIGNIFIQUE algo. "
        "Un CAT es funcion del monto y del plazo, asi que un mismo valor en 3,930 montos "
        "distintos es una constante copiada, no la salida de un motor. El cruce global "
        "reportaba 11.60% y ese numero medía EL CAMPO, no el CAT. Subirlo a ~100% sobre "
        "los 31,866 no es una meta alcanzable ni deseable: seria comparar contra constantes "
        "hasta que cuadren."),
    tablas=["aurumcore.lc_loan_contract", "aurumcore.lc_loan_amortization",
            "aurumcore.lc_account_commission"],
    filtros=["c.cat is not null", "c.cat <> 0",
             "cat NO compartido por >= 100 contratos (umbral_constante)",
             "c.activation_date is not null"],
    llave="contract_number",
    formula=("CAT = tasa anual i que iguala VP(monto - comision de apertura) = "
             "VP(pagos sin IVA)"),
    tolerancia="0.01 puntos porcentuales, con prueba de signo",
    oraculo="oraculos/cat.py::fila_cat (reusa comparadores/oraculo_cat.py, 3/3 vs doc)",
    sql="validador/extraccion/aurum/cat_per_contrato.sql",
    resultado="28.50% al centavo (1,204 / 4,225) — calculado por este validador",
    granularidades="1e-8 23.43% · 1e-5 23.43% · centavo 28.50%",
    sesgo=("no detectado (p = 0.673, +1,629/-1,604). La primera corrida SI marco sesgo "
           "(p = 0.0089) y era del METODO: el core guarda el CAT con dos decimales y el "
           "oraculo comparaba sin redondear. Con half-up desaparece."),
    no_conformes=(
        "3,021. El residuo es la COMISION realmente cobrada: la implicita despejada del "
        "cat guardado sale ~2% mientras la configurada es 3.99%."),
    clase_no_conforme="data-sourcing",
    no_concluye=[
        "El residuo NO se atribuye a AurumCore: falta saber que comision se cobro, que no "
        "es la pregunta de si la formula esta bien. La formula reproduce 3/3 el doc.",
        "El escalon 23.43% -> 28.50% NO es el diagnostico habitual de residuo sub-centavo: "
        "cat guarda dos decimales, asi que no hay residuo sub-centavo que absorber.",
    ],
    solicitudes=("SOL-015",),
    evidencia=["validador/reportes/CAT-01_2026-08-28_*/",
               "50_hallazgos/CANDIDATOS_A_HALLAZGO.md (A28-CAT-CONSTANTE / CERO / FINANCED)"],
    reproducir="cd validador && python cli.py --caso CAT-01 --confirmar",
    caso_validador="CAT-01",
),

Punto(
    id="V-19", familia="Credito", motores="C vs config B",
    titulo="IFRS 9 — etapas y porcentaje de reserva",
    que_se_valida=(
        "Que los porcentajes de reserva por (cartera, zona, dias de mora) que aplica el "
        "core sean los de las Tablas del GTM, y que la etapa se asigne por dias de mora."),
    que_NO_se_valida=[
        "Etapas 1 y 2 en creditos amortizando: la base capital / intereses exigibles "
        "depende de un spec que sigue pendiente.",
        "La composicion de reserva_int: Finsus la definio el 2026-08-24 pero sin formulas.",
        "Cartera COMERCIAL y creditos REESTRUCTURADOS: necesitan las 9 tablas prometidas.",
        "Zona MARGINADA: el staging no trae la zona, se asume no marginada.",
    ],
    ventana_datos="agosto 2026 sobre lc_finantial_data_stage",
    corte="2026-08-28", ejecutado="2026-08-28",
    n_comparado="20,000", unidad="filas de staging en etapa 3",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta=("select count(*) from aurumcore.lc_finantial_data_stage "
                  "where capital_mora_days >= 90 and information_date between ..."),
        nota=("El 20,000 es la COTA de la extraccion, no el universo. Ademas hay un segundo "
              "denominador, el de la config: 37 de 37 celdas de lc_reserve_ifrs, que ese "
              "SI es completo.")),
    conciliacion=(
        "SI en el eje de configuracion: las 37 celdas de la tabla del GTM contra las 37 de "
        "lc_reserve_ifrs, exactas. Ese cruce es completo, no muestral."),
    racional_subconjunto=(
        "ALCANCE DELIBERADAMENTE ESTRECHO: solo etapa 3, consumo, zona no marginada. Es la "
        "parte donde la regla esta CERRADA en la fuente y se puede afirmar algo. Cubrir "
        "E1/E2 hoy exigiria inventar la base de calculo, que es lo unico que este proyecto "
        "no hace. El limite de 20,000 filas es la cota operativa para no degradar "
        "produccion."),
    tablas=["aurumcore.lc_finantial_data_stage", "aurumcore.lc_reserve_ifrs",
            "aurumcore.lc_risk_stage"],
    filtros=["dias_mora >= 90 (etapa 3)", "capital_venc <> 0",
             "information_date en la ventana"],
    llave="stage_id",
    formula=("Reserva = |capital_venc| x pct(dias_mora); pct de las Tablas 1/2/3 del GTM "
             "(75/90/100)"),
    tolerancia="0.01 por evento, con prueba de signo",
    oraculo="oraculos/ifrs9.py::fila_reserva_e3",
    sql="validador/extraccion/aurum/ifrs9_e3_reserva.sql",
    resultado="100.00% al centavo (20,000 / 20,000) — CERO violaciones",
    granularidades="1e-8 88.10% · 1e-5 88.10% · centavo 100.00%",
    sesgo=("La corrida marca sesgo sub-centavo y NO es del core: 5,133 diferencias bajaron "
           "a 2,381 al aplicar half-up, y en las restantes el porcentaje IMPLICITO sale "
           "correcto (75.0000 / 90.0001 / 100.0000). Es precision de la base, patron "
           "P-019."),
    no_conformes="cero al centavo",
    no_concluye=[
        "El 100% es sobre etapa 3 consumo zona no marginada. NO dice nada de E1/E2, "
        "comercio ni reestructurados.",
        "La INDEPENDENCIA es lo que da valor aqui: el porcentaje de C sale del GTM, no de "
        "lc_reserve_ifrs. Que ademas coincida 37/37 con la config es un RESULTADO, no el "
        "metodo — si se hubiera leido del core, probaria consistencia consigo mismo.",
    ],
    solicitudes=("SOL-015",),
    evidencia=["validador/reportes/IFRS9-E3_2026-08-28_*/", "COMPARACION_C_vs_DOC.md E4"],
    reproducir="cd validador && python cli.py --caso IFRS9-E3 --confirmar",
    caso_validador="IFRS9-E3",
),

# =============================================================================
# D · TRANSACCIONAL / CONTABLE  y  E · PADRON
# =============================================================================

Punto(
    id="V-20", familia="Transaccional/Contable", motores="A vs B",
    titulo="Motor B diario — completitud A vs B",
    que_se_valida=("Que NO FALTE ninguna operacion de openfin (A) en AurumCore (B). Es "
                   "completitud de volumen por dia, no igualdad de importes."),
    que_NO_se_valida=[
        "La correspondencia instancia-a-instancia: falta el crosswalk de tipos "
        "transaccionales (SOL-004). Se compara VOLUMEN por dia, no transaccion por "
        "transaccion.",
        "Que los importes cuadren — solo que el conteo de B no sea menor que el de A.",
    ],
    ventana_datos="2026-08-10 -> 2026-08-18",
    corte="2026-08-18", ejecutado="2026-08-18",
    n_comparado="6", unidad="dias (21K-29K operaciones por dia)",
    denominador=Denominador(
        total=PEND, segun="A (openfin) y B (AurumCore)",
        consulta="contar dias disponibles post-cutover en ambos cores",
        nota="6 dias de una ventana post-cutover cuyo largo total no se declaro."),
    conciliacion="conteo diario A contra conteo diario B, dia por dia",
    racional_subconjunto=(
        "Seis dias CONSECUTIVOS, no seis dias sueltos: la completitud se rompe por lotes "
        "(un proceso que no corrio, una ventana que se salto), asi que dias seguidos "
        "detectan el hueco y dias dispersos no. El largo lo limito la ventana post-cutover "
        "disponible al momento de la corrida."),
    tablas=["openfin (transaccional)", "aurumcore.transaction_detail"],
    filtros=["fecha entre 2026-08-10 y 2026-08-18"],
    llave="conteo por dia",
    formula="A >= B (completitud); 0 faltantes",
    tolerancia="0 faltantes — no admite holgura",
    oraculo="comparadores/motor_b_diario.py",
    resultado=("OF >= AU siempre (delta +0.1% a +2.1%), es decir 0 faltantes en B. "
               "Ejemplos: 08-14 OF 29,029 vs AU 29,004 (+0.1%); 08-11 OF 21,956 vs AU "
               "21,501 (+2.1%)."),
    no_conformes="ninguno en la direccion validada",
    no_concluye=[
        "El delta positivo (openfin tiene MAS) no esta explicado: puede ser tipos que "
        "AurumCore no replica por diseno, o puede ser faltante real en la otra direccion. "
        "Sin el crosswalk no se puede distinguir.",
    ],
    solicitudes=("SOL-004",),
    evidencia=["MOTOR_B_multidia_2026-08.txt", "motor_b_diario_2026-08-14.txt"],
    caso_validador="DIARIO-B",
),

Punto(
    id="V-21/22", familia="Transaccional/Contable", motores="B",
    titulo="Contable — doble partida diaria y detalle transaccional",
    que_se_valida=("Que cada dia la balanza cumpla DOBLE PARTIDA: la suma de debitos mas "
                   "la de creditos da exactamente cero."),
    que_NO_se_valida=[
        "Que el asiento este en la CUENTA CONTABLE correcta: la doble partida cuadra "
        "aunque el mapeo contable sea erroneo.",
        "La balanza contra saldos: hay una alerta abierta (producto 2001 -34%, "
        "daily_account_balances stale) que es de MAPEO, no de doble partida.",
    ],
    ventana_datos="2026-08-10 -> 2026-08-16 (7 dias)",
    corte="2026-08-16", ejecutado="2026-08-28",
    n_comparado="7", unidad="dias (17K-220K asientos por dia)",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore)",
        consulta=("select count(distinct date_trunc('day', ...)) from "
                  "aurumcore.transaction_detail  -- dias disponibles post-cutover"),
        nota=("7 dias consecutivos. El detalle transaccional del 08-14 son 96,235 "
              "movimientos, el dia completo.")),
    conciliacion=("SI: el detalle del 08-14 (96,235 movimientos) reproduce el mismo "
                  "descuadre de 0.00 que el agregado del dia."),
    racional_subconjunto=(
        "La doble partida es una identidad EXACTA, no un estimador: si un dia cuadra a "
        "0.00, ese dia cuadra, sin margen de error muestral. Siete dias consecutivos "
        "cubren un ciclo semanal completo, incluyendo fin de semana, que es cuando los "
        "procesos batch se comportan distinto. Ampliar a mas dias agrega confianza sobre "
        "la ESTABILIDAD, no sobre la correccion de los dias medidos."),
    tablas=["aurumcore.transaction_detail", "aurumcore.cat_accounting_account"],
    filtros=["fecha entre 2026-08-10 y 2026-08-16"],
    llave="dia contable",
    formula="SUM(debit_amount) + SUM(credit_amount) = 0 por dia (el debito viene negativo)",
    tolerancia="0.00 EXACTO — una identidad contable no admite holgura",
    oraculo="engine/compare.py::comparar_suma_cero",
    sql="validador/extraccion/aurum/contable_b1_doble_partida.sql",
    resultado=("descuadre = $0.00 en 7 de 7 dias (0 dias violan). Montos diarios de $84M "
               "a $1,301M."),
    no_conformes="ninguno",
    no_concluye=[
        "Doble partida en cero NO significa contabilidad correcta: significa que los "
        "asientos estan balanceados. La alerta de balanza (producto 2001) sigue abierta y "
        "es de otra naturaleza.",
    ],
    evidencia=["validador/reportes/CONTABLE-B1_2026-08-28_*/", "CONTABLE_BC_2026-08-20.txt"],
    reproducir="cd validador && python cli.py --caso CONTABLE-B1 --confirmar",
    caso_validador="CONTABLE-B1",
),

Punto(
    id="V-23", familia="Padron", motores="cobertura",
    titulo="Cuentahabientes — WSO2 vs padron Aurum",
    que_se_valida="Cobertura bidireccional entre el proveedor de identidad y el padron.",
    que_NO_se_valida=["Los datos personales en si; solo la EXISTENCIA de la correspondencia."],
    ventana_datos="corte del padron", corte="2026-08-20", ejecutado="2026-08-20",
    n_comparado="20", unidad="huerfanos Aurum -> WSO2",
    denominador=Denominador(
        total=PEND, segun="B (AurumCore) — padron completo",
        consulta="select count(*) from aurumcore.accountholder",
        nota=("Los 20 huerfanos son el RESULTADO, no el universo. El universo es el padron "
              "completo y no se declaro. En la otra direccion: 181,850 telefonos de WSO2 "
              "que no estan en Aurum, y 295 altas incompletas.")),
    conciliacion="cruce bidireccional; 1 telefono duplicado en Aurum",
    racional_subconjunto=(
        "No hay subconjunto: se cruzaron los dos padrones completos. Lo que falta declarar "
        "es el TAMANO de cada uno, para que 20 y 181,850 se lean como fracciones y no como "
        "numeros sueltos."),
    tablas=["aurumcore.accountholder", "WSO2 (identidad)"],
    filtros=["padron completo, ambas direcciones"],
    llave="telefono",
    formula="cruce de conjuntos, ambas direcciones",
    tolerancia="cobertura, no importe",
    oraculo="cruce de conjuntos",
    resultado=("Aurum -> WSO2: 20 huerfanos. WSO2 -> Aurum: 181,850 telefonos no en Aurum. "
               "Altas incompletas: 295. Telefono duplicado en Aurum: 1."),
    no_conformes="los 20 huerfanos y las 295 altas incompletas",
    clase_no_conforme="linaje",
    no_concluye=[
        "La asimetria de 181,850 se ESPERA por ciclo de vida de identidad (P-017): quien "
        "se registro y nunca abrio cuenta queda en WSO2 y no en Aurum. Esa explicacion "
        "es plausible y NO esta verificada.",
    ],
    evidencia=["cuentahab_aurum_no_en_wso2.csv", "cuentahab_wso2_no_en_aurum.csv",
               "cuentahab_altas_incompletas.csv"],
    caso_validador="CUENTAHAB-01",
),
]
