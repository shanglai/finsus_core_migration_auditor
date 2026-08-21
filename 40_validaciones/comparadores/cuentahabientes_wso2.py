"""
CUENTAHAB-01 — Conciliacion de identidad WSO2 (identityshared) <-> AurumCore (accountholder).

Tercero independiente. Cruza el padron de identidades (WSO2) contra el padron de cuentahabientes
(AurumCore) y DEVUELVE LAS VIOLACIONES (cero filas = pasa). No all-pass.

Insumos (exportados por Finsus a landing/, ver extraccion/wso2_cuentahabientes.sql):
  - wso2_clientes_roles.csv : phone + matriz de roles CTP de onboarding
  - aurum_accountholders.csv: accountholder_id/number, username, contact_mobile_phone, email

Llave: telefono de 10 digitos. WSO2.phone  <->  Aurum.username (o contact_mobile_phone normalizado).

Uso:  python cuentahabientes_wso2.py
"""
import sys
from pathlib import Path
import duckdb
import polars as pl
sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
LAND = RAIZ / "landing"
RES = RAIZ / "40_validaciones" / "_resultados"
RES.mkdir(exist_ok=True)
WSO2 = LAND / "wso2_clientes_roles.csv"
AUR = LAND / "aurum_accountholders.csv"

con = duckdb.connect()  # base analitica propia (in-memory)
con.execute(f"""
  create view wso2 as
  select trim(phone) as phone,
         (r_created='t' or r_created=true) as r_created,
         (r_confirmed='t' or r_confirmed=true) as r_confirmed,
         (r_accounts='t' or r_accounts=true) as r_accounts,
         (r_investments='t' or r_investments=true) as r_investments,
         (r_cards='t' or r_cards=true) as r_cards,
         total_roles
  from read_csv_auto('{WSO2.as_posix()}', header=true, all_varchar=true)
""")
con.execute(f"""
  create view aur as
  select accountholder_id, accountholder_number, external_id,
         nullif(trim(username),'') as username,
         regexp_replace(coalesce(contact_mobile_phone,''),'[^0-9]','','g') as phone_norm,
         nullif(trim(email),'') as email
  from read_csv_auto('{AUR.as_posix()}', header=true, all_varchar=true)
""")

# Universos normalizados (telefono 10 digitos valido)
con.execute("""create view wso2_tel as
  select phone from wso2 where regexp_matches(phone,'^[0-9]{10}$')""")
con.execute("""create view aur_tel as
  select accountholder_id, accountholder_number,
      (accountholder_number not like '201-%') as es_cliente,   -- 201 = fondeadora (K-MIG-004)
      coalesce(
      case when regexp_matches(coalesce(username,''),'^[0-9]{10}$') then username end,
      case when length(phone_norm)>=10 then right(phone_norm,10) end) as tel,
      username, email
  from aur""")

def n(sql):
    return con.execute(sql).fetchone()[0]

def save(nombre, sql):
    out = (RES / f"cuentahab_{nombre}.csv").as_posix()
    con.execute(f"COPY ({sql}) TO '{out}' (HEADER, FORMAT CSV)")

print("=== CUENTAHAB-01 · Conciliacion WSO2 <-> AurumCore ===\n")

# Volumetria
w_tot = n("select count(distinct phone) from wso2")
w_tel = n("select count(distinct phone) from wso2_tel")
a_tot = n("select count(*) from aur")
a_tel = n("select count(distinct tel) from aur_tel where tel is not null")
print(f"WSO2  identidades distintas : {w_tot:>10,}   (telefono valido 10d: {w_tel:,})")
print(f"Aurum accountholders        : {a_tot:>10,}   (telefono valido 10d: {a_tel:,})")
print(f"Delta padron (WSO2 - Aurum) : {w_tot - a_tot:>+10,}\n")

# --- VIOLACION 1: identidad en WSO2 y NO en Aurum ---
v1 = n("""select count(*) from wso2_tel w
          where not exists (select 1 from aur_tel a where a.tel=w.phone)""")
