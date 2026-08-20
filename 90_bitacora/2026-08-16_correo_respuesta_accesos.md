# Borrador de respuesta — Solicitud de accesos (para enviar por David/Linko)

> No enviado por Claude. Revísalo y envíalo tú. Responde al correo de Armando Gutiérrez (infra),
> con copia a los mismos + Mario Ahumada (espacio) y Ernesto Muciño (esquema de conciliación).

**Asunto:** RE: Solicitud de accesos — Modelo de conciliación de cores

---

Estimado Armando, estimados todos:

Gracias por la guía. Respondemos puntualmente cada requerimiento para que puedan dimensionar y proceder:

**1) Espacio para alojar la información de conciliación**
Requerimos un **esquema (o base) independiente, administrado por nosotros**, exclusivo para las tablas de comprobación del proceso. **No escribiremos en ningún esquema de los cores ni de Reportes Unificados**; toda escritura queda contenida en ese espacio aislado. Quedamos atentos a lo que defina Mario Ahumada respecto a su ubicación.

**2) Volumetría estimada (carga inicial y crecimiento)**
Con base en el corte del 02–03 de agosto que ya analizamos:
- Clientes: ~956 mil
- Cuentas a la vista: ~2.05 millones
- Inversiones: ~18.6 mil
- Créditos One Click (5004): ~7.7 mil
- Transacciones: ~20 mil/día

Un corte completo de ambos cores pesa ≈ **1.5 GB**. Sumando nuestras tablas de comprobación e histórico de corridas, estimamos dimensionar el espacio en el **orden de decenas de GB**. Crecimiento aproximado: ~20 mil transacciones/día más los snapshots diarios.

**3) Base/esquema donde se realizará la conciliación**
La conciliación corre en **nuestro esquema independiente** (punto 1). Ahí materializamos cálculos y comparativos; las fuentes se consultan solo en lectura. Atentos a lo que valide Ernesto Muciño.

**4) Lectura vs lectura/escritura**
- **Lectura:** OpenFin (réplica t-1), AurumCore y Base de Reportes Unificados.
- **Lectura/escritura:** únicamente sobre nuestro esquema de comprobación.

Nota sobre t-1: para construir e iterar el modelo, la **t-1 nos es suficiente**. Sin embargo, para las cifras que formen parte de la **evidencia final de certificación**, necesitaremos poder **revalidarlas contra productiva** (por consistencia de fuente). Agradeceremos dejar previsto ese camino de validación.

**5) Tablas/esquemas a consultar**
- **OpenFin (Captación):** `asociados`, `acreedores`, `deudores`, `detalle_auxiliar`, `detalle_auxiliar_masdatos`.
- **AurumCore (esquema `aurumcore`):** `accountholder`, `account`, `account_scheme`, `account_yield`, `stored_value`, `iv_account_commission`, `iv_payment_plan`, `lc_loan_contract`, `lc_products`, `lc_loan_charge`, `"transaction"`.
- **Reportes Unificados:** balance y detalle de movimientos (para cotejo).

**6) Servidores origen/destino y puertos**
Es el dato que nos falta de su lado. En particular, quedamos atentos a los **datos de conexión de AurumCore** (servidor/base/puerto) y a la confirmación de host/puerto de **OpenFin t-1** y de **Reportes Unificados**. Con eso completamos la matriz origen–destino.

**7) Conectividad y accesos de red**
Una vez confirmados servidores y puertos (punto 6), validamos conectividad extremo a extremo y los permisos sobre las bases/esquemas definidos.

**Usuarios a habilitar (accesos + VPN):**
- David López — dlopez@linko.mx
- José Vargas — jevargas@linko.mx
- Salvador Munguía — smunguia@linko.mx
- Reinier Alonso — ralonso@linko.mx
- Mario Urbina — murbina@linko.mx

Si les resulta más ágil, agendamos 20 minutos para cerrar los puntos **1** (espacio de escritura) y **6** (datos de conexión) y destrabar el resto.

Quedamos atentos. Gracias y saludos,
David López
Linko
