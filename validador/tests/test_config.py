# -*- coding: utf-8 -*-
"""Resolucion de credenciales — SIN BD y SIN credenciales reales.

Ningun test de este archivo lee un db_connections.yaml real: todos construyen
diccionarios en memoria. La contrasena nunca se escribe en el repositorio ni
en la evidencia.
"""

import pytest

from engine import config
from engine.errores import ConexionNoConfigurada

FORMA_VALIDADOR = {
    "cores": {"aurum": {"host": "h1", "dbname": "aurumcore"}},
    "extraccion": {"max_filas": 123},
}
FORMA_PREVIA = {                      # convencion de fase1_isr_runner.py
    "aurum": {"host": "h1", "dbname": "aurumcore"},
    "openfin": {"host": "h2", "dbname": "openfin_aurum"},
}


def test_acepta_la_forma_anidada_del_validador():
    d = config._normalizar_conexiones(FORMA_VALIDADOR)
    assert sorted(d["cores"]) == ["aurum"]
    assert d["extraccion"]["max_filas"] == 123


def test_acepta_la_forma_previa_del_repositorio():
    """El repo ya tenia db_connections.yaml en la raiz, sin la llave `cores:`.

    Aceptar las dos formas evita el fallo mas tonto posible: credenciales
    correctas y un 'no hay conexion configurada' por la sangria del archivo.
    """
    d = config._normalizar_conexiones(FORMA_PREVIA)
    assert sorted(d["cores"]) == ["aurum", "openfin"]
    assert d["cores"]["openfin"]["dbname"] == "openfin_aurum"


def test_no_pierde_destinos_adicionales():
    """El archivo real trae un tercer destino (`identityshared`).

    Reconocer los cores por una lista de nombres conocidos lo habria dejado
    fuera en silencio. Se reconocen por forma: un bloque con host+dbname (o
    dsn) es una conexion.
    """
    d = config._normalizar_conexiones({
        "aurum": {"host": "h1", "dbname": "aurumcore"},
        "openfin": {"host": "h2", "dbname": "openfin_aurum"},
        "identityshared": {"host": "h3", "dbname": "wso2_identity_shared_db"},
    })
    assert sorted(d["cores"]) == ["aurum", "identityshared", "openfin"]


def test_no_confunde_los_bloques_de_configuracion_con_cores():
    """`extraccion:` y `warehouse:` no tienen host: no son destinos."""
    d = config._normalizar_conexiones({
        "aurum": {"host": "h1", "dbname": "aurumcore"},
        "extraccion": {"max_filas": 1000},
        "warehouse": {"ruta": "datos/x.duckdb"},
    })
    assert sorted(d["cores"]) == ["aurum"]
    assert d["extraccion"]["max_filas"] == 1000
    assert d["warehouse"]["ruta"] == "datos/x.duckdb"


def test_archivo_vacio_no_revienta():
    assert config._normalizar_conexiones({}) == {}
    assert config._normalizar_conexiones(None) == {}


def test_core_faltante_dice_donde_busco():
    with pytest.raises(ConexionNoConfigurada) as exc:
        config.config_core("openfin", FORMA_VALIDADOR)
    mensaje = str(exc.value)
    assert "db_connections.yaml" in mensaje
    assert "SOLO LECTURA" in mensaje


def test_password_desde_variable_de_ambiente(monkeypatch):
    """Preferimos la variable de ambiente al texto plano en el archivo."""
    monkeypatch.setenv("PRUEBA_RO_PASSWORD", "no-es-real")
    cfg = config.config_core("aurum", {
        "cores": {"aurum": {"host": "h", "password_env": "PRUEBA_RO_PASSWORD"}}
    })
    assert cfg["password"] == "no-es-real"
    assert "password_env" not in cfg


def test_password_env_sin_definir_falla_en_vez_de_conectar_sin_ella(monkeypatch):
    monkeypatch.delenv("PRUEBA_RO_PASSWORD", raising=False)
    with pytest.raises(ConexionNoConfigurada, match="ambiente"):
        config.config_core("aurum", {
            "cores": {"aurum": {"host": "h", "password_env": "PRUEBA_RO_PASSWORD"}}
        })


def test_dsn_por_ambiente_paridad_con_el_runner_previo(monkeypatch):
    """fase1_isr_runner.py acepta OF_DSN / AC_DSN. El VALIDADOR tambien."""
    monkeypatch.setenv("AC_DSN", "postgresql://ro@host/aurumcore")
    cfg = config.config_core("aurum", {"cores": {"aurum": {}}})
    assert cfg["dsn"] == "postgresql://ro@host/aurumcore"


def test_se_busca_en_validador_y_en_la_raiz_del_repo():
    rutas = [p.name for p in config.UBICACIONES_CONEXIONES]
    assert rutas == ["db_connections.yaml", "db_connections.yaml"]
    padres = [p.parent.name for p in config.UBICACIONES_CONEXIONES]
    assert padres[0] == "validador"
    assert config.UBICACIONES_CONEXIONES[1].parent == config.RAIZ_REPO


def test_el_archivo_de_credenciales_no_esta_versionado():
    """Invariante de seguridad: si esto falla, hay credenciales en git."""
    import subprocess
    salida = subprocess.run(
        ["git", "ls-files", "db_connections.yaml", "validador/db_connections.yaml"],
        cwd=config.RAIZ_REPO, capture_output=True, text=True,
    )
    assert not salida.stdout.strip(), \
        f"HAY CREDENCIALES VERSIONADAS: {salida.stdout.strip()}"


def test_la_plantilla_no_trae_una_password_real():
    texto = config.ARCHIVO_CONEXIONES_EJEMPLO.read_text(encoding="utf-8")
    for linea in texto.splitlines():
        limpia = linea.strip()
        if limpia.startswith("password:"):
            pytest.fail(f"la plantilla trae una password sin comentar: {limpia}")