# --- VIOLACION 2: accountholder en Aurum y NO en WSO2 (descompuesto) ---
v2_bruto = n("""select count(*) from aur_tel a where a.tel is not null
          and not exists (select 1 from wso2_tel w where w.phone=a.tel)""")
v2_suc201 = n("""select count(*) from aur_tel a where a.tel is not null and not a.es_cliente
          and not exists (select 1 from wso2_tel w where w.phone=a.tel)""")
v2_sintel = n("""select count(*) from aur_tel a where a.es_cliente
          and (a.tel is null or not regexp_matches(a.tel,'^[0-9]{10}$'))""")
v2 = n("""select count(*) from aur_tel a
          where a.es_cliente and a.tel is not null and regexp_matches(a.tel,'^[0-9]{10}$')
          and not exists (select 1 from wso2_tel w where w.phone=a.tel)""")
# --- VIOLACION 3: altas incompletas (created sin confirmed/accounts/investments) ---
v3_conf = n("select count(*) from wso2 where r_created and not r_confirmed")
v3_acc = n("select count(*) from wso2 where r_created and not r_accounts")
v3_inv = n("select count(*) from wso2 where r_created and not r_investments")
# --- VIOLACION 4: integridad ---
i_nul = n("select count(*) from wso2 where phone is null or phone=''")
i_mal = n("select count(*) from wso2 where phone<>'' and not regexp_matches(phone,'^[0-9]{10}$') and phone not like '%@%'")
a_sinuser = n("select count(*) from aur where username is null")
a_sinmail = n("select count(*) from aur where email is null")
# --- VIOLACION 5: telefono duplicado en Aurum (mismo tel, >1 accountholder) ---
v5 = n("""select count(*) from (select tel from aur_tel where tel is not null
          group by tel having count(*)>1) x""")

print("VIOLACIONES (cero = pasa):")
print(f"  1. En WSO2 y NO en Aurum (roles compl.) {v1:>10,}")
print(f"  2. En Aurum-CLIENTE y NO en WSO2 ...... {v2:>10,}   (real, excl. fondeadora)")
print(f"       - bruto (con contaminacion) ...... {v2_bruto:>10,}")
print(f"       - de esos, sucursal 201 (fond.) .. {v2_suc201:>10,}")
print(f"       - cliente sin telefono valido .... {v2_sintel:>10,}")
print(f"  3. Altas incompletas (created sin ...):")
print(f"       - sin confirmed .................. {v3_conf:>10,}")
print(f"       - sin accounts ................... {v3_acc:>10,}")
print(f"       - sin investments ................ {v3_inv:>10,}")
print(f"  4. Integridad:")
print(f"       - WSO2 phone nulo/vacio .......... {i_nul:>10,}")
print(f"       - WSO2 phone malformado .......... {i_mal:>10,}")
print(f"       - Aurum sin username ............. {a_sinuser:>10,}")
print(f"       - Aurum sin email ................ {a_sinmail:>10,}")
print(f"  5. Telefono duplicado en Aurum (>1 ah). {v5:>10,}")

# Guardar sets de violacion
save("wso2_no_en_aurum", "select w.phone from wso2_tel w where not exists (select 1 from aur_tel a where a.tel=w.phone)")
save("aurum_no_en_wso2", "select a.accountholder_id, a.accountholder_number, a.tel from aur_tel a where a.es_cliente and a.tel is not null and regexp_matches(a.tel,'^[0-9]{10}$') and not exists (select 1 from wso2_tel w where w.phone=a.tel)")
save("altas_incompletas", "select phone, r_confirmed, r_accounts, r_investments from wso2 where r_created and (not r_confirmed or not r_accounts or not r_investments)")
save("tel_duplicado_aurum", "select tel, count(*) n from aur_tel where tel is not null group by tel having count(*)>1 order by n desc")

print(f"\nSets de violacion guardados en {RES}/cuentahab_*.parquet")
con.close()
