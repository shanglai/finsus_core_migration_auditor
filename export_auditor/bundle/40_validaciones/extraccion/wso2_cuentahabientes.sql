-- =====================================================================
-- Cuentahabientes / identidad — extracción para conciliación WSO2 <-> AurumCore
-- SOLO LECTURA. Correr cada bloque en su base. Exportar los CSV y subirlos a landing/.
-- Llave: WSO2 um_user_name = telefono 10 dig (MSISDN) para clientes (roles CTP_*).
--        En Aurum casa contra accountholder.username / contact_mobile_phone.
-- =====================================================================

-- #####################################################################
-- BLOQUE 1 — base WSO2 (identityshared: 10.10.160.27 / wso2_identity_shared_db)
-- #####################################################################

-- W1. Volumetria de identidades (paste-and-see)
SELECT count(DISTINCT um_user_name) AS usuarios_distintos,
       count(*)                     AS role_links
FROM public.um_hybrid_user_role;

-- W2. Universo por rol (clientes CTP_* vs staff AP_*) (paste-and-see)
SELECT r.um_id, r.um_role_name, count(ur.um_user_name) AS usuarios
FROM public.um_hybrid_role r
LEFT JOIN public.um_hybrid_user_role ur ON ur.um_role_id = r.um_id
GROUP BY 1,2 ORDER BY usuarios DESC;

-- W3. Integridad de username (deben ser telefono 10 dig; staff son correo) (paste-and-see)
SELECT count(*)                                                          AS usuarios,
       count(*) FILTER (WHERE um_user_name IS NULL OR btrim(um_user_name)='') AS nulos,
       count(*) FILTER (WHERE um_user_name LIKE '%@%')                  AS tipo_correo_staff,
       count(*) FILTER (WHERE um_user_name !~ '^[0-9]{10}$'
                         AND um_user_name NOT LIKE '%@%')               AS malformados
FROM (SELECT DISTINCT um_user_name FROM public.um_hybrid_user_role) x;

-- W4. EXPORT -> wso2_clientes_roles.csv : clientes CTP con su matriz de roles de onboarding
--     (para detectar altas incompletas: created sin confirmed/accounts/investments)
\copy (SELECT ur.um_user_name AS phone, bool_or(ur.um_role_id=42) AS r_created, bool_or(ur.um_role_id=41) AS r_confirmed, bool_or(ur.um_role_id=40) AS r_completed, bool_or(ur.um_role_id=43) AS r_accounts, bool_or(ur.um_role_id=47) AS r_payments, bool_or(ur.um_role_id=45) AS r_cards, bool_or(ur.um_role_id=46) AS r_investments, bool_or(ur.um_role_id=48) AS r_profile, count(*) AS total_roles FROM public.um_hybrid_user_role ur WHERE ur.um_role_id IN (40,41,42,43,45,46,47,48) GROUP BY 1) TO 'wso2_clientes_roles.csv' WITH CSV HEADER;


-- #####################################################################
-- BLOQUE 2 — base AurumCore (aurum: 10.10.160.53 / aurumcore)
-- #####################################################################

-- A1. Volumetria accountholder + cobertura de llaves candidatas (paste-and-see)
SELECT count(*)                                                        AS accountholders,
       count(*) FILTER (WHERE username ~ '^[0-9]{10}$')               AS username_tel10,
       count(*) FILTER (WHERE regexp_replace(coalesce(contact_mobile_phone,''),'[^0-9]','','g') ~ '[0-9]{10}$') AS phone_10,
       count(*) FILTER (WHERE email IS NULL OR btrim(email)='')       AS sin_email
FROM aurumcore.accountholder;

-- A2. EXPORT -> aurum_accountholders.csv : padron para el cruce (llaves candidatas)
\copy (SELECT accountholder_id, accountholder_number, external_id, username, contact_mobile_phone, email FROM aurumcore.accountholder) TO 'aurum_accountholders.csv' WITH CSV HEADER;
