# -*- coding: utf-8 -*-
"""Tabla de motores del tablero — espejo declarativo del DOSSIER.

FUENTE: 40_validaciones/DOSSIER_MOTORES_ORACULO_C.md (corte 2026-08-23).
Este modulo NO calcula nada: declara, por motor, que afirma, con que formula,
CONTRA QUE se valida y con que fuente, y donde vive su oraculo.

La distincion que sostiene la honestidad del tablero es `origen_resultado`:

    corrida_local  el % lo calculo ESTA maquina, contra la BD, ahora.
    dossier        el % lo reporta el DOSSIER de una corrida previa hecha en
                   el repo de validacion. El tablero lo muestra CITADO, nunca
                   como si lo hubiera calculado.
    sin_cruce      hay formula y autoprueba, no hay cruce contra datos.

Mezclar esos tres en una sola barra verde seria exactamente el "todo pasa" que
este producto existe para evitar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# --- Vocabulario controlado --------------------------------------------------

# Contra que se contrasta la formula. El orden es de mas fuerte a mas debil.
TIPO_VALIDACION = {
    "config": "El valor consta en una tabla de configuracion de la propia BD de Aurum. Es la validacion mas fuerte: C = config real.",
    "norma": "Sustento legal (LISR, CNBV, Banxico).",
    "doc": "La formula o el parametro constan en un GTM oficial, con pagina.",
    "inferencia": "La mecanica se dedujo de los datos. POR CONFIRMAR, no es un hecho.",
}

# Por que un no-conforme no cuadra. Distinguirlos es el trabajo del auditor:
# reportar linaje como defecto es tan grave como ocultar un defecto.
CLASES_NO_CONFORME = {
    "defecto": "El motor calcula distinto de la regla. Es hallazgo.",
    "linaje": "El dato de contraste discrepa entre tablas; el motor no esta en duda.",
    "data-sourcing": "Falta el insumo punto-en-tiempo para comparar de forma justa.",
    "bloqueo": "No hay corrida todavia (tiempo o log faltante).",
    "redondeo": "Diferencia sub-centavo por modo de redondeo no desambiguado.",
}

# Agrupacion para el menu del tablero. Es una vista de NEGOCIO, distinta del
# `dominio` tecnico (DEV/FIS/COL/CTB/MOV/MIG) que usa el catalogo del validador:
# el auditor de Finsus piensa en productos, no en codigos de dominio.
CATEGORIAS = ("Captacion", "Fiscal", "Credito", "Transaccional/Contable", "Padron")

CATEGORIA_POR_MOTOR = {
    "VISTA": "Captacion", "PLAZO": "Captacion", "SALDO-PROM": "Captacion", "GAT": "Captacion",
    "ISR": "Fiscal", "ISR-VIVO": "Fiscal",
    "CRED-ORD": "Credito", "CRED-MOR": "Credito", "CRED-DIAS": "Credito",
    "CRED-IVA": "Credito", "IFRS9": "Credito", "AMORT": "Credito", "CAT": "Credito",
    "MOTOR-B": "Transaccional/Contable", "CONTABLE": "Transaccional/Contable",
    "WSO2": "Padron",
}

# Motores de IDENTIDAD / COMPLETITUD: su cuadre NO son las tres granularidades,
# porque no comparan dos importes calculados sino que afirman una identidad.
# Mostrarles tres barras sugeriria una precision que su regla no tiene.
TOLERANCIA_PROPIA = {
    "CONTABLE": ("0.00 exacto",
                 "Identidad contable: la suma de cargos y abonos del dia se cancela. "
                 "No admite holgura, asi que no hay escalon de granularidad que leer."),
    "MOTOR-B": ("A >= B",
                "Completitud, no calculo: se afirma que OpenFin nunca tiene menos "
                "transacciones que AurumCore. Lo que se mide es faltante, no diferencia de importe."),
}

ESTADOS = {
    "validado": "regla + oraculo + cruce corrido, resultado documentado",
    "parcial": "mecanica confirmada, falta cerrar alcance",
    "bloqueado": "falta insumo externo (dato, log, definicion)",
    "sin_cruce": "formula lista y autoprobada, sin cruce contra datos",
}


@dataclass
class Fuente:
    tipo: str          # config | norma | doc | inferencia
    cita: str          # de donde sale, con pagina o tabla

    def como_dict(self) -> dict:
        return {"tipo": self.tipo, "cita": self.cita,
                "significado": TIPO_VALIDACION.get(self.tipo, "")}


@dataclass
class Alcance:
    """Que se toma y que NO, con el universo detras. Fuente: el INFORME DETALLADO.

    Lo pidio la auditoria en la sesion del 2026-08-28: no basta el porcentaje,
    hace falta saber sobre QUE se calculo y cuanto representa. Un 100% sobre un
    cohorte de 39.6% del libro y un 100% sobre el libro entero son afirmaciones
    muy distintas, y la tarjeta las mostraba igual.

    `tipo` separa las dos cosas que se confundian:
      censo        se tomo el 100% de un alcance BIEN DEFINIDO. No extrapola
                   porque no hace falta: no quedo nada fuera de ese alcance.
      subconjunto  recorte con rationale (metodologico o de performance).
      muestra      seleccion parcial. Es la unica que necesitaria metodo de
                   muestreo declarado para poder extrapolar.
    """
    si: str
    no: tuple[str, ...]
    tipo: str
    n: str
    universo: str                  # total del que sale `n`, o "[PEND]"
    representatividad: str
    rationale: str
    ref: str                       # ficha del informe detallado
    nota: str = ""                 # matices (p.ej. ciclo distinto al citado)

    def como_dict(self) -> dict:
        return {"si": self.si, "no": list(self.no), "tipo": self.tipo, "n": self.n,
                "universo": self.universo, "representatividad": self.representatividad,
                "rationale": self.rationale, "ref": self.ref, "nota": self.nota}


@dataclass
class Motor:
    id: str
    nombre: str
    dominio: str
    formula: str
    ejemplo: str                      # el ejemplo del doc, para verificar de un vistazo
    fuentes: tuple[Fuente, ...]
    oraculo: str                      # modulo::funcion, para trazabilidad
    estado: str
    # Resultado tal como lo reporta el DOSSIER. Se muestra CITADO.
    dossier_pct: str | None = None
    dossier_detalle: str = ""
    no_conformes: str = ""
    clase_no_conforme: str = ""
    # Si el motor tiene un caso ejecutable en validador/catalogo, su id.
    caso_validador: str | None = None
    # Insumos y bloqueos
    insumos: str = ""
    bloqueo: str = ""
    solicitudes: tuple[str, ...] = ()
    depende_de_logs: bool = False
    autopruebas: str = ""             # que autoprueba respalda la formula
    # Las tres granularidades TAL COMO LAS CITA `MATRIZ_TOLERANCIAS.md`, para
    # los motores que este tablero no ha corrido. Un porcentaje sin su escala
    # desinforma: el moratorio "81.1%" es a 1e-8 y al centavo es 95.7%, que es
    # justo el ejemplo canonico del escalon diagnostico. Mostrar el 81 pelon
    # hace pensar que el motor falla 1 de cada 5 veces.
    dossier_match: dict | None = None   # {"1e-8": "...", "1e-5": "...", "centavo": "...", "n": "...", "sesgo": "no"}
    # La lectura VERDADERA del escalon de este motor, cuando se conoce. El
    # tablero tiene una lectura generica ("escalon ancho = residuo sub-centavo")
    # que vale para casi todos, y para CAT es FALSA: ahi el escalon es angosto
    # porque `lc_loan_contract.cat` solo guarda dos decimales, no porque haya
    # residuo sub-centavo que absorber. Un tablero que aplica la plantilla a
    # ciegas afirma un diagnostico que no verifico, que es la misma fabricacion
    # que NORTE_SANIDAD persigue — solo que en la prosa en vez de en la cifra.
    lectura_escalon: str = ""
    # Alcance declarado (INFORME_DETALLADO_AUDITORIA). Sin esto, la tarjeta
    # muestra un porcentaje sin decir sobre que universo se calculo.
    alcance: "Alcance | None" = None

    @property
    def categoria(self) -> str:
        return CATEGORIA_POR_MOTOR.get(self.id, "Otros")

    @property
    def tolerancia_propia(self) -> tuple[str, str] | None:
        return TOLERANCIA_PROPIA.get(self.id)

    @property
    def evidencia_config(self) -> str:
        """Las citas de las fuentes tipo `config`, que son la validacion mas fuerte."""
        return " · ".join(f.cita for f in self.fuentes if f.tipo == "config")

    @property
    def pct_citado(self) -> tuple[str, str] | None:
        """(porcentaje, escala) del numero citado. NUNCA un numero sin escala.

        Se prefiere el CENTAVO cuando existe, porque es la tolerancia de
        negocio — "lo que le importa al cliente y a la contabilidad". Mostrar
        el de 1e-8 como titular desinforma: el moratorio a 1e-8 es 81.10% y al
        centavo 95.70%, y el 81 pelon hace pensar que el motor falla una de
        cada cinco veces. Las tres barras van igual debajo, asi que el numero
        estricto no se esconde: se contextualiza.
        """
        m = self.dossier_match or {}
        for esc in ("centavo", "1e-5", "1e-8", "volumen"):
            if m.get(esc):
                return (m[esc], esc)
        if self.dossier_pct:
            # Sin entrada en la matriz NO se inventa una escala: etiquetar un
            # numero "al 1e-8" cuando no lo es seria peor que no etiquetarlo.
            # §3.3 pide que ningun % se muestre sin escala; la salida correcta
            # es declarar cual es, no suponerla.
            return (self.dossier_pct, "sin escala declarada")
        return None

    def cobertura(self, hay_cruce: bool, escala: str | None = None) -> str:
        """De que CLASE es la evidencia: datos, volumen, completitud, config o nada.

        Lo decide el backend y no el frontend, porque es una afirmacion sobre
        la EVIDENCIA, no una decision de presentacion. Si el SPA lo dedujera
        inspeccionando chips, dos vistas del mismo motor podrian contarlo
        distinto (§3.2 del brief).

        `datos` no es un cajon para todo lo que trae porcentaje. Un cruce a
        VOLUMEN (CAT) y una identidad de COMPLETITUD (contable, motor B) tienen
        porcentaje y no tienen granularidad: meterlos en `datos` invita a
        leerlos como precision aritmetica, que es exactamente como CAT termino
        etiquetado "al 1e-8" (NORTE_SANIDAD INV-H2).
        """
        if hay_cruce:
            if escala == "volumen":
                return "volumen"
            if escala == "completitud" or self.tolerancia_propia:
                return "completitud"
            return "datos"
        if any(f.tipo == "config" for f in self.fuentes):
            return "config"
        return "sin_cruce"

    def como_dict(self) -> dict:
        tp = self.tolerancia_propia
        return {
            "id": self.id, "nombre": self.nombre, "dominio": self.dominio,
            "categoria": self.categoria,
            "tolerancia_propia": ({"regla": tp[0], "porque": tp[1]} if tp else None),
            "formula": self.formula, "ejemplo": self.ejemplo,
            "valida_contra": [f.como_dict() for f in self.fuentes],
            "oraculo": self.oraculo, "estado": self.estado,
            "estado_significado": ESTADOS.get(self.estado, ""),
            "dossier_pct": self.dossier_pct, "dossier_detalle": self.dossier_detalle,
            "no_conformes": self.no_conformes,
            "clase_no_conforme": self.clase_no_conforme,
            "clase_significado": CLASES_NO_CONFORME.get(self.clase_no_conforme, ""),
            "caso_validador": self.caso_validador, "insumos": self.insumos,
            "bloqueo": self.bloqueo, "solicitudes": list(self.solicitudes),
            "depende_de_logs": self.depende_de_logs, "autopruebas": self.autopruebas,
            "evidencia_config": self.evidencia_config,
            "dossier_match": self.dossier_match,
            "lectura_escalon": self.lectura_escalon,
            "alcance": self.alcance.como_dict() if self.alcance else None,
            "pct_escala": (self.pct_citado or (None, None))[1],
        }


D = "doc"; C = "config"; N = "norma"; I = "inferencia"

MOTORES: tuple[Motor, ...] = (
    Motor(
        id="VISTA", nombre="Rendimiento — cuenta a la VISTA", dominio="DEV",
        formula="Rendimiento = Round2( Trunc20( Trunc20((SPM x Tasa)/100) / DiasAnio ) x DiasPeriodo )",
        ejemplo="SPM 5,000 · tasa 7% · base 360 · 31 dias -> 30.14",
        fuentes=(Fuente(D, "GTM-Pago de Rendimientos p.3"),),
        oraculo="oraculo_rendimientos.rendimiento_vista", estado="parcial",
        dossier_pct="82.1",
        dossier_detalle=("DESTRABADO 2026-08-24 y REALINEADO el 28-ago: B se toma de `yield_dto` "
                         "(el registro del posteo) en vez de la referencia de texto de "
                         "transaction_detail, y la base de dias se elige por evidencia entre las "
                         "cuatro convenciones. El cuadre pasa de 91.52% a 96.63%."),
        insumos="finsus_account_history (average_balance_amount, interest_rate, iv_term_days) + esquema de rendimientos",
        bloqueo=("Ya NO es bloqueo de tiempo. El 18% residual depende de dos cosas: la convencion "
                 "exacta de `dt` (inclusivo en ambos extremos, el dia de fondeo no cuenta) y el "
                 "SPM-de-RENDIMIENTO, que Finsus dice se guarda en la poliza de intereses y PUEDE "
                 "DIFERIR del average de consulta. En transaction_detail no esta."),
        no_conformes=("Corrida realineada sobre 20,000 pares: 96.63% conforme, 675 no conformes, "
                      "con SESGO (+719/-7). Siguiendo el playbook: el redondeo esta descartado "
                      "(cerramos half-up igual que el core) y la magnitud lo ubica — 398 de los 675 "
                      "son de MENOS DE UN PESO y solo 8 pasan de 100. Esos 8 materiales tienen "
                      "dt=31 con activacion en abril y junio, y el core pago como si fueran 17 a 24 "
                      "dias: usamos la fecha de ACTIVACION como proxy del FONDEO, y Finsus dijo que "
                      "lo que no cuenta es el dia de fondeo. Una cuenta activada en abril puede "
                      "fondearse en julio. Es el techo de nuestro proxy, no un defecto del motor; "
                      "el dt real vive en la poliza (SOL-003)."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-003",), depende_de_logs=False,
        caso_validador="REND-VISTA", autopruebas="reproduce el 30.14 del doc",
    ),
    Motor(
        id="PLAZO", nombre="Rendimiento — INVERSION a plazo fijo", dominio="DEV",
        formula="Rendimiento = RoundHalfEven2( Ceil10( Ceil10((Capital x Tasa)/100) / DiasAnio ) x DiasTranscurridos )",
        ejemplo="1,000 a 100 dias @5% base 360 -> 13.89",
        fuentes=(Fuente(D, "GTM-Pago de Rendimientos p.5"),),
        oraculo="oraculo_rendimientos.rendimiento_plazo", estado="validado",
        dossier_pct="100.00",
        dossier_detalle="0 violaciones en 530,195 periodos (157,999 cuentas), cohorte live `origin is null`. Migrado (C=A) 97.8%.",
        no_conformes="Cero. Es el motor mas solido del conjunto.",
        caso_validador="REND-PLAZO",
        insumos="account.iv_initial_amount · iv_payment_plan (origin, interest_amount, interest_paid)",
        autopruebas="reproduce el 13.89 del doc",
        dossier_match={"1e-8": "100.00", "1e-5": "100.00", "centavo": "100.00", "n": "530,195 periodos", "sesgo": "no"},
    ),
    Motor(
        id="SALDO-PROM", nombre="Saldo promedio (SPM)", dominio="DEV",
        formula="SPM = (saldo_cuenta x difference_of_days + acumulado) / elapsed_days",
        ejemplo="(30,000 x 8 + 20,000) / 9 -> 28,888.88",
        fuentes=(Fuente(D, "GTM-Saldo Promedio p.8-9"),),
        oraculo="oraculo_rendimientos.saldo_promedio_rendimiento", estado="parcial",
        dossier_detalle=("Formula CONFIRMADA al centavo por Finsus (2026-08-24): base 360, "
                         "interes = SPM x dt x tasa / 36000. Caso limpio 6de5351e: "
                         "10,165.70 x 31 x 4% / 36000 = 35.02 = posteado. Promedia sobre los dias "
                         "efectivamente DEVENGADOS, no los naturales del mes."),
        insumos="finsus_account_history (105M filas, por cuenta y por dia) · poliza de intereses (SPM + dt)",
        bloqueo=("`account.average_balance_amount` es el SPM de CONSULTA (rolling) y el propio doc "
                 "advierte que puede diferir del SPM de RENDIMIENTO: usarlo como sustituto seria "
                 "una aproximacion presentada como validacion. El SPM de rendimiento vive en la "
                 "poliza de intereses, cuyas formulas exactas siguen en el doc pendiente."),
        no_conformes="Sin corrida propia todavia: la consulta contra finsus_account_history esta por escribir.",
        clase_no_conforme="data-sourcing",
        solicitudes=("SOL-003",), depende_de_logs=False, caso_validador="SALDO-PROM",
        autopruebas="reproduce el 28,888.89 del doc",
    ),
    Motor(
        id="ISR", nombre="ISR — retencion sobre rendimientos", dominio="FIS",
        formula=("Base Gravable = Saldo Total - Exencion\n"
                 "ISR Diario    = Trunc5( Base x Trunc20( Tasa / (100 x 365) ) )\n"
                 "ISR Retenido  = Round2( Trunc20( ISR Diario x DiasPeriodo ) x Proporcion )\n"
                 "Proporcion    = saldo_cuenta / saldo_total"),
        ejemplo="cliente 1-10-370 · 300,000 a 361 dias -> 765.75",
        fuentes=(Fuente(D, "GTM-Pago de Rendimientos p.6"),
                 Fuente(N, "LISR 54/135 · LIF 2026 Art.24 · UMA DOF 9-ene-2026"),
                 Fuente(C, "system_configuration: tax.days.year, yield.tax.exempt.uma.amount")),
        oraculo="oraculo_isr.isr_retenido", estado="validado",
        dossier_pct=None,
        dossier_detalle="Historico C = B = 765.75. Parametros 2026: tasa 0.9%, exencion 5xUMA = 213,973.20, base 365.",
        no_conformes=("El EJEMPLO del doc tenia un error (dividia entre la base gravable); Finsus "
                      "corroboro que lo correcto es dividir entre el saldo total (C-002 cerrada). "
                      "Personas morales sin resolver (SOL-011)."),
        caso_validador="ISR-01",
        insumos="transaction_detail (INTERNAL TRANSFER/Generic -> cuenta ISR 100-0000-438220) · account.iv_initial_amount",
        solicitudes=("SOL-011",), autopruebas="5 casos de oro de S-FIS-001",
    ),
    Motor(
        id="ISR-VIVO", nombre="ISR vivo nativo (post-cutover)", dominio="FIS",
        formula="misma regla del ISR, sobre retenciones generadas por Aurum: created >= cutover",
        ejemplo="delimitador `created >= 2026-08-03`, NO `origin is null`",
        fuentes=(Fuente(D, "GTM-Pago de Rendimientos p.6"), Fuente(N, "LISR 54/135")),
        oraculo="isr_live_nativo.py", estado="bloqueado",
        bloqueo=("Necesita el saldo base PUNTO-EN-TIEMPO del cliente al momento del pago. "
                 "Los saldos actuales solo dan una aproximacion, y el residual mezclaria "
                 "deriva de saldo con defecto de calculo: no es validacion."),
        no_conformes="Sin corrida limpia.", clase_no_conforme="data-sourcing",
        solicitudes=("SOL-003", "SOL-004"), depende_de_logs=True,
        insumos="transaction_detail + saldo base al instante del pago",
    ),
    Motor(
        id="CRED-ORD", nombre="Credito — interes ORDINARIO", dominio="COL",
        formula="Interes = Capital_Insoluto x (tasa/100) x (dias / DiasAnio)",
        ejemplo="50,000 @15% 1 dia base 360 -> 20.83",
        fuentes=(Fuente(D, "GTM-Motor de creditos p.3 (calendar_type 1 = comercial 360)"),),
        oraculo="oraculo_credito.interes_ordinario_dia", estado="validado",
        dossier_pct="96.8",
        dossier_detalle="Exacto a 1e-8 contra el campo `capital` de la BD. 0 de 4,091 mismatch de tasa (feed 08-20).",
        no_conformes=("El 3% restante es LINAJE (P-019): tres tablas guardan `capital` "
                      "(stage / fin_data / current) y discrepan en el valor punto-en-tiempo. "
                      "Los saldos implicitos son fracciones amortizadas sensatas: NO es defecto de motor."),
        clase_no_conforme="linaje", depende_de_logs=True,
        insumos="lc_loan_contract (loan_amount, ordinary_interest_rate, calendar_type) · lc_finantial_data.capital · feed credits-closing-trans",
        autopruebas="reproduce el 20.83 del doc",
        dossier_match={"1e-8": "96.80", "1e-5": None, "centavo": None, "n": "4,091", "sesgo": "no",
                        "nota": "el centavo esta [PEND] y sera >= 96.8; el residuo ~12% es data-sourcing de reserva (P-019), no sesgo de motor"},
    ),
    Motor(
        id="CRED-MOR", nombre="Credito — interes MORATORIO", dominio="COL",
        formula="Moratorio = Capital_Vencido x (tasa_mor/100) x (dias_atraso / DiasAnio)",
        ejemplo="500 @36% 1 dia base 360 -> 0.50",
        fuentes=(Fuente(D, "GTM-Motor de creditos p.3"),),
        oraculo="oraculo_credito.interes_moratorio_dia", estado="validado",
        dossier_pct="81.1",
        dossier_detalle="Exacto a 1e-8 (95.7% dentro de $0.01) contra `capital_venc`, dias=1, 0 mismatch de tasa.",
        no_conformes=("P-020 fue FALSA ALARMA: se comparaba el moratorio redondeado contra el feed "
                      "sin redondear. Resuelto. El residual sub-centavo es granularidad del snapshot "
                      "de capital_venc; ~30 casos fuera son placeholders (capital_venc = 10M) o "
                      "liquidados, misma clase que P-019."),
        clase_no_conforme="redondeo", depende_de_logs=True,
        insumos="lc_finantial_data (capital_venc, mora_days) · lc_loan_contract.moratorium_interest_rate",
        autopruebas="reproduce el 0.50 del doc",
        dossier_match={"1e-8": "81.10", "1e-5": None, "centavo": "95.70", "n": "1,274", "sesgo": "no",
                        "nota": "escalon clasico 81 -> 96: el residuo sub-centavo es granularidad del snapshot, NO defecto. P-020 cerrada"},
    ),
    Motor(
        id="CRED-DIAS", nombre="Credito — conteo de DIAS de devengo", dominio="COL",
        formula="Days N = dias del PERIODO DE AMORTIZACION (topa al periodo), no dias transcurridos",
        ejemplo="CreditAmortizationChargeServiceImpl.java:844 · InterestMoraDays db[N] = dias de mora",
        fuentes=(Fuente(I, "deducido del log del CORE y confirmado contra el doc"),),
        oraculo="(mecanica, sin funcion propia)", estado="validado",
        dossier_detalle="Confirmado. Cierra el residual historico del ordinario, donde usabamos dias transcurridos.",
        no_conformes="Ninguno.", depende_de_logs=True,
        insumos="log del CORE",
    ),
    Motor(
        id="CRED-IVA", nombre="Credito — IVA sobre interes", dominio="COL",
        formula="IVA = Interes x (TasaIVA/100)   ·   16 decimales, Round2 half-up",
        ejemplo="tasa implicita 16.0% en el 95% de las filas",
        fuentes=(Fuente(D, "GTM-Motor de creditos p.4"), Fuente(C, "datos de lc_loan_amortization")),
        oraculo="oraculo_credito.iva_interes", estado="validado",
        dossier_pct="99.0",
        dossier_detalle="54,716 filas con IVA.",
        no_conformes="Redondeo en montos chicos.", clase_no_conforme="redondeo",
        insumos="lc_loan_amortization (interest_amount, interest_tax_amount)",
        dossier_match={"1e-8": "99.00", "1e-5": None, "centavo": None, "n": "54,716", "sesgo": "no",
                        "nota": "el resto es redondeo en montos chicos; tasa implicita 16.0% en el 95%"},
    ),
    Motor(
        id="GAT", nombre="GAT — Ganancia Anual Total (inversion)", dominio="DEV",
        formula=("m = DiasAnio / DiasInversion\n"
                 "GAT Nominal % = Round16( ((Inicial + Interes) / Inicial)^m - 1 ) x 100\n"
                 "GAT Real usa la inflacion punto-en-tiempo"),
        ejemplo="1,000 a 90 dias, interes 200 -> 107.36% nominal / 99.04% real",
        fuentes=(Fuente(D, "GTM-GAT p.5"), Fuente(C, "cat_financial_variables.INFLATIONMXN")),
        oraculo="oraculo_gat.gat_inversion", estado="validado",
        dossier_detalle=("Motor validado por prueba NO circular: `nominal_cgat` resulta ser funcion pura "
                         "de (tasa, plazo) — identico para decenas de miles de inversiones sin importar el "
                         "monto (term7 = 10.42 en 126,465 inversiones) — y el oraculo lo reproduce exacto "
                         "desde la tasa contratada."),
        no_conformes=("El cruce 1-a-1 masivo da 35% porque `iv_payment_plan.interest_amount` posteado no es "
                      "el proyectado en originacion (cancelacion anticipada, tasa real distinta de la nominal). "
                      "Falta la tabla de tramos de tasa (SOL-015). NO es defecto de motor."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-015",),
        insumos="account.nominal_cgat / real_cgat (689,479 inversiones)",
        autopruebas="2/2",
    ),
    Motor(
        id="IFRS9", nombre="IFRS 9 — etapas y reserva por porcentaje", dominio="REG",
        formula=("Etapa 1: 0-30 dias mora · Etapa 2: 31-89 · Etapa 3: >=90\n"
                 "Reserva = (capital + intereses exigibles) x %,  % por (cartera, zona marginada, dias mora)"),
        ejemplo="Cartera de Finsus = CONSUMO · reserva_cap = capital_venc x % en E3 vencido = 65%",
        fuentes=(Fuente(C, "lc_reserve_ifrs — 37 de 37 porcentajes exactos"),
                 Fuente(C, "lc_risk_stage — etapas exactas"),
                 Fuente(D, "GTM-IFRS9 Tablas 1/2/3")),
        oraculo="oraculo_ifrs9.etapa / pct_consumo / reserva_pct", estado="parcial",
        caso_validador="IFRS9-E3",
        dossier_detalle=("C = configuracion real de Aurum: es la validacion mas fuerte del conjunto. "
                         "Corrida propia 2026-08-28 sobre 20,000 filas de etapa 3: CERO violaciones "
                         "al centavo; los porcentajes 75/90/100 del GTM reproducen exactamente lo "
                         "que aplica el core."),
        no_conformes=("[ACLARADO 2026-08-24] El Core NO calcula PD: usa el % directo de CNBV "
                      "(DOF 04/jun/2012) por dias de mora, que es justo lo que validamos 37/37. "
                      "El modelo EI x PI x SP de oraculo_ifrs9 NO aplica al motor de Aurum y queda "
                      "marcado como no usado. La composicion de `reserva_int` tambien quedo definida "
                      "(EPRC cubierta + expuesta + intereses vencidos; en E3 el interes vencido es "
                      "INFORMATIVO y no entra al requerimiento) — eso explica por que no cuadraba "
                      "contra un solo campo. Falta: las 9 tablas de % y las formulas exactas, y "
                      "validar las variantes comercio y reestructurado, que aun no se prueban. "
                      "La prueba de signo marca sesgo (2,381 diferencias sub-centavo, todas "
                      "negativas) y NO es del core: la mitad del sesgo original era nuestro por "
                      "omitir el redondeo half-up que Finsus confirmo, y en el resto el porcentaje "
                      "implicito sale correcto (75.0000 / 90.0001 / 100.0000) — la diferencia esta "
                      "en la precision de la base, que leemos a 4 decimales. Misma clase que P-019."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-015",),
        insumos="lc_risk_stage · lc_reserve_ifrs · lc_finantial_data",
        autopruebas="14/14",
    ),
    Motor(
        id="AMORT", nombre="Amortizacion (tabla francesa)", dominio="COL",
        formula=("Francesa = cuota financiera (capital + interes) CONSTANTE\n"
                 "interes = saldo x tasa/360 x dias   (Actual/360)\n"
                 "capital = cuota - interes ; saldo -> 0"),
        ejemplo="P1 158.33 · P3 112.37 (interes Actual/360 exacto)",
        fuentes=(Fuente(D, "GTM §8.6"), Fuente(C, "lc_loan_amortization")),
        oraculo="oraculo_amortizacion.cuota_francesa / interes_periodo", estado="parcial",
        dossier_pct="99.9",
        dossier_detalle="Identidad de fila 99.9% (794 contratos). En contratos FRESCOS, rollforward / suma de capital / cuota constante = 91.7%.",
        no_conformes=("(a) `capital_remaining_amount` es un campo VIVO que se actualiza con los pagos, asi "
                      "que solo se puede validar en contratos frescos; (b) la cuota sale ~0.1% off por el "
                      "ajuste Actual/360 contra la anualidad; (c) Americana, Italiana y Alemana no tienen "
                      "formula en el doc."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-015",),
        insumos="lc_loan_amortization (capital_amount, interest_amount, total_amount, fechas)",
        autopruebas="6/6",
        dossier_match={"1e-8": None, "1e-5": None, "centavo": "99.90", "n": "794 contratos", "sesgo": None,
                        "nota": "interes Actual/360 EXACTO; el 99.9% es identidad de fila. En contratos frescos 91.7%"},
    ),
    Motor(
        id="CAT", nombre="CAT — Costo Anual Total (credito)", dominio="COL",
        formula=("One Click: CAT = [ (pago_sin_iva / monto_recibido)^(360/dias) - 1 ] x 100\n"
                 "Francesa : la i que iguala VP(disposicion) = VP(pagos), por IRR\n"
                 "pago para CAT = capital + interes + comision/seguro SIN IVA (excluye moratorios y prepago)"),
        ejemplo="autoprueba 3/3 contra el doc: 45.80% · 289,458,538.17% · 34.48%. Caso real exacto: 35.1%",
        fuentes=(Fuente(N, "Circular 21/2009 Banxico"), Fuente(D, "GTM §8"),
                 Fuente(C, "lc_account_commission — apertura 3.99% type=2")),
        oraculo="oraculo_cat.cat_oneclick / cat_frances", estado="parcial",
        dossier_pct="11.6",
        dossier_detalle="El cruce masivo da 11.6%, pero la formula NO esta en duda: reproduce los 3 ejemplos del doc y un caso real exacto.",
        no_conformes=("MEDIDO 2026-08-28: `lc_loan_contract.cat` es un campo MIXTO. En 25,026 de "
                      "31,866 contratos guarda una CONSTANTE copiada — `cat = 27.10` cubre 15,300 "
                      "contratos con 521 plazos y 3,930 montos distintos, y un CAT es funcion del "
                      "monto y del plazo, asi que ahi el campo no es la salida de un motor. CAT-01 "
                      "acota el universo al estrato donde SI varia por contrato (4,220). El residuo "
                      "de ese estrato es la comision realmente cobrada (implicita ~2% contra 3.99% "
                      "configurada): data-sourcing, no formula. La formula reproduce 3/3 el doc."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-015",),
        caso_validador="CAT-01",
        lectura_escalon=(
            "El escalon 23.43% -> 28.50% NO es el diagnostico habitual. "
            "`lc_loan_contract.cat` guarda DOS DECIMALES en las 4,224 filas del "
            "universo, asi que no hay residuo sub-centavo que absorber: 1e-8 y "
            "1e-5 cuentan las coincidencias exactas al centesimo y el centavo "
            "admite una unidad mas en el ultimo decimal. El residuo real es la "
            "comision que se cobro (implicita ~2% contra 3.99% configurada), y "
            "eso es data-sourcing, no formula."),
        insumos="lc_loan_contract.cat · lc_loan_amortization · lc_account_commission",
        autopruebas="3/3 contra el doc",
        dossier_match={"1e-8": None, "1e-5": None, "centavo": None, "volumen": "11.60",
                       "n": "3 ejemplos del doc + caso real", "sesgo": None,
                       "nota": ("El 11.60% NO es una granularidad: es el cruce a VOLUMEN. La formula "
                                "reproduce 3/3 los ejemplos del doc y un caso real exacto (35.1%), "
                                "asi que NO esta en duda. El cruce sale bajo porque "
                                "`lc_loan_contract.cat` guarda en muchos contratos el CAT NOMINAL "
                                "DEL PRODUCTO (miles con cat=27.1), no el per-contrato: es semantica "
                                "del campo, no error de calculo.")},
    ),
    Motor(
        id="MOTOR-B", nombre="Motor B — transaccional diaria (completitud A vs B)", dominio="MOV",
        formula="normalizacion por tipo: PEER 2:1 (cargo+abono -> 1 tx Aurum) · UNI 1:1 (SPEI, servicios)",
        ejemplo="6 dias medidos: OF >= AU siempre, de +0.1% a +2.1%",
        fuentes=(Fuente(I, "clasificacion observada; el catalogo de ~400 tipos sigue pendiente (SOL-014)"),),
        oraculo="motor_b_diario.py", estado="validado",
        dossier_detalle="Robusto: OF >= AU en los 6 dias, es decir sin faltante en AurumCore.",
        no_conformes=("`origin is null` aparece en los queries oficiales solo dentro de subconsultas de "
                      "exclusion. La semantica de origin sigue en disputa (P-013 / SOL-004)."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-004", "SOL-014"),
        caso_validador="DIARIO-B",
    ),
    Motor(
        id="CONTABLE", nombre="Contable — doble partida y amarre", dominio="CTB",
        formula="SUM(debit_amount) + SUM(credit_amount) = 0 por dia   (debito viene negativo)",
        ejemplo="B1 = $0.00 en 0 de 7 dias descuadrados",
        fuentes=(Fuente(C, "transaction_detail + cat_accounting_account"),),
        oraculo="contable_bc.py", estado="validado",
        dossier_pct="100.00", dossier_detalle="B1 doble partida cuadra exacto: 0 de 7 dias con descuadre.",
        no_conformes=("El doc NO mapea tipo_movimiento -> cuenta contable (la matriz esta 'por incorporar'), "
                      "asi que nuestra matriz de amarre es OBSERVADA, no documentada. Alerta abierta: "
                      "producto 2001 con -34% en balanza."),
        clase_no_conforme="data-sourcing", caso_validador="CONTABLE-B1",
    ),
    Motor(
        id="WSO2", nombre="Cuentahabientes — WSO2 contra padron", dominio="MIG",
        formula="set-diff por telefono de 10 digitos, en ambos sentidos",
        ejemplo="Aurum -> WSO2 completo (20 huerfanos)",
        fuentes=(Fuente(C, "um_hybrid_user_role / accountholder"),),
        oraculo="cuentahabientes_wso2.py", estado="parcial",
        dossier_detalle="Aurum -> WSO2 completo. En sentido contrario, 181,844 identidades sin cuenta.",
        no_conformes=("Se interpreta como churn: `accountholder` es 100% ACTIVE, no retiene cerradas, "
                      "mientras WSO2 conserva la identidad tras el cierre. Hasta que Finsus lo confirme "
                      "NO se puede decidir si es defecto de migracion o asimetria esperada."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-007",),
        caso_validador="CUENTAHAB-01",
    ),
)

POR_ID = {m.id: m for m in MOTORES}


def por_categoria() -> dict[str, list[str]]:
    """Motores agrupados para el menu, en el orden declarado de CATEGORIAS."""
    out: dict[str, list[str]] = {c: [] for c in CATEGORIAS}
    for m in MOTORES:
        out.setdefault(m.categoria, []).append(m.id)
    return {k: v for k, v in out.items() if v}


def resumen_cobertura() -> dict[str, Any]:
    """Conteo por estado. Se muestra en el encabezado del tablero."""
    conteo: dict[str, int] = {}
    for m in MOTORES:
        conteo[m.estado] = conteo.get(m.estado, 0) + 1
    return {
        "total": len(MOTORES),
        "por_estado": conteo,
        "por_categoria": por_categoria(),
        "categorias": list(CATEGORIAS),
        "bloqueados_por_logs": [m.id for m in MOTORES if m.depende_de_logs],
        "solicitudes_abiertas": sorted({s for m in MOTORES for s in m.solicitudes}),
    }

# --- Alcance por motor -------------------------------------------------------
# FUENTE: 40_validaciones/INFORME_DETALLADO_AUDITORIA/ (corte 2026-08-26,
# denominadores verificados en BD el 2026-08-28). Se CITA, no se recalcula: los
# denominadores los midio el repo de validacion con acceso a la base, y este
# tablero no los ha reproducido. Donde este tablero SI corrio el caso, el
# alcance dice de que corrida habla.
_I = "40_validaciones/INFORME_DETALLADO_AUDITORIA"

ALCANCE_POR_MOTOR: dict[str, Alcance] = {
    "PLAZO": Alcance(
        si="Interes de inversion a plazo GENERADO por AurumCore (no migrado), todos los periodos del cohorte.",
        no=("Inversiones migradas de openfin (`origin = 'FINSUS'`) — es otro punto.",
            "Cuentas de UN SOLO PAGO: el metodo despeja la tasa del periodo 1 y la "
            "reproduce en los demas, asi que con un solo pago no hay de donde despejar "
            "sin circularidad. Quedan fuera POR METODOLOGIA, no por muestreo.",
            "Productos sin plan de pagos."),
        tipo="censo del cohorte aplicable",
        n="530,195 periodos / 157,999 cuentas",
        universo="1,339,023 periodos live-pagados (de 36,905,411 totales en iv_payment_plan)",
        representatividad="~39.6% de los periodos live-pagados",
        rationale=(
            "CORRECCION DE HONESTIDAD (informe detallado §3): antes se reportaba como "
            "'100% de lo live' y NO lo es. El cohorte exige >= 2 pagos, `interest_paid`, "
            "`interest_amount > 0` e `iv_initial_amount > 0`. Dentro de ese cohorte se "
            "corre el 100% —es censo, no muestra— pero el cohorte es el 39.6% de los "
            "periodos live-pagados. El resultado (0 violaciones en 530,195) no cambia; "
            "el DENOMINADOR si."),
        ref=f"{_I}/01_CAPTACION_FISCAL.md#v-01"),

    "VISTA": Alcance(
        si="Interes mensual de cuenta a la VISTA que Aurum posteo, recalculado por el oraculo.",
        no=("Cuentas sin pago en el ciclo.",
            "El ciclo vivo de agosto: cierra el 31-ago y se re-corre entonces.",
            "El SPM de RENDIMIENTO real: se usa `finsus_account_history`, no la poliza."),
        tipo="cota de extraccion (esta corrida) / censo del ciclo (la cifra citada)",
        n="20,000 pagos (corrida de este tablero)",
        universo="[PEND] para la corrida de este tablero",
        representatividad="[PEND]",
        rationale=(
            "El limite de 20,000 filas es una COTA OPERATIVA para no degradar AurumCore, "
            "que es produccion — no una decision estadistica. La herramienta puede correr "
            "el universo completo en cuanto se acuerde la ventana."),
        nota=(
            "esta corrida es del CIERRE DE AGOSTO sobre una cota de "
            "20,000 filas y da 96.62% al centavo. El informe detallado cita otra cosa: "
            "el CICLO DE JULIO como CENSO de 83,094 cuentas (~100% de los pagadores del "
            "ciclo), con 94.76% a 1e-8 y 95.03% al centavo. Son ciclos y universos "
            "distintos, no una contradiccion — pero tampoco son comparables. "
            "`MATRIZ_TOLERANCIAS.md` mantiene VISTA en [PEND] A PROPOSITO: se sella con "
            "el ciclo vivo del 31-ago."),
        ref=f"{_I}/01_CAPTACION_FISCAL.md#v-04"),

    "SALDO-PROM": Alcance(
        si="El SPM de RENDIMIENTO (distinto del de consulta `account.average_balance_amount`).",
        no=("Todo: el punto declara un bloqueo, no un resultado.",),
        tipo="subconjunto parcial (barrido de logs)",
        n="90 filas / 27 cuentas",
        universo="[PEND] — el dato no esta en la base, esta en la traza de log",
        representatividad="[PEND]",
        rationale=(
            "No hubo eleccion de subconjunto: es lo que el barrido de logs alcanzo a "
            "capturar. Nota del informe: V-04 ya NO depende de este SPM, usa "
            "`finsus_account_history`."),
        ref=f"{_I}/01_CAPTACION_FISCAL.md#v-05"),

    "GAT": Alcance(
        si="El GAT publicado al cliente (`nominal_cgat` / `real_cgat`), como prueba NO-CIRCULAR.",
        no=("El cruce 1-a-1 a volumen sobre todo el padron de inversiones.",
            "El GAT real per-contrato: falta la tabla de tramos de tasa."),
        tipo="estrato de prueba no-circular",
        n="126,465 inversiones (plazo 7)",
        universo="706,600 cuentas de inversion (`account.nominal_cgat > 0`, de 8,325,509 cuentas)",
        representatividad="17.90%",
        rationale=(
            "La validacion NO depende del volumen: si `nominal_cgat` es funcion pura de "
            "(tasa, plazo, 360), reproducirla exacto en 126,465 casos ya lo demuestra. Se "
            "eligio el plazo 7 por ser el de mayor volumen. NOTA: no existe tabla "
            "`investment_account`; las inversiones son filas de `aurumcore.account`."),
        ref=f"{_I}/01_CAPTACION_FISCAL.md#v-06"),

    "ISR": Alcance(
        si="ISR de inversiones con los TRES motores (A openfin / B Aurum / C oraculo).",
        no=("El ISR de cuentas a la VISTA.",
            "Las inversiones que existen en UN solo core: el join las excluye por "
            "construccion, y ese diferencial no se cuantifico.",
            "El cruce masivo per-contrato al pago: requiere el Manual (SOL-015)."),
        tipo="censo del universo comun A ∩ B",
        n="18,599 inversiones / 14,913 clientes",
        universo="el universo comun A ∩ B de inversiones",
        representatividad="100% del comun",
        rationale=(
            "El universo lo define la INTERSECCION, no una muestra: solo se puede comparar "
            "A contra B donde la inversion existe en los dos. El recorte es estructural."),
        ref=f"{_I}/01_CAPTACION_FISCAL.md#v-0708"),

    "ISR-VIVO": Alcance(
        si="El ISR que AurumCore calcula por si mismo despues del cutover.",
        no=("Todo: el punto esta BLOQUEADO por falta de insumo.",),
        tipo="bloqueado",
        n="[PEND]", universo="[PEND]", representatividad="[PEND]",
        rationale=(
            "El ~13% que se ha citado NO es un resultado de validacion sino la senal del "
            "bloqueo: falta el saldo base PUNTO-EN-TIEMPO al momento del pago. Publicarlo "
            "como porcentaje de acierto seria enganoso."),
        ref=f"{_I}/01_CAPTACION_FISCAL.md#v-12"),

    "CRED-ORD": Alcance(
        si="La provision DIARIA de interes ordinario que el core escribe en su feed operativo.",
        no=("El interes moratorio (otro punto, otra base y otra tasa).",
            "Contratos sin provision ese dia.",
            "Que la tasa pactada sea la correcta contra el contrato: solo que la del feed "
            "coincida con la de la DB (0 mismatch en 4,091)."),
        tipo="censo del dia",
        n="4,091 provisiones ordinarias",
        universo="todas las provisiones ordinarias del feed 2026-08-20 (4,945 contratos con evento; 31,867 contratos en total)",
        representatividad="100% del dia",
        rationale=(
            "El universo lo define el EVENTO, no una muestra: la provision diaria es el "
            "acto de calculo que se audita, y el feed del dia trae todos los contratos que "
            "devengaron. Un solo dia porque el feed lo produce un proceso de extraccion de "
            "logs aparte, no una consulta a la base."),
        ref=f"{_I}/02_CREDITO.md#v-13"),

    "CRED-MOR": Alcance(
        si="Provision diaria de interes MORATORIO sobre capital vencido.",
        no=("Contratos sin mora.",
            "La correccion de la CLASIFICACION en mora: se toma el `capital_venc` que el "
            "core declara."),
        tipo="censo del dia",
        n="1,274 provisiones moratorias (692 con `capital_venc`)",
        universo="todas las provisiones moratorias del feed 2026-08-20",
        representatividad="100% del dia",
        rationale=(
            "Mismo criterio que ordinario. El sub-recorte a 692 no es eleccion sino "
            "consecuencia: comparar contra un `capital_venc` de cero no prueba nada, y "
            "contarlas como no conformes acusaria al motor de un dato que no existe. Las "
            "582 restantes se declaran, no se esconden."),
        ref=f"{_I}/02_CREDITO.md#v-14"),

    "CRED-DIAS": Alcance(
        si="Que los dias de provision sean los del PERIODO de amortizacion, no los transcurridos.",
        no=("El monto del interes.",),
        tipo="verificacion de mecanica",
        n="3 contratos (traza de log)",
        universo="[PEND]", representatividad="no aplica",
        rationale=(
            "Es una pregunta BINARIA sobre la convencion del motor. Tres trazas con el "
            "mismo comportamiento la contestan; trescientas no la contestarian mejor. Lo "
            "que n=3 NO puede decir es si hay productos con otra convencion."),
        ref=f"{_I}/02_CREDITO.md#v-15"),

    "CRED-IVA": Alcance(
        si="IVA sobre el interes de credito.",
        no=("Productos que no gravan.",
            "Que la tasa de 16% sea la aplicable a cada cliente (exenciones, frontera)."),
        tipo="censo",
        n="54,716 filas",
        universo="55,636 filas con IVA > 0 (de 102,605 filas de amortizacion)",
        representatividad="98.35% de las filas con IVA",
        rationale=(
            "El recorte 'filas con IVA' es estructural: una fila sin IVA no tiene nada que "
            "validar. No hubo muestreo, se tomaron todas."),
        ref=f"{_I}/02_CREDITO.md#v-16"),

    "AMORT": Alcance(
        si="Mecanica de la tabla: cuota constante, interes Actual/360, capital = cuota - interes, saldo -> 0.",
        no=("Amortizacion AMERICANA, ITALIANA y ALEMANA: no tienen formula en el doc.",
            "Contratos CON pagos aplicados: `capital_remaining_amount` es un campo VIVO."),
        tipo="subconjunto por linaje",
        n="794 contratos",
        universo="31,970 contratos con tabla de amortizacion",
        representatividad="2.48%",
        rationale=(
            "El recorte es METODOLOGICO, no de volumen: en un contrato con pagos el "
            "`capital_remaining_amount` ya se movio, asi que compararlo contra la tabla "
            "original daria diferencias del paso del tiempo, no del motor. Validar donde "
            "la comparacion es JUSTA y declarar el resto es preferible a un porcentaje mas "
            "grande y sin significado."),
        ref=f"{_I}/02_CREDITO.md#v-17"),

    "CAT": Alcance(
        si="El CAT per-contrato (Circular 21/2009), sobre el estrato donde `cat` de verdad varia por contrato.",
        no=("Los 25,026 contratos con `cat` CONSTANTE copiada: no es un calculo, comparar "
            "contra el no mide el motor.",
            "Los 2,576 con `cat = 0`: es el hallazgo A28-CAT-CERO, no un cuadre.",
            "El CAT de amortizacion italiana y alemana."),
        tipo="subconjunto estratificado",
        n="4,225 contratos (corrida de este tablero)",
        universo="31,867 contratos de credito (25,026 constante / 4,220 per-contrato / 2,576 cat=0 / 44 sin cat)",
        representatividad="13.2% es el estrato con CAT real",
        rationale=(
            "El recorte NO busca subir el porcentaje: busca que el porcentaje SIGNIFIQUE "
            "algo. Un CAT es funcion del monto y del plazo, asi que `cat = 27.10` en 15,300 "
            "contratos con 3,930 montos distintos es una constante, no un calculo. El "
            "11.6% global medía EL CAMPO, no el CAT."),
        nota=(
            "DISCREPANCIA MENOR ABIERTA: este tablero midio 31,866 contratos el 2026-08-28 "
            "y el informe detallado dice 31,867. Un contrato de diferencia, probablemente "
            "por el momento de la medicion. Se levanta en vez de alinearlo en silencio."),
        ref=f"{_I}/02_CREDITO.md#v-18"),

    "IFRS9": Alcance(
        si="Las etapas (mora -> etapa) y los % de reserva, y la aplicacion en E3.",
        no=("Etapas 1 y 2 amortizando: la base depende de un spec pendiente.",
            "La composicion de `reserva_int`: definida el 2026-08-24 pero sin formulas.",
            "Cartera COMERCIAL y creditos REESTRUCTURADOS: faltan las 9 tablas.",
            "Zona MARGINADA: el staging no trae la zona, se asume no marginada."),
        tipo="censo de la config + corrida sobre cota de extraccion",
        n="37/37 celdas de config · 20,000 filas de staging (corrida de este tablero)",
        universo="toda la tabla `lc_reserve_ifrs` + `lc_risk_stage`",
        representatividad="100% de la config",
        rationale=(
            "ALCANCE DELIBERADAMENTE ESTRECHO: solo etapa 3, consumo, zona no marginada — "
            "la parte donde la regla esta CERRADA en la fuente. Cubrir E1/E2 hoy exigiria "
            "inventar la base de calculo. La INDEPENDENCIA es lo que da valor: el % de C "
            "sale del GTM, no de `lc_reserve_ifrs`; que ademas coincida 37/37 es un "
            "RESULTADO, no el metodo."),
        ref=f"{_I}/02_CREDITO.md#v-19"),

    "MOTOR-B": Alcance(
        si="Que NO FALTE ninguna operacion de openfin (A) en AurumCore (B), por dia.",
        no=("El cruce instancia-a-instancia: falta el crosswalk de tipos (SOL-004).",
            "Que los importes cuadren: solo que el conteo de B no sea menor que el de A."),
        tipo="censo por dia",
        n="6 dias (21K-29K operaciones por dia)",
        universo="todas las operaciones de esos 6 dias",
        representatividad="100% de 6 dias",
        rationale=(
            "Seis dias CONSECUTIVOS, no sueltos: la completitud se rompe por lotes, asi "
            "que dias seguidos detectan el hueco y dias dispersos no. Ampliable a mas dias."),
        ref=f"{_I}/03_CONTABLE_PADRON.md#v-20"),

    "CONTABLE": Alcance(
        si="Que cada dia la suma de debitos mas creditos sea exactamente 0.00.",
        no=("El amarre contra saldos y el mapeo a cuenta contable: la doble partida cuadra "
            "aunque el mapeo sea erroneo. La alerta de balanza (producto 2001) es de otra "
            "naturaleza y sigue abierta.",),
        tipo="censo por dia",
        n="7 dias (17K-220K asientos por dia)",
        universo="todos los asientos de esos 7 dias",
        representatividad="100% de 7 dias",
        rationale=(
            "La doble partida es una identidad EXACTA, no un estimador: si un dia cuadra a "
            "0.00, cuadra, sin margen muestral. Siete dias consecutivos cubren un ciclo "
            "semanal completo, incluido el fin de semana, que es cuando los batch se "
            "comportan distinto."),
        ref=f"{_I}/03_CONTABLE_PADRON.md#v-2122"),

    "WSO2": Alcance(
        si="Cobertura BIDIRECCIONAL entre el proveedor de identidad y el padron.",
        no=("La semantica del ciclo de vida de identidad: la asimetria se ESPERA (P-017) y "
            "esa explicacion no esta verificada.",),
        tipo="censo bidireccional",
        n="20 huerfanos / 181,850 / 295 altas incompletas",
        universo="todo el padron contra todo WSO2",
        representatividad="100%",
        rationale=(
            "No hay subconjunto: se cruzaron los dos padrones completos. Lo que falta "
            "declarar es el TAMANO de cada uno, para que 20 y 181,850 se lean como "
            "fracciones y no como numeros sueltos."),
        ref=f"{_I}/03_CONTABLE_PADRON.md#v-23"),
}

for _mid, _a in ALCANCE_POR_MOTOR.items():
    POR_ID[_mid].alcance = _a
