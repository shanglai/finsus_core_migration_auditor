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

    @property
    def categoria(self) -> str:
        return CATEGORIA_POR_MOTOR.get(self.id, "Otros")

    @property
    def tolerancia_propia(self) -> tuple[str, str] | None:
        return TOLERANCIA_PROPIA.get(self.id)

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
        dossier_detalle=("DESTRABADO 2026-08-24: ya no hay que esperar al 31-ago. El SPM se "
                         "reconstruye de `aurumcore.finsus_account_history` y reconcilia el 82.1% "
                         "de los posteos reales del 31-jul (70.7% con dt=31 fijo)."),
        insumos="finsus_account_history (average_balance_amount, interest_rate, iv_term_days) + esquema de rendimientos",
        bloqueo=("Ya NO es bloqueo de tiempo. El 18% residual depende de dos cosas: la convencion "
                 "exacta de `dt` (inclusivo en ambos extremos, el dia de fondeo no cuenta) y el "
                 "SPM-de-RENDIMIENTO, que Finsus dice se guarda en la poliza de intereses y PUEDE "
                 "DIFERIR del average de consulta. En transaction_detail no esta."),
        no_conformes=("Corrida del 2026-08-28 sobre el posteo del 31-jul (5,000 cuentas): 91.52% "
                      "conforme, 424 no conformes, y la prueba de signo marca SESGO. El sesgo es "
                      "del METODO, no de AurumCore, y se puede demostrar: de esos 424, "
                      "378 (89%) no tienen NINGUN dt entero que reproduzca el posteo — el SPM que "
                      "leemos no es el que uso el core — y de los 46 restantes, 44 tienen un dt "
                      "real MENOR que el nuestro. Las dos causas empujan C por arriba de B, que es "
                      "el signo observado. Leerlo como defecto del motor de vista seria una "
                      "acusacion falsa; se cierra con el SPM de la poliza (SOL-003)."),
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
        dossier_detalle="C = configuracion real de Aurum: es la validacion mas fuerte que tenemos en el conjunto.",
        no_conformes=("[ACLARADO 2026-08-24] El Core NO calcula PD: usa el % directo de CNBV "
                      "(DOF 04/jun/2012) por dias de mora, que es justo lo que validamos 37/37. "
                      "El modelo EI x PI x SP de oraculo_ifrs9 NO aplica al motor de Aurum y queda "
                      "marcado como no usado. La composicion de `reserva_int` tambien quedo definida "
                      "(EPRC cubierta + expuesta + intereses vencidos; en E3 el interes vencido es "
                      "INFORMATIVO y no entra al requerimiento) — eso explica por que no cuadraba "
                      "contra un solo campo. Falta: las 9 tablas de % y las formulas exactas, y "
                      "validar las variantes comercio y reestructurado, que aun no se prueban."),
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
        no_conformes=("`lc_loan_contract.cat` guarda en muchos contratos el CAT NOMINAL DEL PRODUCTO "
                      "(miles con cat = 27.1), no el CAT por contrato. Es semantica del campo, no error de "
                      "calculo. Falta confirmar esa semantica y la convencion de dias (SOL-015)."),
        clase_no_conforme="data-sourcing", solicitudes=("SOL-015",),
        insumos="lc_loan_contract.cat · lc_loan_amortization · lc_account_commission",
        autopruebas="3/3 contra el doc",
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
